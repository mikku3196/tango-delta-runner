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
        """繝｡繧､繝ｳ繧ｳ繝ｳ繝医Ο繝ｼ繝ｩ繝ｼ縺ｮ蛻晄悄蛹・""
        self.config = ConfigLoader()
        self.discord = DiscordLogger(self.config.get("discord_webhook_url"))
        self.ib_connector = IBConnector()
        self.scheduler = BlockingScheduler()
        self.stop_flag_file = "STOP.flag"
        
        # NISA逶｣隕悶ｒ蛻晄悄蛹・        self.nisa_monitor = NISAMonitor(self.config, self.discord, self.ib_connector)
        
        # Bot繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ
        self.index_bot = CoreIndexBot(self.config, self.discord, self.ib_connector)
        self.dividend_bot = SatelliteDividendBot(self.config, self.discord, self.ib_connector)
        self.range_bot = SatelliteRangeBot(self.config, self.discord, self.ib_connector)
    
    def start(self):
        """繧ｷ繧ｹ繝・Β繧定ｵｷ蜍・""
        try:
            # STOP.flag縺ｮ蟄伜惠繧偵メ繧ｧ繝・け
            if self.check_stop_flag():
                self.discord.error("縲燭RITICAL縲全TOP.flag縺梧､懷・縺輔ｌ縺ｾ縺励◆縲ゅす繧ｹ繝・Β繧定ｵｷ蜍輔＠縺ｾ縺帙ｓ縲・)
                print("STOP.flag縺悟ｭ伜惠縺吶ｋ縺溘ａ縲√す繧ｹ繝・Β繧定ｵｷ蜍輔＠縺ｾ縺帙ｓ縲・)
                print("emergency_stop.py繧貞ｮ溯｡後＠縺ｦSTOP.flag繧貞炎髯､縺励※縺上□縺輔＞縲・)
                return False
            
            # IB謗･邯・            ib_config = self.config.get("ib_account")
            if not self.ib_connector.connect_to_ib(
                ib_config["host"], 
                ib_config["port"], 
                ib_config["client_id"]
            ):
                raise Exception("IB謗･邯壹↓螟ｱ謨励＠縺ｾ縺励◆")
            
            self.discord.success("Project Chimera 縺瑚ｵｷ蜍輔＠縺ｾ縺励◆")
            
            # 繧ｹ繧ｱ繧ｸ繝･繝ｼ繝ｩ繝ｼ險ｭ螳・            self.setup_scheduler()
            
            # 繝｡繧､繝ｳ繝ｫ繝ｼ繝鈴幕蟋・            self.scheduler.start()
            
        except Exception as e:
            self.discord.error(f"繧ｷ繧ｹ繝・Β襍ｷ蜍輔お繝ｩ繝ｼ: {str(e)}")
            raise
    
    def check_stop_flag(self) -> bool:
        """STOP.flag縺ｮ蟄伜惠繧偵メ繧ｧ繝・け"""
        return os.path.exists(self.stop_flag_file)
    
    def monitor_stop_flag(self):
        """STOP.flag繧堤屮隕悶＠縲∵､懷・譎ゅ・繧ｷ繧ｹ繝・Β繧貞●豁｢"""
        if self.check_stop_flag():
            self.discord.error("縲燭RITICAL縲全TOP.flag縺梧､懷・縺輔ｌ縺ｾ縺励◆縲ゅす繧ｹ繝・Β繧貞●豁｢縺励∪縺吶・)
            print("STOP.flag縺梧､懷・縺輔ｌ縺ｾ縺励◆縲ゅす繧ｹ繝・Β繧貞●豁｢縺励∪縺吶・)
            self.scheduler.shutdown()
            return True
        return False
    
    def setup_scheduler(self):
        """繧ｹ繧ｱ繧ｸ繝･繝ｼ繝ｩ繝ｼ縺ｫ繧ｿ繧ｹ繧ｯ繧堤匳骭ｲ"""
        # STOP.flag逶｣隕・ 1蛻・＃縺ｨ
        self.scheduler.add_job(
            self.monitor_stop_flag,
            CronTrigger(minute="*"),
            id="stop_flag_monitor",
            name="STOP.flag逶｣隕・
        )
        
        # 繧､繝ｳ繝・ャ繧ｯ繧ｹBot: 豈取怦1譌･ 9:30
        self.scheduler.add_job(
            self.index_bot.execute_monthly_investment,
            CronTrigger(day=1, hour=9, minute=30),
            id="index_monthly",
            name="繧､繝ｳ繝・ャ繧ｯ繧ｹ遨咲ｫ句ｮ溯｡・
        )
        
        # 鬮倬・蠖釘ot: 豈朱ｱ譌･譖・22:00 (繧ｹ繧ｯ繝ｪ繝ｼ繝九Φ繧ｰ)
        self.scheduler.add_job(
            self.dividend_bot.run_screening,
            CronTrigger(day_of_week=6, hour=22, minute=0),
            id="dividend_screening",
            name="鬮倬・蠖捺ｪ繧ｹ繧ｯ繝ｪ繝ｼ繝九Φ繧ｰ"
        )
        
        # 鬮倬・蠖釘ot: 豈主霧讌ｭ譌･ 9:05 (雉ｼ蜈･蛻､譁ｭ)
        self.scheduler.add_job(
            self.dividend_bot.run_purchase_decision,
            CronTrigger(day_of_week="mon-fri", hour=9, minute=5),
            id="dividend_purchase",
            name="鬮倬・蠖捺ｪ雉ｼ蜈･蛻､譁ｭ"
        )
        
        # 繝ｬ繝ｳ繧ｸBot: 豈主霧讌ｭ譌･ 16:00 (繧ｹ繧ｯ繝ｪ繝ｼ繝九Φ繧ｰ)
        self.scheduler.add_job(
            self.range_bot.run_screening,
            CronTrigger(day_of_week="mon-fri", hour=16, minute=0),
            id="range_screening",
            name="繝ｬ繝ｳ繧ｸ逶ｸ蝣ｴ繧ｹ繧ｯ繝ｪ繝ｼ繝九Φ繧ｰ"
        )
        
        # 繝ｬ繝ｳ繧ｸBot: 蜿門ｼ墓凾髢謎ｸｭ 蟶ｸ譎ょｮ溯｡・        self.scheduler.add_job(
            self.range_bot.run_range_trading,
            CronTrigger(day_of_week="mon-fri", hour="9-15", minute="*"),
            id="range_trading",
            name="繝ｬ繝ｳ繧ｸ蜿門ｼ募ｮ溯｡・
        )
        
        # 繝昴・繝医ヵ繧ｩ繝ｪ繧ｪ繝ｪ繝舌Λ繝ｳ繧ｹ: 豈取怦1譌･ 10:00
        self.scheduler.add_job(
            self.rebalance_portfolio,
            CronTrigger(day=1, hour=10, minute=0),
            id="portfolio_rebalance",
            name="繝昴・繝医ヵ繧ｩ繝ｪ繧ｪ繝ｪ繝舌Λ繝ｳ繧ｹ"
        )
        
        # NISA菴ｿ逕ｨ迥ｶ豕√Ξ繝昴・繝・ 豈取律 18:00
        self.scheduler.add_job(
            self.nisa_monitor.send_usage_report,
            CronTrigger(hour=18, minute=0),
            id="nisa_report",
            name="NISA菴ｿ逕ｨ迥ｶ豕√Ξ繝昴・繝・
        )
        
        self.discord.info("繧ｹ繧ｱ繧ｸ繝･繝ｼ繝ｩ繝ｼ縺瑚ｨｭ螳壹＆繧後∪縺励◆")
    
    def rebalance_portfolio(self):
        """繝昴・繝医ヵ繧ｩ繝ｪ繧ｪ繝ｪ繝舌Λ繝ｳ繧ｹ繧貞ｮ溯｡・""
        try:
            self.discord.info("繝昴・繝医ヵ繧ｩ繝ｪ繧ｪ繝ｪ繝舌Λ繝ｳ繧ｹ繧貞ｮ溯｡御ｸｭ...")
            
            # 迴ｾ蝨ｨ縺ｮ邱剰ｳ・肇隧穂ｾ｡鬘阪ｒ蜿門ｾ・            total_value = self.get_total_portfolio_value()
            
            # 蜷・姶逡･縺ｮ迴ｾ蝨ｨ縺ｮ隧穂ｾ｡鬘阪ｒ蜿門ｾ・            index_value = self.get_strategy_value("index")
            dividend_value = self.get_strategy_value("dividend")
            range_value = self.get_strategy_value("range")
            
            # 迴ｾ蝨ｨ縺ｮ豈皮紫繧定ｨ育ｮ・            current_ratios = {
                "index": index_value / total_value if total_value > 0 else 0,
                "dividend": dividend_value / total_value if total_value > 0 else 0,
                "range": range_value / total_value if total_value > 0 else 0
            }
            
            # 逶ｮ讓呎ｯ皮紫
            target_ratios = self.config.get("portfolio_ratios")
            
            # 譛繧よｯ皮紫縺御ｸ崎ｶｳ縺励※縺・ｋ謌ｦ逡･繧堤音螳・            max_deviation = 0
            target_strategy = "index"
            
            for strategy in ["index", "dividend", "range"]:
                deviation = target_ratios[strategy] - current_ratios[strategy]
                if deviation > max_deviation:
                    max_deviation = deviation
                    target_strategy = strategy
            
            # 霑ｽ蜉謚戊ｳ・ｳ・≡繧堤音螳壽姶逡･縺ｫ蜑ｲ繧雁ｽ薙※
            monthly_investment = self.config.get("index_bot.monthly_investment")
            
            if target_strategy == "index":
                self.index_bot.execute_additional_investment(monthly_investment)
            elif target_strategy == "dividend":
                self.dividend_bot.execute_additional_investment(monthly_investment)
            elif target_strategy == "range":
                self.range_bot.execute_additional_investment(monthly_investment)
            
            self.discord.success(f"繝ｪ繝舌Λ繝ｳ繧ｹ螳御ｺ・ {target_strategy}謌ｦ逡･縺ｫ{monthly_investment}蜀・ｒ霑ｽ蜉謚戊ｳ・)
            
        except Exception as e:
            self.discord.error(f"繝ｪ繝舌Λ繝ｳ繧ｹ繧ｨ繝ｩ繝ｼ: {str(e)}")
    
    def get_total_portfolio_value(self):
        """邱上・繝ｼ繝医ヵ繧ｩ繝ｪ繧ｪ萓｡蛟､繧貞叙蠕・""
        # 螳溯｣・・蠕後〒隧ｳ邏ｰ蛹・        return 1000000  # 莉ｮ縺ｮ蛟､
    
    def get_strategy_value(self, strategy):
        """蜷・姶逡･縺ｮ隧穂ｾ｡鬘阪ｒ蜿門ｾ・""
        # 螳溯｣・・蠕後〒隧ｳ邏ｰ蛹・        values = {
            "index": 500000,
            "dividend": 300000,
            "range": 200000
        }
        return values.get(strategy, 0)
    
    def stop(self):
        """繧ｷ繧ｹ繝・Β繧貞●豁｢"""
        try:
            self.scheduler.shutdown()
            self.ib_connector.disconnect_from_ib()
            self.discord.info("Project Chimera 縺悟●豁｢縺励∪縺励◆")
        except Exception as e:
            print(f"繧ｷ繧ｹ繝・Β蛛懈ｭ｢繧ｨ繝ｩ繝ｼ: {e}")

if __name__ == "__main__":
    controller = MainController()
    try:
        controller.start()
    except KeyboardInterrupt:
        controller.stop()
