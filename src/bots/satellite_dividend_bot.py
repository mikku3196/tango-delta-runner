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
        """高�E当株のスクリーニングを実衁E""
        try:
            self.discord.info("高�E当株スクリーニングを開姁E)
            
            # TOPIX100構�E銘柄のスクリーニング
            candidates = self.screen_dividend_stocks()
            
            # 結果をCSVに保孁E            candidates.to_csv(self.candidates_file, index=False)
            
            self.discord.success(f"スクリーニング完亁E {len(candidates)}銘柄を候補として保孁E)
            
        except Exception as e:
            self.discord.error(f"スクリーニングエラー: {str(e)}")
    
    def screen_dividend_stocks(self):
        """高�E当株のスクリーニング条件を適用"""
        try:
            # TOPIX100構�E銘柄リスト（仮のチE�Eタ�E�E            topix100_symbols = self.get_topix100_symbols()
            
            candidates = []
            
            for symbol in topix100_symbols[:10]:  # チE��ト用に10銘柄のみ
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
                    print(f"銘柄 {symbol} のチE�Eタ取得エラー: {e}")
                    continue
            
            return pd.DataFrame(candidates)
            
        except Exception as e:
            self.discord.error(f"スクリーニング処琁E��ラー: {str(e)}")
            return pd.DataFrame()
    
    def get_topix100_symbols(self):
        """TOPIX100構�E銘柄を取征E""
        # 実裁E�E後で詳細化（外部APIまた�Eスクレイピング�E�E        return ["7203", "6758", "9984", "6861", "9432"]  # 仮のチE�Eタ
    
    def get_stock_fundamentals(self, symbol):
        """銘柄の財務データを取征E""
        try:
            # yfinanceを使用してチE�Eタを取征E            ticker = yf.Ticker(f"{symbol}.T")
            info = ticker.info
            
            return {
                'dividend_yield': info.get('dividendYield', 0) * 100,  # パ�EセンチE                'per': info.get('trailingPE', 0),
                'equity_ratio': 50.0,  # 仮の値�E�実裁E�E後で詳細化！E                'no_dividend_cut': True  # 仮の値�E�実裁E�E後で詳細化！E            }
            
        except Exception as e:
            print(f"財務データ取得エラー {symbol}: {e}")
            return {}
    
    def check_dividend_criteria(self, stock_data):
        """高�E当株の条件をチェチE��"""
        try:
            # 配当利回り >= 3.5%
            if stock_data.get('dividend_yield', 0) < 3.5:
                return False
            
            # 自己賁E��比率 >= 40.0%
            if stock_data.get('equity_ratio', 0) < 40.0:
                return False
            
            # PER < 25
            if stock_data.get('per', 0) >= 25:
                return False
            
            # 過去10年間�E減�EなぁE            if not stock_data.get('no_dividend_cut', False):
                return False
            
            return True
            
        except Exception as e:
            print(f"条件チェチE��エラー: {e}")
            return False
    
    def run_purchase_decision(self):
        """高�E当株の購入判断を実衁E""
        try:
            self.discord.info("高�E当株購入判断を開姁E)
            
            # 現在の保有銘柄数チェチE��
            current_holdings = self.get_current_holdings()
            max_holdings = self.config.get("dividend_bot.max_holding_stocks")
            
            if len(current_holdings) >= max_holdings:
                self.discord.info("保有銘柄数が上限に達してぁE��ため、購入をスキチE�E")
                return
            
            # 購入候補から選宁E            try:
                candidates = pd.read_csv(self.candidates_file)
            except FileNotFoundError:
                self.discord.warning("購入候補ファイルが見つかりません")
                return
            
            if candidates.empty:
                self.discord.warning("購入候補がありません")
                return
            
            # 購入条件チェチE��
            for _, candidate in candidates.iterrows():
                if self.check_purchase_condition(candidate):
                    self.execute_purchase(candidate)
                    break
            
        except Exception as e:
            self.discord.error(f"購入判断エラー: {str(e)}")
    
    def check_purchase_condition(self, candidate):
        """購入条件をチェチE��"""
        try:
            symbol = candidate['symbol']
            
            # 現在の株価 < 25日移動平坁E��E            current_price = self.get_current_price(symbol)
            ma25 = self.get_moving_average(symbol, 25)
            
            if current_price < ma25:
                return True
            
            return False
            
        except Exception as e:
            print(f"購入条件チェチE��エラー: {e}")
            return False
    
    def execute_purchase(self, candidate):
        """購入を実衁E""
        try:
            symbol = candidate['symbol']
            nisa_account = self.config.get("ib_account.nisa_account_id")
            
            # 購入金額を決定（仮の値�E�E            purchase_amount = 50000  # 5丁E�E
            
            self.discord.info(f"高�E当株購入を開姁E {symbol} {purchase_amount}冁E)
            
            # 契紁E���E
            contract = self.ib_connector.create_stock_contract(symbol)
            
            # 成行買ぁE��斁E            order = self.ib_connector.create_market_order("BUY", purchase_amount)
            
            # 注斁E��衁E            order_id = self.ib_connector.place_order(contract, order)
            
            # 取引通知
            self.discord.trade_notification("BUY", symbol, purchase_amount, order_id=order_id)
            
            # 保有銘柄リストに追加
            self.add_to_holdings(symbol, purchase_amount, order_id)
            
            self.discord.success(f"高�E当株購入完亁E {symbol} {purchase_amount}冁E(注文ID: {order_id})")
            
        except Exception as e:
            self.discord.error(f"購入実行エラー: {str(e)}")
    
    def get_current_price(self, symbol):
        """現在の株価を取征E""
        try:
            ticker = yf.Ticker(f"{symbol}.T")
            hist = ticker.history(period="1d")
            return hist['Close'].iloc[-1]
        except Exception as e:
            print(f"株価取得エラー {symbol}: {e}")
            return 0
    
    def get_moving_average(self, symbol, period):
        """移動平坁E��取征E""
        try:
            ticker = yf.Ticker(f"{symbol}.T")
            hist = ticker.history(period=f"{period+10}d")
            return hist['Close'].rolling(window=period).mean().iloc[-1]
        except Exception as e:
            print(f"移動平坁E��得エラー {symbol}: {e}")
            return 0
    
    def get_current_holdings(self):
        """現在の保有銘柄を取征E""
        try:
            df = pd.read_csv(self.holdings_file)
            return df['symbol'].tolist()
        except FileNotFoundError:
            return []
        except Exception as e:
            print(f"保有銘柄取得エラー: {e}")
            return []
    
    def add_to_holdings(self, symbol, amount, order_id):
        """保有銘柄リストに追加"""
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
            print(f"保有銘柄追加エラー: {e}")
    
    def execute_additional_investment(self, amount):
        """追加投賁E��実行（リバランス時！E""
        try:
            self.discord.info(f"高�E当株追加投賁E��開姁E {amount}冁E)
            
            # 購入候補から最適な銘柄を選宁E            try:
                candidates = pd.read_csv(self.candidates_file)
            except FileNotFoundError:
                self.discord.warning("購入候補ファイルが見つかりません")
                return
            
            if candidates.empty:
                self.discord.warning("購入候補がありません")
                return
            
            # 最も�E当利回りが高い銘柄を選宁E            best_candidate = candidates.loc[candidates['dividend_yield'].idxmax()]
            
            # 購入実衁E            self.execute_purchase(best_candidate)
            
        except Exception as e:
            self.discord.error(f"追加投賁E��ラー: {str(e)}")
