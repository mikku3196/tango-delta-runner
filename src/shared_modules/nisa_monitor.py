#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NISA非課税枠監視モジュール
"""

import json
import os
from datetime import datetime, date
from typing import Dict, Tuple, Optional
from src.shared_modules.config_loader import ConfigLoader
from src.shared_modules.discord_logger import DiscordLogger
from src.shared_modules.ib_connector import IBConnector

class NISAMonitor:
    def __init__(self, config: ConfigLoader, discord: DiscordLogger, ib_connector: IBConnector):
        self.config = config
        self.discord = discord
        self.ib_connector = ib_connector
        
        # NISA設宁E        self.annual_limit = self.config.get("nisa_settings.annual_limit", 3600000)  # 360丁E�E
        self.lifetime_limit = self.config.get("nisa_settings.lifetime_limit", 18000000)  # 1,800丁E�E
        self.monitoring_enabled = self.config.get("nisa_settings.monitoring_enabled", True)
        
        # チE�Eタファイル
        self.usage_file = "nisa_usage.json"
        self.current_year = date.today().year
        
        # 使用状況データ
        self.usage_data = self._load_usage_data()
    
    def _load_usage_data(self) -> Dict:
        """NISA使用状況データを読み込み"""
        try:
            if os.path.exists(self.usage_file):
                with open(self.usage_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                return self._initialize_usage_data()
        except Exception as e:
            print(f"NISA使用状況データ読み込みエラー: {e}")
            return self._initialize_usage_data()
    
    def _initialize_usage_data(self) -> Dict:
        """初期使用状況データを作�E"""
        return {
            "annual_usage": {str(self.current_year): 0},
            "lifetime_usage": 0,
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_usage_data(self):
        """NISA使用状況データを保孁E""
        try:
            self.usage_data["last_updated"] = datetime.now().isoformat()
            with open(self.usage_file, "w", encoding="utf-8") as f:
                json.dump(self.usage_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"NISA使用状況データ保存エラー: {e}")
    
    def get_current_usage(self) -> Tuple[int, int]:
        """現在のNISA使用状況を取得（年間、生涯�E�E""
        try:
            annual_usage = self.usage_data["annual_usage"].get(str(self.current_year), 0)
            lifetime_usage = self.usage_data["lifetime_usage"]
            
            return annual_usage, lifetime_usage
        except Exception as e:
            print(f"使用状況取得エラー: {e}")
            return 0, 0
    
    def update_usage(self, amount: int, account_type: str = "nisa"):
        """NISA使用状況を更新"""
        if not self.monitoring_enabled:
            return
        
        try:
            # 年間使用量を更新
            if str(self.current_year) not in self.usage_data["annual_usage"]:
                self.usage_data["annual_usage"][str(self.current_year)] = 0
            
            self.usage_data["annual_usage"][str(self.current_year)] += amount
            
            # 生涯使用量を更新
            self.usage_data["lifetime_usage"] += amount
            
            # チE�Eタを保孁E            self._save_usage_data()
            
            print(f"NISA使用状況を更新: +{amount:,}冁E(年閁E {self.usage_data['annual_usage'][str(self.current_year)]:,}冁E 生涯: {self.usage_data['lifetime_usage']:,}冁E")
            
            # 上限チェチE��
            self._check_limits()
            
        except Exception as e:
            print(f"使用状況更新エラー: {e}")
    
    def _check_limits(self):
        """NISA上限をチェチE��"""
        annual_usage, lifetime_usage = self.get_current_usage()
        
        # 年間上限チェチE��
        if annual_usage >= self.annual_limit:
            self.discord.error(f"【NISA年間上限到達】年間使用釁E {annual_usage:,}冁E/ {self.annual_limit:,}冁E)
            self._create_stop_flag("annual_limit_reached")
        
        # 生涯上限チェチE��
        elif lifetime_usage >= self.lifetime_limit:
            self.discord.error(f"【NISA生涯上限到達】生涯使用釁E {lifetime_usage:,}冁E/ {self.lifetime_limit:,}冁E)
            self._create_stop_flag("lifetime_limit_reached")
        
        # 警告レベル�E�E0%到達！E        elif annual_usage >= self.annual_limit * 0.8:
            remaining = self.annual_limit - annual_usage
            self.discord.warning(f"【NISA年間上限警告】残り: {remaining:,}冁E(使用釁E {annual_usage:,}冁E")
        
        elif lifetime_usage >= self.lifetime_limit * 0.8:
            remaining = self.lifetime_limit - lifetime_usage
            self.discord.warning(f"【NISA生涯上限警告】残り: {remaining:,}冁E(使用釁E {lifetime_usage:,}冁E")
    
    def _create_stop_flag(self, reason: str):
        """停止フラグを作�E"""
        try:
            stop_data = {
                "reason": reason,
                "timestamp": datetime.now().isoformat(),
                "annual_usage": self.usage_data["annual_usage"].get(str(self.current_year), 0),
                "lifetime_usage": self.usage_data["lifetime_usage"]
            }
            
            with open("STOP.flag", "w", encoding="utf-8") as f:
                json.dump(stop_data, f, ensure_ascii=False, indent=2)
            
            print(f"停止フラグを作�Eしました: {reason}")
            
        except Exception as e:
            print(f"停止フラグ作�Eエラー: {e}")
    
    def check_stop_flag(self) -> bool:
        """停止フラグの存在をチェチE��"""
        return os.path.exists("STOP.flag")
    
    def remove_stop_flag(self):
        """停止フラグを削除"""
        try:
            if os.path.exists("STOP.flag"):
                os.remove("STOP.flag")
                print("停止フラグを削除しました")
        except Exception as e:
            print(f"停止フラグ削除エラー: {e}")
    
    def can_invest(self, amount: int) -> Tuple[bool, str]:
        """持E����額�E投賁E��可能かチェチE��"""
        if not self.monitoring_enabled:
            return True, "監視無効"
        
        annual_usage, lifetime_usage = self.get_current_usage()
        
        # 年間上限チェチE��
        if annual_usage + amount > self.annual_limit:
            remaining = self.annual_limit - annual_usage
            return False, f"年間上限趁E�� (残り: {remaining:,}冁E"
        
        # 生涯上限チェチE��
        if lifetime_usage + amount > self.lifetime_limit:
            remaining = self.lifetime_limit - lifetime_usage
            return False, f"生涯上限趁E�� (残り: {remaining:,}冁E"
        
        return True, "投賁E��能"
    
    def get_remaining_limits(self) -> Tuple[int, int]:
        """残り使用可能額を取得（年間、生涯�E�E""
        annual_usage, lifetime_usage = self.get_current_usage()
        
        annual_remaining = max(0, self.annual_limit - annual_usage)
        lifetime_remaining = max(0, self.lifetime_limit - lifetime_usage)
        
        return annual_remaining, lifetime_remaining
    
    def send_usage_report(self):
        """使用状況レポ�EトをDiscordに送信"""
        try:
            annual_usage, lifetime_usage = self.get_current_usage()
            annual_remaining, lifetime_remaining = self.get_remaining_limits()
            
            fields = [
                {"name": "年間使用釁E, "value": f"{annual_usage:,}冁E, "inline": True},
                {"name": "年間残り", "value": f"{annual_remaining:,}冁E, "inline": True},
                {"name": "生涯使用釁E, "value": f"{lifetime_usage:,}冁E, "inline": True},
                {"name": "生涯残り", "value": f"{lifetime_remaining:,}冁E, "inline": True},
                {"name": "年間使用玁E, "value": f"{(annual_usage/self.annual_limit)*100:.1f}%", "inline": True},
                {"name": "生涯使用玁E, "value": f"{(lifetime_usage/self.lifetime_limit)*100:.1f}%", "inline": True}
            ]
            
            self.discord.info("NISA使用状況レポ�EチE, fields)
            
        except Exception as e:
            print(f"レポ�Eト送信エラー: {e}")
    
    def reset_annual_usage(self):
        """年間使用量をリセチE���E�新年用�E�E""
        try:
            new_year = date.today().year
            if new_year != self.current_year:
                self.usage_data["annual_usage"][str(new_year)] = 0
                self.current_year = new_year
                self._save_usage_data()
                self.discord.info(f"NISA年間使用量をリセチE��しました ({new_year}年)")
        except Exception as e:
            print(f"年間使用量リセチE��エラー: {e}")
