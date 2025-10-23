#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Chimera 運用開始準備スクリプト
実際の運用開始前の最終チェックと準備
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

def check_prerequisites():
    """前提条件のチェック"""
    print("🔍 前提条件をチェック中...")
    
    prerequisites = {
        "Python 3.10+": sys.version_info >= (3, 10),
        "Git": check_command_exists("git"),
        "pip": check_command_exists("pip"),
        "プロジェクトディレクトリ": os.path.exists("src"),
        "設定ファイル": os.path.exists("src/config/config.yaml"),
        "環境変数ファイル": os.path.exists(".env"),
        "ログディレクトリ": os.path.exists("logs"),
        "requirements.txt": os.path.exists("requirements.txt")
    }
    
    for item, status in prerequisites.items():
        icon = "✅" if status else "❌"
        print(f"  {icon} {item}")
    
    return all(prerequisites.values())

def check_command_exists(command):
    """コマンドの存在確認"""
    try:
        subprocess.run([command, "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_dependencies():
    """依存関係のインストール"""
    print("\n📦 依存関係をインストール中...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("  ✅ 依存関係のインストールが完了しました")
            return True
        else:
            print(f"  ❌ 依存関係のインストールに失敗しました: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"  ❌ 依存関係のインストールエラー: {e}")
        return False

def setup_environment():
    """環境設定"""
    print("\n⚙️ 環境設定を実行中...")
    
    # ログディレクトリの作成
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    print("  ✅ ログディレクトリを作成しました")
    
    # バックテスト結果ディレクトリの作成
    backtest_dir = Path("logs/backtest_results")
    backtest_dir.mkdir(parents=True, exist_ok=True)
    print("  ✅ バックテスト結果ディレクトリを作成しました")
    
    # 環境変数ファイルの確認
    if not Path(".env").exists():
        print("  ⚠️ .envファイルが存在しません")
        print("  .env.exampleをコピーして.envを作成してください")
        return False
    
    print("  ✅ 環境設定が完了しました")
    return True

def validate_configuration():
    """設定の検証"""
    print("\n🔧 設定を検証中...")
    
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
            "ib_account.port",
            "discord_webhook_url"
        ]
        
        missing_settings = []
        for setting in required_settings:
            value = config.get(seting)
            if value is None:
                missing_settings.append(setting)
            else:
                print(f"  ✅ {setting}: {value}")
        
        if missing_settings:
            print(f"\n  ❌ 不足している設定: {', '.join(missing_settings)}")
            return False
        
        # 設定値の妥当性チェック
        portfolio_ratios = config.get("portfolio_ratios", {})
        total_ratio = sum(portfolio_ratios.values())
        
        if abs(total_ratio - 1.0) > 0.01:
            print(f"  ⚠️ ポートフォリオ比率の合計が1.0ではありません: {total_ratio}")
            return False
        
        print("  ✅ 設定の検証が完了しました")
        return True
        
    except Exception as e:
        print(f"  ❌ 設定検証エラー: {e}")
        return False

def test_ib_connection():
    """IB接続テスト"""
    print("\n🔌 IB接続をテスト中...")
    
    try:
        result = subprocess.run([
            sys.executable, "test_ib_connection.py"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("  ✅ IB接続テストが成功しました")
            return True
        else:
            print("  ❌ IB接続テストが失敗しました")
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
    print("\n📢 Discord Webhookをテスト中...")
    
    try:
        from src.shared_modules.config_loader import ConfigLoader
        from src.shared_modules.discord_logger import DiscordLogger
        
        config = ConfigLoader()
        webhook_url = config.get("discord_webhook_url")
        
        if not webhook_url or webhook_url == "https://discord.com/api/webhooks/...":
            print("  ⚠️ Discord Webhook URLが設定されていません")
            return False
        
        discord = DiscordLogger(webhook_url)
        discord.info("🧪 Project Chimera 運用開始準備テスト", "システムの準備が完了しました")
        
        print("  ✅ Discord Webhookテストが成功しました")
        return True
        
    except Exception as e:
        print(f"  ❌ Discord Webhookテストエラー: {e}")
        return False

def run_system_tests():
    """システムテストの実行"""
    print("\n🧪 システムテストを実行中...")
    
    try:
        result = subprocess.run([
            sys.executable, "run_tests.py", "--unit"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("  ✅ システムテストが成功しました")
            return True
        else:
            print("  ❌ システムテストが失敗しました")
            print(f"  エラー: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("  ⚠️ システムテストがタイムアウトしました")
        return False
    except Exception as e:
        print(f"  ❌ システムテスト実行エラー: {e}")
        return False

def create_operation_files():
    """運用ファイルの作成"""
    print("\n📋 運用ファイルを作成中...")
    
    # 運用開始ログファイル
    operation_log = {
        "startup_time": datetime.now().isoformat(),
        "version": "3.2",
        "status": "preparing",
        "checks": []
    }
    
    with open("operation_log.json", "w", encoding="utf-8") as f:
        json.dump(operation_log, f, ensure_ascii=False, indent=2)
    
    print("  ✅ 運用ログファイルを作成しました")
    
    # 運用チェックリスト
    checklist = """# Project Chimera 運用チェックリスト

## 運用開始前
- [ ] IB Client Portal Gatewayが起動している
- [ ] API接続が有効になっている
- [ ] Discord Webhookが設定されている
- [ ] .envファイルが正しく設定されている
- [ ] 設定ファイルが適切に設定されている
- [ ] ログディレクトリが存在する
- [ ] 依存関係がインストールされている

## 運用開始
- [ ] 本番環境テストが成功している
- [ ] IB接続テストが成功している
- [ ] Discord通知テストが成功している
- [ ] システムテストが成功している
- [ ] 緊急停止手順を確認している

## 運用中
- [ ] ログファイルを定期的に確認している
- [ ] Discord通知を監視している
- [ ] システムリソースを監視している
- [ ] NISA非課税枠の使用状況を確認している
- [ ] ポートフォリオの状態を確認している

## 定期メンテナンス
- [ ] 週次レポートを確認している
- [ ] 月次パフォーマンスレビューを実施している
- [ ] バックアップを確認している
- [ ] セキュリティ監査を実施している
- [ ] システムアップデートを確認している
"""
    
    with open("operation_checklist.md", "w", encoding="utf-8") as f:
        f.write(checklist)
    
    print("  ✅ 運用チェックリストを作成しました")
    
    return True

def generate_startup_report():
    """起動レポートの生成"""
    print("\n📊 起動レポートを生成中...")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "system": {
            "python_version": sys.version,
            "platform": sys.platform,
            "working_directory": os.getcwd()
        },
        "files": {
            "config_exists": os.path.exists("src/config/config.yaml"),
            "env_exists": os.path.exists(".env"),
            "logs_dir_exists": os.path.exists("logs"),
            "requirements_exists": os.path.exists("requirements.txt")
        },
        "status": "ready_for_production"
    }
    
    with open("startup_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("  ✅ 起動レポートを生成しました")
    
    return True

def main():
    """メイン関数"""
    print("=" * 60)
    print("🚀 Project Chimera 運用開始準備")
    print("=" * 60)
    
    # 各ステップの実行
    steps = [
        ("前提条件チェック", check_prerequisites),
        ("依存関係インストール", install_dependencies),
        ("環境設定", setup_environment),
        ("設定検証", validate_configuration),
        ("IB接続テスト", test_ib_connection),
        ("Discord Webhookテスト", test_discord_webhook),
        ("システムテスト", run_system_tests),
        ("運用ファイル作成", create_operation_files),
        ("起動レポート生成", generate_startup_report)
    ]
    
    results = {}
    
    for step_name, step_func in steps:
        print(f"\n{'='*20} {step_name} {'='*20}")
        try:
            result = step_func()
            results[step_name] = result
            if result:
                print(f"✅ {step_name}が完了しました")
            else:
                print(f"❌ {step_name}が失敗しました")
        except Exception as e:
            print(f"❌ {step_name}でエラーが発生しました: {e}")
            results[step_name] = False
    
    # 結果サマリー
    print("\n" + "=" * 60)
    print("📊 準備結果サマリー")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for step_name, result in results.items():
        status = "✅ 成功" if result else "❌ 失敗"
        print(f"{step_name:20} {status}")
    
    print(f"\n結果: {passed}/{total} ステップが成功")
    
    if passed == total:
        print("\n🎉 運用開始準備が完了しました！")
        print("\n次のステップ:")
        print("1. IB Client Portal Gatewayを起動")
        print("2. python src/main_controller.py でシステムを起動")
        print("3. 監視ダッシュボードで状態を確認")
        print("4. Discord通知を監視")
        return True
    else:
        print("\n⚠️ 一部の準備が失敗しました。")
        print("エラーを確認してから再実行してください。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
