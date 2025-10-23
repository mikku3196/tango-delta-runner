#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Chimera テストスイート
各モジュールの単体テストと統合テスト
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.shared_modules.config_loader import ConfigLoader
from src.shared_modules.discord_logger import DiscordLogger
from src.shared_modules.ib_connector import IBConnector
from src.shared_modules.detailed_logger import DetailedLogger
from src.shared_modules.nisa_monitor import NISAMonitor
from src.shared_modules.risk_assessor import RiskAssessor
from src.shared_modules.watchdog import Watchdog
from src.bots.core_index_bot import CoreIndexBot
from src.bots.satellite_dividend_bot import SatelliteDividendBot
from src.bots.satellite_range_bot import SatelliteRangeBot
from src.backtesting.backtest_engine import BacktestEngine

class TestConfigLoader(unittest.TestCase):
    """ConfigLoaderのテスト"""
    
    def setUp(self):
        self.config = ConfigLoader()
    
    def test_get_existing_key(self):
        """既存のキーの取得テスト"""
        value = self.config.get("portfolio_ratios.index")
        self.assertEqual(value, 0.50)
    
    def test_get_nonexistent_key(self):
        """存在しないキーの取得テスト"""
        value = self.config.get("nonexistent.key")
        self.assertIsNone(value)
    
    def test_get_with_default(self):
        """デフォルト値付きの取得テスト"""
        value = self.config.get("nonexistent.key", "default")
        self.assertEqual(value, "default")

class TestDiscordLogger(unittest.TestCase):
    """DiscordLoggerのテスト"""
    
    def setUp(self):
        self.discord = DiscordLogger("https://discord.com/api/webhooks/test")
    
    @patch('requests.post')
    def test_send_message(self, mock_post):
        """メッセージ送信テスト"""
        mock_post.return_value.status_code = 204
        
        self.discord.send_message("Test Title", "Test Message")
        
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]['url'], "https://discord.com/api/webhooks/test")
    
    @patch('requests.post')
    def test_success_message(self, mock_post):
        """成功メッセージテスト"""
        mock_post.return_value.status_code = 204
        
        self.discord.success("Test Success")
        
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_error_message(self, mock_post):
        """エラーメッセージテスト"""
        mock_post.return_value.status_code = 204
        
        self.discord.error("Test Error")
        
        mock_post.assert_called_once()

class TestDetailedLogger(unittest.TestCase):
    """DetailedLoggerのテスト"""
    
    def setUp(self):
        self.logger = DetailedLogger(log_dir="test_logs")
    
    def tearDown(self):
        # テスト用ログファイルを削除
        import shutil
        if os.path.exists("test_logs"):
            shutil.rmtree("test_logs")
    
    def test_log_event(self):
        """イベントログテスト"""
        self.logger.log_event("INFO", "TEST", "Test event", {"test": True})
        
        # ログファイルが作成されているかチェック
        log_files = list(self.logger.log_dir.glob("*.log"))
        self.assertTrue(len(log_files) > 0)
    
    def test_log_trade(self):
        """取引ログテスト"""
        self.logger.log_trade("BUY", "2559", 100, 1500.0, "U1234567")
        
        log_files = list(self.logger.log_dir.glob("*.log"))
        self.assertTrue(len(log_files) > 0)
    
    def test_log_portfolio_change(self):
        """ポートフォリオ変更ログテスト"""
        self.logger.log_portfolio_change("index", 500000, 520000, 4.0)
        
        log_files = list(self.logger.log_dir.glob("*.log"))
        self.assertTrue(len(log_files) > 0)

class TestNISAMonitor(unittest.TestCase):
    """NISAMonitorのテスト"""
    
    def setUp(self):
        self.config = ConfigLoader()
        self.discord = Mock(spec=DiscordLogger)
        self.ib_connector = Mock(spec=IBConnector)
        self.monitor = NISAMonitor(self.config, self.discord, self.ib_connector)
    
    def test_calculate_usage_percentage(self):
        """使用率計算テスト"""
        usage = self.monitor.calculate_usage_percentage(100000, 3600000)
        expected = (100000 / 3600000) * 100
        self.assertAlmostEqual(usage, expected, places=2)
    
    def test_check_annual_limit(self):
        """年間制限チェックテスト"""
        # 制限内
        result = self.monitor.check_annual_limit(1000000)
        self.assertFalse(result)
        
        # 制限超過
        result = self.monitor.check_annual_limit(3700000)
        self.assertTrue(result)
    
    def test_check_lifetime_limit(self):
        """生涯制限チェックテスト"""
        # 制限内
        result = self.monitor.check_lifetime_limit(10000000)
        self.assertFalse(result)
        
        # 制限超過
        result = self.monitor.check_lifetime_limit(19000000)
        self.assertTrue(result)

