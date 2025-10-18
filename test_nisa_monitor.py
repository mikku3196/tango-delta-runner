#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NISA非課税枠監視�EチE��トスクリプト
"""

import sys
from src.shared_modules.config_loader import ConfigLoader
from src.shared_modules.discord_logger import DiscordLogger
from src.shared_modules.ib_connector import IBConnector
from src.shared_modules.nisa_monitor import NISAMonitor

def test_nisa_monitor():
    """NISA監視機�EをテストすめE""
    print("NISA非課税枠監視テストを開始しまぁE..")
    
    try:
        # モジュールを�E期化
        config_loader = ConfigLoader()
        discord_logger = DiscordLogger("dummy_webhook_url")  # チE��ト用
        ib_connector = IBConnector()
        
        # NISA監視を初期匁E        nisa_monitor = NISAMonitor(config_loader, discord_logger, ib_connector)
        
        print("\\n=== NISA設定情報 ===")
        print(f"年間上限: {nisa_monitor.annual_limit:,}冁E)
        print(f"生涯上限: {nisa_monitor.lifetime_limit:,}冁E)
        print(f"監視有効: {nisa_monitor.monitoring_enabled}")
        
        print("\\n=== 現在の使用状況E===")
        annual_usage, lifetime_usage = nisa_monitor.get_current_usage()
        print(f"年間使用釁E {annual_usage:,}冁E)
        print(f"生涯使用釁E {lifetime_usage:,}冁E)
        
        print("\\n=== 残り使用可能顁E===")
        annual_remaining, lifetime_remaining = nisa_monitor.get_remaining_limits()
        print(f"年間残り: {annual_remaining:,}冁E)
        print(f"生涯残り: {lifetime_remaining:,}冁E)
        
        print("\\n=== 投賁E��能性チE��チE===")
        test_amounts = [100000, 1000000, 5000000]  # 10丁E�E、E00丁E�E、E00丁E�E
        
        for amount in test_amounts:
            can_invest, reason = nisa_monitor.can_invest(amount)
            print(f"{amount:,}冁E�E投賁E {'可能' if can_invest else '不可能'} - {reason}")
        
        print("\\n=== 使用状況更新チE��チE===")
        print("チE��ト用に10丁E�Eの使用を記録しまぁE)
        nisa_monitor.update_usage(100000)
        
        # 更新後�E状況を表示
        annual_usage, lifetime_usage = nisa_monitor.get_current_usage()
        print(f"更新征E- 年間使用釁E {annual_usage:,}冁E 生涯使用釁E {lifetime_usage:,}冁E)
        
        print("\\n=== 停止フラグチェチE�� ===")
        if nisa_monitor.check_stop_flag():
            print("停止フラグが存在しまぁE)
        else:
            print("停止フラグは存在しません")
        
        print("\\nチE��ト完亁E)
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        print("エラーの詳細:")
        print(f"エラータイチE {type(e).__name__}")

if __name__ == "__main__":
    test_nisa_monitor()
