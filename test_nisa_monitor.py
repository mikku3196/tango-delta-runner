#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NISA髱櫁ｪｲ遞取棧逶｣隕悶・繝・せ繝医せ繧ｯ繝ｪ繝励ヨ
"""

import sys
from src.shared_modules.config_loader import ConfigLoader
from src.shared_modules.discord_logger import DiscordLogger
from src.shared_modules.ib_connector import IBConnector
from src.shared_modules.nisa_monitor import NISAMonitor

def test_nisa_monitor():
    """NISA逶｣隕匁ｩ溯・繧偵ユ繧ｹ繝医☆繧・""
    print("NISA髱櫁ｪｲ遞取棧逶｣隕悶ユ繧ｹ繝医ｒ髢句ｧ九＠縺ｾ縺・..")
    
    try:
        # 繝｢繧ｸ繝･繝ｼ繝ｫ繧貞・譛溷喧
        config_loader = ConfigLoader()
        discord_logger = DiscordLogger("dummy_webhook_url")  # 繝・せ繝育畑
        ib_connector = IBConnector()
        
        # NISA逶｣隕悶ｒ蛻晄悄蛹・        nisa_monitor = NISAMonitor(config_loader, discord_logger, ib_connector)
        
        print("\\n=== NISA險ｭ螳壽ュ蝣ｱ ===")
        print(f"蟷ｴ髢謎ｸ企剞: {nisa_monitor.annual_limit:,}蜀・)
        print(f"逕滓ｶｯ荳企剞: {nisa_monitor.lifetime_limit:,}蜀・)
        print(f"逶｣隕匁怏蜉ｹ: {nisa_monitor.monitoring_enabled}")
        
        print("\\n=== 迴ｾ蝨ｨ縺ｮ菴ｿ逕ｨ迥ｶ豕・===")
        annual_usage, lifetime_usage = nisa_monitor.get_current_usage()
        print(f"蟷ｴ髢謎ｽｿ逕ｨ驥・ {annual_usage:,}蜀・)
        print(f"逕滓ｶｯ菴ｿ逕ｨ驥・ {lifetime_usage:,}蜀・)
        
        print("\\n=== 谿九ｊ菴ｿ逕ｨ蜿ｯ閭ｽ鬘・===")
        annual_remaining, lifetime_remaining = nisa_monitor.get_remaining_limits()
        print(f"蟷ｴ髢捺ｮ九ｊ: {annual_remaining:,}蜀・)
        print(f"逕滓ｶｯ谿九ｊ: {lifetime_remaining:,}蜀・)
        
        print("\\n=== 謚戊ｳ・庄閭ｽ諤ｧ繝・せ繝・===")
        test_amounts = [100000, 1000000, 5000000]  # 10荳・・縲・00荳・・縲・00荳・・
        
        for amount in test_amounts:
            can_invest, reason = nisa_monitor.can_invest(amount)
            print(f"{amount:,}蜀・・謚戊ｳ・ {'蜿ｯ閭ｽ' if can_invest else '荳榊庄閭ｽ'} - {reason}")
        
        print("\\n=== 菴ｿ逕ｨ迥ｶ豕∵峩譁ｰ繝・せ繝・===")
        print("繝・せ繝育畑縺ｫ10荳・・縺ｮ菴ｿ逕ｨ繧定ｨ倬鹸縺励∪縺・)
        nisa_monitor.update_usage(100000)
        
        # 譖ｴ譁ｰ蠕後・迥ｶ豕√ｒ陦ｨ遉ｺ
        annual_usage, lifetime_usage = nisa_monitor.get_current_usage()
        print(f"譖ｴ譁ｰ蠕・- 蟷ｴ髢謎ｽｿ逕ｨ驥・ {annual_usage:,}蜀・ 逕滓ｶｯ菴ｿ逕ｨ驥・ {lifetime_usage:,}蜀・)
        
        print("\\n=== 蛛懈ｭ｢繝輔Λ繧ｰ繝√ぉ繝・け ===")
        if nisa_monitor.check_stop_flag():
            print("蛛懈ｭ｢繝輔Λ繧ｰ縺悟ｭ伜惠縺励∪縺・)
        else:
            print("蛛懈ｭ｢繝輔Λ繧ｰ縺ｯ蟄伜惠縺励∪縺帙ｓ")
        
        print("\\n繝・せ繝亥ｮ御ｺ・)
        
    except Exception as e:
        print(f"繧ｨ繝ｩ繝ｼ縺檎匱逕溘＠縺ｾ縺励◆: {str(e)}")
        print("繧ｨ繝ｩ繝ｼ縺ｮ隧ｳ邏ｰ:")
        print(f"繧ｨ繝ｩ繝ｼ繧ｿ繧､繝・ {type(e).__name__}")

if __name__ == "__main__":
    test_nisa_monitor()
