import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
from src.shared_modules.config_loader import ConfigLoader
from src.shared_modules.discord_logger import DiscordLogger
from src.shared_modules.ib_connector import IBConnector
from src.shared_modules.detailed_logger import get_detailed_logger
from datetime import datetime
import time

class SatelliteDividendBot:
    def __init__(self, config, discord, ib_connector):
        self.config = config
        self.discord = discord
        self.ib_connector = ib_connector
        self.detailed_logger = get_detailed_logger()
        
        # Bot状態
        self.is_running = False
        self.last_execution = None
        self.execution_count = 0
        self.error_count = 0
        
        # 高配当株リスト
        self.dividend_stocks = []
        self.current_holdings = []
        
        self.detailed_logger.log_event("INFO", "SATELLITE_DIVIDEND_BOT", "Bot initialized")
        
        # ファイル設定
        self.candidates_file = "purchase_candidate.csv"
        self.holdings_file = "dividend_holdings.csv"
    
    def run_screening(self):
        """高配当株のスクリーニングを実行"""
        try:
            self.discord.info("高配当株スクリーニングを開始")
            
            # TOPIX100構成銘柄のスクリーニング
            candidates = self.screen_dividend_stocks()
            
            # 結果をCSVに保存
            candidates.to_csv(self.candidates_file, index=False)
            
            self.discord.success(f"スクリーニング完了: {len(candidates)}銘柄を候補として保存")
            
        except Exception as e:
            self.discord.error(f"スクリーニングエラー: {str(e)}")
    
    def screen_dividend_stocks(self):
        """高配当株のスクリーニング条件を適用"""
        try:
            # TOPIX100構成銘柄リスト（仮のデータ）
            topix100_symbols = self.get_topix100_symbols()
            
            candidates = []
            
            for symbol in topix100_symbols[:10]:  # テスト用に10銘柄のみ
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
                    print(f"銘柄 {symbol} のデータ取得エラー: {e}")
                    continue
            
            return pd.DataFrame(candidates)
            
        except Exception as e:
            self.discord.error(f"スクリーニング処理エラー: {str(e)}")
            return pd.DataFrame()
    
    def get_topix100_symbols(self):
        """TOPIX100構成銘柄を取得"""
        # 実装は後で詳細化（外部APIまたはスクレイピング）
        return ["7203", "6758", "9984", "6861", "9432"]  # 仮のデータ
    
    def get_stock_fundamentals(self, symbol):
        """銘柄の財務データを取得"""
        try:
            # yfinanceを使用してデータを取得
            ticker = yf.Ticker(f"{symbol}.T")
            info = ticker.info
            
            return {
                'dividend_yield': info.get('dividendYield', 0) * 100,  # パーセント
                'per': info.get('trailingPE', 0),
                'equity_ratio': 50.0,  # 仮の値（実装は後で詳細化）
                'no_dividend_cut': True  # 仮の値（実装は後で詳細化）
            }
            
        except Exception as e:
            print(f"財務データ取得エラー {symbol}: {e}")
            return {}
    
    def check_dividend_criteria(self, stock_data):
        """高配当株の条件をチェック"""
        try:
            # 配当利回り >= 3.5%
            if stock_data.get('dividend_yield', 0) < 3.5:
                return False
            
            # 自己資本比率 >= 40.0%
            if stock_data.get('equity_ratio', 0) < 40.0:
                return False
            
            # PER < 25
            if stock_data.get('per', 0) >= 25:
                return False
            
            # 過去10年間の減配なし
            if not stock_data.get('no_dividend_cut', False):
                return False
            
            return True
            
        except Exception as e:
            print(f"条件チェックエラー: {e}")
            return False
    
    def run_purchase_decision(self):
        """高配当株の購入判断を実行"""
        try:
            self.discord.info("高配当株購入判断を開始")
            
            # 現在の保有銘柄数チェック
            current_holdings = self.get_current_holdings()
            max_holdings = self.config.get("dividend_bot.max_holding_stocks")
            
            if len(current_holdings) >= max_holdings:
                self.discord.info("保有銘柄数が上限に達しているため、購入をスキップ")
                return
            
            # 購入候補から選定
            try:
                candidates = pd.read_csv(self.candidates_file)
            except FileNotFoundError:
                self.discord.warning("購入候補ファイルが見つかりません")
                return
            
            if candidates.empty:
                self.discord.warning("購入候補がありません")
                return
            
            # 購入条件チェック
            for _, candidate in candidates.iterrows():
                if self.check_purchase_condition(candidate):
                    self.execute_purchase(candidate)
                    break
            
        except Exception as e:
            self.discord.error(f"購入判断エラー: {str(e)}")
    
    def check_purchase_condition(self, candidate):
        """購入条件をチェック"""
        try:
            symbol = candidate['symbol']
            
            # 現在の株価 < 25日移動平均線
            current_price = self.get_current_price(symbol)
            ma25 = self.get_moving_average(symbol, 25)
            
            if current_price < ma25:
                return True
            
            return False
            
        except Exception as e:
            print(f"購入条件チェックエラー: {e}")
            return False
    
    def execute_purchase(self, candidate):
        """購入を実行"""
        try:
            symbol = candidate['symbol']
            nisa_account = self.config.get("ib_account.nisa_account_id")
            
            # 購入金額を決定（仮の値）
            purchase_amount = 50000  # 5万円
            
            self.discord.info(f"高配当株購入を開始: {symbol} {purchase_amount}円")
            
            # 契約作成
            contract = self.ib_connector.create_stock_contract(symbol)
            
            # 成行買い注文
            order = self.ib_connector.create_market_order("BUY", purchase_amount)
            
            # 注文実行
            order_id = self.ib_connector.place_order(contract, order)
            
            # 取引通知
            self.discord.trade_notification("BUY", symbol, purchase_amount, order_id=order_id)
            
            # 保有銘柄リストに追加
            self.add_to_holdings(symbol, purchase_amount, order_id)
            
            self.discord.success(f"高配当株購入完了: {symbol} {purchase_amount}円 (注文ID: {order_id})")
            
        except Exception as e:
            self.discord.error(f"購入実行エラー: {str(e)}")
    
    def get_current_price(self, symbol):
        """現在の株価を取得"""
        try:
            ticker = yf.Ticker(f"{symbol}.T")
            hist = ticker.history(period="1d")
            return hist['Close'].iloc[-1]
        except Exception as e:
            print(f"株価取得エラー {symbol}: {e}")
            return 0
    
    def get_moving_average(self, symbol, period):
        """移動平均を取得"""
        try:
            ticker = yf.Ticker(f"{symbol}.T")
            hist = ticker.history(period=f"{period+10}d")
            return hist['Close'].rolling(window=period).mean().iloc[-1]
        except Exception as e:
            print(f"移動平均取得エラー {symbol}: {e}")
            return 0
    
    def get_current_holdings(self):
        """現在の保有銘柄を取得"""
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
        """追加投資を実行（リバランス時）"""
        try:
            self.discord.info(f"高配当株追加投資を開始: {amount}円")
            
            # 購入候補から最適な銘柄を選定
            try:
                candidates = pd.read_csv(self.candidates_file)
            except FileNotFoundError:
                self.discord.warning("購入候補ファイルが見つかりません")
                return
            
            if candidates.empty:
                self.discord.warning("購入候補がありません")
                return
            
            # 最も配当利回りが高い銘柄を選定
            best_candidate = candidates.loc[candidates['dividend_yield'].idxmax()]
            
            # 購入実行
            self.execute_purchase(best_candidate)
            
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
            self.detailed_logger.log_error("SATELLITE_DIVIDEND_BOT", e, "Health check")
            return False
    
    def get_status(self) -> dict:
        """Botの状態を取得"""
        return {
            "is_running": self.is_running,
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "execution_count": self.execution_count,
            "error_count": self.error_count,
            "is_healthy": self.is_healthy(),
            "current_holdings_count": len(self.current_holdings)
        }
