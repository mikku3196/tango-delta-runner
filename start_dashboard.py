#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Chimera ダッシュボード起動スクリプト
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dashboard_dependencies():
    """ダッシュボードの依存関係をチェック"""
    print("🔍 ダッシュボード依存関係をチェック中...")
    
    required_packages = ["flask", "psutil", "matplotlib", "pandas"]
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

def start_dashboard():
    """ダッシュボードを起動"""
    print("🚀 Project Chimera ダッシュボードを起動中...")
    
    try:
        # ダッシュボードディレクトリに移動
        dashboard_dir = Path("dashboard")
        if not dashboard_dir.exists():
            print("❌ ダッシュボードディレクトリが見つかりません")
            return False
        
        # ダッシュボードアプリを起動
        subprocess.run([
            sys.executable, "dashboard/app.py"
        ], cwd=dashboard_dir.parent)
        
        return True
        
    except KeyboardInterrupt:
        print("\n🛑 ダッシュボードを停止しました")
        return True
    except Exception as e:
        print(f"❌ ダッシュボード起動エラー: {e}")
        return False

def main():
    """メイン関数"""
    print("=" * 60)
    print("📊 Project Chimera ダッシュボード起動")
    print("=" * 60)
    
    # 依存関係チェック
    if not check_dashboard_dependencies():
        print("\n❌ 依存関係のインストールが必要です")
        return False
    
    # ダッシュボード起動
    print("\n🌐 ダッシュボードにアクセス:")
    print("   http://localhost:5001")
    print("\n🛑 停止するには Ctrl+C を押してください")
    
    success = start_dashboard()
    
    if success:
        print("\n✅ ダッシュボードが正常に停止しました")
    else:
        print("\n❌ ダッシュボードの起動に失敗しました")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
