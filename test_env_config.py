#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
環墁E��数と設定ファイルのチE��トスクリプト
"""

import sys
import os

def test_env_config():
    """環墁E��数と設定ファイルの読み込みをテストすめE""
    print("環墁E��数と設定ファイルのチE��トを開始しまぁE..")
    
    try:
        # 環墁E��数ローダーをテスチE        from src.shared_modules.env_loader import EnvLoader
        env_loader = EnvLoader()
        
        print("\\n=== 環墁E��数チE��チE===")
        print(f"IB_MAIN_ACCOUNT_ID: {env_loader.get('IB_MAIN_ACCOUNT_ID', 'NOT_SET')}")
        print(f"IB_NISA_ACCOUNT_ID: {env_loader.get('IB_NISA_ACCOUNT_ID', 'NOT_SET')}")
        print(f"DISCORD_WEBHOOK_URL: {env_loader.get('DISCORD_WEBHOOK_URL', 'NOT_SET')}")
        
        # 設定ローダーをテスチE        from src.shared_modules.config_loader import ConfigLoader
        config_loader = ConfigLoader()
        
        print("\\n=== 設定ファイルチE��チE===")
        print(f"ポ�Eトフォリオ比率 - インチE��クス: {config_loader.get('portfolio_ratios.index')}")
        print(f"ポ�Eトフォリオ比率 - 高�E彁E {config_loader.get('portfolio_ratios.dividend')}")
        print(f"ポ�Eトフォリオ比率 - レンジ: {config_loader.get('portfolio_ratios.range')}")
        print(f"インチE��クスBot銘柄: {config_loader.get('index_bot.ticker')}")
        print(f"月次投賁E��E {config_loader.get('index_bot.monthly_investment')}")
        
        # 設定検証
        print("\\n=== 設定検証 ===")
        if config_loader.validate_config():
            print("設定検証: 成功")
        else:
            print("設定検証: 失敁E)
        
        print("\\nチE��ト完亁E)
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        print("エラーの詳細:")
        print(f"エラータイチE {type(e).__name__}")
        print("\\n対処方況E")
        print("1. .envファイルが存在するか確誁E)
        print("2. .envファイルに忁E��な環墁E��数が設定されてぁE��か確誁E)
        print("3. src/config/config.yamlファイルが存在するか確誁E)

if __name__ == "__main__":
    test_env_config()
