#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
繝ｪ繧ｹ繧ｯ險ｱ螳ｹ蠎ｦ險ｺ譁ｭ縺ｮ繝・せ繝医せ繧ｯ繝ｪ繝励ヨ
"""

import sys
from src.shared_modules.config_loader import ConfigLoader
from src.shared_modules.risk_assessor import RiskAssessor

def test_risk_assessment():
    """繝ｪ繧ｹ繧ｯ險ｱ螳ｹ蠎ｦ險ｺ譁ｭ繧偵ユ繧ｹ繝医☆繧・""
    print("繝ｪ繧ｹ繧ｯ險ｱ螳ｹ蠎ｦ險ｺ譁ｭ繝・せ繝医ｒ髢句ｧ九＠縺ｾ縺・..")
    
    try:
        # 險ｭ螳壹Ο繝ｼ繝繝ｼ繧貞・譛溷喧
        config_loader = ConfigLoader()
        
        # 繝ｪ繧ｹ繧ｯ繧｢繧ｻ繝・し繝ｼ繧貞・譛溷喧
        risk_assessor = RiskAssessor(config_loader)
        
        print("\\n=== 繝励Ο繝輔ぃ繧､繝ｫ諠・ｱ ===")
        profiles = config_loader.get("risk_assessment.profiles", {})
        for profile_name, ratios in profiles.items():
            description = risk_assessor.get_profile_description(profile_name)
            print(f"{profile_name}: {description}")
            print(f"  豈皮紫 - 繧､繝ｳ繝・ャ繧ｯ繧ｹ: {ratios['index']:.1%}, 鬮倬・蠖・ {ratios['dividend']:.1%}, 繝ｬ繝ｳ繧ｸ: {ratios['range']:.1%}")
        
        print("\\n=== 險ｺ譁ｭ螳溯｡・===")
        print("螳滄圀縺ｮ險ｺ譁ｭ繧貞ｮ溯｡後☆繧句ｴ蜷医・ 'y' 繧貞・蜉帙＠縺ｦ縺上□縺輔＞")
        print("繧ｹ繧ｭ繝・・縺吶ｋ蝣ｴ蜷医・ 'n' 繧貞・蜉帙＠縺ｦ縺上□縺輔＞")
        
        choice = input("險ｺ譁ｭ繧貞ｮ溯｡後＠縺ｾ縺吶°・・(y/n): ").lower()
        
        if choice == 'y':
            # 螳滄圀縺ｮ險ｺ譁ｭ繧貞ｮ溯｡・            profile = risk_assessor.conduct_risk_assessment()
            
            # 險ｭ螳壹ｒ譖ｴ譁ｰ
            if risk_assessor.update_config_with_profile(profile):
                print("\\n險ｭ螳壹′豁｣蟶ｸ縺ｫ譖ｴ譁ｰ縺輔ｌ縺ｾ縺励◆")
            else:
                print("\\n險ｭ螳壹・譖ｴ譁ｰ縺ｫ螟ｱ謨励＠縺ｾ縺励◆")
        else:
            print("\\n險ｺ譁ｭ繧偵せ繧ｭ繝・・縺励∪縺励◆")
            print("蜷・・繝ｭ繝輔ぃ繧､繝ｫ縺ｮ豈皮紫繧定｡ｨ遉ｺ縺励∪縺・")
            
            for profile_name in ["stable", "balanced", "aggressive"]:
                ratios = risk_assessor.get_portfolio_ratios(profile_name)
                print(f"{profile_name}: {ratios}")
        
        print("\\n繝・せ繝亥ｮ御ｺ・)
        
    except Exception as e:
        print(f"繧ｨ繝ｩ繝ｼ縺檎匱逕溘＠縺ｾ縺励◆: {str(e)}")
        print("繧ｨ繝ｩ繝ｼ縺ｮ隧ｳ邏ｰ:")
        print(f"繧ｨ繝ｩ繝ｼ繧ｿ繧､繝・ {type(e).__name__}")

if __name__ == "__main__":
    test_risk_assessment()
