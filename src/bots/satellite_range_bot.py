import pandas as pd
import numpy as np
import yfinance as yf
from src.shared_modules.config_loader import ConfigLoader
from src.shared_modules.discord_logger import DiscordLogger
from src.shared_modules.ib_connector import IBConnector
from src.shared_modules.detailed_logger import get_detailed_logger
from datetime import datetime
import time

class SatelliteRangeBot:
    def __init__(self, stop_loss_percentage=0.05, trailing_stop_percentage=0.08, bollinger_period=20, bollinger_std_dev=2.0):
        """
        Botを初期化し、戦略パラメータと内部状態を設定します。
        """
        self.name = "SatelliteRangeBot"

        # --- 戦略パラメータの設定 ---
        self.stop_loss_percentage = stop_loss_percentage
        self.trailing_stop_percentage = trailing_stop_percentage
        self.bollinger_period = bollinger_period
        self.bollinger_std_dev = bollinger_std_dev

        # --- 内部状態の初期化 (前回これが欠落していました) ---
        self.position = 'none'      # 現在のポジション ('none' または 'long')
        self.entry_price = 0.0      # ポジションを持った時の価格
        self.last_signal = 'hold'   # 最後に出したシグナル
        
        # 取引履歴
        self.trade_history = []
        self.current_positions = []
        
        # ログとファイル設定
        self.detailed_logger = get_detailed_logger()
        self.targets_file = "range_trade_target.csv"
        self.holdings_file = "range_holdings.csv"
        self.holdings = {}
    
    def run_screening(self):
        """レンジ相場のスクリーニングを実行"""
        try:
            self.discord.info("レンジ相場スクリーニングを開始")
            
            # 日経225構成銘柄のスクリーニング
            targets = self.screen_range_stocks()
            
            # 結果をCSVに保存
            targets.to_csv(self.targets_file, index=False)
            
            self.discord.success(f"レンジ相場スクリーニング完了: {len(targets)}銘柄を対象として保存")
            
        except Exception as e:
            self.discord.error(f"レンジ相場スクリーニングエラー: {str(e)}")
    
    def screen_range_stocks(self):
        """レンジ相場のスクリーニング条件を適用"""
        try:
            # 日経225構成銘柄リスト（仮のデータ）
            nikkei225_symbols = self.get_nikkei225_symbols()
            
            targets = []
            
            for symbol in nikkei225_symbols[:20]:  # テスト用に20銘柄のみ
                try:
                    # 過去6ヶ月の価格データを取得
                    price_data = self.get_price_data(symbol, period="6mo")
                    
                    if self.check_range_criteria(price_data):
                        targets.append({
                            'symbol': symbol,
                            'high_6m': price_data['High'].max(),
                            'low_6m': price_data['Low'].min(),
                            'range_ratio': self.calculate_range_ratio(price_data)
                        })
                        
                except Exception as e:
                    print(f"銘柄 {symbol} のデータ取得エラー: {e}")
                    continue
            
            return pd.DataFrame(targets)
            
        except Exception as e:
            self.discord.error(f"スクリーニング処理エラー: {str(e)}")
            return pd.DataFrame()
    
    def get_nikkei225_symbols(self):
        """日経225構成銘柄を取得"""
        # 実装は後で詳細化（外部APIまたはスクレイピング）
        return ["7203", "6758", "9984", "6861", "9432", "7201", "6752", "8035", "8306", "4503"]  # 仮のデータ
    
    def get_price_data(self, symbol, period="6mo"):
        """価格データを取得"""
        try:
            ticker = yf.Ticker(f"{symbol}.T")
            hist = ticker.history(period=period)
            return hist
        except Exception as e:
            print(f"価格データ取得エラー {symbol}: {e}")
            return pd.DataFrame()
    
    def check_range_criteria(self, price_data):
        """レンジ相場の条件をチェック"""
        try:
            if price_data.empty:
                return False
            
            # (過去6ヶ月の最高値 - 最安値) / 最安値 <= 0.25
            high_6m = price_data['High'].max()
            low_6m = price_data['Low'].min()
            range_ratio = (high_6m - low_6m) / low_6m
            
            return range_ratio <= 0.25
            
        except Exception as e:
            print(f"レンジ条件チェックエラー: {e}")
            return False
    
    def calculate_range_ratio(self, price_data):
        """レンジ比率を計算"""
        try:
            high_6m = price_data['High'].max()
            low_6m = price_data['Low'].min()
            return (high_6m - low_6m) / low_6m
        except Exception as e:
            print(f"レンジ比率計算エラー: {e}")
            return 0
    
    def run_range_trading(self):
        """レンジ取引を実行"""
        try:
            # 取引対象銘柄の監視
            try:
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
            
            # 現在の株価を取得
            current_price = self.get_current_price(symbol)
            if current_price == 0:
                return
            
            # ボリンジャーバンドを計算
            bb_data = self.calculate_bollinger_bands(symbol)
            if bb_data is None:
                return
            
            upper_band = bb_data['upper']
            lower_band = bb_data['lower']
            middle_band = bb_data['middle']
            
            # 現在の保有状況を確認
            if symbol in self.holdings:
                # 売却判断
                self.check_sell_conditions(symbol, current_price, bb_data)
            else:
                # 購入判断
                self.check_buy_conditions(symbol, current_price, bb_data)
                
        except Exception as e:
            print(f"銘柄監視エラー {target['symbol']}: {e}")
    
    def check_buy_conditions(self, symbol, current_price, bb_data):
        """購入条件をチェック"""
        try:
            lower_band = bb_data['lower']
            
            # 現在の株価 <= ボリンジャーバンド下限 (-2σ)
            if current_price <= lower_band:
                self.execute_buy(symbol, current_price)
                
        except Exception as e:
            print(f"購入条件チェックエラー {symbol}: {e}")
    
    def check_sell_conditions(self, symbol, current_price, bb_data):
        """売却条件をチェック"""
        try:
            upper_band = bb_data['upper']
            lower_band = bb_data['lower']
            holding = self.holdings[symbol]
            purchase_price = holding['price']
            
            # 利確: 現在の株価 >= ボリンジャーバンド上限 (+2σ)
            if current_price >= upper_band:
                self.execute_sell(symbol, current_price, "利確")
                return
            
            # 損切り: 現在の株価 <= 購入時のボリンジャーバンド下限 * 0.98
            stop_loss_price = lower_band * 0.98
            if current_price <= stop_loss_price:
                self.execute_sell(symbol, current_price, "損切り")
                return
            
            # レンジブレイク損切り
            if current_price <= purchase_price * (1 - self.config.get("range_bot.stop_loss_percentage_on_break")):
                self.execute_sell(symbol, current_price, "レンジブレイク損切り")
                
        except Exception as e:
            print(f"売却条件チェックエラー {symbol}: {e}")
    
    def execute_buy(self, symbol, price):
        """購入を実行"""
        try:
            main_account = self.config.get("ib_account.main_account_id")
            
            # 購入数量を決定（仮の値）
            quantity = 100  # 100株
            
            self.discord.info(f"レンジ取引購入を開始: {symbol} {quantity}株 @{price}円")
            
            # 契約作成
            contract = self.ib_connector.create_stock_contract(symbol)
            
            # 成行買い注文
            order = self.ib_connector.create_market_order("BUY", quantity)
            
            # 注文実行
            order_id = self.ib_connector.place_order(contract, order)
            
            # 取引通知
            self.discord.trade_notification("BUY", symbol, quantity, price, order_id)
            
            # 保有情報を記録
            self.holdings[symbol] = {
                'price': price,
                'quantity': quantity,
                'order_id': order_id,
                'purchase_time': pd.Timestamp.now()
            }
            
            self.discord.success(f"レンジ取引購入完了: {symbol} {quantity}株 @{price}円 (注文ID: {order_id})")
            
        except Exception as e:
            self.discord.error(f"レンジ取引購入エラー: {str(e)}")
    
    def execute_sell(self, symbol, price, reason):
        """売却を実行"""
        try:
            if symbol not in self.holdings:
                return
            
            holding = self.holdings[symbol]
            quantity = holding['quantity']
            
            self.discord.info(f"レンジ取引売却を開始: {symbol} {quantity}株 @{price}円 ({reason})")
            
            # 契約作成
            contract = self.ib_connector.create_stock_contract(symbol)
            
            # 成行売り注文
            order = self.ib_connector.create_market_order("SELL", quantity)
            
            # 注文実行
            order_id = self.ib_connector.place_order(contract, order)
            
            # 取引通知
            self.discord.trade_notification("SELL", symbol, quantity, price, order_id)
            
            # 保有情報を削除
            del self.holdings[symbol]
            
            # 損益計算
            profit_loss = (price - holding['price']) * quantity
            profit_loss_text = f"損益: {profit_loss:+,.0f}円"
            
            self.discord.success(f"レンジ取引売却完了: {symbol} {quantity}株 @{price}円 ({reason}) - {profit_loss_text} (注文ID: {order_id})")
            
        except Exception as e:
            self.discord.error(f"レンジ取引売却エラー: {str(e)}")
    
    def get_current_price(self, symbol):
        """現在の株価を取得"""
        try:
            ticker = yf.Ticker(f"{symbol}.T")
            hist = ticker.history(period="1d")
            return hist['Close'].iloc[-1]
        except Exception as e:
            print(f"株価取得エラー {symbol}: {e}")
            return 0
    
    def calculate_bollinger_bands(self, symbol):
        """ボリンジャーバンドを計算"""
        try:
            period = self.config.get("range_bot.bollinger_period")
            std_dev = self.config.get("range_bot.bollinger_std_dev")
            
            ticker = yf.Ticker(f"{symbol}.T")
            hist = ticker.history(period=f"{period+10}d")
            
            if len(hist) < period:
                return None
            
            # 移動平均
            middle_band = hist['Close'].rolling(window=period).mean().iloc[-1]
            
            # 標準偏差
            std = hist['Close'].rolling(window=period).std().iloc[-1]
            
            # ボリンジャーバンド
            upper_band = middle_band + (std * std_dev)
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
        """追加投資を実行（リバランス時）"""
        try:
            self.discord.info(f"レンジ相場追加投資を開始: {amount}円")
            
            # 取引対象から最適な銘柄を選定
            try:
                targets = pd.read_csv(self.targets_file)
            except FileNotFoundError:
                self.discord.warning("取引対象ファイルが見つかりません")
                return
            
            if targets.empty:
                self.discord.warning("取引対象がありません")
                return
            
            # 最もレンジ比率が小さい（安定した）銘柄を選定
            best_target = targets.loc[targets['range_ratio'].idxmin()]
            
            # 購入実行
            current_price = self.get_current_price(best_target['symbol'])
            if current_price > 0:
                self.execute_buy(best_target['symbol'], current_price)
            
        except Exception as e:
            self.discord.error(f"追加投資エラー: {str(e)}")
    
    def is_healthy(self) -> bool:
        """Botのヘルスチェック"""
        try:
            # 基本的なヘルスチェック
            if self.error_count > 10:  # エラーが10回以上
                return False
            
            # 最後の実行から1時間以上経過している場合は問題なし
            if self.last_execution:
                time_since_last = (datetime.now() - self.last_execution).total_seconds()
                if time_since_last > 3600:  # 1時間
                    return True
            
            # 実行中でない場合は健康
            return not self.is_running
            
        except Exception as e:
            self.detailed_logger.log_error("SATELLITE_RANGE_BOT", e, "Health check")
            return False
    
    def get_status(self) -> dict:
        """Botの状態を取得"""
        return {
            "is_running": self.is_running,
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "execution_count": self.execution_count,
            "error_count": self.error_count,
            "is_healthy": self.is_healthy(),
            "current_positions_count": len(self.current_positions),
            "trade_history_count": len(self.trade_history)
        }
    
    def prepare_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        株価データにボリンジャーバンドと200日移動平均線を追加する
        
        Args:
            data: 株価データ（pandas DataFrame）
            
        Returns:
            pd.DataFrame: ボリンジャーバンドと200日移動平均線が追加されたデータ
        """
        try:
            # データのコピーを作成
            prepared_data = data.copy()
            
            # ボリンジャーバンドの計算
            # 移動平均（中心線）
            prepared_data['BB_Middle'] = prepared_data['Close'].rolling(window=self.bollinger_period).mean()
            
            # 標準偏差
            prepared_data['BB_Std'] = prepared_data['Close'].rolling(window=self.bollinger_period).std()
            
            # 上限バンド
            prepared_data['BB_Upper'] = prepared_data['BB_Middle'] + (prepared_data['BB_Std'] * self.bollinger_std)
            
            # 下限バンド
            prepared_data['BB_Lower'] = prepared_data['BB_Middle'] - (prepared_data['BB_Std'] * self.bollinger_std)
            
            # 200日単純移動平均線（トレンドフィルター用）
            prepared_data['SMA200'] = prepared_data['Close'].rolling(window=200).mean()
            
            # 欠損値を前方埋め
            prepared_data = prepared_data.ffill()
            
            self.detailed_logger.log_event("DEBUG", "SATELLITE_RANGE_BOT", "Data prepared with Bollinger Bands and SMA200", {
                "data_points": len(prepared_data),
                "bollinger_period": self.bollinger_period,
                "bollinger_std": self.bollinger_std,
                "sma200_period": 200
            })
            
            return prepared_data
            
        except Exception as e:
            self.detailed_logger.log_error("SATELLITE_RANGE_BOT", e, "Prepare data")
            return data
    
    def generate_signal(self, data_row):
        """
        1日分のデータ(data_row)を受け取り、売買シグナルを生成する
        
        Args:
            data_row (pd.Series): 1日分の株価データ（Close, BB_Upper, BB_Lower, SMA200などを含む）
            
        Returns:
            str: 'BUY', 'SELL', 'HOLD' のいずれか
        """
        # --- FINAL PROOF ---
        # このメッセージが表示されなければ、古いコードが実行されています。
        # print("--- RUNNING LATEST generate_signal v3.2 ---") 
        # --- END OF FINAL PROOF ---

        try:
            # ボリンジャーバンドやSMA200が計算されているか（データが十分か）をチェック
            if pd.isna(data_row['BB_Upper']) or pd.isna(data_row['SMA200']):
                return 'HOLD'

            # --- ここからが判断ロジック（純粋な逆張り戦略） ---
            
            # 純粋な逆張り・レンジ相場戦略
            # SMA200の上昇トレンドフィルターを削除し、ボリンジャーバンドのシグナルのみに基づいて取引
            
            # 現在の価格とボリンジャーバンドの値を取得
            current_price = data_row['Close']
            bb_lower = data_row['BB_Lower']
            
            # 買いシグナル判定のみに特化
            if self.position == 'none':
                # BUYシグナル: 価格がBB下限を下回る (純粋な逆張り)
                if current_price < bb_lower:
                    self.position = 'long'
                    self.entry_price = current_price
                    self.last_signal = 'buy'
                    return 'BUY'
            
            # ポジションがある場合は何もしない（エンジンに任せる）
            return 'HOLD'

        except KeyError as e:
            # 必要な列（'Close', 'BB_Upper'など）が存在しない場合のエラーハンドリング
            return 'HOLD'
    
    def reset(self):
        """取引が終了した際に、Botの内部状態をリセットする。"""
        self.position = 'none'
        self.entry_price = 0.0
        self.last_signal = 'hold'
    
    def calculate_bollinger_bands_simple(self, data: pd.DataFrame, period: int, std_dev: float) -> dict:
        """
        シンプルなボリンジャーバンド計算（バックテスト用）
        
        Args:
            data: 価格データ
            period: 期間
            std_dev: 標準偏差の倍数
            
        Returns:
            dict: ボリンジャーバンドの値
        """
        try:
            if len(data) < period:
                return None
            
            # 最新の期間分のデータを使用
            recent_data = data['Close'].tail(period)
            
            # 移動平均
            middle_band = recent_data.mean()
            
            # 標準偏差
            std = recent_data.std()
            
            # ボリンジャーバンド
            upper_band = middle_band + (std * std_dev)
            lower_band = middle_band - (std * std_dev)
            
            return {
                'upper': upper_band,
                'middle': middle_band,
                'lower': lower_band
            }
            
        except Exception as e:
            self.detailed_logger.log_error("SATELLITE_RANGE_BOT", e, "Calculate Bollinger Bands")
            return None
