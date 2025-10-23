#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Chimera 実際の運用開始スクリプト
本番環境での実際の運用開始
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

def final_system_check():
    """最終システムチェック"""
    print("🔍 最終システムチェックを実行中...")
    
    checks = {
        "Python環境": sys.version_info >= (3, 10),
        "プロジェクトディレクトリ": os.path.exists("src"),
        "設定ファイル": os.path.exists("src/config/config.yaml"),
        "環境変数ファイル": os.path.exists(".env"),
        "ログディレクトリ": os.path.exists("logs"),
        "依存関係": check_dependencies(),
        "IB接続": test_ib_connection(),
        "Discord通知": test_discord_webhook()
    }
    
    for check_name, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check_name}")
    
    return all(checks.values())

def check_dependencies():
    """依存関係のチェック"""
    try:
        import ibapi, pandas, numpy, requests, apscheduler, yfinance, beautifulsoup4, yaml
        return True
    except ImportError:
        return False

def test_ib_connection():
    """IB接続テスト"""
    try:
        result = subprocess.run([
            sys.executable, "test_ib_connection.py"
        ], capture_output=True, text=True, timeout=30)
        return result.returncode == 0
    except:
        return False

def test_discord_webhook():
    """Discord Webhookテスト"""
    try:
        from src.shared_modules.config_loader import ConfigLoader
        from src.shared_modules.discord_logger import DiscordLogger
        
        config = ConfigLoader()
        webhook_url = config.get("discord_webhook_url")
        
        if not webhook_url or webhook_url == "https://discord.com/api/webhooks/...":
            return False
        
        discord = DiscordLogger(webhook_url)
        discord.info("🧪 Project Chimera 最終チェック", "システムの最終チェックが完了しました")
        return True
    except:
        return False

def create_operation_log():
    """運用ログの作成"""
    print("📝 運用ログを作成中...")
    
    operation_log = {
        "startup_time": datetime.now().isoformat(),
        "version": "3.2",
        "status": "starting",
        "environment": {
            "python_version": sys.version,
            "platform": sys.platform,
            "working_directory": os.getcwd()
        },
        "checks": {
            "system_check": final_system_check(),
            "timestamp": datetime.now().isoformat()
        }
    }
    
    with open("operation_log.json", "w", encoding="utf-8") as f:
        json.dump(operation_log, f, ensure_ascii=False, indent=2)
    
    print("  ✅ 運用ログを作成しました")
    return True

def start_monitoring():
    """監視の開始"""
    print("👁️ 監視を開始中...")
    
    # 監視ダッシュボードを起動
    try:
        dashboard_process = subprocess.Popen([
            sys.executable, "start_dashboard.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("  ✅ 監視ダッシュボードを起動しました")
        print("  📊 ダッシュボード: http://localhost:5001")
        
        return dashboard_process
    except Exception as e:
        print(f"  ❌ 監視ダッシュボードの起動に失敗しました: {e}")
        return None

def start_main_system():
    """メインシステムの開始"""
    print("🚀 メインシステムを開始中...")
    
    try:
        # メインコントローラーを起動
        main_process = subprocess.Popen([
            sys.executable, "src/main_controller.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("  ✅ メインシステムを起動しました")
        
        # 起動確認
        time.sleep(5)
        
        if main_process.poll() is None:
            print("  ✅ システムが正常に起動しています")
            return main_process
        else:
            print("  ❌ システムの起動に失敗しました")
            return None
            
    except Exception as e:
        print(f"  ❌ メインシステムの起動に失敗しました: {e}")
        return None

def monitor_system_health(main_process, dashboard_process):
    """システムヘルス監視"""
    print("💓 システムヘルス監視を開始中...")
    
    try:
        while True:
            # メインプロセスの状態確認
            if main_process.poll() is not None:
                print("❌ メインシステムが停止しました")
                break
            
            # ダッシュボードプロセスの状態確認
            if dashboard_process and dashboard_process.poll() is not None:
                print("⚠️ 監視ダッシュボードが停止しました")
                # ダッシュボードを再起動
                dashboard_process = start_monitoring()
            
            # ログファイルの確認
            log_file = Path(f"logs/chimera_{datetime.now().strftime('%Y-%m-%d')}.log")
            if log_file.exists():
                # 最新のログを確認
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        last_line = lines[-1].strip()
                        if "ERROR" in last_line or "CRITICAL" in last_line:
                            print(f"⚠️ エラーが検出されました: {last_line}")
            
            # 5分ごとにヘルスチェック
            time.sleep(300)
            
    except KeyboardInterrupt:
        print("\n🛑 システム監視を停止しました")
        return False
    except Exception as e:
        print(f"❌ システム監視エラー: {e}")
        return False

def cleanup_processes(main_process, dashboard_process):
    """プロセスのクリーンアップ"""
    print("🧹 プロセスをクリーンアップ中...")
    
    try:
        if main_process:
            main_process.terminate()
            main_process.wait(timeout=10)
            print("  ✅ メインシステムを停止しました")
        
        if dashboard_process:
            dashboard_process.terminate()
            dashboard_process.wait(timeout=10)
            print("  ✅ 監視ダッシュボードを停止しました")
        
        return True
    except Exception as e:
        print(f"  ❌ プロセスクリーンアップエラー: {e}")
        return False

def generate_operation_report():
    """運用レポートの生成"""
    print("📊 運用レポートを生成中...")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "operation_status": "completed",
        "system_info": {
            "python_version": sys.version,
            "platform": sys.platform,
            "working_directory": os.getcwd()
        },
        "files": {
            "config_exists": os.path.exists("src/config/config.yaml"),
            "env_exists": os.path.exists(".env"),
            "logs_dir_exists": os.path.exists("logs"),
            "operation_log_exists": os.path.exists("operation_log.json")
        },
        "recommendations": [
            "定期的にログファイルを確認してください",
            "Discord通知を監視してください",
            "システムリソースを監視してください",
            "NISA非課税枠の使用状況を確認してください",
            "ポートフォリオの状態を確認してください"
        ]
    }
    
    with open("operation_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("  ✅ 運用レポートを生成しました")
    return True

def main():
    """メイン関数"""
    print("=" * 60)
    print("🚀 Project Chimera 実際の運用開始")
    print("=" * 60)
    
    # 最終システムチェック
    if not final_system_check():
        print("\n❌ 最終システムチェックが失敗しました")
        print("問題を解決してから再実行してください")
        return False
    
    # 運用ログの作成
    create_operation_log()
    
    # 監視の開始
    dashboard_process = start_monitoring()
    
    # メインシステムの開始
    main_process = start_main_system()
    
    if not main_process:
        print("\n❌ メインシステムの起動に失敗しました")
        cleanup_processes(main_process, dashboard_process)
        return False
    
    print("\n🎉 Project Chimera が正常に起動しました！")
    print("\n📊 監視ダッシュボード: http://localhost:5001")
    print("📢 Discord通知を監視してください")
    print("📝 ログファイルを定期的に確認してください")
    print("\n🛑 停止するには Ctrl+C を押してください")
    
    try:
        # システムヘルス監視
        monitor_system_health(main_process, dashboard_process)
    except KeyboardInterrupt:
        print("\n🛑 ユーザーによる停止要求")
    except Exception as e:
        print(f"\n❌ システムエラー: {e}")
    finally:
        # プロセスのクリーンアップ
        cleanup_processes(main_process, dashboard_process)
        
        # 運用レポートの生成
        generate_operation_report()
        
        print("\n✅ Project Chimera が正常に停止しました")
        print("📋 運用レポート: operation_report.json")
        print("📝 運用ログ: operation_log.json")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
