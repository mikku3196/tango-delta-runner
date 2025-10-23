#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Chimera バックテストシステム
yfinanceを使用した過去データでの戦略検証
"""

import os
import json
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from src.shared_modules.config_loader import ConfigLoader
from src.shared_modules.detailed_logger import get_detailed_logger

class BacktestEngine:
    def __init__(self, strategy, ticker: str, start_date: str, end_date: str, initial_capital: float):
        """
        バックテストエンジンの初期化
        
        Args:
            strategy: テスト対象の戦略オブジェクト
            ticker: 銘柄コード
            start_date: 開始日 (YYYY-MM-DD)
            end_date: 終了日 (YYYY-MM-DD)
            initial_capital: 初期資金
        """
        self.strategy = strategy
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        
        # バックテスト設定
        self.commission_rate = 0.001  # 手数料0.1%
        self.slippage_rate = 0.0005  # スリッページ0.05%
        
        # ポートフォリオ状態
        self.cash = initial_capital
        self.shares = 0
        self.portfolio_value = initial_capital
        
        # 取引履歴
        self.trades = []
        self.portfolio_history = []
        
        # データ
        self.data = None
        
        # ログ設定
        self.detailed_logger = get_detailed_logger()
        
        # 結果保存ディレクトリ
        self.results_dir = Path("logs/backtest_results")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        self.detailed_logger.log_event("INFO", "BACKTEST", "Backtest engine initialized", {
            "strategy": strategy.__class__.__name__,
            "ticker": ticker,
            "start_date": start_date,
            "end_date": end_date,
            "initial_capital": initial_capital
        })
    
    def load_data(self) -> bool:
        """
        yfinanceを使い、指定された銘柄の過去の日足データを取得し、欠損値を前方フィルで補完する
        
        Returns:
            bool: データ取得が成功したかどうか
        """
        print(f"--- DEBUG --- Ticker being sent to yfinance: '{self.ticker}'")
        try:
            self.detailed_logger.log_event("INFO", "BACKTEST", "Loading price data", {
                "ticker": self.ticker,
                "start_date": self.start_date,
                "end_date": self.end_date
            })
            
            # yf.Ticker(...).history() の代わりに、yf.download() を直接使用する！
            self.data = yf.download(
                self.ticker,
                start=self.start_date,
                end=self.end_date,
                repair=True  # 念のため、キャッシュ修復オプションも付けておく
            )
            
            if self.data.empty:
                self.detailed_logger.log_event("ERROR", "BACKTEST", "No data retrieved", {
                    "ticker": self.ticker
                })
                return False
            
            # --- ここからが修正箇所 ---
            # yfinanceが返す多層カラムを、シンプルなカラムに変換する
            if isinstance(self.data.columns, pd.MultiIndex):
                self.data.columns = self.data.columns.droplevel(1)
            # --- 修正箇所ここまで ---

            # 欠損値を前方埋め
            self.data = self.data.ffill()
            
            self.detailed_logger.log_event("INFO", "BACKTEST", "Data loaded successfully", {
                "ticker": self.ticker,
                "data_points": len(self.data),
                "date_range": f"{self.data.index[0].strftime('%Y-%m-%d')} to {self.data.index[-1].strftime('%Y-%m-%d')}"
            })
            
            return True
            
        except Exception as e:
            self.detailed_logger.log_error("BACKTEST", e, f"Load data for {self.ticker}")
            return False
    
    def run(self) -> Dict[str, Any]:
        """
        取得したデータを1日ずつループ処理し、戦略に基づいて取引をシミュレートする
        
        Returns:
            バックテスト結果
        """
        try:
            # データが読み込まれていない場合はエラー
            if self.data is None:
                raise ValueError("データが読み込まれていません。load_data()を先に実行してください。")
            
            self.detailed_logger.log_event("INFO", "BACKTEST", "Backtest simulation started", {
                "strategy": self.strategy.__class__.__name__,
                "ticker": self.ticker,
                "data_points": len(self.data)
            })
            
            # 戦略を初期化
            if hasattr(self.strategy, 'initialize'):
                self.strategy.initialize()
            
            # 1日ずつループ処理
            for date, row in self.data.iterrows():
                current_price = row['Close']
                
                # --- ここからが追加箇所 ---
                # ストップロス（損切り）の判断
                # もし、現在株を保有しているなら...
                if self.shares > 0:
                    # 最後に買った時の取引記録を探す
                    last_buy_trade = next((trade for trade in reversed(self.trades) if trade['type'] == 'buy'), None)
                    if last_buy_trade:
                        purchase_price = last_buy_trade['price']
                        stop_loss_price = purchase_price * (1 - 0.15) # 例：購入価格から15%下落したら損切り

                        # もし、現在の価格が損切りラインを下回ったら...
                        if current_price < stop_loss_price:
                            print(f"--- STOP LOSS TRIGGERED at {date.strftime('%Y-%m-%d')} ---")
                            self._execute_sell(current_price, date) # 強制的に売却！
                            self._update_portfolio_value(current_price, date) # ポートフォリオを更新
                            # ストップロスが発動したので、この日のシグナル判断はスキップする
                            continue
                # --- 追加箇所ここまで ---

                # 戦略からシグナルを取得（新しい仕様）
                signal = self.strategy.generate_signal(row)
                
                # シグナルに基づいて取引を実行
                if signal == 'BUY':
                    self._execute_buy(current_price, date)
                elif signal == 'SELL':
                    self._execute_sell(current_price, date)
                # 'HOLD'の場合は何もしない
                
                # ポートフォリオ価値を更新
                self._update_portfolio_value(current_price, date)
            
            # 結果を生成
            results = self.generate_results()
            
            # 結果を保存
            self._save_backtest_results(self.strategy.__class__.__name__.lower(), results)
            
            self.detailed_logger.log_event("INFO", "BACKTEST", "Backtest simulation completed", {
                "strategy": self.strategy.__class__.__name__,
                "total_return": results["total_return"],
                "win_rate": results["win_rate"],
                "total_trades": results["total_trades"]
            })
            
            return results
            
        except Exception as e:
            self.detailed_logger.log_error("BACKTEST", e, "Backtest simulation")
            raise
    
    def generate_results(self) -> Dict[str, Any]:
        """
        シミュレーション完了後、最終的な資産額、トータルリターン（%）、勝率、取引回数などのパフォーマンス指標を計算し、辞書形式で返す
        
        Returns:
            パフォーマンス指標の辞書
        """
        try:
            # 最終的な資産額
            final_value = self.portfolio_value
            
            # トータルリターン（%）
            total_return = (final_value - self.initial_capital) / self.initial_capital
            
            # 年率リターン
            days = (self.data.index[-1] - self.data.index[0]).days
            years = days / 365.25
            annual_return = (final_value / self.initial_capital) ** (1 / years) - 1 if years > 0 else 0
            
            # 取引回数
            total_trades = len(self.trades)
            
            # 勝率計算
            winning_trades = 0
            losing_trades = 0
            
            for trade in self.trades:
                if trade['type'] == 'sell' and trade['profit'] > 0:
                    winning_trades += 1
                elif trade['type'] == 'sell' and trade['profit'] < 0:
                    losing_trades += 1
            
            win_rate = winning_trades / (winning_trades + losing_trades) if (winning_trades + losing_trades) > 0 else 0
            
            # 最大ドローダウン
            max_drawdown = self._calculate_max_drawdown([entry['portfolio_value'] for entry in self.portfolio_history])
            
            # シャープレシオ（簡易版）
            if len(self.portfolio_history) > 1:
                returns = []
                for i in range(1, len(self.portfolio_history)):
                    prev_value = self.portfolio_history[i-1]['portfolio_value']
                    curr_value = self.portfolio_history[i]['portfolio_value']
                    daily_return = (curr_value - prev_value) / prev_value
                    returns.append(daily_return)
                
                if returns:
                    avg_return = np.mean(returns)
                    std_return = np.std(returns)
                    sharpe_ratio = avg_return / std_return if std_return > 0 else 0
                else:
                    sharpe_ratio = 0
            else:
                sharpe_ratio = 0
            
            # 結果をまとめる
            results = {
                "strategy": self.strategy.__class__.__name__,
                "ticker": self.ticker,
                "start_date": self.start_date,
                "end_date": self.end_date,
                "initial_capital": self.initial_capital,
                "final_value": final_value,
                "total_return": total_return,
                "annual_return": annual_return,
                "max_drawdown": max_drawdown,
                "sharpe_ratio": sharpe_ratio,
                "total_trades": total_trades,
                "winning_trades": winning_trades,
                "losing_trades": losing_trades,
                "win_rate": win_rate,
                "trades": self.trades,
                "portfolio_history": self.portfolio_history
            }
            
            self.detailed_logger.log_event("INFO", "BACKTEST", "Results generated", {
                "total_return": f"{total_return:.2%}",
                "annual_return": f"{annual_return:.2%}",
                "max_drawdown": f"{max_drawdown:.2%}",
                "win_rate": f"{win_rate:.2%}",
                "total_trades": total_trades
            })
            
            return results
            
        except Exception as e:
            self.detailed_logger.log_error("BACKTEST", e, "Generate results")
            raise
    
    def _execute_buy(self, price: float, date: pd.Timestamp):
        """買い注文を実行"""
        try:
            # スリッページを適用
            execution_price = price * (1 + self.slippage_rate)
            
            # 手数料を計算
            commission = execution_price * self.commission_rate
            
            # 購入可能な株数を計算
            available_cash = self.cash - commission
            if available_cash <= 0:
                return  # 資金不足
            
            shares_to_buy = available_cash / execution_price
            total_cost = shares_to_buy * execution_price + commission
            
            # ポートフォリオを更新
            self.cash -= total_cost
            self.shares += shares_to_buy
            
            # 取引履歴に記録
            trade = {
                'date': date.strftime('%Y-%m-%d'),
                'type': 'buy',
                'price': execution_price,
                'shares': shares_to_buy,
                'total_cost': total_cost,
                'commission': commission,
                'cash_after': self.cash,
                'shares_after': self.shares
            }
            self.trades.append(trade)
            
            self.detailed_logger.log_event("DEBUG", "BACKTEST", "Buy order executed", trade)
            
        except Exception as e:
            self.detailed_logger.log_error("BACKTEST", e, f"Execute buy at {price}")
    
    def _execute_sell(self, price: float, date: pd.Timestamp):
        """売り注文を実行"""
        try:
            if self.shares <= 0:
                return  # 売却する株がない
            
            # スリッページを適用
            execution_price = price * (1 - self.slippage_rate)
            
            # 手数料を計算
            commission = execution_price * self.commission_rate
            
            # 全株を売却
            shares_to_sell = self.shares
            total_proceeds = shares_to_sell * execution_price - commission
            
            # 利益を計算（簡易版：最後の買い価格との差）
            profit = 0
            if self.trades:
                last_buy_trades = [t for t in self.trades if t['type'] == 'buy']
                if last_buy_trades:
                    avg_buy_price = sum(t['price'] * t['shares'] for t in last_buy_trades) / sum(t['shares'] for t in last_buy_trades)
                    profit = (execution_price - avg_buy_price) * shares_to_sell
            
            # ポートフォリオを更新
            self.cash += total_proceeds
            self.shares = 0
            
            # 取引履歴に記録
            trade = {
                'date': date.strftime('%Y-%m-%d'),
                'type': 'sell',
                'price': execution_price,
                'shares': shares_to_sell,
                'total_proceeds': total_proceeds,
                'commission': commission,
                'profit': profit,
                'cash_after': self.cash,
                'shares_after': self.shares
            }
            self.trades.append(trade)
            
            self.detailed_logger.log_event("DEBUG", "BACKTEST", "Sell order executed", trade)
            
        except Exception as e:
            self.detailed_logger.log_error("BACKTEST", e, f"Execute sell at {price}")
    
    def _update_portfolio_value(self, price: float, date: pd.Timestamp):
        """ポートフォリオ価値を更新"""
        try:
            # 現在のポートフォリオ価値を計算
            stock_value = self.shares * price
            self.portfolio_value = self.cash + stock_value
            
            # ポートフォリオ履歴に記録
            portfolio_entry = {
                'date': date.strftime('%Y-%m-%d'),
                'price': price,
                'cash': self.cash,
                'shares': self.shares,
                'stock_value': stock_value,
                'portfolio_value': self.portfolio_value
            }
            self.portfolio_history.append(portfolio_entry)
            
        except Exception as e:
            self.detailed_logger.log_error("BACKTEST", e, f"Update portfolio value at {price}")
    
    
    def _calculate_max_drawdown(self, values: List[float]) -> float:
        """最大ドローダウンを計算"""
        if not values:
            return 0
        
        peak = values[0]
        max_dd = 0
        
        for value in values:
            if value > peak:
                peak = value
            dd = (peak - value) / peak
            if dd > max_dd:
                max_dd = dd
        
        return max_dd
    
    def _save_backtest_results(self, strategy_name: str, results: Dict[str, Any]):
        """バックテスト結果を保存"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{strategy_name}_{timestamp}.json"
        filepath = self.results_dir / filename
        
        # 結果にメタデータを追加
        results["metadata"] = {
            "timestamp": datetime.now().isoformat(),
            "strategy": strategy_name,
            "ticker": self.ticker,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "initial_capital": self.initial_capital,
            "commission_rate": self.commission_rate,
            "slippage_rate": self.slippage_rate
        }
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        self.detailed_logger.log_event("INFO", "BACKTEST", f"Results saved: {filename}", {
            "strategy": strategy_name,
            "filepath": str(filepath)
        })
    
    def get_backtest_summary(self) -> Dict[str, Any]:
        """バックテスト結果のサマリーを取得"""
        summary = {
            "total_backtests": 0,
            "strategies": {},
            "latest_results": []
        }
        
        # 結果ファイルをスキャン
        for result_file in self.results_dir.glob("*.json"):
            try:
                with open(result_file, "r", encoding="utf-8") as f:
                    result = json.load(f)
                
                strategy = result.get("strategy", "unknown")
                summary["total_backtests"] += 1
                
                if strategy not in summary["strategies"]:
                    summary["strategies"][strategy] = 0
                summary["strategies"][strategy] += 1
                
                # 最新の結果を記録
                summary["latest_results"].append({
                    "file": result_file.name,
                    "strategy": strategy,
                    "total_return": result.get("total_return", 0),
                    "annual_return": result.get("annual_return", 0),
                    "max_drawdown": result.get("max_drawdown", 0),
                    "timestamp": result.get("metadata", {}).get("timestamp", "")
                })
                
            except Exception as e:
                self.detailed_logger.log_error("BACKTEST", e, f"Load result file {result_file}")
        
        # 最新の結果をソート
        summary["latest_results"].sort(key=lambda x: x["timestamp"], reverse=True)
        summary["latest_results"] = summary["latest_results"][:10]  # 最新10件
        
        return summary

