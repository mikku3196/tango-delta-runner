#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
迺ｰ蠅・､画焚縺ｨ險ｭ螳壹ヵ繧｡繧､繝ｫ縺ｮ繝・せ繝医せ繧ｯ繝ｪ繝励ヨ
"""

import sys
import os

def test_env_config():
    """迺ｰ蠅・､画焚縺ｨ險ｭ螳壹ヵ繧｡繧､繝ｫ縺ｮ隱ｭ縺ｿ霎ｼ縺ｿ繧偵ユ繧ｹ繝医☆繧・""
    print("迺ｰ蠅・､画焚縺ｨ險ｭ螳壹ヵ繧｡繧､繝ｫ縺ｮ繝・せ繝医ｒ髢句ｧ九＠縺ｾ縺・..")
    
    try:
        # 迺ｰ蠅・､画焚繝ｭ繝ｼ繝繝ｼ繧偵ユ繧ｹ繝・        from src.shared_modules.env_loader import EnvLoader
        env_loader = EnvLoader()
        
        print("\\n=== 迺ｰ蠅・､画焚繝・せ繝・===")
        print(f"IB_MAIN_ACCOUNT_ID: {env_loader.get('IB_MAIN_ACCOUNT_ID', 'NOT_SET')}")
        print(f"IB_NISA_ACCOUNT_ID: {env_loader.get('IB_NISA_ACCOUNT_ID', 'NOT_SET')}")
        print(f"DISCORD_WEBHOOK_URL: {env_loader.get('DISCORD_WEBHOOK_URL', 'NOT_SET')}")
        
        # 險ｭ螳壹Ο繝ｼ繝繝ｼ繧偵ユ繧ｹ繝・        from src.shared_modules.config_loader import ConfigLoader
        config_loader = ConfigLoader()
        
        print("\\n=== 險ｭ螳壹ヵ繧｡繧､繝ｫ繝・せ繝・===")
        print(f"繝昴・繝医ヵ繧ｩ繝ｪ繧ｪ豈皮紫 - 繧､繝ｳ繝・ャ繧ｯ繧ｹ: {config_loader.get('portfolio_ratios.index')}")
        print(f"繝昴・繝医ヵ繧ｩ繝ｪ繧ｪ豈皮紫 - 鬮倬・蠖・ {config_loader.get('portfolio_ratios.dividend')}")
        print(f"繝昴・繝医ヵ繧ｩ繝ｪ繧ｪ豈皮紫 - 繝ｬ繝ｳ繧ｸ: {config_loader.get('portfolio_ratios.range')}")
        print(f"繧､繝ｳ繝・ャ繧ｯ繧ｹBot驫俶氛: {config_loader.get('index_bot.ticker')}")
        print(f"譛域ｬ｡謚戊ｳ・｡・ {config_loader.get('index_bot.monthly_investment')}")
        
        # 險ｭ螳壽､懆ｨｼ
        print("\\n=== 險ｭ螳壽､懆ｨｼ ===")
        if config_loader.validate_config():
            print("險ｭ螳壽､懆ｨｼ: 謌仙粥")
        else:
            print("險ｭ螳壽､懆ｨｼ: 螟ｱ謨・)
        
        print("\\n繝・せ繝亥ｮ御ｺ・)
        
    except Exception as e:
        print(f"繧ｨ繝ｩ繝ｼ縺檎匱逕溘＠縺ｾ縺励◆: {str(e)}")
        print("繧ｨ繝ｩ繝ｼ縺ｮ隧ｳ邏ｰ:")
        print(f"繧ｨ繝ｩ繝ｼ繧ｿ繧､繝・ {type(e).__name__}")
        print("\\n蟇ｾ蜃ｦ譁ｹ豕・")
        print("1. .env繝輔ぃ繧､繝ｫ縺悟ｭ伜惠縺吶ｋ縺狗｢ｺ隱・)
        print("2. .env繝輔ぃ繧､繝ｫ縺ｫ蠢・ｦ√↑迺ｰ蠅・､画焚縺瑚ｨｭ螳壹＆繧後※縺・ｋ縺狗｢ｺ隱・)
        print("3. src/config/config.yaml繝輔ぃ繧､繝ｫ縺悟ｭ伜惠縺吶ｋ縺狗｢ｺ隱・)

if __name__ == "__main__":
    test_env_config()
