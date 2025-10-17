import pandas as pd
import numpy as np
import yfinance as yf
from src.shared_modules.config_loader import ConfigLoader
from src.shared_modules.discord_logger import DiscordLogger
from src.shared_modules.ib_connector import IBConnector

class SatelliteRangeBot:
    def __init__(self, config, discord, ib_connector):
        self.config = config
        self.discord = discord
        self.ib_connector = ib_connector
        self.targets_file = "range_trade_target.csv"
        self.holdings_file = "range_holdings.csv"
        self.holdings = {}
    
    def run_screening(self):
        """レンジ相場のスクリーニングを実衁E""
        try:
            self.discord.info("レンジ相場スクリーニングを開姁E)
            
            # 日絁E25構�E銘柄のスクリーニング
            targets = self.screen_range_stocks()
            
            # 結果をCSVに保孁E            targets.to_csv(self.targets_file, index=False)
            
            self.discord.success(f"レンジ相場スクリーニング完亁E {len(targets)}銘柄を対象として保孁E)
            
        except Exception as e:
            self.discord.error(f"レンジ相場スクリーニングエラー: {str(e)}")
    
    def screen_range_stocks(self):
        """レンジ相場のスクリーニング条件を適用"""
        try:
            # 日絁E25構�E銘柄リスト（仮のチE�Eタ�E�E            nikkei225_symbols = self.get_nikkei225_symbols()
            
            targets = []
            
            for symbol in nikkei225_symbols[:20]:  # チE��ト用に20銘柄のみ
                try:
                    # 過去6ヶ月�E価格チE�Eタを取征E                    price_data = self.get_price_data(symbol, period="6mo")
                    
                    if self.check_range_criteria(price_data):
                        targets.append({
                            'symbol': symbol,
                            'high_6m': price_data['High'].max(),
                            'low_6m': price_data['Low'].min(),
                            'range_ratio': self.calculate_range_ratio(price_data)
                        })
                        
                except Exception as e:
                    print(f"銘柄 {symbol} のチE�Eタ取得エラー: {e}")
                    continue
            
            return pd.DataFrame(targets)
            
        except Exception as e:
            self.discord.error(f"スクリーニング処琁E��ラー: {str(e)}")
            return pd.DataFrame()
    
    def get_nikkei225_symbols(self):
        """日絁E25構�E銘柄を取征E""
        # 実裁E�E後で詳細化（外部APIまた�Eスクレイピング�E�E        return ["7203", "6758", "9984", "6861", "9432", "7201", "6752", "8035", "8306", "4503"]  # 仮のチE�Eタ
    
    def get_price_data(self, symbol, period="6mo"):
        """価格チE�Eタを取征E""
        try:
            ticker = yf.Ticker(f"{symbol}.T")
            hist = ticker.history(period=period)
            return hist
        except Exception as e:
            print(f"価格チE�Eタ取得エラー {symbol}: {e}")
            return pd.DataFrame()
    
    def check_range_criteria(self, price_data):
        """レンジ相場の条件をチェチE��"""
        try:
            if price_data.empty:
                return False
            
            # (過去6ヶ月�E最高値 - 最安値) / 最安値 <= 0.25
            high_6m = price_data['High'].max()
            low_6m = price_data['Low'].min()
            range_ratio = (high_6m - low_6m) / low_6m
            
            return range_ratio <= 0.25
            
        except Exception as e:
            print(f"レンジ条件チェチE��エラー: {e}")
            return False
    
    def calculate_range_ratio(self, price_data):
        """レンジ比率を計箁E""
        try:
            high_6m = price_data['High'].max()
            low_6m = price_data['Low'].min()
            return (high_6m - low_6m) / low_6m
        except Exception as e:
            print(f"レンジ比率計算エラー: {e}")
            return 0
    
    def run_range_trading(self):
        """レンジ取引を実衁E""
        try:
            # 取引対象銘柄の監要E            try:
                targets = pd.read_csv(self.targets_file)
            except FileNotFoundError:
                self.discord.warning("取引対象ファイルが見つかりません")
                return
            
            if targets.empty:
                self.discord.warning("取引対象がありません")
                return
            
            for _, target in targets.iterrows():
                self.monitor_stock(target)
                
        except Exception as e:
            self.discord.error(f"レンジ取引エラー: {str(e)}")
    
    def monitor_stock(self, target):
        """銘柄を監視して売買判断"""
        try:
            symbol = target['symbol']
            
            # 現在の株価を取征E            current_price = self.get_current_price(symbol)
            if current_price == 0:
                return
            
            # ボリンジャーバンドを計箁E            bb_data = self.calculate_bollinger_bands(symbol)
            if bb_data is None:
                return
            
            upper_band = bb_data['upper']
            lower_band = bb_data['lower']
            middle_band = bb_data['middle']
            
            # 現在の保有状況を確誁E            if symbol in self.holdings:
                # 売却判断
                self.check_sell_conditions(symbol, current_price, bb_data)
            else:
                # 購入判断
                self.check_buy_conditions(symbol, current_price, bb_data)
                
        except Exception as e:
            print(f"銘柄監視エラー {target['symbol']}: {e}")
    
    def check_buy_conditions(self, symbol, current_price, bb_data):
        """購入条件をチェチE��"""
        try:
            lower_band = bb_data['lower']
            
            # 現在の株価 <= ボリンジャーバンド下限 (-2ρE
            if current_price <= lower_band:
                self.execute_buy(symbol, current_price)
                
        except Exception as e:
            print(f"購入条件チェチE��エラー {symbol}: {e}")
    
    def check_sell_conditions(self, symbol, current_price, bb_data):
        """売却条件をチェチE��"""
        try:
            upper_band = bb_data['upper']
            lower_band = bb_data['lower']
            holding = self.holdings[symbol]
            purchase_price = holding['price']
            
            # 利確: 現在の株価 >= ボリンジャーバンド上限 (+2ρE
            if current_price >= upper_band:
                self.execute_sell(symbol, current_price, "利確")
                return
            
            # 損�EめE 現在の株価 <= 購入時�Eボリンジャーバンド下限 * 0.98
            stop_loss_price = lower_band * 0.98
            if current_price <= stop_loss_price:
                self.execute_sell(symbol, current_price, "損�EめE)
                return
            
            # レンジブレイク損�EめE            if current_price <= purchase_price * (1 - self.config.get("range_bot.stop_loss_percentage_on_break")):
                self.execute_sell(symbol, current_price, "レンジブレイク損�EめE)
                
        except Exception as e:
            print(f"売却条件チェチE��エラー {symbol}: {e}")
    
    def execute_buy(self, symbol, price):
        """購入を実衁E""
        try:
            main_account = self.config.get("ib_account.main_account_id")
            
            # 購入数量を決定（仮の値�E�E            quantity = 100  # 100株
            
            self.discord.info(f"レンジ取引購入を開姁E {symbol} {quantity}株 @{price}冁E)
            
            # 契紁E���E
            contract = self.ib_connector.create_stock_contract(symbol)
            
            # 成行買ぁE��斁E            order = self.ib_connector.create_market_order("BUY", quantity)
            
            # 注斁E��衁E            order_id = self.ib_connector.place_order(contract, order)
            
            # 取引通知
            self.discord.trade_notification("BUY", symbol, quantity, price, order_id)
            
            # 保有惁E��を記録
            self.holdings[symbol] = {
                'price': price,
                'quantity': quantity,
                'order_id': order_id,
                'purchase_time': pd.Timestamp.now()
            }
            
            self.discord.success(f"レンジ取引購入完亁E {symbol} {quantity}株 @{price}冁E(注文ID: {order_id})")
            
        except Exception as e:
            self.discord.error(f"レンジ取引購入エラー: {str(e)}")
    
    def execute_sell(self, symbol, price, reason):
        """売却を実衁E""
        try:
            if symbol not in self.holdings:
                return
            
            holding = self.holdings[symbol]
            quantity = holding['quantity']
            
            self.discord.info(f"レンジ取引売却を開姁E {symbol} {quantity}株 @{price}冁E({reason})")
            
            # 契紁E���E
            contract = self.ib_connector.create_stock_contract(symbol)
            
            # 成行売り注斁E            order = self.ib_connector.create_market_order("SELL", quantity)
            
            # 注斁E��衁E            order_id = self.ib_connector.place_order(contract, order)
            
            # 取引通知
            self.discord.trade_notification("SELL", symbol, quantity, price, order_id)
            
            # 保有惁E��を削除
            del self.holdings[symbol]
            
            # 損益計箁E            profit_loss = (price - holding['price']) * quantity
            profit_loss_text = f"損益: {profit_loss:+,.0f}冁E
            
            self.discord.success(f"レンジ取引売却完亁E {symbol} {quantity}株 @{price}冁E({reason}) - {profit_loss_text} (注文ID: {order_id})")
            
        except Exception as e:
            self.discord.error(f"レンジ取引売却エラー: {str(e)}")
    
    def get_current_price(self, symbol):
        """現在の株価を取征E""
        try:
            ticker = yf.Ticker(f"{symbol}.T")
            hist = ticker.history(period="1d")
            return hist['Close'].iloc[-1]
        except Exception as e:
            print(f"株価取得エラー {symbol}: {e}")
            return 0
    
    def calculate_bollinger_bands(self, symbol):
        """ボリンジャーバンドを計箁E""
        try:
            period = self.config.get("range_bot.bollinger_period")
            std_dev = self.config.get("range_bot.bollinger_std_dev")
            
            ticker = yf.Ticker(f"{symbol}.T")
            hist = ticker.history(period=f"{period+10}d")
            
            if len(hist) < period:
                return None
            
            # 移動平坁E            middle_band = hist['Close'].rolling(window=period).mean().iloc[-1]
            
            # 標準偏差
            std = hist['Close'].rolling(window=period).std().iloc[-1]
            
            # ボリンジャーバンチE            upper_band = middle_band + (std * std_dev)
            lower_band = middle_band - (std * std_dev)
            
            return {
                'upper': upper_band,
                'middle': middle_band,
                'lower': lower_band
            }
            
        except Exception as e:
            print(f"ボリンジャーバンド計算エラー {symbol}: {e}")
            return None
    
    def execute_additional_investment(self, amount):
        """追加投賁E��実行（リバランス時！E""
        try:
            self.discord.info(f"レンジ相場追加投賁E��開姁E {amount}冁E)
            
            # 取引対象から最適な銘柄を選宁E            try:
                targets = pd.read_csv(self.targets_file)
            except FileNotFoundError:
                self.discord.warning("取引対象ファイルが見つかりません")
                return
            
            if targets.empty:
                self.discord.warning("取引対象がありません")
                return
            
            # 最もレンジ比率が小さぁE��安定した）銘柁E��選宁E            best_target = targets.loc[targets['range_ratio'].idxmin()]
            
            # 購入実衁E            current_price = self.get_current_price(best_target['symbol'])
            if current_price > 0:
                self.execute_buy(best_target['symbol'], current_price)
            
        except Exception as e:
            self.discord.error(f"追加投賁E��ラー: {str(e)}")
