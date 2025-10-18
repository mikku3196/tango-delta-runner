#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
リスク許容度診断のチE��トスクリプト
"""

import sys
from src.shared_modules.config_loader import ConfigLoader
from src.shared_modules.risk_assessor import RiskAssessor

def test_risk_assessment():
    """リスク許容度診断をテストすめE""
    print("リスク許容度診断チE��トを開始しまぁE..")
    
    try:
        # 設定ローダーを�E期化
        config_loader = ConfigLoader()
        
        # リスクアセチE��ーを�E期化
        risk_assessor = RiskAssessor(config_loader)
        
        print("\\n=== プロファイル惁E�� ===")
        profiles = config_loader.get("risk_assessment.profiles", {})
        for profile_name, ratios in profiles.items():
            description = risk_assessor.get_profile_description(profile_name)
            print(f"{profile_name}: {description}")
            print(f"  比率 - インチE��クス: {ratios['index']:.1%}, 高�E彁E {ratios['dividend']:.1%}, レンジ: {ratios['range']:.1%}")
        
        print("\\n=== 診断実衁E===")
        print("実際の診断を実行する場合�E 'y' を�E力してください")
        print("スキチE�Eする場合�E 'n' を�E力してください")
        
        choice = input("診断を実行しますか�E�E(y/n): ").lower()
        
        if choice == 'y':
            # 実際の診断を実衁E            profile = risk_assessor.conduct_risk_assessment()
            
            # 設定を更新
            if risk_assessor.update_config_with_profile(profile):
                print("\\n設定が正常に更新されました")
            else:
                print("\\n設定�E更新に失敗しました")
        else:
            print("\\n診断をスキチE�Eしました")
            print("吁E�Eロファイルの比率を表示しまぁE")
            
            for profile_name in ["stable", "balanced", "aggressive"]:
                ratios = risk_assessor.get_portfolio_ratios(profile_name)
                print(f"{profile_name}: {ratios}")
        
        print("\\nチE��ト完亁E)
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        print("エラーの詳細:")
        print(f"エラータイチE {type(e).__name__}")

if __name__ == "__main__":
    test_risk_assessment()
