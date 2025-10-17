#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IB証券Gateway接続テストスクリプト
"""

import sys
import time
from src.shared_modules.ib_connector import IBConnector

def test_ib_connection():
    """IB証券Gatewayへの接続をチE��トすめE""
    print("IB証券Gateway接続テストを開始しまぁE..")
    
    # IBConnectorインスタンスを作�E
    ib_connector = IBConnector()
    
    try:
        # 設定値�E�Eonfig.yamlから読み込むか、直接持E��！E        host = "127.0.0.1"
        port = 5000
        client_id = 1
        
        print(f"接続�E: {host}:{port} (Client ID: {client_id})")
        
        # IB Gatewayに接続を試衁E        success = ib_connector.connect_to_ib(host, port, client_id)
        
        if success:
            print("接続�E劁E)
            
            # 接続を維持してから刁E��
            time.sleep(2)
            ib_connector.disconnect_from_ib()
            print("接続を刁E��しました")
            
        else:
            print("接続失敁E IB Gatewayに接続できませんでした")
            print("以下�E点を確認してください:")
            print("1. IB Client Portal Gatewayが起動してぁE��ぁE)
            print("2. API接続が有効になってぁE��ぁE)
            print("3. ポ�Eト番号が正しいぁE(チE��ォルチE 5000)")
            print("4. ファイアウォールの設宁E)
            
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        print("エラーの詳細:")
        print(f"エラータイチE {type(e).__name__}")
        
    finally:
        # 念のため接続を刁E��
        try:
            ib_connector.disconnect_from_ib()
        except:
            pass

if __name__ == "__main__":
    test_ib_connection()
