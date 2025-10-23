#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from src.backtesting.backtest_engine import BacktestEngine
from src.bots.satellite_range_bot import SatelliteRangeBot
from src.shared_modules.config_loader import ConfigLoader
from src.shared_modules.detailed_logger import get_detailed_logger

print("=== DEBUGGING THE GHOST ===")
config = ConfigLoader()
strategy = SatelliteRangeBot(config=config, detailed_logger=get_detailed_logger())
engine = BacktestEngine(strategy=strategy, ticker="7203.T", start_date="2022-01-01", end_date="2024-12-31", initial_capital=1000000)
print("Engine created with ticker:", repr(engine.ticker))
print("About to call load_data...")
result = engine.load_data()
print("Load data result:", result)
