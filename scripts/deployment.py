#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Chimera デプロイメントスクリプト
本番環境への自動デプロイメント
"""

import os
import sys
import shutil
import subprocess
import json
from datetime import datetime
from pathlib import Path

def create_systemd_service():
    """systemdサービスファイルを作成"""
    print("🔧 systemdサービスファイルを作成中...")
    
    service_content = f"""[Unit]
Description=Project Chimera Trading Bot
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'ubuntu')}
WorkingDirectory={os.getcwd()}
Environment=PATH={os.getenv('PATH')}
ExecStart={sys.executable} src/main_controller.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""
    
    service_file = Path("/etc/systemd/system/chimera.service")
    
    try:
        with open("chimera.service", "w") as f:
            f.write(service_content)
        
        print(f"  ✅ サービスファイルを作成しました: chimera.service")
        print(f"  以下のコマンドでインストールしてください:")
        print(f"  sudo cp chimera.service /etc/systemd/system/")
        print(f"  sudo systemctl daemon-reload")
        print(f"  sudo systemctl enable chimera")
        print(f"  sudo systemctl start chimera")
        
        return True
        
    except Exception as e:
        print(f"  ❌ サービスファイル作成エラー: {e}")
        return False

def create_logrotate_config():
    """logrotate設定ファイルを作成"""
    print("📝 logrotate設定ファイルを作成中...")
    
    logrotate_content = f"""{os.getcwd()}/logs/*.log {{
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 {os.getenv('USER', 'ubuntu')} {os.getenv('USER', 'ubuntu')}
    postrotate
        systemctl reload chimera
    endscript
}}
"""
    
    try:
        with open("chimera.logrotate", "w") as f:
            f.write(logrotate_content)
        
        print(f"  ✅ logrotate設定ファイルを作成しました: chimera.logrotate")
        print(f"  以下のコマンドでインストールしてください:")
        print(f"  sudo cp chimera.logrotate /etc/logrotate.d/chimera")
        
        return True
        
    except Exception as e:
        print(f"  ❌ logrotate設定ファイル作成エラー: {e}")
        return False

def create_monitoring_script():
    """監視スクリプトを作成"""
    print("👁️ 監視スクリプトを作成中...")
    
    monitoring_script = f"""#!/bin/bash
# Project Chimera 監視スクリプト

LOG_FILE="{os.getcwd()}/logs/monitoring.log"
SERVICE_NAME="chimera"

# ログ関数
log_message() {{
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> $LOG_FILE
}}

# サービス状態チェック
check_service() {{
    if systemctl is-active --quiet $SERVICE_NAME; then
        log_message "INFO: Service $SERVICE_NAME is running"
        return 0
    else
        log_message "ERROR: Service $SERVICE_NAME is not running"
        return 1
    fi
}}

# プロセス状態チェック
check_process() {{
    if pgrep -f "main_controller.py" > /dev/null; then
        log_message "INFO: Main controller process is running"
        return 0
    else
        log_message "ERROR: Main controller process is not running"
        return 1
    fi
}}

# ディスク使用量チェック
check_disk_usage() {{
    USAGE=$(df {os.getcwd()} | tail -1 | awk '{{print $5}}' | sed 's/%//')
    if [ $USAGE -gt 90 ]; then
        log_message "WARNING: Disk usage is $USAGE%"
        return 1
    else
        log_message "INFO: Disk usage is $USAGE%"
        return 0
    fi
}}

# メイン監視ループ
main() {{
    log_message "INFO: Starting monitoring check"
    
    SERVICE_OK=0
    PROCESS_OK=0
    DISK_OK=0
    
    check_service && SERVICE_OK=1
    check_process && PROCESS_OK=1
    check_disk_usage && DISK_OK=1
    
    if [ $SERVICE_OK -eq 0 ] || [ $PROCESS_OK -eq 0 ]; then
        log_message "ERROR: Service or process issue detected"
        # サービス再起動を試行
        systemctl restart $SERVICE_NAME
        sleep 10
        if systemctl is-active --quiet $SERVICE_NAME; then
            log_message "INFO: Service restarted successfully"
        else
            log_message "CRITICAL: Service restart failed"
        fi
    fi
    
    log_message "INFO: Monitoring check completed"
}}

# スクリプト実行
main
"""
    
    try:
        with open("monitor_chimera.sh", "w") as f:
            f.write(monitoring_script)
        
        # 実行権限を付与
        os.chmod("monitor_chimera.sh", 0o755)
        
        print(f"  ✅ 監視スクリプトを作成しました: monitor_chimera.sh")
        print(f"  以下のコマンドでcronに追加してください:")
        print(f"  crontab -e")
        print(f"  # 5分ごとに監視実行")
        print(f"  */5 * * * * {os.getcwd()}/monitor_chimera.sh")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 監視スクリプト作成エラー: {e}")
        return False

