#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Chimera 実際のテスト実行スクリプト
本番環境での実際のテスト実行
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

def run_ib_connection_test():
    """IB接続テストの実行"""
    print("🔌 IB接続テストを実行中...")
    
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

def run_environment_test():
    """環境設定テストの実行"""
    print("⚙️ 環境設定テストを実行中...")
    
    try:
        result = subprocess.run([
            sys.executable, "test_env_config.py"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("  ✅ 環境設定テストが成功しました")
            return True
        else:
            print("  ❌ 環境設定テストが失敗しました")
            print(f"  エラー: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("  ⚠️ 環境設定テストがタイムアウトしました")
        return False
    except Exception as e:
        print(f"  ❌ 環境設定テスト実行エラー: {e}")
        return False

def run_risk_assessment_test():
    """リスク診断テストの実行"""
    print("🎯 リスク診断テストを実行中...")
    
    try:
        result = subprocess.run([
            sys.executable, "test_risk_assessment.py"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("  ✅ リスク診断テストが成功しました")
            return True
        else:
            print("  ❌ リスク診断テストが失敗しました")
            print(f"  エラー: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("  ⚠️ リスク診断テストがタイムアウトしました")
        return False
    except Exception as e:
        print(f"  ❌ リスク診断テスト実行エラー: {e}")
        return False

def run_nisa_monitor_test():
    """NISA監視テストの実行"""
    print("📊 NISA監視テストを実行中...")
    
    try:
        result = subprocess.run([
            sys.executable, "test_nisa_monitor.py"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("  ✅ NISA監視テストが成功しました")
            return True
        else:
            print("  ❌ NISA監視テストが失敗しました")
            print(f"  エラー: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("  ⚠️ NISA監視テストがタイムアウトしました")
        return False
    except Exception as e:
        print(f"  ❌ NISA監視テスト実行エラー: {e}")
        return False

def run_backtest_test():
    """バックテストの実行"""
    print("📈 バックテストを実行中...")
    
    try:
        # 1年間のバックテストを実行
        result = subprocess.run([
            sys.executable, "run_backtest.py", 
            "--strategy", "index",
            "--years", "1"
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("  ✅ バックテストが成功しました")
            return True
        else:
            print("  ❌ バックテストが失敗しました")
            print(f"  エラー: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("  ⚠️ バックテストがタイムアウトしました")
        return False
    except Exception as e:
        print(f"  ❌ バックテスト実行エラー: {e}")
        return False

def run_unit_tests():
    """単体テストの実行"""
    print("🧪 単体テストを実行中...")
    
    try:
        result = subprocess.run([
            sys.executable, "run_tests.py", "--unit"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("  ✅ 単体テストが成功しました")
            return True
        else:
            print("  ❌ 単体テストが失敗しました")
            print(f"  エラー: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("  ⚠️ 単体テストがタイムアウトしました")
        return False
    except Exception as e:
        print(f"  ❌ 単体テスト実行エラー: {e}")
        return False

def test_dashboard():
    """ダッシュボードテストの実行"""
    print("📊 ダッシュボードテストを実行中...")
    
    try:
        # ダッシュボードの依存関係をチェック
        result = subprocess.run([
            sys.executable, "start_dashboard.py", "--test"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("  ✅ ダッシュボードテストが成功しました")
            return True
        else:
            print("  ❌ ダッシュボードテストが失敗しました")
            print(f"  エラー: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("  ⚠️ ダッシュボードテストがタイムアウトしました")
        return False
    except Exception as e:
        print(f"  ❌ ダッシュボードテスト実行エラー: {e}")
        return False

def test_emergency_stop():
    """緊急停止テストの実行"""
    print("🛑 緊急停止テストを実行中...")
    
    try:
        # 緊急停止スクリプトの構文チェック
        result = subprocess.run([
            sys.executable, "-m", "py_compile", "emergency_stop.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("  ✅ 緊急停止スクリプトの構文チェックが成功しました")
            return True
        else:
            print("  ❌ 緊急停止スクリプトの構文チェックが失敗しました")
            print(f"  エラー: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"  ❌ 緊急停止テスト実行エラー: {e}")
        return False

def run_integration_test():
    """統合テストの実行"""
    print("🔗 統合テストを実行中...")
    
    try:
        # メインコントローラーの構文チェック
        result = subprocess.run([
            sys.executable, "-m", "py_compile", "src/main_controller.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("  ✅ メインコントローラーの構文チェックが成功しました")
            
            # Botの構文チェック
            bot_files = [
                "src/bots/core_index_bot.py",
                "src/bots/satellite_dividend_bot.py",
                "src/bots/satellite_range_bot.py"
            ]
            
            all_bots_ok = True
            for bot_file in bot_files:
                if os.path.exists(bot_file):
                    result = subprocess.run([
                        sys.executable, "-m", "py_compile", bot_file
                    ], capture_output=True, text=True)
                    
                    if result.returncode != 0:
                        print(f"  ❌ {bot_file}の構文チェックが失敗しました")
                        all_bots_ok = False
                    else:
                        print(f"  ✅ {bot_file}の構文チェックが成功しました")
            
            return all_bots_ok
        else:
            print("  ❌ メインコントローラーの構文チェックが失敗しました")
            print(f"  エラー: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"  ❌ 統合テスト実行エラー: {e}")
        return False

def generate_test_report(results):
    """テストレポートの生成"""
    print("\n📋 テストレポートを生成中...")
    
    timestamp = datetime.now().isoformat()
    
    report = {
        "timestamp": timestamp,
        "test_results": results,
        "summary": {
            "total_tests": len(results),
            "passed": sum(1 for result in results.values() if result),
            "failed": sum(1 for result in results.values() if not result),
            "success_rate": (sum(1 for result in results.values() if result) / len(results)) * 100
        },
        "recommendations": []
    }
    
    # 推奨事項を生成
    if not results.get("ib_connection", True):
        report["recommendations"].append("IB Client Portal Gatewayの起動とAPI設定を確認してください")
    
    if not results.get("environment_test", True):
        report["recommendations"].append(".envファイルとconfig.yamlの設定を確認してください")
    
    if not results.get("unit_tests", True):
        report["recommendations"].append("単体テストの失敗を確認し、コードを修正してください")
    
    if not results.get("integration_test", True):
        report["recommendations"].append("統合テストの失敗を確認し、コードを修正してください")
    
    if not results.get("backtest_test", True):
        report["recommendations"].append("バックテストの失敗を確認し、データ取得を確認してください")
    
    # レポート保存
    with open("test_execution_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"  ✅ テストレポートを保存しました: test_execution_report.json")
    
    return report

def main():
    """メイン関数"""
    print("=" * 60)
    print("🧪 Project Chimera 実際のテスト実行")
    print("=" * 60)
    
    # テスト実行
    tests = [
        ("IB接続テスト", run_ib_connection_test),
        ("環境設定テスト", run_environment_test),
        ("リスク診断テスト", run_risk_assessment_test),
        ("NISA監視テスト", run_nisa_monitor_test),
        ("バックテスト", run_backtest_test),
        ("単体テスト", run_unit_tests),
        ("ダッシュボードテスト", test_dashboard),
        ("緊急停止テスト", test_emergency_stop),
        ("統合テスト", run_integration_test)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results[test_name] = result
            if result:
                print(f"✅ {test_name}が成功しました")
            else:
                print(f"❌ {test_name}が失敗しました")
        except Exception as e:
            print(f"❌ {test_name}でエラーが発生しました: {e}")
            results[test_name] = False
    
    # 結果サマリー
    print("\n" + "=" * 60)
    print("📊 テスト結果サマリー")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ 成功" if result else "❌ 失敗"
        print(f"{test_name:20} {status}")
    
    print(f"\n結果: {passed}/{total} テストが成功")
    print(f"成功率: {(passed/total)*100:.1f}%")
    
    # レポート生成
    report = generate_test_report(results)
    
    # 最終判定
    if passed == total:
        print("\n🎉 全てのテストが成功しました！")
        print("システムは本番運用の準備が整っています。")
        return True
    elif passed >= total * 0.8:
        print("\n⚠️ 大部分のテストが成功しました。")
        print("失敗したテストを確認してから本番運用を開始してください。")
        return True
    else:
        print("\n❌ 多くのテストが失敗しました。")
        print("システムの問題を修正してから再テストしてください。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
