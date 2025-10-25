from ib_insync import IB
import asyncio
import os
from dotenv import load_dotenv

class IBConnector:
    def __init__(self, host='127.0.0.1', port=5000, client_id=1):
        """
        IB APIへの接続を管理するクラス。
        """
        self.host = host
        self.port = port
        self.client_id = client_id
        self.ib = IB()
        
        # 環境変数を読み込み
        load_dotenv()
        
        # 環境変数から設定を取得（存在する場合）
        self.host = os.getenv('IB_GATEWAY_HOST', host)
        self.port = int(os.getenv('IB_GATEWAY_PORT', port))
        self.client_id = int(os.getenv('IB_CLIENT_ID', client_id))

    async def connect(self):
        """
        IB Client Portal Gatewayに非同期で接続を試みる。
        """
        print("IB Gatewayへの接続を試みています...")
        try:
            if not self.ib.isConnected():
                await self.ib.connectAsync(self.host, self.port, clientId=self.client_id)
                print(f"接続成功: {self.ib.client}")
                return True
        except Exception as e:
            print(f"接続失敗: {e}")
            return False

    def disconnect(self):
        """
        IB Gatewayから切断する。
        """
        if self.ib.isConnected():
            print("IB Gatewayから切断します...")
            self.ib.disconnect()
            print("切断完了。")

    def get_ib_instance(self):
        """
        接続済みのIBインスタンスを返す。
        """
        return self.ib if self.ib.isConnected() else None

    async def get_account_summary(self):
        """
        口座サマリーを取得する。
        """
        if not self.ib.isConnected():
            raise Exception("IB接続が確立されていません")
        
        try:
            account_summary = self.ib.accountSummary()
            return account_summary
        except Exception as e:
            print(f"口座サマリー取得エラー: {e}")
            return None

    async def get_positions(self):
        """
        現在のポジションを取得する。
        """
        if not self.ib.isConnected():
            raise Exception("IB接続が確立されていません")
        
        try:
            positions = self.ib.positions()
            return positions
        except Exception as e:
            print(f"ポジション取得エラー: {e}")
            return None

    async def place_market_order(self, symbol, action, quantity, exchange="TSE"):
        """
        成行注文を発注する。
        """
        if not self.ib.isConnected():
            raise Exception("IB接続が確立されていません")
        
        try:
            # 契約を作成
            contract = self.ib.stock(symbol, exchange, "JPY")
            
            # 注文を作成
            order = self.ib.marketOrder(action, quantity)
            
            # 注文を発注
            trade = self.ib.placeOrder(contract, order)
            
            print(f"注文発注: {symbol} {action} {quantity}株")
            return trade
            
        except Exception as e:
            print(f"注文発注エラー: {e}")
            return None

# このファイルが直接実行された場合のテスト用コード
async def main():
    connector = IBConnector()
    if await connector.connect():
        # 接続成功時のテストアクション (例: 口座情報を取得)
        account_summary = await connector.get_account_summary()
        if account_summary:
            print("\n--- 口座サマリー ---")
            for item in account_summary:
                if item.tag == 'NetLiquidation':
                    print(f"  純資産価値: {item.value} {item.currency}")
                elif item.tag == 'TotalCashValue':
                    print(f"  現金残高: {item.value} {item.currency}")
            print("--------------------")
        
        # ポジション情報を取得
        positions = await connector.get_positions()
        if positions:
            print("\n--- 現在のポジション ---")
            for position in positions:
                print(f"  {position.contract.symbol}: {position.position}株")
            print("--------------------")
        
        # 切断
        connector.disconnect()
    else:
        print("プログラムを終了します。IB Gatewayが起動しているか、ホスト/ポート設定を確認してください。")


if __name__ == "__main__":
    # Windowsで 'asyncio' を正しく動作させるための設定
    # `asyncio.run` はイベントループを自動管理してくれる
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("プログラムが中断されました。")
