#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Chimera 本番環境テストスクリプト
本番運用前の最終テストと検証
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

def check_environment():
    """環境チェック"""
    print("🔍 環境チェックを実行中...")
    
    checks = {
        "Python version": sys.version_info >= (3, 10),
        "Required directories": all([
            os.path.exists("src"),
            os.path.exists("logs"),
            os.path.exists("src/config"),
            os.path.exists("src/shared_modules"),
            os.path.exists("src/bots")
        ]),
        "Config files": all([
            os.path.exists("src/config/config.yaml"),
            os.path.exists(".env.example")
        ]),
        "Main files": all([
            os.path.exists("src/main_controller.py"),
            os.path.exists("emergency_stop.py"),
            os.path.exists("test_ib_connection.py")
        ])
    }
    
    for check_name, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check_name}")
    
    return all(checks.values())

def check_dependencies():
    """依存関係チェック"""
    print("\n📦 依存関係チェックを実行中...")
    
    required_packages = [
        "ibapi", "pandas", "numpy", "requests", 
        "apscheduler", "yfinance", "beautifulsoup4", "PyYAML"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ 不足しているパッケージ: {', '.join(missing_packages)}")
        print("以下のコマンドでインストールしてください:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_configuration():
    """設定ファイルチェック"""
    print("\n⚙️ 設定ファイルチェックを実行中...")
    
    try:
        from src.shared_modules.config_loader import ConfigLoader
        config = ConfigLoader()
        
        # 必須設定のチェック
        required_settings = [
            "portfolio_ratios.index",
            "portfolio_ratios.dividend", 
            "portfolio_ratios.range",
            "index_bot.ticker",
            "index_bot.monthly_investment",
            "ib_account.host",
            "ib_account.port"
        ]
        
        missing_settings = []
        for setting in required_settings:
            value = config.get(setting)
            if value is None:
                missing_settings.append(setting)
            else:
                print(f"  ✅ {setting}: {value}")
        
        if missing_settings:
            print(f"\n⚠️ 不足している設定: {', '.join(missing_settings)}")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ 設定ファイル読み込みエラー: {e}")
        return False

def check_env_file():
    """環境変数ファイルチェック"""
    print("\n🔐 環境変数ファイルチェックを実行中...")
    
    if not os.path.exists(".env"):
        print("  ⚠️ .envファイルが存在しません")
        print("  .env.exampleをコピーして.envを作成してください")
        return False
    
    try:
        with open(".env", "r", encoding="utf-8") as f:
            content = f.read()
        
        required_vars = ["IB_MAIN_ACCOUNT_ID", "IB_NISA_ACCOUNT_ID", "DISCORD_WEBHOOK_URL"]
        missing_vars = []
        
        for var in required_vars:
            if var not in content or f"{var}=\"\"" in content:
                missing_vars.append(var)
            else:
                print(f"  ✅ {var}")
        
        if missing_vars:
            print(f"\n⚠️ 設定されていない環境変数: {', '.join(missing_vars)}")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ .envファイル読み込みエラー: {e}")
        return False

def test_ib_connection():
    """IB接続テスト"""
    print("\n🔌 IB接続テストを実行中...")
    
    try:
        result = subprocess.run([
            sys.executable, "test_ib_connection.py"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("  ✅ IB接続テスト成功")
            return True
        else:
            print("  ❌ IB接続テスト失敗")
            print(f"  エラー: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("  ⚠️ IB接続テストがタイムアウトしました")
        return False
    except Exception as e:
        print(f"  ❌ IB接続テスト実行エラー: {e}")
        return False

def test_discord_webhook():
    """Discord Webhookテスト"""
    print("\n📢 Discord Webhookテストを実行中...")
    
    try:
        from src.shared_modules.config_loader import ConfigLoader
        from src.shared_modules.discord_logger import DiscordLogger
        
        config = ConfigLoader()
        webhook_url = config.get("discord_webhook_url")
        
        if not webhook_url or webhook_url == "https://discord.com/api/webhooks/...":
            print("  ⚠️ Discord Webhook URLが設定されていません")
            return False
        
        discord = DiscordLogger(webhook_url)
        discord.info("🧪 Project Chimera テスト通知", "本番環境テストが実行されました")
        
        print("  ✅ Discord Webhookテスト成功")
        return True
        
    except Exception as e:
        print(f"  ❌ Discord Webhookテストエラー: {e}")
        return False

def test_bot_initialization():
    """Bot初期化テスト"""
    print("\n🤖 Bot初期化テストを実行中...")
    
    try:
        from src.shared_modules.config_loader import ConfigLoader
        from src.shared_modules.discord_logger import DiscordLogger
        from src.shared_modules.ib_connector import IBConnector
        from src.bots.core_index_bot import CoreIndexBot
        from src.bots.satellite_dividend_bot import SatelliteDividendBot
        from src.bots.satellite_range_bot import SatelliteRangeBot
        
        config = ConfigLoader()
        discord = DiscordLogger(config.get("discord_webhook_url"))
        ib_connector = IBConnector()
        
        # Bot初期化
        index_bot = CoreIndexBot(config, discord, ib_connector)
        dividend_bot = SatelliteDividendBot(config, discord, ib_connector)
        range_bot = SatelliteRangeBot(config, discord, ib_connector)
        
        # ヘルスチェック
        bots = [
            ("Core Index Bot", index_bot),
            ("Satellite Dividend Bot", dividend_bot),
            ("Satellite Range Bot", range_bot)
        ]
        
        all_healthy = True
        for bot_name, bot in bots:
            is_healthy = bot.is_healthy()
            status = "✅" if is_healthy else "❌"
            print(f"  {status} {bot_name}")
            if not is_healthy:
                all_healthy = False
        
        return all_healthy
        
    except Exception as e:
        print(f"  ❌ Bot初期化テストエラー: {e}")
        return False

def test_logging_system():
    """ログシステムテスト"""
    print("\n📝 ログシステムテストを実行中...")
    
    try:
        from src.shared_modules.detailed_logger import get_detailed_logger
        
        logger = get_detailed_logger()
        
        # テストログ
        logger.log_event("INFO", "TEST", "Production test log", {"test": True})
        logger.log_trade("BUY", "TEST", 100, 1000.0, "TEST_ACCOUNT")
        
        # ログファイルの存在確認
        log_files = list(logger.log_dir.glob("*.log"))
        if log_files:
            print(f"  ✅ ログファイル作成成功: {len(log_files)}個")
            return True
        else:
            print("  ❌ ログファイルが作成されませんでした")
            return False
            
    except Exception as e:
        print(f"  ❌ ログシステムテストエラー: {e}")
        return False

def test_watchdog_system():
    """Watchdogシステムテスト"""
    print("\n🐕 Watchdogシステムテストを実行中...")
    
    try:
        from src.shared_modules.config_loader import ConfigLoader
        from src.shared_modules.discord_logger import DiscordLogger
        from src.shared_modules.watchdog import Watchdog
        
        config = ConfigLoader()
        discord = DiscordLogger(config.get("discord_webhook_url"))
        watchdog = Watchdog(config, discord)
        
        # テストプロセス登録
        def test_process():
            time.sleep(1)
        
        watchdog.register_process("test_process", test_process)
        
        # 監視開始・停止テスト
        watchdog.start_monitoring()
        time.sleep(2)
        watchdog.stop_monitoring()
        
        print("  ✅ Watchdogシステムテスト成功")
        return True
        
    except Exception as e:
        print(f"  ❌ Watchdogシステムテストエラー: {e}")
        return False

def run_unit_tests():
    """単体テスト実行"""
    print("\n🧪 単体テストを実行中...")
    
    try:
        result = subprocess.run([
            sys.executable, "run_tests.py", "--unit"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("  ✅ 単体テスト成功")
            return True
        else:
            print("  ❌ 単体テスト失敗")
            print(f"  エラー: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("  ⚠️ 単体テストがタイムアウトしました")
        return False
    except Exception as e:
        print(f"  ❌ 単体テスト実行エラー: {e}")
        return False

def generate_test_report(results):
    """テストレポート生成"""
    print("\n📋 テストレポートを生成中...")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = {
        "timestamp": timestamp,
        "environment": "production_test",
        "results": results,
        "overall_status": "PASS" if all(results.values()) else "FAIL",
        "recommendations": []
    }
    
    # 推奨事項を追加
    if not results.get("ib_connection", True):
        report["recommendations"].append("IB Client Portal Gatewayの起動とAPI設定を確認してください")
    
    if not results.get("discord_webhook", True):
        report["recommendations"].append("Discord Webhook URLの設定を確認してください")
    
    if not results.get("env_file", True):
        report["recommendations"].append(".envファイルの設定を完了してください")
    
    # レポート保存
    with open("production_test_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"  ✅ テストレポートを保存しました: production_test_report.json")
    
    return report

def main():
    """メイン関数"""
    print("=" * 60)
    print("🚀 Project Chimera 本番環境テスト")
    print("=" * 60)
    
    # テスト実行
    test_results = {
        "environment": check_environment(),
        "dependencies": check_dependencies(),
        "configuration": check_configuration(),
        "env_file": check_env_file(),
        "ib_connection": test_ib_connection(),
        "discord_webhook": test_discord_webhook(),
        "bot_initialization": test_bot_initialization(),
        "logging_system": test_logging_system(),
        "watchdog_system": test_watchdog_system(),
        "unit_tests": run_unit_tests()
    }
    
    # 結果表示
    print("\n" + "=" * 60)
    print("📊 テスト結果サマリー")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\n結果: {passed}/{total} テストが成功")
    
    # レポート生成
    report = generate_test_report(test_results)
    
    # 最終判定
    if all(test_results.values()):
        print("\n🎉 全てのテストが成功しました！")
        print("本番環境での運用準備が完了しています。")
        return True
    else:
        print("\n⚠️ 一部のテストが失敗しました。")
        print("上記の推奨事項を確認してから本番運用を開始してください。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
