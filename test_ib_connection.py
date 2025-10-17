#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IB險ｼ蛻ｸGateway謗･邯壹ユ繧ｹ繝医せ繧ｯ繝ｪ繝励ヨ
"""

import sys
import time
from src.shared_modules.ib_connector import IBConnector

def test_ib_connection():
    """IB險ｼ蛻ｸGateway縺ｸ縺ｮ謗･邯壹ｒ繝・せ繝医☆繧・""
    print("IB險ｼ蛻ｸGateway謗･邯壹ユ繧ｹ繝医ｒ髢句ｧ九＠縺ｾ縺・..")
    
    # IBConnector繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ繧剃ｽ懈・
    ib_connector = IBConnector()
    
    try:
        # 險ｭ螳壼､・・onfig.yaml縺九ｉ隱ｭ縺ｿ霎ｼ繧縺九∫峩謗･謖・ｮ夲ｼ・        host = "127.0.0.1"
        port = 5000
        client_id = 1
        
        print(f"謗･邯壼・: {host}:{port} (Client ID: {client_id})")
        
        # IB Gateway縺ｫ謗･邯壹ｒ隧ｦ陦・        success = ib_connector.connect_to_ib(host, port, client_id)
        
        if success:
            print("謗･邯壽・蜉・)
            
            # 謗･邯壹ｒ邯ｭ謖√＠縺ｦ縺九ｉ蛻・妙
            time.sleep(2)
            ib_connector.disconnect_from_ib()
            print("謗･邯壹ｒ蛻・妙縺励∪縺励◆")
            
        else:
            print("謗･邯壼､ｱ謨・ IB Gateway縺ｫ謗･邯壹〒縺阪∪縺帙ｓ縺ｧ縺励◆")
            print("莉･荳九・轤ｹ繧堤｢ｺ隱阪＠縺ｦ縺上□縺輔＞:")
            print("1. IB Client Portal Gateway縺瑚ｵｷ蜍輔＠縺ｦ縺・ｋ縺・)
            print("2. API謗･邯壹′譛牙柑縺ｫ縺ｪ縺｣縺ｦ縺・ｋ縺・)
            print("3. 繝昴・繝育分蜿ｷ縺梧ｭ｣縺励＞縺・(繝・ヵ繧ｩ繝ｫ繝・ 5000)")
            print("4. 繝輔ぃ繧､繧｢繧ｦ繧ｩ繝ｼ繝ｫ縺ｮ險ｭ螳・)
            
    except Exception as e:
        print(f"繧ｨ繝ｩ繝ｼ縺檎匱逕溘＠縺ｾ縺励◆: {str(e)}")
        print("繧ｨ繝ｩ繝ｼ縺ｮ隧ｳ邏ｰ:")
        print(f"繧ｨ繝ｩ繝ｼ繧ｿ繧､繝・ {type(e).__name__}")
        
    finally:
        # 蠢ｵ縺ｮ縺溘ａ謗･邯壹ｒ蛻・妙
        try:
            ib_connector.disconnect_from_ib()
        except:
            pass

if __name__ == "__main__":
    test_ib_connection()
