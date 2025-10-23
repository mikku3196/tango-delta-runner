#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Chimera 監視ダッシュボード
Webベースの監視ダッシュボード
"""

import os
import json
import time
import psutil
from datetime import datetime, timedelta
from pathlib import Path
from flask import Flask, render_template, jsonify, request
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # GUI不要のバックエンド
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

class ChimeraDashboard:
    def __init__(self):
        self.log_dir = Path("logs")
        self.backtest_dir = Path("logs/backtest_results")
        
    def get_system_status(self):
        """システム状態を取得"""
        try:
            # プロセス確認
            chimera_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent']):
                try:
                    if proc.info['cmdline'] and any('main_controller.py' in cmd for cmd in proc.info['cmdline']):
                        chimera_processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cpu_percent': proc.info['cpu_percent'],
                            'memory_percent': proc.info['memory_percent']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # システムリソース
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'timestamp': datetime.now().isoformat(),
                'processes': chimera_processes,
                'system': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_used': memory.used,
                    'memory_total': memory.total,
                    'disk_percent': disk.percent,
                    'disk_used': disk.used,
                    'disk_total': disk.total
                }
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_log_summary(self):
        """ログサマリーを取得"""
        try:
            log_files = list(self.log_dir.glob("chimera_*.log"))
            if not log_files:
                return {'error': 'No log files found'}
            
            # 最新のログファイルを取得
            latest_log = max(log_files, key=os.path.getmtime)
            
            # ログファイルの基本情報
            stat = latest_log.stat()
            
            # ログエントリ数をカウント
            with open(latest_log, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # ログレベル別カウント
            level_counts = {'INFO': 0, 'WARNING': 0, 'ERROR': 0, 'CRITICAL': 0}
            for line in lines[-1000:]:  # 最新1000行のみ
                try:
                    log_entry = json.loads(line.strip())
                    level = log_entry.get('level', 'INFO')
                    if level in level_counts:
                        level_counts[level] += 1
                except json.JSONDecodeError:
                    continue
            
            return {
                'latest_log_file': latest_log.name,
                'file_size': stat.st_size,
                'last_modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'total_lines': len(lines),
                'level_counts': level_counts
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_trading_summary(self):
        """取引サマリーを取得"""
        try:
            log_files = list(self.log_dir.glob("chimera_*.log"))
            if not log_files:
                return {'error': 'No log files found'}
            
            # 最新のログファイルを取得
            latest_log = max(log_files, key=os.path.getmtime)
            
            trades = []
            with open(latest_log, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        log_entry = json.loads(line.strip())
                        if log_entry.get('module') == 'TRADE':
                            trades.append(log_entry)
                    except json.JSONDecodeError:
                        continue
            
            # 取引統計
            buy_trades = [t for t in trades if t.get('details', {}).get('action') == 'BUY']
            sell_trades = [t for t in trades if t.get('details', {}).get('action') == 'SELL']
            
            return {
                'total_trades': len(trades),
                'buy_trades': len(buy_trades),
                'sell_trades': len(sell_trades),
                'recent_trades': trades[-10:] if trades else []
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_portfolio_status(self):
        """ポートフォリオ状態を取得"""
        try:
            # 設定ファイルからポートフォリオ比率を取得
            from src.shared_modules.config_loader import ConfigLoader
            config = ConfigLoader()
            
            portfolio_ratios = config.get("portfolio_ratios", {})
            
            # 実際のポートフォリオ価値は後で実装
            # 現在は仮の値
            total_value = 1000000  # 100万円
            current_values = {
                'index': total_value * portfolio_ratios.get('index', 0.5),
                'dividend': total_value * portfolio_ratios.get('dividend', 0.3),
                'range': total_value * portfolio_ratios.get('range', 0.2)
            }
            
            return {
                'total_value': total_value,
                'current_values': current_values,
                'target_ratios': portfolio_ratios,
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_nisa_status(self):
        """NISA状態を取得"""
        try:
            from src.shared_modules.config_loader import ConfigLoader
            config = ConfigLoader()
            
            nisa_settings = config.get("nisa_settings", {})
            
            # 実際のNISA使用状況は後で実装
            # 現在は仮の値
            annual_used = 500000  # 50万円
            lifetime_used = 2000000  # 200万円
            
            annual_limit = nisa_settings.get('annual_limit', 3600000)
            lifetime_limit = nisa_settings.get('lifetime_limit', 18000000)
            
            return {
                'annual_used': annual_used,
                'annual_limit': annual_limit,
                'annual_usage_percent': (annual_used / annual_limit) * 100,
                'lifetime_used': lifetime_used,
                'lifetime_limit': lifetime_limit,
                'lifetime_usage_percent': (lifetime_used / lifetime_limit) * 100,
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_backtest_summary(self):
        """バックテストサマリーを取得"""
        try:
            if not self.backtest_dir.exists():
                return {'error': 'Backtest directory not found'}
            
            backtest_files = list(self.backtest_dir.glob("*.json"))
            if not backtest_files:
                return {'error': 'No backtest files found'}
            
            # 最新のバックテスト結果を取得
            latest_backtest = max(backtest_files, key=os.path.getmtime)
            
            with open(latest_backtest, 'r', encoding='utf-8') as f:
                backtest_data = json.load(f)
            
            return {
                'latest_backtest': latest_backtest.name,
                'strategy': backtest_data.get('strategy', 'unknown'),
                'total_return': backtest_data.get('total_return', 0),
                'annual_return': backtest_data.get('annual_return', 0),
                'max_drawdown': backtest_data.get('max_drawdown', 0),
                'timestamp': backtest_data.get('metadata', {}).get('timestamp', ''),
                'total_backtests': len(backtest_files)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def create_performance_chart(self):
        """パフォーマンスチャートを作成"""
        try:
            # 仮のデータでチャートを作成
            dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
            values = 1000000 + (dates - dates[0]).days * 1000 + pd.Series(range(len(dates))) * 50
            
            plt.figure(figsize=(12, 6))
            plt.plot(dates, values, linewidth=2)
            plt.title('Portfolio Performance', fontsize=16)
            plt.xlabel('Date')
            plt.ylabel('Portfolio Value (JPY)')
            plt.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # チャートをBase64エンコード
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            chart_data = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return chart_data
        except Exception as e:
            return None

# ダッシュボードインスタンス
dashboard = ChimeraDashboard()

@app.route('/')
def index():
    """メインダッシュボードページ"""
    return render_template('dashboard.html')

@app.route('/api/system')
def api_system():
    """システム状態API"""
    return jsonify(dashboard.get_system_status())

@app.route('/api/logs')
def api_logs():
    """ログサマリーAPI"""
    return jsonify(dashboard.get_log_summary())

@app.route('/api/trading')
def api_trading():
    """取引サマリーAPI"""
    return jsonify(dashboard.get_trading_summary())

@app.route('/api/portfolio')
def api_portfolio():
    """ポートフォリオ状態API"""
    return jsonify(dashboard.get_portfolio_status())

@app.route('/api/nisa')
def api_nisa():
    """NISA状態API"""
    return jsonify(dashboard.get_nisa_status())

@app.route('/api/backtest')
def api_backtest():
    """バックテストサマリーAPI"""
    return jsonify(dashboard.get_backtest_summary())

@app.route('/api/chart')
def api_chart():
    """パフォーマンスチャートAPI"""
    chart_data = dashboard.create_performance_chart()
    if chart_data:
        return jsonify({'chart': chart_data})
    else:
        return jsonify({'error': 'Failed to create chart'})

@app.route('/api/status')
def api_status():
    """全体状態API"""
    return jsonify({
        'system': dashboard.get_system_status(),
        'logs': dashboard.get_log_summary(),
        'trading': dashboard.get_trading_summary(),
        'portfolio': dashboard.get_portfolio_status(),
        'nisa': dashboard.get_nisa_status(),
        'backtest': dashboard.get_backtest_summary()
    })

if __name__ == '__main__':
    # テンプレートディレクトリを作成
    template_dir = Path("dashboard/templates")
    template_dir.mkdir(parents=True, exist_ok=True)
    
    # 静的ファイルディレクトリを作成
    static_dir = Path("dashboard/static")
    static_dir.mkdir(parents=True, exist_ok=True)
    
    app.run(host='0.0.0.0', port=5001, debug=True)
