#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IB証券Gateway接続テストスクリプト
"""

import sys
import time
from src.shared_modules.ib_connector import IBConnector

def test_ib_connection():
    """IB証券Gatewayへの接続をテストする"""
    print("IB証券Gateway接続テストを開始します...")
    
    # IBConnectorインスタンスを作成
    ib_connector = IBConnector()
    
    try:
        # 設定値（config.yamlから読み込むか、直接指定）
        host = "127.0.0.1"
        port = 5000
        client_id = 1
        
        print(f"接続先: {host}:{port} (Client ID: {client_id})")
        
        # IB Gatewayに接続を試行
        success = ib_connector.connect_to_ib(host, port, client_id)
        
        if success:
            print("接続成功")
            
            # 接続を維持してから切断
            time.sleep(2)
            ib_connector.disconnect_from_ib()
            print("接続を切断しました")
            
        else:
            print("接続失敗: IB Gatewayに接続できませんでした")
            print("以下の点を確認してください:")
            print("1. IB Client Portal Gatewayが起動しているか")
            print("2. API接続が有効になっているか")
            print("3. ポート番号が正しいか (デフォルト: 5000)")
            print("4. ファイアウォールの設定")
            
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        print("エラーの詳細:")
        print(f"エラータイプ: {type(e).__name__}")
        
    finally:
        # 念のため接続を切断
        try:
            ib_connector.disconnect_from_ib()
        except:
            pass

if __name__ == "__main__":
    test_ib_connection()