if __name__ == "__main__":
    # テスト用の戦略クラス（サンプル）
    class SampleStrategy:
        def __init__(self):
            self.bought = False
        
        def generate_signal(self, price, volume, date, data):
            """サンプル戦略：単純な買い持ち戦略"""
            if not self.bought and len(data) > 20:  # 20日経過後に買い
                self.bought = True
                return 'buy'
            return 'hold'
    
    # テスト実行
    print("BacktestEngineのテストを実行中...")
    
    # 戦略とバックテストエンジンを初期化
    strategy = SampleStrategy()
    backtest = BacktestEngine(
        strategy=strategy,
        ticker="2559.T",  # 日経レバレッジETF
        start_date="2020-01-01",
        end_date="2023-12-31",
        initial_capital=1000000  # 100万円
    )
    
    # データを読み込み
    if backtest.load_data():
        print("データ読み込み成功")
        
        # バックテストを実行
        results = backtest.run()
        
        # 結果を表示
        print(f"\n=== バックテスト結果 ===")
        print(f"戦略: {results['strategy']}")
        print(f"銘柄: {results['ticker']}")
        print(f"期間: {results['start_date']} - {results['end_date']}")
        print(f"初期資金: ¥{results['initial_capital']:,}")
        print(f"最終資産: ¥{results['final_value']:,.0f}")
        print(f"総リターン: {results['total_return']:.2%}")
        print(f"年率リターン: {results['annual_return']:.2%}")
        print(f"最大ドローダウン: {results['max_drawdown']:.2%}")
        print(f"シャープレシオ: {results['sharpe_ratio']:.2f}")
        print(f"取引回数: {results['total_trades']}")
        print(f"勝率: {results['win_rate']:.2%}")
        
        # サマリーを表示
        summary = backtest.get_backtest_summary()
        print(f"\nバックテスト総数: {summary['total_backtests']}")
        print(f"戦略別: {summary['strategies']}")
    else:
        print("データ読み込みに失敗しました")
