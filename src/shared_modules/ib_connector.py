from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
import threading
import time

class IBConnector(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.connected = False
        self.next_order_id = 1
        self.thread = None
    
    def connect_to_ib(self, host, port, client_id):
        """IB Gateway縺ｫ謗･邯・""
        try:
            self.connect(host, port, client_id)
            self.thread = threading.Thread(target=self.run, daemon=True)
            self.thread.start()
            time.sleep(1)
            return self.connected
        except Exception as e:
            print(f"IB謗･邯壹お繝ｩ繝ｼ: {e}")
            return False
    
    def disconnect_from_ib(self):
        """IB Gateway縺九ｉ蛻・妙"""
        if self.connected:
            self.disconnect()
            if self.thread:
                self.thread.join(timeout=5)
    
    def connectionClosed(self):
        """謗･邯壹′髢峨§繧峨ｌ縺滓凾縺ｮ繧ｳ繝ｼ繝ｫ繝舌ャ繧ｯ"""
        self.connected = False
        print("IB謗･邯壹′蛻・妙縺輔ｌ縺ｾ縺励◆")
    
    def nextValidId(self, orderId):
        """谺｡縺ｮ譛牙柑縺ｪ豕ｨ譁⑩D繧貞女縺大叙縺｣縺滓凾縺ｮ繧ｳ繝ｼ繝ｫ繝舌ャ繧ｯ"""
        self.next_order_id = orderId
        self.connected = True
        print(f"IB謗･邯壹′遒ｺ遶九＆繧後∪縺励◆縲よｬ｡縺ｮ豕ｨ譁⑩D: {orderId}")
    
    def place_order(self, contract, order):
        """豕ｨ譁・ｒ逋ｺ豕ｨ"""
        if not self.connected:
            raise Exception("IB謗･邯壹′遒ｺ遶九＆繧後※縺・∪縺帙ｓ")
        
        self.placeOrder(self.next_order_id, contract, order)
        order_id = self.next_order_id
        self.next_order_id += 1
        return order_id
    
    def create_stock_contract(self, symbol, exchange="TSE"):
        """譬ｪ蠑丞･醍ｴ・ｒ菴懈・"""
        contract = Contract()
        contract.symbol = symbol
        contract.secType = "STK"
        contract.exchange = exchange
        contract.currency = "JPY"
        return contract
    
    def create_market_order(self, action, quantity):
        """謌占｡梧ｳｨ譁・ｒ菴懈・"""
        order = Order()
        order.action = action
        order.orderType = "MKT"
        order.totalQuantity = quantity
        return order
    
    def create_limit_order(self, action, quantity, limit_price):
        """謖・､豕ｨ譁・ｒ菴懈・"""
        order = Order()
        order.action = action
        order.orderType = "LMT"
        order.totalQuantity = quantity
        order.lmtPrice = limit_price
        return order
    
    def get_account_summary(self, account_id):
        """蜿｣蠎ｧ繧ｵ繝槭Μ繝ｼ繧貞叙蠕・""
        if not self.connected:
            raise Exception("IB謗･邯壹′遒ｺ遶九＆繧後※縺・∪縺帙ｓ")
        
        self.reqAccountSummary(1, "All", "TotalCashValue,NetLiquidation,GrossPositionValue")
        return True
    
    def accountSummary(self, reqId, account, tag, value, currency):
        """蜿｣蠎ｧ繧ｵ繝槭Μ繝ｼ縺ｮ繧ｳ繝ｼ繝ｫ繝舌ャ繧ｯ"""
        print(f"蜿｣蠎ｧ繧ｵ繝槭Μ繝ｼ - {tag}: {value} {currency}")
    
    def error(self, reqId, errorCode, errorString):
        """繧ｨ繝ｩ繝ｼ縺ｮ繧ｳ繝ｼ繝ｫ繝舌ャ繧ｯ"""
        print(f"IB API 繧ｨ繝ｩ繝ｼ [{errorCode}]: {errorString}")