class TestRiskAssessor(unittest.TestCase):
    """RiskAssessorのテスト"""
    
    def setUp(self):
        self.config = ConfigLoader()
        self.assessor = RiskAssessor(self.config)
    
    def test_assess_risk_profile(self):
        """リスクプロファイル診断テスト"""
        # 安定型の回答
        answers = {
            "age": "30-40",
            "investment_experience": "beginner",
            "risk_tolerance": "low",
            "investment_period": "long",
            "loss_tolerance": "low"
        }
        
        profile = self.assessor.assess_risk_profile(answers)
        self.assertEqual(profile["profile_type"], "stable")
        self.assertEqual(profile["ratios"]["index"], 0.70)
    
    def test_get_profile_ratios(self):
        """プロファイル比率取得テスト"""
        ratios = self.assessor.get_profile_ratios("aggressive")
        self.assertEqual(ratios["index"], 0.50)
        self.assertEqual(ratios["dividend"], 0.30)
        self.assertEqual(ratios["range"], 0.20)

class TestCoreIndexBot(unittest.TestCase):
    """CoreIndexBotのテスト"""
    
    def setUp(self):
        self.config = ConfigLoader()
        self.discord = Mock(spec=DiscordLogger)
        self.ib_connector = Mock(spec=IBConnector)
        self.bot = CoreIndexBot(self.config, self.discord, self.ib_connector)
    
    def test_is_healthy(self):
        """ヘルスチェックテスト"""
        # 初期状態は健康
        self.assertTrue(self.bot.is_healthy())
        
        # エラー数が多すぎる場合は不健康
        self.bot.error_count = 15
        self.assertFalse(self.bot.is_healthy())
    
    def test_get_status(self):
        """状態取得テスト"""
        status = self.bot.get_status()
        
        self.assertIn("is_running", status)
        self.assertIn("last_execution", status)
        self.assertIn("execution_count", status)
        self.assertIn("error_count", status)
        self.assertIn("is_healthy", status)

class TestSatelliteDividendBot(unittest.TestCase):
    """SatelliteDividendBotのテスト"""
    
    def setUp(self):
        self.config = ConfigLoader()
        self.discord = Mock(spec=DiscordLogger)
        self.ib_connector = Mock(spec=IBConnector)
        self.bot = SatelliteDividendBot(self.config, self.discord, self.ib_connector)
    
    def test_is_healthy(self):
        """ヘルスチェックテスト"""
        self.assertTrue(self.bot.is_healthy())
    
    def test_get_status(self):
        """状態取得テスト"""
        status = self.bot.get_status()
        
        self.assertIn("is_running", status)
        self.assertIn("current_holdings_count", status)
        self.assertIn("is_healthy", status)

class TestSatelliteRangeBot(unittest.TestCase):
    """SatelliteRangeBotのテスト"""
    
    def setUp(self):
        self.config = ConfigLoader()
        self.discord = Mock(spec=DiscordLogger)
        self.ib_connector = Mock(spec=IBConnector)
        self.bot = SatelliteRangeBot(self.config, self.discord, self.ib_connector)
    
    def test_is_healthy(self):
        """ヘルスチェックテスト"""
        self.assertTrue(self.bot.is_healthy())
    
    def test_get_status(self):
        """状態取得テスト"""
        status = self.bot.get_status()
        
        self.assertIn("is_running", status)
        self.assertIn("current_positions_count", status)
        self.assertIn("trade_history_count", status)
        self.assertIn("is_healthy", status)