def create_backup_script():
    """バックアップスクリプトを作成"""
    print("💾 バックアップスクリプトを作成中...")
    
    backup_script = f"""#!/bin/bash
# Project Chimera バックアップスクリプト

BACKUP_DIR="/backup/chimera"
SOURCE_DIR="{os.getcwd()}"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="chimera_backup_$DATE.tar.gz"

# バックアップディレクトリ作成
mkdir -p $BACKUP_DIR

# バックアップ実行
tar -czf $BACKUP_DIR/$BACKUP_FILE \\
    --exclude='logs/*.log' \\
    --exclude='__pycache__' \\
    --exclude='*.pyc' \\
    --exclude='.git' \\
    $SOURCE_DIR

# 古いバックアップを削除（7日以上古いもの）
find $BACKUP_DIR -name "chimera_backup_*.tar.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/$BACKUP_FILE"
"""
    
    try:
        with open("backup_chimera.sh", "w") as f:
            f.write(backup_script)
        
        # 実行権限を付与
        os.chmod("backup_chimera.sh", 0o755)
        
        print(f"  ✅ バックアップスクリプトを作成しました: backup_chimera.sh")
        print(f"  以下のコマンドでcronに追加してください:")
        print(f"  crontab -e")
        print(f"  # 毎日深夜2時にバックアップ実行")
        print(f"  0 2 * * * {os.getcwd()}/backup_chimera.sh")
        
        return True
        
    except Exception as e:
        print(f"  ❌ バックアップスクリプト作成エラー: {e}")
        return False

def create_update_script():
    """アップデートスクリプトを作成"""
    print("🔄 アップデートスクリプトを作成中...")
    
    update_script = f"""#!/bin/bash
# Project Chimera アップデートスクリプト

SERVICE_NAME="chimera"
BACKUP_DIR="/backup/chimera"
SOURCE_DIR="{os.getcwd()}"

# ログ関数
log_message() {{
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}}

# サービス停止
log_message "INFO: Stopping service"
systemctl stop $SERVICE_NAME

# バックアップ作成
log_message "INFO: Creating backup"
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf $BACKUP_DIR/pre_update_backup_$DATE.tar.gz $SOURCE_DIR

# Git更新
log_message "INFO: Updating from Git"
cd $SOURCE_DIR
git pull origin main

# 依存関係更新
log_message "INFO: Updating dependencies"
pip install -r requirements.txt --upgrade

# 設定ファイルチェック
log_message "INFO: Checking configuration"
python scripts/production_test.py

# サービス再開
log_message "INFO: Starting service"
systemctl start $SERVICE_NAME

# サービス状態確認
sleep 10
if systemctl is-active --quiet $SERVICE_NAME; then
    log_message "INFO: Update completed successfully"
else
    log_message "ERROR: Service failed to start after update"
    exit 1
fi
"""
    
    try:
        with open("update_chimera.sh", "w") as f:
            f.write(update_script)
        
        # 実行権限を付与
        os.chmod("update_chimera.sh", 0o755)
        
        print(f"  ✅ アップデートスクリプトを作成しました: update_chimera.sh")
        print(f"  以下のコマンドでアップデートを実行してください:")
        print(f"  ./update_chimera.sh")
        
        return True
        
    except Exception as e:
        print(f"  ❌ アップデートスクリプト作成エラー: {e}")
        return False

