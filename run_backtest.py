#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Chimera バックテスト実行スクリプト
SatelliteRangeBotを使用したトヨタ自動車のバックテスト実行
"""

import sys
import json
from datetime import datetime
from pathlib import Path
from src.backtesting.backtest_engine import BacktestEngine
from src.bots.satellite_range_bot import SatelliteRangeBot
from src.shared_modules.config_loader import ConfigLoader
from src.shared_modules.detailed_logger import get_detailed_logger

def main():
    """メイン関数"""
    print("=" * 80)
    print("🚀 Project Chimera バックテスト実行")
    print("=" * 80)
    
    try:
        # 設定を読み込み
        config = ConfigLoader()
        detailed_logger = get_detailed_logger()
        
        # SatelliteRangeBotのインスタンスを作成（strategyとして）
        print("📊 Satellite Range Bot を初期化中...")
        strategy = SatelliteRangeBot(
            config=config,
            detailed_logger=detailed_logger
        )
        
        # BacktestEngineを初期化
        # トヨタ自動車（'7203.T'）を対象に、2022-01-01から2024-12-31までの期間、初期資金100万円
        print("🔧 BacktestEngine を初期化中...")
        engine = BacktestEngine(
            strategy=strategy,
            ticker="7203.T",  # トヨタ自動車
            start_date="2022-01-01",
            end_date="2024-12-31",
            initial_capital=1000000  # 100万円
        )
        
        print(f"📈 対象銘柄: {engine.ticker}")
        print(f"📅 期間: {engine.start_date} ～ {engine.end_date}")
        print(f"💰 初期資金: ¥{engine.initial_capital:,}")
        print("=" * 80)
        
        # データを読み込み
        print("📥 価格データを読み込み中...")
        if not engine.load_data():
            print("❌ データの読み込みに失敗しました")
            return False
        
        print(f"✅ データ読み込み完了 ({len(engine.data)} 日分)")
        print()
        
        # データを準備（ボリンジャーバンドとSMA200を追加）
        print("🔧 データを準備中（ボリンジャーバンドとSMA200計算）...")
        prepared_data = strategy.prepare_data(engine.data)
        engine.data = prepared_data
        print("✅ データ準備完了")
        print()
        
        # バックテストを実行
        print("🔄 バックテストを実行中...")
        engine.run()
        
        # 結果を生成
        print("📊 結果を生成中...")
        results = engine.generate_results()
        
        # 結果を表示
        print("=" * 80)
        print("📊 バックテスト結果")
        print("=" * 80)
        
        print(f"戦略: {results['strategy']}")
        print(f"銘柄: {results['ticker']}")
        print(f"期間: {results['start_date']} ～ {results['end_date']}")
        print()
        
        print("💰 パフォーマンス指標:")
        print(f"  初期資金: ¥{results['initial_capital']:,}")
        print(f"  最終資産: ¥{results['final_value']:,.0f}")
        print(f"  総リターン: {results['total_return']:.2%}")
        print(f"  年率リターン: {results['annual_return']:.2%}")
        print(f"  最大ドローダウン: {results['max_drawdown']:.2%}")
        print(f"  シャープレシオ: {results['sharpe_ratio']:.2f}")
        print()
        
        print("📈 取引統計:")
        print(f"  総取引回数: {results['total_trades']}")
        print(f"  勝ち取引: {results['winning_trades']}")
        print(f"  負け取引: {results['losing_trades']}")
        print(f"  勝率: {results['win_rate']:.2%}")
        print()
        
        # 取引履歴の詳細（最新5件）
        if results['trades']:
            print("📋 最新の取引履歴 (最新5件):")
            print("-" * 60)
            recent_trades = results['trades'][-5:]
            for trade in recent_trades:
                trade_type = "🟢 買い" if trade['type'] == 'buy' else "🔴 売り"
                print(f"  {trade['date']} | {trade_type} | ¥{trade['price']:,.0f} | {trade['shares']:.2f}株")
            print()
        
        # ポートフォリオ価値の推移（月次サンプル）
        if results['portfolio_history']:
            print("📊 ポートフォリオ価値の推移 (月次サンプル):")
            print("-" * 60)
            monthly_samples = results['portfolio_history'][::30]  # 30日ごとにサンプル
            for entry in monthly_samples[-6:]:  # 最新6件
                print(f"  {entry['date']} | ¥{entry['portfolio_value']:,.0f}")
            print()
        
        # 結果をJSONファイルとして保存
        print("💾 結果を保存中...")
        save_results_to_file(results)
        print("✅ 結果保存完了")
        print()
        
        # 詳細ログ
        detailed_logger.log_event("INFO", "BACKTEST", "Backtest execution completed", {
            "strategy": results['strategy'],
            "ticker": results['ticker'],
            "total_return": results['total_return'],
            "annual_return": results['annual_return'],
            "max_drawdown": results['max_drawdown'],
            "total_trades": results['total_trades'],
            "win_rate": results['win_rate']
        })
        
        print("✅ バックテストが正常に完了しました")
        return True
        
    except Exception as e:
        print(f"❌ バックテスト実行中にエラーが発生しました: {e}")
        detailed_logger.log_error("BACKTEST", e, "Backtest execution")
        return False

def save_results_to_file(results: dict):
    """結果をJSONファイルとして保存"""
    try:
        # 保存ディレクトリを作成
        results_dir = Path("logs/backtest_results")
        results_dir.mkdir(parents=True, exist_ok=True)
        
        # ファイル名を生成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backtest_results_{timestamp}.json"
        filepath = results_dir / filename
        
        # 結果を保存
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"📁 結果ファイル: {filepath}")
        
    except Exception as e:
        print(f"❌ 結果保存エラー: {e}")

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
