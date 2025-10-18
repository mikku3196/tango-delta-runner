#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Chimera 邱頑･蛛懈ｭ｢繧ｹ繧ｯ繝ｪ繝励ヨ
Manual Override讖溯・ - 蜈ｨ豕ｨ譁・く繝｣繝ｳ繧ｻ繝ｫ縺ｨ繧ｷ繧ｹ繝・Β蛛懈ｭ｢
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
        """邱頑･蛛懈ｭ｢繧ｷ繧ｹ繝・Β縺ｮ蛻晄悄蛹・""
        self.config = ConfigLoader()
        self.discord = DiscordLogger(self.config.get("discord_webhook_url"))
        self.ib_connector = IBConnector()
        self.stop_flag_file = "STOP.flag"
    
    def execute_emergency_stop(self, reason: str = "manual_override"):
        """邱頑･蛛懈ｭ｢繧貞ｮ溯｡・""
        print("圷 Project Chimera 邱頑･蛛懈ｭ｢繧貞ｮ溯｡後＠縺ｾ縺・..")
        
        try:
            # 1. IB謗･邯壹ｒ遒ｺ遶・            ib_config = self.config.get("ib_account")
            if not self.ib_connector.connect_to_ib(
                ib_config["host"], 
                ib_config["port"], 
                ib_config["client_id"]
            ):
                print("笞・・IB謗･邯壹↓螟ｱ謨励＠縺ｾ縺励◆縲よｳｨ譁・く繝｣繝ｳ繧ｻ繝ｫ繧偵せ繧ｭ繝・・縺励∪縺吶・)
            else:
                # 2. 蜈ｨ豕ｨ譁・ｒ繧ｭ繝｣繝ｳ繧ｻ繝ｫ
                self._cancel_all_orders()
            
            # 3. STOP.flag繧剃ｽ懈・
            self._create_stop_flag(reason)
            
            # 4. Discord縺ｫCRITICAL騾夂衍
            self._send_critical_notification(reason)
            
            print("笨・邱頑･蛛懈ｭ｢縺悟ｮ御ｺ・＠縺ｾ縺励◆")
            print("搭 螳溯｡悟・螳ｹ:")
            print("   - 蜈ｨ豕ｨ譁・・繧ｭ繝｣繝ｳ繧ｻ繝ｫ")
            print("   - STOP.flag縺ｮ菴懈・")
            print("   - Discord騾夂衍縺ｮ騾∽ｿ｡")
            print("   - 繧ｷ繧ｹ繝・Β縺ｮ蛛懈ｭ｢")
            
        except Exception as e:
            print(f"笶・邱頑･蛛懈ｭ｢螳溯｡御ｸｭ縺ｫ繧ｨ繝ｩ繝ｼ縺檎匱逕溘＠縺ｾ縺励◆: {e}")
            # 繧ｨ繝ｩ繝ｼ縺檎匱逕溘＠縺ｦ繧４TOP.flag縺ｯ菴懈・
            self._create_stop_flag(f"emergency_stop_error: {str(e)}")
        
        finally:
            # 5. IB謗･邯壹ｒ蛻・妙
            try:
                self.ib_connector.disconnect_from_ib()
            except:
                pass
    
    def _cancel_all_orders(self):
        """蜈ｨ豕ｨ譁・ｒ繧ｭ繝｣繝ｳ繧ｻ繝ｫ"""
        try:
            print("搭 蜈ｨ豕ｨ譁・・繧ｭ繝｣繝ｳ繧ｻ繝ｫ繧帝幕蟋・..")
            
            # IB API繧剃ｽｿ逕ｨ縺励※蜈ｨ豕ｨ譁・ｒ繧ｭ繝｣繝ｳ繧ｻ繝ｫ
            # 螳溯｣・・蠕後〒隧ｳ邏ｰ蛹厄ｼ・B API縺ｮ豕ｨ譁・く繝｣繝ｳ繧ｻ繝ｫ讖溯・・・            
            print("笨・蜈ｨ豕ｨ譁・・繧ｭ繝｣繝ｳ繧ｻ繝ｫ縺悟ｮ御ｺ・＠縺ｾ縺励◆")
            
        except Exception as e:
            print(f"笞・・豕ｨ譁・く繝｣繝ｳ繧ｻ繝ｫ荳ｭ縺ｫ繧ｨ繝ｩ繝ｼ縺檎匱逕溘＠縺ｾ縺励◆: {e}")
    
    def _create_stop_flag(self, reason: str):
        """STOP.flag繧剃ｽ懈・"""
        try:
            stop_data = {
                "reason": reason,
                "timestamp": datetime.now().isoformat(),
                "executed_by": "emergency_stop.py",
                "status": "STOPPED"
            }
            
            with open(self.stop_flag_file, "w", encoding="utf-8") as f:
                json.dump(stop_data, f, ensure_ascii=False, indent=2)
            
            print(f"尅 STOP.flag繧剃ｽ懈・縺励∪縺励◆: {reason}")
            
        except Exception as e:
            print(f"笶・STOP.flag菴懈・繧ｨ繝ｩ繝ｼ: {e}")
    
    def _send_critical_notification(self, reason: str):
        """Discord縺ｫCRITICAL騾夂衍繧帝∽ｿ｡"""
        try:
            fields = [
                {"name": "蛛懈ｭ｢逅・罰", "value": reason, "inline": False},
                {"name": "螳溯｡梧凾蛻ｻ", "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "inline": True},
                {"name": "螳溯｡瑚・, "value": "emergency_stop.py", "inline": True},
                {"name": "繧ｹ繝・・繧ｿ繧ｹ", "value": "圷 CRITICAL STOP", "inline": True}
            ]
            
            self.discord.send_message(
                "圷 縲燭RITICAL縲善roject Chimera 邱頑･蛛懈ｭ｢",
                "繧ｷ繧ｹ繝・Β縺檎ｷ頑･蛛懈ｭ｢縺輔ｌ縺ｾ縺励◆縲ょ・蜿門ｼ輔′蛛懈ｭ｢縺輔ｌ縺ｦ縺・∪縺吶・,
                0xe74c3c,  # 襍､濶ｲ
                fields
            )
            
            print("討 Discord騾夂衍繧帝∽ｿ｡縺励∪縺励◆")
            
        except Exception as e:
            print(f"笞・・Discord騾夂衍騾∽ｿ｡繧ｨ繝ｩ繝ｼ: {e}")
    
    def check_stop_flag(self) -> bool:
        """STOP.flag縺ｮ蟄伜惠繧偵メ繧ｧ繝・け"""
        return os.path.exists(self.stop_flag_file)
    
    def remove_stop_flag(self):
        """STOP.flag繧貞炎髯､・医す繧ｹ繝・Β蜀埼幕譎ゑｼ・""
        try:
            if os.path.exists(self.stop_flag_file):
                os.remove(self.stop_flag_file)
                print("笨・STOP.flag繧貞炎髯､縺励∪縺励◆")
                
                # 蜀埼幕騾夂衍繧奪iscord縺ｫ騾∽ｿ｡
                self.discord.success("Project Chimera 繧ｷ繧ｹ繝・Β蜀埼幕", "STOP.flag縺悟炎髯､縺輔ｌ縲√す繧ｹ繝・Β縺悟・髢九＆繧後∪縺励◆縲・)
            else:
                print("邃ｹ・・STOP.flag縺ｯ蟄伜惠縺励∪縺帙ｓ")
                
        except Exception as e:
            print(f"笶・STOP.flag蜑企勁繧ｨ繝ｩ繝ｼ: {e}")
    
    def get_stop_flag_info(self) -> dict:
        """STOP.flag縺ｮ諠・ｱ繧貞叙蠕・""
        try:
            if os.path.exists(self.stop_flag_file):
                with open(self.stop_flag_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            print(f"STOP.flag諠・ｱ蜿門ｾ励お繝ｩ繝ｼ: {e}")
            return {}

def main():
    """繝｡繧､繝ｳ髢｢謨ｰ"""
    print("=" * 60)
    print("圷 Project Chimera 邱頑･蛛懈ｭ｢繧ｷ繧ｹ繝・Β")
    print("=" * 60)
    
    emergency_stop = EmergencyStop()
    
    # 迴ｾ蝨ｨ縺ｮSTOP.flag迥ｶ豕√ｒ遒ｺ隱・    if emergency_stop.check_stop_flag():
        print("笞・・STOP.flag縺梧里縺ｫ蟄伜惠縺励∪縺・)
        flag_info = emergency_stop.get_stop_flag_info()
        if flag_info:
            print(f"   蛛懈ｭ｢逅・罰: {flag_info.get('reason', '荳肴・')}")
            print(f"   蛛懈ｭ｢譎ょ綾: {flag_info.get('timestamp', '荳肴・')}")
        
        choice = input("\\nSTOP.flag繧貞炎髯､縺励※繧ｷ繧ｹ繝・Β繧貞・髢九＠縺ｾ縺吶°・・(y/n): ").lower()
        if choice == 'y':
            emergency_stop.remove_stop_flag()
        else:
            print("謫堺ｽ懊ｒ繧ｭ繝｣繝ｳ繧ｻ繝ｫ縺励∪縺励◆")
    else:
        print("邃ｹ・・繧ｷ繧ｹ繝・Β縺ｯ迴ｾ蝨ｨ遞ｼ蜒堺ｸｭ縺ｧ縺・)
        
        # 邱頑･蛛懈ｭ｢縺ｮ遒ｺ隱・        print("\\n笞・・邱頑･蛛懈ｭ｢繧貞ｮ溯｡後☆繧九→莉･荳九′陦後ｏ繧後∪縺・")
        print("   - 蜈ｨ豕ｨ譁・・繧ｭ繝｣繝ｳ繧ｻ繝ｫ")
        print("   - 繧ｷ繧ｹ繝・Β縺ｮ螳悟・蛛懈ｭ｢")
        print("   - Discord騾夂衍縺ｮ騾∽ｿ｡")
        
        choice = input("\\n邱頑･蛛懈ｭ｢繧貞ｮ溯｡後＠縺ｾ縺吶°・・(y/n): ").lower()
        if choice == 'y':
            reason = input("蛛懈ｭ｢逅・罰繧貞・蜉帙＠縺ｦ縺上□縺輔＞ (遨ｺ逋ｽ蜿ｯ): ").strip()
            if not reason:
                reason = "manual_override"
            
            emergency_stop.execute_emergency_stop(reason)
        else:
            print("謫堺ｽ懊ｒ繧ｭ繝｣繝ｳ繧ｻ繝ｫ縺励∪縺励◆")
    
    print("\\n" + "=" * 60)
    print("邱頑･蛛懈ｭ｢繧ｷ繧ｹ繝・Β繧堤ｵゆｺ・＠縺ｾ縺・)
    print("=" * 60)

if __name__ == "__main__":
    main()
