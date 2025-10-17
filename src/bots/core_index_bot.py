from src.shared_modules.config_loader import ConfigLoader
from src.shared_modules.discord_logger import DiscordLogger
from src.shared_modules.ib_connector import IBConnector

class CoreIndexBot:
    def __init__(self, config, discord, ib_connector):
        self.config = config
        self.discord = discord
        self.ib_connector = ib_connector
    
    def execute_monthly_investment(self):
        """豈取怦縺ｮ遨咲ｫ区兜雉・ｒ螳溯｡・""
        try:
            ticker = self.config.get("index_bot.ticker")
            amount = self.config.get("index_bot.monthly_investment")
            nisa_account = self.config.get("ib_account.nisa_account_id")
            
            self.discord.info(f"繧､繝ｳ繝・ャ繧ｯ繧ｹ遨咲ｫ九ｒ髢句ｧ・ {ticker} {amount}蜀・)
            
            # 螂醍ｴ・ｽ懈・
            contract = self.ib_connector.create_stock_contract(ticker)
            
            # 謌占｡瑚ｲｷ縺・ｳｨ譁・            order = self.ib_connector.create_market_order("BUY", amount)
            
            # 豕ｨ譁・ｮ溯｡・            order_id = self.ib_connector.place_order(contract, order)
            
            # 蜿門ｼ暮夂衍
            self.discord.trade_notification("BUY", ticker, amount, order_id=order_id)
            
            self.discord.success(f"繧､繝ｳ繝・ャ繧ｯ繧ｹ遨咲ｫ句ｮ御ｺ・ {ticker} {amount}蜀・(豕ｨ譁⑩D: {order_id})")
            
        except Exception as e:
            self.discord.error(f"繧､繝ｳ繝・ャ繧ｯ繧ｹ遨咲ｫ九お繝ｩ繝ｼ: {str(e)}")
    
    def execute_additional_investment(self, amount):
        """霑ｽ蜉謚戊ｳ・ｒ螳溯｡鯉ｼ医Μ繝舌Λ繝ｳ繧ｹ譎ゑｼ・""
        try:
            ticker = self.config.get("index_bot.ticker")
            nisa_account = self.config.get("ib_account.nisa_account_id")
            
            self.discord.info(f"繧､繝ｳ繝・ャ繧ｯ繧ｹ霑ｽ蜉謚戊ｳ・ｒ髢句ｧ・ {ticker} {amount}蜀・)
            
            # 螂醍ｴ・ｽ懈・
            contract = self.ib_connector.create_stock_contract(ticker)
            
            # 謌占｡瑚ｲｷ縺・ｳｨ譁・            order = self.ib_connector.create_market_order("BUY", amount)
            
            # 豕ｨ譁・ｮ溯｡・            order_id = self.ib_connector.place_order(contract, order)
            
            # 蜿門ｼ暮夂衍
            self.discord.trade_notification("BUY", ticker, amount, order_id=order_id)
            
            self.discord.success(f"繧､繝ｳ繝・ャ繧ｯ繧ｹ霑ｽ蜉謚戊ｳ・ｮ御ｺ・ {ticker} {amount}蜀・(豕ｨ譁⑩D: {order_id})")
            
        except Exception as e:
            self.discord.error(f"繧､繝ｳ繝・ャ繧ｯ繧ｹ霑ｽ蜉謚戊ｳ・お繝ｩ繝ｼ: {str(e)}")
    
    def get_current_holdings(self):
        """迴ｾ蝨ｨ縺ｮ菫晄怏迥ｶ豕√ｒ蜿門ｾ・""
        try:
            # 螳溯｣・・蠕後〒隧ｳ邏ｰ蛹・            # IB API繧剃ｽｿ逕ｨ縺励※菫晄怏驫俶氛繧貞叙蠕・            return []
        except Exception as e:
            self.discord.error(f"菫晄怏迥ｶ豕∝叙蠕励お繝ｩ繝ｼ: {str(e)}")
            return []
    
    def get_position_value(self):
        """迴ｾ蝨ｨ縺ｮ繝昴ず繧ｷ繝ｧ繝ｳ萓｡蛟､繧貞叙蠕・""
        try:
            # 螳溯｣・・蠕後〒隧ｳ邏ｰ蛹・            # IB API繧剃ｽｿ逕ｨ縺励※繝昴ず繧ｷ繝ｧ繝ｳ萓｡蛟､繧貞叙蠕・            return 0
        except Exception as e:
            self.discord.error(f"繝昴ず繧ｷ繝ｧ繝ｳ萓｡蛟､蜿門ｾ励お繝ｩ繝ｼ: {str(e)}")
            return 0
