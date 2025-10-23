from src.shared_modules.config_loader import ConfigLoader
from src.shared_modules.discord_logger import DiscordLogger
from src.shared_modules.ib_connector import IBConnector
from src.shared_modules.detailed_logger import get_detailed_logger
from datetime import datetime
import time

class CoreIndexBot:
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
        
        self.detailed_logger.log_event("INFO", "CORE_INDEX_BOT", "Bot initialized")
    
    def execute_monthly_investment(self):
        """毎月の積立投資を実行"""
        self.is_running = True
        start_time = datetime.now()
        
        try:
            ticker = self.config.get("index_bot.ticker")
            amount = self.config.get("index_bot.monthly_investment")
            nisa_account = self.config.get("ib_account.nisa_account_id")
            
            self.detailed_logger.log_event("INFO", "CORE_INDEX_BOT", "Monthly investment started", {
                "ticker": ticker,
                "amount": amount,
                "account": nisa_account
            })
            
            self.discord.info(f"インデックス積立を開始: {ticker} {amount}円")
            
            # 契約作成
            contract = self.ib_connector.create_stock_contract(ticker)
            
            # 成行買い注文
            order = self.ib_connector.create_market_order("BUY", amount)
            
            # 注文実行
            order_id = self.ib_connector.place_order(contract, order)
            
            # 取引ログ
            self.detailed_logger.log_trade("BUY", ticker, amount, 0, nisa_account, {
                "order_id": order_id,
                "execution_type": "monthly_investment"
            })
            
            # 取引通知
            self.discord.trade_notification("BUY", ticker, amount, order_id=order_id)
            
            # 実行統計を更新
            self.execution_count += 1
            self.last_execution = start_time
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            self.detailed_logger.log_event("INFO", "CORE_INDEX_BOT", "Monthly investment completed", {
                "order_id": order_id,
                "execution_time": execution_time,
                "execution_count": self.execution_count
            })
            
            self.discord.success(f"インデックス積立完了: {ticker} {amount}円 (注文ID: {order_id})")
            
        except Exception as e:
            self.error_count += 1
            self.detailed_logger.log_error("CORE_INDEX_BOT", e, "Monthly investment execution")
            self.discord.error(f"インデックス積立エラー: {str(e)}")
        finally:
            self.is_running = False
    
    def execute_additional_investment(self, amount):
        """追加投資を実行（リバランス時）"""
        try:
            ticker = self.config.get("index_bot.ticker")
            nisa_account = self.config.get("ib_account.nisa_account_id")
            
            self.discord.info(f"インデックス追加投資を開始: {ticker} {amount}円")
            
            # 契約作成
            contract = self.ib_connector.create_stock_contract(ticker)
            
            # 成行買い注文
            order = self.ib_connector.create_market_order("BUY", amount)
            
            # 注文実行
            order_id = self.ib_connector.place_order(contract, order)
            
            # 取引通知
            self.discord.trade_notification("BUY", ticker, amount, order_id=order_id)
            
            self.discord.success(f"インデックス追加投資完了: {ticker} {amount}円 (注文ID: {order_id})")
            
        except Exception as e:
            self.discord.error(f"インデックス追加投資エラー: {str(e)}")
    
    def get_current_holdings(self):
        """現在の保有状況を取得"""
        try:
            # 実装は後で詳細化
            # IB APIを使用して保有銘柄を取得
            return []
        except Exception as e:
            self.discord.error(f"保有状況取得エラー: {str(e)}")
            return []
    
    def get_position_value(self):
        """現在のポジション価値を取得"""
        try:
            # 実装は後で詳細化
            # IB APIを使用してポジション価値を取得
            return 0
        except Exception as e:
            self.discord.error(f"ポジション価値取得エラー: {str(e)}")
            return 0
    
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
            self.detailed_logger.log_error("CORE_INDEX_BOT", e, "Health check")
            return False
    
    def get_status(self) -> dict:
        """Botの状態を取得"""
        return {
            "is_running": self.is_running,
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "execution_count": self.execution_count,
            "error_count": self.error_count,
            "is_healthy": self.is_healthy()
        }
