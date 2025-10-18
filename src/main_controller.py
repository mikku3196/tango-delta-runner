import yaml
import os
import time
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from src.shared_modules.config_loader import ConfigLoader
from src.shared_modules.discord_logger import DiscordLogger
from src.shared_modules.ib_connector import IBConnector
from src.shared_modules.nisa_monitor import NISAMonitor
from src.bots.core_index_bot import CoreIndexBot
from src.bots.satellite_dividend_bot import SatelliteDividendBot
from src.bots.satellite_range_bot import SatelliteRangeBot

class MainController:
    def __init__(self):
        """メインコントローラーの初期匁E""
        self.config = ConfigLoader()
        self.discord = DiscordLogger(self.config.get("discord_webhook_url"))
        self.ib_connector = IBConnector()
        self.scheduler = BlockingScheduler()
        self.stop_flag_file = "STOP.flag"
        
        # NISA監視を初期匁E        self.nisa_monitor = NISAMonitor(self.config, self.discord, self.ib_connector)
        
        # Botインスタンス
        self.index_bot = CoreIndexBot(self.config, self.discord, self.ib_connector)
        self.dividend_bot = SatelliteDividendBot(self.config, self.discord, self.ib_connector)
        self.range_bot = SatelliteRangeBot(self.config, self.discord, self.ib_connector)
    
    def start(self):
        """シスチE��を起勁E""
        try:
            # STOP.flagの存在をチェチE��
            if self.check_stop_flag():
                self.discord.error("【CRITICAL】STOP.flagが検�Eされました。シスチE��を起動しません、E)
                print("STOP.flagが存在するため、シスチE��を起動しません、E)
                print("emergency_stop.pyを実行してSTOP.flagを削除してください、E)
                return False
            
            # IB接綁E            ib_config = self.config.get("ib_account")
            if not self.ib_connector.connect_to_ib(
                ib_config["host"], 
                ib_config["port"], 
                ib_config["client_id"]
            ):
                raise Exception("IB接続に失敗しました")
            
            self.discord.success("Project Chimera が起動しました")
            
            # スケジューラー設宁E            self.setup_scheduler()
            
            # メインループ開姁E            self.scheduler.start()
            
        except Exception as e:
            self.discord.error(f"シスチE��起動エラー: {str(e)}")
            raise
    
    def check_stop_flag(self) -> bool:
        """STOP.flagの存在をチェチE��"""
        return os.path.exists(self.stop_flag_file)
    
    def monitor_stop_flag(self):
        """STOP.flagを監視し、検�E時�EシスチE��を停止"""
        if self.check_stop_flag():
            self.discord.error("【CRITICAL】STOP.flagが検�Eされました。シスチE��を停止します、E)
            print("STOP.flagが検�Eされました。シスチE��を停止します、E)
            self.scheduler.shutdown()
            return True
        return False
    
    def setup_scheduler(self):
        """スケジューラーにタスクを登録"""
        # STOP.flag監要E 1刁E��と
        self.scheduler.add_job(
            self.monitor_stop_flag,
            CronTrigger(minute="*"),
            id="stop_flag_monitor",
            name="STOP.flag監要E
        )
        
        # インチE��クスBot: 毎月1日 9:30
        self.scheduler.add_job(
            self.index_bot.execute_monthly_investment,
            CronTrigger(day=1, hour=9, minute=30),
            id="index_monthly",
            name="インチE��クス積立実衁E
        )
        
        # 高�E当Bot: 毎週日曁E22:00 (スクリーニング)
        self.scheduler.add_job(
            self.dividend_bot.run_screening,
            CronTrigger(day_of_week=6, hour=22, minute=0),
            id="dividend_screening",
            name="高�E当株スクリーニング"
        )
        
        # 高�E当Bot: 毎営業日 9:05 (購入判断)
        self.scheduler.add_job(
            self.dividend_bot.run_purchase_decision,
            CronTrigger(day_of_week="mon-fri", hour=9, minute=5),
            id="dividend_purchase",
            name="高�E当株購入判断"
        )
        
        # レンジBot: 毎営業日 16:00 (スクリーニング)
        self.scheduler.add_job(
            self.range_bot.run_screening,
            CronTrigger(day_of_week="mon-fri", hour=16, minute=0),
            id="range_screening",
            name="レンジ相場スクリーニング"
        )
        
        # レンジBot: 取引時間中 常時実衁E        self.scheduler.add_job(
            self.range_bot.run_range_trading,
            CronTrigger(day_of_week="mon-fri", hour="9-15", minute="*"),
            id="range_trading",
            name="レンジ取引実衁E
        )
        
        # ポ�Eトフォリオリバランス: 毎月1日 10:00
        self.scheduler.add_job(
            self.rebalance_portfolio,
            CronTrigger(day=1, hour=10, minute=0),
            id="portfolio_rebalance",
            name="ポ�Eトフォリオリバランス"
        )
        
        # NISA使用状況レポ�EチE 毎日 18:00
        self.scheduler.add_job(
            self.nisa_monitor.send_usage_report,
            CronTrigger(hour=18, minute=0),
            id="nisa_report",
            name="NISA使用状況レポ�EチE
        )
        
        self.discord.info("スケジューラーが設定されました")
    
    def rebalance_portfolio(self):
        """ポ�Eトフォリオリバランスを実衁E""
        try:
            self.discord.info("ポ�Eトフォリオリバランスを実行中...")
            
            # 現在の総賁E��評価額を取征E            total_value = self.get_total_portfolio_value()
            
            # 吁E��略の現在の評価額を取征E            index_value = self.get_strategy_value("index")
            dividend_value = self.get_strategy_value("dividend")
            range_value = self.get_strategy_value("range")
            
            # 現在の比率を計箁E            current_ratios = {
                "index": index_value / total_value if total_value > 0 else 0,
                "dividend": dividend_value / total_value if total_value > 0 else 0,
                "range": range_value / total_value if total_value > 0 else 0
            }
            
            # 目標比率
            target_ratios = self.config.get("portfolio_ratios")
            
            # 最も比率が不足してぁE��戦略を特宁E            max_deviation = 0
            target_strategy = "index"
            
            for strategy in ["index", "dividend", "range"]:
                deviation = target_ratios[strategy] - current_ratios[strategy]
                if deviation > max_deviation:
                    max_deviation = deviation
                    target_strategy = strategy
            
            # 追加投賁E��E��を特定戦略に割り当て
            monthly_investment = self.config.get("index_bot.monthly_investment")
            
            if target_strategy == "index":
                self.index_bot.execute_additional_investment(monthly_investment)
            elif target_strategy == "dividend":
                self.dividend_bot.execute_additional_investment(monthly_investment)
            elif target_strategy == "range":
                self.range_bot.execute_additional_investment(monthly_investment)
            
            self.discord.success(f"リバランス完亁E {target_strategy}戦略に{monthly_investment}冁E��追加投賁E)
            
        except Exception as e:
            self.discord.error(f"リバランスエラー: {str(e)}")
    
    def get_total_portfolio_value(self):
        """総�Eートフォリオ価値を取征E""
        # 実裁E�E後で詳細匁E        return 1000000  # 仮の値
    
    def get_strategy_value(self, strategy):
        """吁E��略の評価額を取征E""
        # 実裁E�E後で詳細匁E        values = {
            "index": 500000,
            "dividend": 300000,
            "range": 200000
        }
        return values.get(strategy, 0)
    
    def stop(self):
        """シスチE��を停止"""
        try:
            self.scheduler.shutdown()
            self.ib_connector.disconnect_from_ib()
            self.discord.info("Project Chimera が停止しました")
        except Exception as e:
            print(f"シスチE��停止エラー: {e}")

if __name__ == "__main__":
    controller = MainController()
    try:
        controller.start()
    except KeyboardInterrupt:
        controller.stop()