class TestBacktestEngine(unittest.TestCase):
    """BacktestEngineのテスト"""
    
    def setUp(self):
        self.config = ConfigLoader()
        self.engine = BacktestEngine(self.config)
    
    def test_get_monthly_investment_dates(self):
        """月次投資日計算テスト"""
        dates = self.engine._get_monthly_investment_dates("2023-01-01", "2023-03-31")
        
        self.assertEqual(len(dates), 3)  # 1月、2月、3月
        self.assertEqual(dates[0], "2023-01-01")
        self.assertEqual(dates[1], "2023-02-01")
        self.assertEqual(dates[2], "2023-03-01")
    
    def test_calculate_max_drawdown(self):
        """最大ドローダウン計算テスト"""
        values = [100, 120, 110, 90, 95, 100]
        max_dd = self.engine._calculate_max_drawdown(values)
        
        # 120から90への下落が最大ドローダウン
        expected = (120 - 90) / 120
        self.assertAlmostEqual(max_dd, expected, places=4)
    
    @patch('yfinance.Ticker')
    def test_get_price_data(self, mock_ticker):
        """価格データ取得テスト"""
        # モックデータを作成
        mock_data = pd.DataFrame({
            'Close': [100, 101, 102, 103, 104]
        }, index=pd.date_range('2023-01-01', periods=5))
        
        mock_ticker.return_value.history.return_value = mock_data
        
        data = self.engine._get_price_data("2559.T", "2023-01-01", "2023-01-05")
        
        self.assertFalse(data.empty)
        self.assertEqual(len(data), 5)

class TestWatchdog(unittest.TestCase):
    """Watchdogのテスト"""
    
    def setUp(self):
        self.config = ConfigLoader()
        self.discord = Mock(spec=DiscordLogger)
        self.watchdog = Watchdog(self.config, self.discord)
    
    def test_register_process(self):
        """プロセス登録テスト"""
        def test_func():
            pass
        
        self.watchdog.register_process("test_process", test_func)
        
        self.assertIn("test_process", self.watchdog.monitored_processes)
        self.assertEqual(self.watchdog.restart_counts["test_process"], 0)
    
    def test_is_in_cooldown(self):
        """クールダウンチェックテスト"""
        # 初回はクールダウン中ではない
        self.assertFalse(self.watchdog._is_in_cooldown("test_process"))
        
        # 最後の再起動時刻を設定
        self.watchdog.last_restart_times["test_process"] = datetime.now()
        
        # クールダウン中
        self.assertTrue(self.watchdog._is_in_cooldown("test_process"))

class TestIntegration(unittest.TestCase):
    """統合テスト"""
    
    def setUp(self):
        self.config = ConfigLoader()
        self.discord = Mock(spec=DiscordLogger)
        self.ib_connector = Mock(spec=IBConnector)
    
    def test_bot_initialization(self):
        """Bot初期化統合テスト"""
        index_bot = CoreIndexBot(self.config, self.discord, self.ib_connector)
        dividend_bot = SatelliteDividendBot(self.config, self.discord, self.ib_connector)
        range_bot = SatelliteRangeBot(self.config, self.discord, self.ib_connector)
        
        # 全てのBotが正常に初期化されているかチェック
        self.assertTrue(index_bot.is_healthy())
        self.assertTrue(dividend_bot.is_healthy())
        self.assertTrue(range_bot.is_healthy())
    
    def test_watchdog_integration(self):
        """Watchdog統合テスト"""
        watchdog = Watchdog(self.config, self.discord)
        
        def test_process():
            pass
        
        # プロセス登録
        watchdog.register_process("test_process", test_process)
        
        # ヘルスチェック関数
        def health_check():
            return True
        
        watchdog.register_process("healthy_process", test_process, health_check_func=health_check)
        
        # 監視対象プロセスが登録されているかチェック
        self.assertIn("test_process", watchdog.monitored_processes)
        self.assertIn("healthy_process", watchdog.monitored_processes)

def run_tests():
    """テスト実行"""
    # テストスイートを作成
    test_suite = unittest.TestSuite()
    
    # テストクラスを追加
    test_classes = [
        TestConfigLoader,
        TestDiscordLogger,
        TestDetailedLogger,
        TestNISAMonitor,
        TestRiskAssessor,
        TestCoreIndexBot,
        TestSatelliteDividendBot,
        TestSatelliteRangeBot,
        TestBacktestEngine,
        TestWatchdog,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # テスト実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