def create_deployment_checklist():
    """デプロイメントチェックリストを作成"""
    print("📋 デプロイメントチェックリストを作成中...")
    
    checklist = f"""# Project Chimera デプロイメントチェックリスト

## 事前準備
- [ ] Ubuntu 22.04 LTS サーバーの準備
- [ ] Python 3.10+ のインストール
- [ ] Git のインストール
- [ ] Interactive Brokers アカウントの準備
- [ ] Discord Webhook の設定

## システム設定
- [ ] システムユーザーの作成
- [ ] SSH キーの設定
- [ ] ファイアウォールの設定
- [ ] 時刻同期の設定

## アプリケーション設定
- [ ] リポジトリのクローン
- [ ] Python仮想環境の作成
- [ ] 依存関係のインストール
- [ ] 設定ファイルの準備 (.env)
- [ ] ログディレクトリの作成

## サービス設定
- [ ] systemdサービスファイルのインストール
- [ ] サービスの有効化
- [ ] サービスの起動
- [ ] サービス状態の確認

## 監視設定
- [ ] 監視スクリプトの設定
- [ ] cronジョブの設定
- [ ] logrotateの設定
- [ ] バックアップスクリプトの設定

## テスト
- [ ] 本番環境テストの実行
- [ ] IB接続テスト
- [ ] Discord通知テスト
- [ ] Bot初期化テスト
- [ ] ログシステムテスト

## 本番運用開始
- [ ] 紙上取引でのテスト運用
- [ ] 監視ダッシュボードの確認
- [ ] アラート設定の確認
- [ ] 緊急停止手順の確認

## 運用開始後
- [ ] 日次監視の実施
- [ ] 週次レポートの確認
- [ ] 月次パフォーマンスレビュー
- [ ] 定期的なバックアップ確認

## 緊急時対応
- [ ] 緊急停止手順の確認
- [ ] ログファイルの確認方法
- [ ] サービス再起動手順
- [ ] 連絡先の確認

---
作成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    try:
        with open("deployment_checklist.md", "w", encoding="utf-8") as f:
            f.write(checklist)
        
        print(f"  ✅ デプロイメントチェックリストを作成しました: deployment_checklist.md")
        
        return True
        
    except Exception as e:
        print(f"  ❌ チェックリスト作成エラー: {e}")
        return False

def main():
    """メイン関数"""
    print("=" * 60)
    print("🚀 Project Chimera デプロイメント準備")
    print("=" * 60)
    
    results = {
        "systemd_service": create_systemd_service(),
        "logrotate_config": create_logrotate_config(),
        "monitoring_script": create_monitoring_script(),
        "backup_script": create_backup_script(),
        "update_script": create_update_script(),
        "deployment_checklist": create_deployment_checklist()
    }
    
    print("\n" + "=" * 60)
    print("📊 デプロイメント準備結果")
    print("=" * 60)
    
    for item_name, result in results.items():
        status = "✅ 完了" if result else "❌ 失敗"
        print(f"{item_name:20} {status}")
    
    if all(results.values()):
        print("\n🎉 デプロイメント準備が完了しました！")
        print("\n次のステップ:")
        print("1. deployment_checklist.md を確認")
        print("2. 本番サーバーでスクリプトを実行")
        print("3. サービスを起動")
        print("4. 監視設定を有効化")
        return True
    else:
        print("\n⚠️ 一部の準備が失敗しました。")
        print("エラーを確認してから再実行してください。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
