from src.shared_modules.config_loader import ConfigLoader
from src.shared_modules.discord_logger import DiscordLogger
from src.shared_modules.ib_connector import IBConnector

class CoreIndexBot:
    def __init__(self, config, discord, ib_connector):
        self.config = config
        self.discord = discord
        self.ib_connector = ib_connector
    
    def execute_monthly_investment(self):
        """毎月の積立投賁E��実衁E""
        try:
            ticker = self.config.get("index_bot.ticker")
            amount = self.config.get("index_bot.monthly_investment")
            nisa_account = self.config.get("ib_account.nisa_account_id")
            
            self.discord.info(f"インチE��クス積立を開姁E {ticker} {amount}冁E)
            
            # 契紁E���E
            contract = self.ib_connector.create_stock_contract(ticker)
            
            # 成行買ぁE��斁E            order = self.ib_connector.create_market_order("BUY", amount)
            
            # 注斁E��衁E            order_id = self.ib_connector.place_order(contract, order)
            
            # 取引通知
            self.discord.trade_notification("BUY", ticker, amount, order_id=order_id)
            
            self.discord.success(f"インチE��クス積立完亁E {ticker} {amount}冁E(注文ID: {order_id})")
            
        except Exception as e:
            self.discord.error(f"インチE��クス積立エラー: {str(e)}")
    
    def execute_additional_investment(self, amount):
        """追加投賁E��実行（リバランス時！E""
        try:
            ticker = self.config.get("index_bot.ticker")
            nisa_account = self.config.get("ib_account.nisa_account_id")
            
            self.discord.info(f"インチE��クス追加投賁E��開姁E {ticker} {amount}冁E)
            
            # 契紁E���E
            contract = self.ib_connector.create_stock_contract(ticker)
            
            # 成行買ぁE��斁E            order = self.ib_connector.create_market_order("BUY", amount)
            
            # 注斁E��衁E            order_id = self.ib_connector.place_order(contract, order)
            
            # 取引通知
            self.discord.trade_notification("BUY", ticker, amount, order_id=order_id)
            
            self.discord.success(f"インチE��クス追加投賁E��亁E {ticker} {amount}冁E(注文ID: {order_id})")
            
        except Exception as e:
            self.discord.error(f"インチE��クス追加投賁E��ラー: {str(e)}")
    
    def get_current_holdings(self):
        """現在の保有状況を取征E""
        try:
            # 実裁E�E後で詳細匁E            # IB APIを使用して保有銘柄を取征E            return []
        except Exception as e:
            self.discord.error(f"保有状況取得エラー: {str(e)}")
            return []
    
    def get_position_value(self):
        """現在のポジション価値を取征E""
        try:
            # 実裁E�E後で詳細匁E            # IB APIを使用してポジション価値を取征E            return 0
        except Exception as e:
            self.discord.error(f"ポジション価値取得エラー: {str(e)}")
            return 0
