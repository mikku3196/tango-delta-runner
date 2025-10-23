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
        """IB Gatewayに接続"""
        try:
            self.connect(host, port, client_id)
            self.thread = threading.Thread(target=self.run, daemon=True)
            self.thread.start()
            time.sleep(1)
            return self.connected
        except Exception as e:
            print(f"IB接続エラー: {e}")
            return False
    
    def disconnect_from_ib(self):
        """IB Gatewayから切断"""
        if self.connected:
            self.disconnect()
            if self.thread:
                self.thread.join(timeout=5)
    
    def connectionClosed(self):
        """接続が閉じられた時のコールバック"""
        self.connected = False
        print("IB接続が切断されました")
    
    def nextValidId(self, orderId):
        """次の有効な注文IDを受け取った時のコールバック"""
        self.next_order_id = orderId
        self.connected = True
        print(f"IB接続が確立されました。次の注文ID: {orderId}")
    
    def place_order(self, contract, order):
        """注文を発注"""
        if not self.connected:
            raise Exception("IB接続が確立されていません")
        
        self.placeOrder(self.next_order_id, contract, order)
        order_id = self.next_order_id
        self.next_order_id += 1
        return order_id
    
    def create_stock_contract(self, symbol, exchange="TSE"):
        """株式契約を作成"""
        contract = Contract()
        contract.symbol = symbol
        contract.secType = "STK"
        contract.exchange = exchange
        contract.currency = "JPY"
        return contract
    
    def create_market_order(self, action, quantity):
        """成行注文を作成"""
        order = Order()
        order.action = action
        order.orderType = "MKT"
        order.totalQuantity = quantity
        return order
    
    def create_limit_order(self, action, quantity, limit_price):
        """指値注文を作成"""
        order = Order()
        order.action = action
        order.orderType = "LMT"
        order.totalQuantity = quantity
        order.lmtPrice = limit_price
        return order
    
    def get_account_summary(self, account_id):
        """口座サマリーを取得"""
        if not self.connected:
            raise Exception("IB接続が確立されていません")
        
        self.reqAccountSummary(1, "All", "TotalCashValue,NetLiquidation,GrossPositionValue")
        return True
    
    def accountSummary(self, reqId, account, tag, value, currency):
        """口座サマリーのコールバック"""
        print(f"口座サマリー - {tag}: {value} {currency}")
    
    def error(self, reqId, errorCode, errorString):
        """エラーのコールバック"""
        print(f"IB API エラー [{errorCode}]: {errorString}")
