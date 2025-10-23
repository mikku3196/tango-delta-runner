#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Chimera パフォーマンス監視スクリプト
システムのパフォーマンスを継続的に監視
"""

import os
import sys
import json
import time
import psutil
import threading
import queue
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

class PerformanceMonitor:
    def __init__(self):
        self.monitoring = False
        self.monitor_thread = None
        self.metrics_queue = queue.Queue()
        self.performance_history = []
        self.alert_thresholds = {
            "cpu_percent": 80,
            "memory_percent": 80,
            "disk_percent": 90,
            "error_rate": 0.05
        }
        self.alerts = []
        
    def start_monitoring(self, interval: int = 60):
        """パフォーマンス監視を開始"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop, 
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        print(f"📊 パフォーマンス監視を開始しました (間隔: {interval}秒)")
    
    def stop_monitoring(self):
        """パフォーマンス監視を停止"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        print("📊 パフォーマンス監視を停止しました")
    
    def _monitoring_loop(self, interval: int):
        """監視ループ"""
        while self.monitoring:
            try:
                metrics = self._collect_metrics()
                self.metrics_queue.put(metrics)
                self._update_history(metrics)
                self._check_alerts(metrics)
                time.sleep(interval)
            except Exception as e:
                print(f"監視ループエラー: {e}")
                time.sleep(interval)
    
    def _collect_metrics(self) -> Dict[str, Any]:
        """メトリクスを収集"""
        try:
            # システムメトリクス
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # プロセスメトリクス
            chimera_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent', 'create_time']):
                try:
                    if proc.info['cmdline'] and any('main_controller.py' in cmd for cmd in proc.info['cmdline']):
                        chimera_processes.append({
                            'pid': proc.info['pid'],
                            'cpu_percent': proc.info['cpu_percent'],
                            'memory_percent': proc.info['memory_percent'],
                            'uptime': time.time() - proc.info['create_time']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # ネットワークメトリクス
            network = psutil.net_io_counters()
            
            # ログメトリクス
            log_metrics = self._analyze_logs()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'system': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_used': memory.used,
                    'memory_total': memory.total,
                    'disk_percent': disk.percent,
                    'disk_used': disk.used,
                    'disk_total': disk.total
                },
                'processes': chimera_processes,
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                'logs': log_metrics
            }
        except Exception as e:
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def _analyze_logs(self) -> Dict[str, Any]:
        """ログを分析"""
        try:
            log_dir = Path("logs")
            if not log_dir.exists():
                return {"error": "Log directory not found"}
            
            log_files = list(log_dir.glob("chimera_*.log"))
            if not log_files:
                return {"error": "No log files found"}
            
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
            
            # エラー率の計算
            total_logs = len(lines)
            error_count = level_counts['ERROR'] + level_counts['CRITICAL']
            error_rate = error_count / total_logs if total_logs > 0 else 0
            
            return {
                'latest_log_file': latest_log.name,
                'file_size': stat.st_size,
                'last_modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'total_lines': total_logs,
                'level_counts': level_counts,
                'error_rate': error_rate
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _update_history(self, metrics: Dict[str, Any]):
        """メトリクス履歴を更新"""
        self.performance_history.append(metrics)
        # 履歴を1000件に制限
        if len(self.performance_history) > 1000:
            self.performance_history = self.performance_history[-1000:]
    
    def _check_alerts(self, metrics: Dict[str, Any]):
        """アラートをチェック"""
        if 'error' in metrics:
            return
        
        alerts = []
        
        # CPU使用率のチェック
        cpu_percent = metrics['system']['cpu_percent']
        if cpu_percent > self.alert_thresholds['cpu_percent']:
            alerts.append({
                'type': 'cpu_high',
                'message': f'CPU使用率が高いです: {cpu_percent:.1f}%',
                'value': cpu_percent,
                'threshold': self.alert_thresholds['cpu_percent']
            })
        
        # メモリ使用率のチェック
        memory_percent = metrics['system']['memory_percent']
        if memory_percent > self.alert_thresholds['memory_percent']:
            alerts.append({
                'type': 'memory_high',
                'message': f'メモリ使用率が高いです: {memory_percent:.1f}%',
                'value': memory_percent,
                'threshold': self.alert_thresholds['memory_percent']
            })
        
        # ディスク使用率のチェック
        disk_percent = metrics['system']['disk_percent']
        if disk_percent > self.alert_thresholds['disk_percent']:
            alerts.append({
                'type': 'disk_high',
                'message': f'ディスク使用率が高いです: {disk_percent:.1f}%',
                'value': disk_percent,
                'threshold': self.alert_thresholds['disk_percent']
            })
        
        # エラー率のチェック
        error_rate = metrics['logs'].get('error_rate', 0)
        if error_rate > self.alert_thresholds['error_rate']:
            alerts.append({
                'type': 'error_rate_high',
                'message': f'エラー率が高いです: {error_rate:.2%}',
                'value': error_rate,
                'threshold': self.alert_thresholds['error_rate']
            })
        
        # プロセス数のチェック
        process_count = len(metrics['processes'])
        if process_count == 0:
            alerts.append({
                'type': 'process_stopped',
                'message': 'Project Chimeraプロセスが停止しています',
                'value': process_count,
                'threshold': 1
            })
        
        # アラートを記録
        for alert in alerts:
            alert['timestamp'] = datetime.now().isoformat()
            self.alerts.append(alert)
            
            # Discord通知を送信
            self._send_alert_notification(alert)
    
    def _send_alert_notification(self, alert: Dict[str, Any]):
        """アラート通知を送信"""
        try:
            from src.shared_modules.config_loader import ConfigLoader
            from src.shared_modules.discord_logger import DiscordLogger
            
            config = ConfigLoader()
            webhook_url = config.get("discord_webhook_url")
            
            if webhook_url and webhook_url != "https://discord.com/api/webhooks/...":
                discord = DiscordLogger(webhook_url)
                
                # アラートレベルに応じて通知色を決定
                if alert['type'] in ['cpu_high', 'memory_high', 'disk_high']:
                    color = 0xffc107  # 黄色
                elif alert['type'] in ['error_rate_high']:
                    color = 0xff6b35  # オレンジ
                else:
                    color = 0xdc3545  # 赤色
                
                discord.send_alert(alert['message'], color=color)
                
        except Exception as e:
            print(f"アラート通知送信エラー: {e}")
    
    def get_current_metrics(self) -> Optional[Dict[str, Any]]:
        """現在のメトリクスを取得"""
        try:
            return self.metrics_queue.get_nowait()
        except queue.Empty:
            return None
    
    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """パフォーマンスサマリーを取得"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_metrics = [
            m for m in self.performance_history 
            if datetime.fromisoformat(m['timestamp']) > cutoff_time
        ]
        
        if not recent_metrics:
            return {"error": "No recent metrics available"}
        
        # 統計計算
        cpu_values = [m['system']['cpu_percent'] for m in recent_metrics if 'system' in m]
        memory_values = [m['system']['memory_percent'] for m in recent_metrics if 'system' in m]
        disk_values = [m['system']['disk_percent'] for m in recent_metrics if 'system' in m]
        error_rates = [m['logs'].get('error_rate', 0) for m in recent_metrics if 'logs' in m]
        
        summary = {
            'period_hours': hours,
            'total_metrics': len(recent_metrics),
            'cpu': {
                'average': sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                'maximum': max(cpu_values) if cpu_values else 0,
                'minimum': min(cpu_values) if cpu_values else 0
            },
            'memory': {
                'average': sum(memory_values) / len(memory_values) if memory_values else 0,
                'maximum': max(memory_values) if memory_values else 0,
                'minimum': min(memory_values) if memory_values else 0
            },
            'disk': {
                'average': sum(disk_values) / len(disk_values) if disk_values else 0,
                'maximum': max(disk_values) if disk_values else 0,
                'minimum': min(disk_values) if disk_values else 0
            },
            'error_rate': {
                'average': sum(error_rates) / len(error_rates) if error_rates else 0,
                'maximum': max(error_rates) if error_rates else 0,
                'minimum': min(error_rates) if error_rates else 0
            },
            'alerts': len([a for a in self.alerts if datetime.fromisoformat(a['timestamp']) > cutoff_time])
        }
        
        return summary
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """パフォーマンスレポートを生成"""
        print("📊 パフォーマンスレポートを生成中...")
        
        # 24時間のサマリー
        summary_24h = self.get_performance_summary(24)
        
        # 7日間のサマリー
        summary_7d = self.get_performance_summary(168)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary_24h': summary_24h,
            'summary_7d': summary_7d,
            'alerts': self.alerts[-100:],  # 最新100件のアラート
            'thresholds': self.alert_thresholds,
            'recommendations': self._generate_recommendations(summary_24h)
        }
        
        with open("performance_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print("  ✅ パフォーマンスレポートを生成しました")
        return report
    
    def _generate_recommendations(self, summary: Dict[str, Any]) -> List[str]:
        """推奨事項を生成"""
        recommendations = []
        
        if summary.get('cpu', {}).get('average', 0) > 70:
            recommendations.append("CPU使用率が高いです。システムリソースを確認してください")
        
        if summary.get('memory', {}).get('average', 0) > 70:
            recommendations.append("メモリ使用率が高いです。メモリリークがないか確認してください")
        
        if summary.get('disk', {}).get('average', 0) > 80:
            recommendations.append("ディスク使用率が高いです。古いファイルを削除してください")
        
        if summary.get('error_rate', {}).get('average', 0) > 0.02:
            recommendations.append("エラー率が高いです。ログを詳細に確認してください")
        
        if summary.get('alerts', 0) > 10:
            recommendations.append("アラート数が多いです。システムの状態を確認してください")
        
        if not recommendations:
            recommendations.append("システムは正常に動作しています")
        
        return recommendations

def main():
    """メイン関数"""
    print("=" * 60)
    print("📊 Project Chimera パフォーマンス監視")
    print("=" * 60)
    
    monitor = PerformanceMonitor()
    
    try:
        # 監視を開始
        monitor.start_monitoring(interval=60)  # 1分ごと
        
        print("📊 パフォーマンス監視が開始されました")
        print("🛑 停止するには Ctrl+C を押してください")
        
        # 監視ループ
        while True:
            time.sleep(300)  # 5分ごとにサマリーを表示
            
            # 現在のメトリクスを取得
            current_metrics = monitor.get_current_metrics()
            if current_metrics:
                print(f"\n📊 現在の状態 ({datetime.now().strftime('%H:%M:%S')})")
                print(f"  CPU: {current_metrics['system']['cpu_percent']:.1f}%")
                print(f"  メモリ: {current_metrics['system']['memory_percent']:.1f}%")
                print(f"  ディスク: {current_metrics['system']['disk_percent']:.1f}%")
                print(f"  プロセス数: {len(current_metrics['processes'])}")
                print(f"  エラー率: {current_metrics['logs'].get('error_rate', 0):.2%}")
            
            # アラート数を表示
            recent_alerts = len([a for a in monitor.alerts 
                               if datetime.fromisoformat(a['timestamp']) > datetime.now() - timedelta(hours=1)])
            if recent_alerts > 0:
                print(f"  ⚠️ 過去1時間のアラート数: {recent_alerts}")
    
    except KeyboardInterrupt:
        print("\n🛑 パフォーマンス監視を停止しました")
    except Exception as e:
        print(f"\n❌ パフォーマンス監視エラー: {e}")
    finally:
        # 監視を停止
        monitor.stop_monitoring()
        
        # 最終レポートを生成
        report = monitor.generate_performance_report()
        
        print("\n📋 パフォーマンスレポートを生成しました: performance_report.json")
        
        # サマリーを表示
        summary = report.get('summary_24h', {})
        if 'error' not in summary:
            print(f"\n📊 24時間サマリー:")
            print(f"  CPU平均: {summary['cpu']['average']:.1f}%")
            print(f"  メモリ平均: {summary['memory']['average']:.1f}%")
            print(f"  ディスク平均: {summary['disk']['average']:.1f}%")
            print(f"  エラー率平均: {summary['error_rate']['average']:.2%}")
            print(f"  アラート数: {summary['alerts']}")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
