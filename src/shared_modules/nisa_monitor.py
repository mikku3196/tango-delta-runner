#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NISA髱櫁ｪｲ遞取棧逶｣隕悶Δ繧ｸ繝･繝ｼ繝ｫ
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
        
        # NISA險ｭ螳・        self.annual_limit = self.config.get("nisa_settings.annual_limit", 3600000)  # 360荳・・
        self.lifetime_limit = self.config.get("nisa_settings.lifetime_limit", 18000000)  # 1,800荳・・
        self.monitoring_enabled = self.config.get("nisa_settings.monitoring_enabled", True)
        
        # 繝・・繧ｿ繝輔ぃ繧､繝ｫ
        self.usage_file = "nisa_usage.json"
        self.current_year = date.today().year
        
        # 菴ｿ逕ｨ迥ｶ豕√ョ繝ｼ繧ｿ
        self.usage_data = self._load_usage_data()
    
    def _load_usage_data(self) -> Dict:
        """NISA菴ｿ逕ｨ迥ｶ豕√ョ繝ｼ繧ｿ繧定ｪｭ縺ｿ霎ｼ縺ｿ"""
        try:
            if os.path.exists(self.usage_file):
                with open(self.usage_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                return self._initialize_usage_data()
        except Exception as e:
            print(f"NISA菴ｿ逕ｨ迥ｶ豕√ョ繝ｼ繧ｿ隱ｭ縺ｿ霎ｼ縺ｿ繧ｨ繝ｩ繝ｼ: {e}")
            return self._initialize_usage_data()
    
    def _initialize_usage_data(self) -> Dict:
        """蛻晄悄菴ｿ逕ｨ迥ｶ豕√ョ繝ｼ繧ｿ繧剃ｽ懈・"""
        return {
            "annual_usage": {str(self.current_year): 0},
            "lifetime_usage": 0,
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_usage_data(self):
        """NISA菴ｿ逕ｨ迥ｶ豕√ョ繝ｼ繧ｿ繧剃ｿ晏ｭ・""
        try:
            self.usage_data["last_updated"] = datetime.now().isoformat()
            with open(self.usage_file, "w", encoding="utf-8") as f:
                json.dump(self.usage_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"NISA菴ｿ逕ｨ迥ｶ豕√ョ繝ｼ繧ｿ菫晏ｭ倥お繝ｩ繝ｼ: {e}")
    
    def get_current_usage(self) -> Tuple[int, int]:
        """迴ｾ蝨ｨ縺ｮNISA菴ｿ逕ｨ迥ｶ豕√ｒ蜿門ｾ暦ｼ亥ｹｴ髢薙∫函豸ｯ・・""
        try:
            annual_usage = self.usage_data["annual_usage"].get(str(self.current_year), 0)
            lifetime_usage = self.usage_data["lifetime_usage"]
            
            return annual_usage, lifetime_usage
        except Exception as e:
            print(f"菴ｿ逕ｨ迥ｶ豕∝叙蠕励お繝ｩ繝ｼ: {e}")
            return 0, 0
    
    def update_usage(self, amount: int, account_type: str = "nisa"):
        """NISA菴ｿ逕ｨ迥ｶ豕√ｒ譖ｴ譁ｰ"""
        if not self.monitoring_enabled:
            return
        
        try:
            # 蟷ｴ髢謎ｽｿ逕ｨ驥上ｒ譖ｴ譁ｰ
            if str(self.current_year) not in self.usage_data["annual_usage"]:
                self.usage_data["annual_usage"][str(self.current_year)] = 0
            
            self.usage_data["annual_usage"][str(self.current_year)] += amount
            
            # 逕滓ｶｯ菴ｿ逕ｨ驥上ｒ譖ｴ譁ｰ
            self.usage_data["lifetime_usage"] += amount
            
            # 繝・・繧ｿ繧剃ｿ晏ｭ・            self._save_usage_data()
            
            print(f"NISA菴ｿ逕ｨ迥ｶ豕√ｒ譖ｴ譁ｰ: +{amount:,}蜀・(蟷ｴ髢・ {self.usage_data['annual_usage'][str(self.current_year)]:,}蜀・ 逕滓ｶｯ: {self.usage_data['lifetime_usage']:,}蜀・")
            
            # 荳企剞繝√ぉ繝・け
            self._check_limits()
            
        except Exception as e:
            print(f"菴ｿ逕ｨ迥ｶ豕∵峩譁ｰ繧ｨ繝ｩ繝ｼ: {e}")
    
    def _check_limits(self):
        """NISA荳企剞繧偵メ繧ｧ繝・け"""
        annual_usage, lifetime_usage = self.get_current_usage()
        
        # 蟷ｴ髢謎ｸ企剞繝√ぉ繝・け
        if annual_usage >= self.annual_limit:
            self.discord.error(f"縲侵ISA蟷ｴ髢謎ｸ企剞蛻ｰ驕斐大ｹｴ髢謎ｽｿ逕ｨ驥・ {annual_usage:,}蜀・/ {self.annual_limit:,}蜀・)
            self._create_stop_flag("annual_limit_reached")
        
        # 逕滓ｶｯ荳企剞繝√ぉ繝・け
        elif lifetime_usage >= self.lifetime_limit:
            self.discord.error(f"縲侵ISA逕滓ｶｯ荳企剞蛻ｰ驕斐醍函豸ｯ菴ｿ逕ｨ驥・ {lifetime_usage:,}蜀・/ {self.lifetime_limit:,}蜀・)
            self._create_stop_flag("lifetime_limit_reached")
        
        # 隴ｦ蜻翫Ξ繝吶Ν・・0%蛻ｰ驕費ｼ・        elif annual_usage >= self.annual_limit * 0.8:
            remaining = self.annual_limit - annual_usage
            self.discord.warning(f"縲侵ISA蟷ｴ髢謎ｸ企剞隴ｦ蜻翫第ｮ九ｊ: {remaining:,}蜀・(菴ｿ逕ｨ驥・ {annual_usage:,}蜀・")
        
        elif lifetime_usage >= self.lifetime_limit * 0.8:
            remaining = self.lifetime_limit - lifetime_usage
            self.discord.warning(f"縲侵ISA逕滓ｶｯ荳企剞隴ｦ蜻翫第ｮ九ｊ: {remaining:,}蜀・(菴ｿ逕ｨ驥・ {lifetime_usage:,}蜀・")
    
    def _create_stop_flag(self, reason: str):
        """蛛懈ｭ｢繝輔Λ繧ｰ繧剃ｽ懈・"""
        try:
            stop_data = {
                "reason": reason,
                "timestamp": datetime.now().isoformat(),
                "annual_usage": self.usage_data["annual_usage"].get(str(self.current_year), 0),
                "lifetime_usage": self.usage_data["lifetime_usage"]
            }
            
            with open("STOP.flag", "w", encoding="utf-8") as f:
                json.dump(stop_data, f, ensure_ascii=False, indent=2)
            
            print(f"蛛懈ｭ｢繝輔Λ繧ｰ繧剃ｽ懈・縺励∪縺励◆: {reason}")
            
        except Exception as e:
            print(f"蛛懈ｭ｢繝輔Λ繧ｰ菴懈・繧ｨ繝ｩ繝ｼ: {e}")
    
    def check_stop_flag(self) -> bool:
        """蛛懈ｭ｢繝輔Λ繧ｰ縺ｮ蟄伜惠繧偵メ繧ｧ繝・け"""
        return os.path.exists("STOP.flag")
    
    def remove_stop_flag(self):
        """蛛懈ｭ｢繝輔Λ繧ｰ繧貞炎髯､"""
        try:
            if os.path.exists("STOP.flag"):
                os.remove("STOP.flag")
                print("蛛懈ｭ｢繝輔Λ繧ｰ繧貞炎髯､縺励∪縺励◆")
        except Exception as e:
            print(f"蛛懈ｭ｢繝輔Λ繧ｰ蜑企勁繧ｨ繝ｩ繝ｼ: {e}")
    
    def can_invest(self, amount: int) -> Tuple[bool, str]:
        """謖・ｮ夐≡鬘阪・謚戊ｳ・′蜿ｯ閭ｽ縺九メ繧ｧ繝・け"""
        if not self.monitoring_enabled:
            return True, "逶｣隕也┌蜉ｹ"
        
        annual_usage, lifetime_usage = self.get_current_usage()
        
        # 蟷ｴ髢謎ｸ企剞繝√ぉ繝・け
        if annual_usage + amount > self.annual_limit:
            remaining = self.annual_limit - annual_usage
            return False, f"蟷ｴ髢謎ｸ企剞雜・℃ (谿九ｊ: {remaining:,}蜀・"
        
        # 逕滓ｶｯ荳企剞繝√ぉ繝・け
        if lifetime_usage + amount > self.lifetime_limit:
            remaining = self.lifetime_limit - lifetime_usage
            return False, f"逕滓ｶｯ荳企剞雜・℃ (谿九ｊ: {remaining:,}蜀・"
        
        return True, "謚戊ｳ・庄閭ｽ"
    
    def get_remaining_limits(self) -> Tuple[int, int]:
        """谿九ｊ菴ｿ逕ｨ蜿ｯ閭ｽ鬘阪ｒ蜿門ｾ暦ｼ亥ｹｴ髢薙∫函豸ｯ・・""
        annual_usage, lifetime_usage = self.get_current_usage()
        
        annual_remaining = max(0, self.annual_limit - annual_usage)
        lifetime_remaining = max(0, self.lifetime_limit - lifetime_usage)
        
        return annual_remaining, lifetime_remaining
    
    def send_usage_report(self):
        """菴ｿ逕ｨ迥ｶ豕√Ξ繝昴・繝医ｒDiscord縺ｫ騾∽ｿ｡"""
        try:
            annual_usage, lifetime_usage = self.get_current_usage()
            annual_remaining, lifetime_remaining = self.get_remaining_limits()
            
            fields = [
                {"name": "蟷ｴ髢謎ｽｿ逕ｨ驥・, "value": f"{annual_usage:,}蜀・, "inline": True},
                {"name": "蟷ｴ髢捺ｮ九ｊ", "value": f"{annual_remaining:,}蜀・, "inline": True},
                {"name": "逕滓ｶｯ菴ｿ逕ｨ驥・, "value": f"{lifetime_usage:,}蜀・, "inline": True},
                {"name": "逕滓ｶｯ谿九ｊ", "value": f"{lifetime_remaining:,}蜀・, "inline": True},
                {"name": "蟷ｴ髢謎ｽｿ逕ｨ邇・, "value": f"{(annual_usage/self.annual_limit)*100:.1f}%", "inline": True},
                {"name": "逕滓ｶｯ菴ｿ逕ｨ邇・, "value": f"{(lifetime_usage/self.lifetime_limit)*100:.1f}%", "inline": True}
            ]
            
            self.discord.info("NISA菴ｿ逕ｨ迥ｶ豕√Ξ繝昴・繝・, fields)
            
        except Exception as e:
            print(f"繝ｬ繝昴・繝磯∽ｿ｡繧ｨ繝ｩ繝ｼ: {e}")
    
    def reset_annual_usage(self):
        """蟷ｴ髢謎ｽｿ逕ｨ驥上ｒ繝ｪ繧ｻ繝・ヨ・域眠蟷ｴ逕ｨ・・""
        try:
            new_year = date.today().year
            if new_year != self.current_year:
                self.usage_data["annual_usage"][str(new_year)] = 0
                self.current_year = new_year
                self._save_usage_data()
                self.discord.info(f"NISA蟷ｴ髢謎ｽｿ逕ｨ驥上ｒ繝ｪ繧ｻ繝・ヨ縺励∪縺励◆ ({new_year}蟷ｴ)")
        except Exception as e:
            print(f"蟷ｴ髢謎ｽｿ逕ｨ驥上Μ繧ｻ繝・ヨ繧ｨ繝ｩ繝ｼ: {e}")
