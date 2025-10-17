import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
from src.shared_modules.config_loader import ConfigLoader
from src.shared_modules.discord_logger import DiscordLogger
from src.shared_modules.ib_connector import IBConnector

class SatelliteDividendBot:
    def __init__(self, config, discord, ib_connector):
        self.config = config
        self.discord = discord
        self.ib_connector = ib_connector
        self.candidates_file = "purchase_candidate.csv"
        self.holdings_file = "dividend_holdings.csv"
    
    def run_screening(self):
        """鬮倬・蠖捺ｪ縺ｮ繧ｹ繧ｯ繝ｪ繝ｼ繝九Φ繧ｰ繧貞ｮ溯｡・""
        try:
            self.discord.info("鬮倬・蠖捺ｪ繧ｹ繧ｯ繝ｪ繝ｼ繝九Φ繧ｰ繧帝幕蟋・)
            
            # TOPIX100讒区・驫俶氛縺ｮ繧ｹ繧ｯ繝ｪ繝ｼ繝九Φ繧ｰ
            candidates = self.screen_dividend_stocks()
            
            # 邨先棡繧辰SV縺ｫ菫晏ｭ・            candidates.to_csv(self.candidates_file, index=False)
            
            self.discord.success(f"繧ｹ繧ｯ繝ｪ繝ｼ繝九Φ繧ｰ螳御ｺ・ {len(candidates)}驫俶氛繧貞呵｣懊→縺励※菫晏ｭ・)
            
        except Exception as e:
            self.discord.error(f"繧ｹ繧ｯ繝ｪ繝ｼ繝九Φ繧ｰ繧ｨ繝ｩ繝ｼ: {str(e)}")
    
    def screen_dividend_stocks(self):
        """鬮倬・蠖捺ｪ縺ｮ繧ｹ繧ｯ繝ｪ繝ｼ繝九Φ繧ｰ譚｡莉ｶ繧帝←逕ｨ"""
        try:
            # TOPIX100讒区・驫俶氛繝ｪ繧ｹ繝茨ｼ井ｻｮ縺ｮ繝・・繧ｿ・・            topix100_symbols = self.get_topix100_symbols()
            
            candidates = []
            
            for symbol in topix100_symbols[:10]:  # 繝・せ繝育畑縺ｫ10驫俶氛縺ｮ縺ｿ
                try:
                    stock_data = self.get_stock_fundamentals(symbol)
                    
                    if self.check_dividend_criteria(stock_data):
                        candidates.append({
                            'symbol': symbol,
                            'dividend_yield': stock_data.get('dividend_yield', 0),
                            'per': stock_data.get('per', 0),
                            'equity_ratio': stock_data.get('equity_ratio', 0),
                            'no_dividend_cut': stock_data.get('no_dividend_cut', True)
                        })
                        
                except Exception as e:
                    print(f"驫俶氛 {symbol} 縺ｮ繝・・繧ｿ蜿門ｾ励お繝ｩ繝ｼ: {e}")
                    continue
            
            return pd.DataFrame(candidates)
            
        except Exception as e:
            self.discord.error(f"繧ｹ繧ｯ繝ｪ繝ｼ繝九Φ繧ｰ蜃ｦ逅・お繝ｩ繝ｼ: {str(e)}")
            return pd.DataFrame()
    
    def get_topix100_symbols(self):
        """TOPIX100讒区・驫俶氛繧貞叙蠕・""
        # 螳溯｣・・蠕後〒隧ｳ邏ｰ蛹厄ｼ亥､夜ΚAPI縺ｾ縺溘・繧ｹ繧ｯ繝ｬ繧､繝斐Φ繧ｰ・・        return ["7203", "6758", "9984", "6861", "9432"]  # 莉ｮ縺ｮ繝・・繧ｿ
    
    def get_stock_fundamentals(self, symbol):
        """驫俶氛縺ｮ雋｡蜍吶ョ繝ｼ繧ｿ繧貞叙蠕・""
        try:
            # yfinance繧剃ｽｿ逕ｨ縺励※繝・・繧ｿ繧貞叙蠕・            ticker = yf.Ticker(f"{symbol}.T")
            info = ticker.info
            
            return {
                'dividend_yield': info.get('dividendYield', 0) * 100,  # 繝代・繧ｻ繝ｳ繝・                'per': info.get('trailingPE', 0),
                'equity_ratio': 50.0,  # 莉ｮ縺ｮ蛟､・亥ｮ溯｣・・蠕後〒隧ｳ邏ｰ蛹厄ｼ・                'no_dividend_cut': True  # 莉ｮ縺ｮ蛟､・亥ｮ溯｣・・蠕後〒隧ｳ邏ｰ蛹厄ｼ・            }
            
        except Exception as e:
            print(f"雋｡蜍吶ョ繝ｼ繧ｿ蜿門ｾ励お繝ｩ繝ｼ {symbol}: {e}")
            return {}
    
    def check_dividend_criteria(self, stock_data):
        """鬮倬・蠖捺ｪ縺ｮ譚｡莉ｶ繧偵メ繧ｧ繝・け"""
        try:
            # 驟榊ｽ灘茜蝗槭ｊ >= 3.5%
            if stock_data.get('dividend_yield', 0) < 3.5:
                return False
            
            # 閾ｪ蟾ｱ雉・悽豈皮紫 >= 40.0%
            if stock_data.get('equity_ratio', 0) < 40.0:
                return False
            
            # PER < 25
            if stock_data.get('per', 0) >= 25:
                return False
            
            # 驕主悉10蟷ｴ髢薙・貂幃・縺ｪ縺・            if not stock_data.get('no_dividend_cut', False):
                return False
            
            return True
            
        except Exception as e:
            print(f"譚｡莉ｶ繝√ぉ繝・け繧ｨ繝ｩ繝ｼ: {e}")
            return False
    
    def run_purchase_decision(self):
        """鬮倬・蠖捺ｪ縺ｮ雉ｼ蜈･蛻､譁ｭ繧貞ｮ溯｡・""
        try:
            self.discord.info("鬮倬・蠖捺ｪ雉ｼ蜈･蛻､譁ｭ繧帝幕蟋・)
            
            # 迴ｾ蝨ｨ縺ｮ菫晄怏驫俶氛謨ｰ繝√ぉ繝・け
            current_holdings = self.get_current_holdings()
            max_holdings = self.config.get("dividend_bot.max_holding_stocks")
            
            if len(current_holdings) >= max_holdings:
                self.discord.info("菫晄怏驫俶氛謨ｰ縺御ｸ企剞縺ｫ驕斐＠縺ｦ縺・ｋ縺溘ａ縲∬ｳｼ蜈･繧偵せ繧ｭ繝・・")
                return
            
            # 雉ｼ蜈･蛟呵｣懊°繧蛾∈螳・            try:
                candidates = pd.read_csv(self.candidates_file)
            except FileNotFoundError:
                self.discord.warning("雉ｼ蜈･蛟呵｣懊ヵ繧｡繧､繝ｫ縺瑚ｦ九▽縺九ｊ縺ｾ縺帙ｓ")
                return
            
            if candidates.empty:
                self.discord.warning("雉ｼ蜈･蛟呵｣懊′縺ゅｊ縺ｾ縺帙ｓ")
                return
            
            # 雉ｼ蜈･譚｡莉ｶ繝√ぉ繝・け
            for _, candidate in candidates.iterrows():
                if self.check_purchase_condition(candidate):
                    self.execute_purchase(candidate)
                    break
            
        except Exception as e:
            self.discord.error(f"雉ｼ蜈･蛻､譁ｭ繧ｨ繝ｩ繝ｼ: {str(e)}")
    
    def check_purchase_condition(self, candidate):
        """雉ｼ蜈･譚｡莉ｶ繧偵メ繧ｧ繝・け"""
        try:
            symbol = candidate['symbol']
            
            # 迴ｾ蝨ｨ縺ｮ譬ｪ萓｡ < 25譌･遘ｻ蜍募ｹｳ蝮・ｷ・            current_price = self.get_current_price(symbol)
            ma25 = self.get_moving_average(symbol, 25)
            
            if current_price < ma25:
                return True
            
            return False
            
        except Exception as e:
            print(f"雉ｼ蜈･譚｡莉ｶ繝√ぉ繝・け繧ｨ繝ｩ繝ｼ: {e}")
            return False
    
    def execute_purchase(self, candidate):
        """雉ｼ蜈･繧貞ｮ溯｡・""
        try:
            symbol = candidate['symbol']
            nisa_account = self.config.get("ib_account.nisa_account_id")
            
            # 雉ｼ蜈･驥鷹｡阪ｒ豎ｺ螳夲ｼ井ｻｮ縺ｮ蛟､・・            purchase_amount = 50000  # 5荳・・
            
            self.discord.info(f"鬮倬・蠖捺ｪ雉ｼ蜈･繧帝幕蟋・ {symbol} {purchase_amount}蜀・)
            
            # 螂醍ｴ・ｽ懈・
            contract = self.ib_connector.create_stock_contract(symbol)
            
            # 謌占｡瑚ｲｷ縺・ｳｨ譁・            order = self.ib_connector.create_market_order("BUY", purchase_amount)
            
            # 豕ｨ譁・ｮ溯｡・            order_id = self.ib_connector.place_order(contract, order)
            
            # 蜿門ｼ暮夂衍
            self.discord.trade_notification("BUY", symbol, purchase_amount, order_id=order_id)
            
            # 菫晄怏驫俶氛繝ｪ繧ｹ繝医↓霑ｽ蜉
            self.add_to_holdings(symbol, purchase_amount, order_id)
            
            self.discord.success(f"鬮倬・蠖捺ｪ雉ｼ蜈･螳御ｺ・ {symbol} {purchase_amount}蜀・(豕ｨ譁⑩D: {order_id})")
            
        except Exception as e:
            self.discord.error(f"雉ｼ蜈･螳溯｡後お繝ｩ繝ｼ: {str(e)}")
    
    def get_current_price(self, symbol):
        """迴ｾ蝨ｨ縺ｮ譬ｪ萓｡繧貞叙蠕・""
        try:
            ticker = yf.Ticker(f"{symbol}.T")
            hist = ticker.history(period="1d")
            return hist['Close'].iloc[-1]
        except Exception as e:
            print(f"譬ｪ萓｡蜿門ｾ励お繝ｩ繝ｼ {symbol}: {e}")
            return 0
    
    def get_moving_average(self, symbol, period):
        """遘ｻ蜍募ｹｳ蝮・ｒ蜿門ｾ・""
        try:
            ticker = yf.Ticker(f"{symbol}.T")
            hist = ticker.history(period=f"{period+10}d")
            return hist['Close'].rolling(window=period).mean().iloc[-1]
        except Exception as e:
            print(f"遘ｻ蜍募ｹｳ蝮・叙蠕励お繝ｩ繝ｼ {symbol}: {e}")
            return 0
    
    def get_current_holdings(self):
        """迴ｾ蝨ｨ縺ｮ菫晄怏驫俶氛繧貞叙蠕・""
        try:
            df = pd.read_csv(self.holdings_file)
            return df['symbol'].tolist()
        except FileNotFoundError:
            return []
        except Exception as e:
            print(f"菫晄怏驫俶氛蜿門ｾ励お繝ｩ繝ｼ: {e}")
            return []
    
    def add_to_holdings(self, symbol, amount, order_id):
        """菫晄怏驫俶氛繝ｪ繧ｹ繝医↓霑ｽ蜉"""
        try:
            new_holding = pd.DataFrame({
                'symbol': [symbol],
                'amount': [amount],
                'order_id': [order_id],
                'purchase_date': [pd.Timestamp.now()]
            })
            
            try:
                existing_df = pd.read_csv(self.holdings_file)
                updated_df = pd.concat([existing_df, new_holding], ignore_index=True)
            except FileNotFoundError:
                updated_df = new_holding
            
            updated_df.to_csv(self.holdings_file, index=False)
            
        except Exception as e:
            print(f"菫晄怏驫俶氛霑ｽ蜉繧ｨ繝ｩ繝ｼ: {e}")
    
    def execute_additional_investment(self, amount):
        """霑ｽ蜉謚戊ｳ・ｒ螳溯｡鯉ｼ医Μ繝舌Λ繝ｳ繧ｹ譎ゑｼ・""
        try:
            self.discord.info(f"鬮倬・蠖捺ｪ霑ｽ蜉謚戊ｳ・ｒ髢句ｧ・ {amount}蜀・)
            
            # 雉ｼ蜈･蛟呵｣懊°繧画怙驕ｩ縺ｪ驫俶氛繧帝∈螳・            try:
                candidates = pd.read_csv(self.candidates_file)
            except FileNotFoundError:
                self.discord.warning("雉ｼ蜈･蛟呵｣懊ヵ繧｡繧､繝ｫ縺瑚ｦ九▽縺九ｊ縺ｾ縺帙ｓ")
                return
            
            if candidates.empty:
                self.discord.warning("雉ｼ蜈･蛟呵｣懊′縺ゅｊ縺ｾ縺帙ｓ")
                return
            
            # 譛繧る・蠖灘茜蝗槭ｊ縺碁ｫ倥＞驫俶氛繧帝∈螳・            best_candidate = candidates.loc[candidates['dividend_yield'].idxmax()]
            
            # 雉ｼ蜈･螳溯｡・            self.execute_purchase(best_candidate)
            
        except Exception as e:
            self.discord.error(f"霑ｽ蜉謚戊ｳ・お繝ｩ繝ｼ: {str(e)}")
