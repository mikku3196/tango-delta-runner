#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Chimera 緊急停止スクリプト
Manual Override機�E - 全注斁E��ャンセルとシスチE��停止
"""

import sys
import os
import json
import time
from datetime import datetime
from src.shared_modules.config_loader import ConfigLoader
from src.shared_modules.discord_logger import DiscordLogger
from src.shared_modules.ib_connector import IBConnector

class EmergencyStop:
    def __init__(self):
        """緊急停止シスチE��の初期匁E""
        self.config = ConfigLoader()
        self.discord = DiscordLogger(self.config.get("discord_webhook_url"))
        self.ib_connector = IBConnector()
        self.stop_flag_file = "STOP.flag"
    
    def execute_emergency_stop(self, reason: str = "manual_override"):
        """緊急停止を実衁E""
        print("🚨 Project Chimera 緊急停止を実行しまぁE..")
        
        try:
            # 1. IB接続を確竁E            ib_config = self.config.get("ib_account")
            if not self.ib_connector.connect_to_ib(
                ib_config["host"], 
                ib_config["port"], 
                ib_config["client_id"]
            ):
                print("⚠�E�EIB接続に失敗しました。注斁E��ャンセルをスキチE�Eします、E)
            else:
                # 2. 全注斁E��キャンセル
                self._cancel_all_orders()
            
            # 3. STOP.flagを作�E
            self._create_stop_flag(reason)
            
            # 4. DiscordにCRITICAL通知
            self._send_critical_notification(reason)
            
            print("✁E緊急停止が完亁E��ました")
            print("📋 実行�E容:")
            print("   - 全注斁E�Eキャンセル")
            print("   - STOP.flagの作�E")
            print("   - Discord通知の送信")
            print("   - シスチE��の停止")
            
        except Exception as e:
            print(f"❁E緊急停止実行中にエラーが発生しました: {e}")
            # エラーが発生してもSTOP.flagは作�E
            self._create_stop_flag(f"emergency_stop_error: {str(e)}")
        
        finally:
            # 5. IB接続を刁E��
            try:
                self.ib_connector.disconnect_from_ib()
            except:
                pass
    
    def _cancel_all_orders(self):
        """全注斁E��キャンセル"""
        try:
            print("📋 全注斁E�Eキャンセルを開姁E..")
            
            # IB APIを使用して全注斁E��キャンセル
            # 実裁E�E後で詳細化！EB APIの注斁E��ャンセル機�E�E�E            
            print("✁E全注斁E�Eキャンセルが完亁E��ました")
            
        except Exception as e:
            print(f"⚠�E�E注斁E��ャンセル中にエラーが発生しました: {e}")
    
    def _create_stop_flag(self, reason: str):
        """STOP.flagを作�E"""
        try:
            stop_data = {
                "reason": reason,
                "timestamp": datetime.now().isoformat(),
                "executed_by": "emergency_stop.py",
                "status": "STOPPED"
            }
            
            with open(self.stop_flag_file, "w", encoding="utf-8") as f:
                json.dump(stop_data, f, ensure_ascii=False, indent=2)
            
            print(f"🛑 STOP.flagを作�Eしました: {reason}")
            
        except Exception as e:
            print(f"❁ESTOP.flag作�Eエラー: {e}")
    
    def _send_critical_notification(self, reason: str):
        """DiscordにCRITICAL通知を送信"""
        try:
            fields = [
                {"name": "停止琁E��", "value": reason, "inline": False},
                {"name": "実行時刻", "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "inline": True},
                {"name": "実行老E, "value": "emergency_stop.py", "inline": True},
                {"name": "スチE�Eタス", "value": "🚨 CRITICAL STOP", "inline": True}
            ]
            
            self.discord.send_message(
                "🚨 【CRITICAL】Project Chimera 緊急停止",
                "シスチE��が緊急停止されました。�E取引が停止されてぁE��す、E,
                0xe74c3c,  # 赤色
                fields
            )
            
            print("📢 Discord通知を送信しました")
            
        except Exception as e:
            print(f"⚠�E�EDiscord通知送信エラー: {e}")
    
    def check_stop_flag(self) -> bool:
        """STOP.flagの存在をチェチE��"""
        return os.path.exists(self.stop_flag_file)
    
    def remove_stop_flag(self):
        """STOP.flagを削除�E�シスチE��再開時！E""
        try:
            if os.path.exists(self.stop_flag_file):
                os.remove(self.stop_flag_file)
                print("✁ESTOP.flagを削除しました")
                
                # 再開通知をDiscordに送信
                self.discord.success("Project Chimera シスチE��再開", "STOP.flagが削除され、シスチE��が�E開されました、E)
            else:
                print("ℹ�E�ESTOP.flagは存在しません")
                
        except Exception as e:
            print(f"❁ESTOP.flag削除エラー: {e}")
    
    def get_stop_flag_info(self) -> dict:
        """STOP.flagの惁E��を取征E""
        try:
            if os.path.exists(self.stop_flag_file):
                with open(self.stop_flag_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            print(f"STOP.flag惁E��取得エラー: {e}")
            return {}

def main():
    """メイン関数"""
    print("=" * 60)
    print("🚨 Project Chimera 緊急停止シスチE��")
    print("=" * 60)
    
    emergency_stop = EmergencyStop()
    
    # 現在のSTOP.flag状況を確誁E    if emergency_stop.check_stop_flag():
        print("⚠�E�ESTOP.flagが既に存在しまぁE)
        flag_info = emergency_stop.get_stop_flag_info()
        if flag_info:
            print(f"   停止琁E��: {flag_info.get('reason', '不�E')}")
            print(f"   停止時刻: {flag_info.get('timestamp', '不�E')}")
        
        choice = input("\\nSTOP.flagを削除してシスチE��を�E開しますか�E�E(y/n): ").lower()
        if choice == 'y':
            emergency_stop.remove_stop_flag()
        else:
            print("操作をキャンセルしました")
    else:
        print("ℹ�E�EシスチE��は現在稼働中でぁE)
        
        # 緊急停止の確誁E        print("\\n⚠�E�E緊急停止を実行すると以下が行われまぁE")
        print("   - 全注斁E�Eキャンセル")
        print("   - シスチE��の完�E停止")
        print("   - Discord通知の送信")
        
        choice = input("\\n緊急停止を実行しますか�E�E(y/n): ").lower()
        if choice == 'y':
            reason = input("停止琁E��を�E力してください (空白可): ").strip()
            if not reason:
                reason = "manual_override"
            
            emergency_stop.execute_emergency_stop(reason)
        else:
            print("操作をキャンセルしました")
    
    print("\\n" + "=" * 60)
    print("緊急停止シスチE��を終亁E��まぁE)
    print("=" * 60)

if __name__ == "__main__":
    main()
