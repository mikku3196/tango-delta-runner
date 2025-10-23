import yaml
import os
import time
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from src.shared_modules.config_loader import ConfigLoader
from src.shared_modules.discord_logger import DiscordLogger
from src.shared_modules.ib_connector import IBConnector
from src.shared_modules.nisa_monitor import NISAMonitor
from src.shared_modules.detailed_logger import get_detailed_logger
from src.shared_modules.watchdog import Watchdog
from src.bots.core_index_bot import CoreIndexBot
from src.bots.satellite_dividend_bot import SatelliteDividendBot
from src.bots.satellite_range_bot import SatelliteRangeBot

class MainController:
    def __init__(self):
        """メインコントローラーの初期化"""
        self.config = ConfigLoader()
        self.discord = DiscordLogger(self.config.get("discord_webhook_url"))
        self.ib_connector = IBConnector()
        self.scheduler = BlockingScheduler()
        self.stop_flag_file = "STOP.flag"
        
        # 詳細ロガーを初期化
        self.detailed_logger = get_detailed_logger()
        
        # NISA監視を初期化
        self.nisa_monitor = NISAMonitor(self.config, self.discord, self.ib_connector)
        
        # Watchdogを初期化
        self.watchdog = Watchdog(self.config, self.discord)
        
        # Botインスタンス
        self.index_bot = CoreIndexBot(self.config, self.discord, self.ib_connector)
        self.dividend_bot = SatelliteDividendBot(self.config, self.discord, self.ib_connector)
        self.range_bot = SatelliteRangeBot(self.config, self.discord, self.ib_connector)
    
    def start(self):
        """システムを起動"""
        try:
            # STOP.flagの存在をチェック
            if self.check_stop_flag():
                self.detailed_logger.log_event("CRITICAL", "MAIN_CONTROLLER", "STOP.flag detected at startup")
                self.discord.error("【CRITICAL】STOP.flagが検出されました。システムを起動しません。")
                print("STOP.flagが存在するため、システムを起動しません。")
                print("emergency_stop.pyを実行してSTOP.flagを削除してください。")
                return False
            
            # IB接続
            ib_config = self.config.get("ib_account")
            if not self.ib_connector.connect_to_ib(
                ib_config["host"], 
                ib_config["port"], 
                ib_config["client_id"]
            ):
                raise Exception("IB接続に失敗しました")
            
            self.detailed_logger.log_event("INFO", "MAIN_CONTROLLER", "System startup initiated")
            self.discord.success("Project Chimera が起動しました")
            
            # Watchdogにプロセスを登録
            self._register_watchdog_processes()
            
            # スケジューラー設定
            self.setup_scheduler()
            
            # Watchdog監視開始
            self.watchdog.start_monitoring()
            
            # メインループ開始
            self.scheduler.start()
            
        except Exception as e:
            self.detailed_logger.log_error("MAIN_CONTROLLER", e, "System startup")
            self.discord.error(f"システム起動エラー: {str(e)}")
            raise
    
    def setup_scheduler(self):
        """スケジューラーにタスクを登録"""
        # インデックスBot: 毎月1日 9:30
        self.scheduler.add_job(
            self.index_bot.execute_monthly_investment,
            CronTrigger(day=1, hour=9, minute=30),
            id="index_monthly",
            name="インデックス積立実行"
        )
        
        # 高配当Bot: 毎週日曜 22:00 (スクリーニング)
        self.scheduler.add_job(
            self.dividend_bot.run_screening,
            CronTrigger(day_of_week=6, hour=22, minute=0),
            id="dividend_screening",
            name="高配当株スクリーニング"
        )
        
        # 高配当Bot: 毎営業日 9:05 (購入判断)
        self.scheduler.add_job(
            self.dividend_bot.run_purchase_decision,
            CronTrigger(day_of_week="mon-fri", hour=9, minute=5),
            id="dividend_purchase",
            name="高配当株購入判断"
        )
        
        # レンジBot: 毎営業日 16:00 (スクリーニング)
        self.scheduler.add_job(
            self.range_bot.run_screening,
            CronTrigger(day_of_week="mon-fri", hour=16, minute=0),
            id="range_screening",
            name="レンジ相場スクリーニング"
        )
        
        # レンジBot: 取引時間中 常時実行
        self.scheduler.add_job(
            self.range_bot.run_range_trading,
            CronTrigger(day_of_week="mon-fri", hour="9-15", minute="*"),
            id="range_trading",
            name="レンジ取引実行"
        )
        
        # ポートフォリオリバランス: 毎月1日 10:00
        self.scheduler.add_job(
            self.rebalance_portfolio,
            CronTrigger(day=1, hour=10, minute=0),
            id="portfolio_rebalance",
            name="ポートフォリオリバランス"
        )
        
        # NISA使用状況レポート: 毎日 18:00
        self.scheduler.add_job(
            self.nisa_monitor.send_usage_report,
            CronTrigger(hour=18, minute=0),
            id="nisa_report",
            name="NISA使用状況レポート"
        )
        
        self.detailed_logger.log_event("INFO", "MAIN_CONTROLLER", "Scheduler configured")
        self.discord.info("スケジューラーが設定されました")
    
    def rebalance_portfolio(self):
        """ポートフォリオリバランスを実行"""
        try:
            self.discord.info("ポートフォリオリバランスを実行中...")
            
            # 現在の総資産評価額を取得
            total_value = self.get_total_portfolio_value()
            
            # 各戦略の現在の評価額を取得
            index_value = self.get_strategy_value("index")
            dividend_value = self.get_strategy_value("dividend")
            range_value = self.get_strategy_value("range")
            
            # 現在の比率を計算
            current_ratios = {
                "index": index_value / total_value if total_value > 0 else 0,
                "dividend": dividend_value / total_value if total_value > 0 else 0,
                "range": range_value / total_value if total_value > 0 else 0
            }
            
            # 目標比率
            target_ratios = self.config.get("portfolio_ratios")
            
            # 最も比率が不足している戦略を特定
            max_deviation = 0
            target_strategy = "index"
            
            for strategy in ["index", "dividend", "range"]:
                deviation = target_ratios[strategy] - current_ratios[strategy]
                if deviation > max_deviation:
                    max_deviation = deviation
                    target_strategy = strategy
            
            # 追加投資資金を特定戦略に割り当て
            monthly_investment = self.config.get("index_bot.monthly_investment")
            
            if target_strategy == "index":
                self.index_bot.execute_additional_investment(monthly_investment)
            elif target_strategy == "dividend":
                self.dividend_bot.execute_additional_investment(monthly_investment)
            elif target_strategy == "range":
                self.range_bot.execute_additional_investment(monthly_investment)
            
            self.discord.success(f"リバランス完了: {target_strategy}戦略に{monthly_investment}円を追加投資")
            
        except Exception as e:
            self.discord.error(f"リバランスエラー: {str(e)}")
    
    def get_total_portfolio_value(self):
        """総ポートフォリオ価値を取得"""
        # 実装は後で詳細化
        return 1000000  # 仮の値
    
    def get_strategy_value(self, strategy):
        """各戦略の評価額を取得"""
        # 実装は後で詳細化
        values = {
            "index": 500000,
            "dividend": 300000,
            "range": 200000
        }
        return values.get(strategy, 0)
    
    def check_stop_flag(self) -> bool:
        """STOP.flagの存在をチェック"""
        return os.path.exists(self.stop_flag_file)
    
    def _register_watchdog_processes(self):
        """Watchdogにプロセスを登録"""
        # インデックスBot
        self.watchdog.register_process(
            "index_bot",
            self.index_bot.execute_monthly_investment,
            health_check_func=lambda: self.index_bot.is_healthy()
        )
        
        # 高配当Bot
        self.watchdog.register_process(
            "dividend_bot",
            self.dividend_bot.run_screening,
            health_check_func=lambda: self.dividend_bot.is_healthy()
        )
        
        # レンジBot
        self.watchdog.register_process(
            "range_bot",
            self.range_bot.run_range_trading,
            health_check_func=lambda: self.range_bot.is_healthy()
        )
        
        self.detailed_logger.log_event("INFO", "MAIN_CONTROLLER", "Watchdog processes registered")
    
    def stop(self):
        """システムを停止"""
        try:
            self.detailed_logger.log_event("INFO", "MAIN_CONTROLLER", "System shutdown initiated")
            
            # Watchdog監視を停止
            self.watchdog.stop_monitoring()
            
            # スケジューラーを停止
            self.scheduler.shutdown()
            
            # IB接続を切断
            self.ib_connector.disconnect_from_ib()
            
            self.detailed_logger.log_event("INFO", "MAIN_CONTROLLER", "System shutdown completed")
            self.discord.info("Project Chimera が停止しました")
        except Exception as e:
            self.detailed_logger.log_error("MAIN_CONTROLLER", e, "System shutdown")
            print(f"システム停止エラー: {e}")

if __name__ == "__main__":
    controller = MainController()
    try:
        controller.start()
    except KeyboardInterrupt:
        controller.stop()
