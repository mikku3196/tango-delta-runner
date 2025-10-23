#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Chimera バックテスト結果分析ツール
バックテスト結果の可視化と分析
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Any
import argparse

class BacktestAnalyzer:
    def __init__(self, results_dir: str = "logs/backtest_results"):
        """
        バックテスト分析ツールの初期化
        
        Args:
            results_dir: 結果ディレクトリ
        """
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # 日本語フォントの設定
        plt.rcParams['font.family'] = 'DejaVu Sans'
        sns.set_style("whitegrid")
    
    def load_results(self, strategy: str = None) -> List[Dict[str, Any]]:
        """
        バックテスト結果を読み込み
        
        Args:
            strategy: 戦略名（Noneの場合は全て）
            
        Returns:
            結果のリスト
        """
        results = []
        
        for result_file in self.results_dir.glob("*.json"):
            try:
                with open(result_file, "r", encoding="utf-8") as f:
                    result = json.load(f)
                
                if strategy is None or result.get("strategy") == strategy:
                    results.append(result)
                    
            except Exception as e:
                print(f"結果ファイル読み込みエラー {result_file}: {e}")
        
        return results
    
    def analyze_performance(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        パフォーマンス分析
        
        Args:
            results: バックテスト結果のリスト
            
        Returns:
            分析結果
        """
        if not results:
            return {}
        
        # 基本統計
        total_returns = [r.get("total_return", 0) for r in results]
        annual_returns = [r.get("annual_return", 0) for r in results]
        max_drawdowns = [r.get("max_drawdown", 0) for r in results]
        
        analysis = {
            "count": len(results),
            "total_return": {
                "mean": sum(total_returns) / len(total_returns),
                "min": min(total_returns),
                "max": max(total_returns),
                "std": pd.Series(total_returns).std()
            },
            "annual_return": {
                "mean": sum(annual_returns) / len(annual_returns),
                "min": min(annual_returns),
                "max": max(annual_returns),
                "std": pd.Series(annual_returns).std()
            },
            "max_drawdown": {
                "mean": sum(max_drawdowns) / len(max_drawdowns),
                "min": min(max_drawdowns),
                "max": max(max_drawdowns),
                "std": pd.Series(max_drawdowns).std()
            }
        }
        
        return analysis
    
    def plot_performance_comparison(self, results: List[Dict[str, Any]], save_path: str = None):
        """
        パフォーマンス比較グラフを作成
        
        Args:
            results: バックテスト結果のリスト
            save_path: 保存パス
        """
        if not results:
            print("結果がありません")
            return
        
        # データを整理
        strategies = []
        total_returns = []
        annual_returns = []
        max_drawdowns = []
        
        for result in results:
            strategies.append(result.get("strategy", "unknown"))
            total_returns.append(result.get("total_return", 0))
            annual_returns.append(result.get("annual_return", 0))
            max_drawdowns.append(result.get("max_drawdown", 0))
        
        # グラフを作成
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle("Project Chimera バックテスト結果分析", fontsize=16)
        
        # 総リターン
        axes[0, 0].bar(strategies, total_returns)
        axes[0, 0].set_title("総リターン")
        axes[0, 0].set_ylabel("リターン")
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # 年率リターン
        axes[0, 1].bar(strategies, annual_returns)
        axes[0, 1].set_title("年率リターン")
        axes[0, 1].set_ylabel("リターン")
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # 最大ドローダウン
        axes[1, 0].bar(strategies, max_drawdowns)
        axes[1, 0].set_title("最大ドローダウン")
        axes[1, 0].set_ylabel("ドローダウン")
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # リスクリターン散布図
        axes[1, 1].scatter(max_drawdowns, annual_returns, s=100, alpha=0.7)
        axes[1, 1].set_title("リスク・リターン散布図")
        axes[1, 1].set_xlabel("最大ドローダウン")
        axes[1, 1].set_ylabel("年率リターン")
        
        # 戦略名をプロット
        for i, strategy in enumerate(strategies):
            axes[1, 1].annotate(strategy, (max_drawdowns[i], annual_returns[i]))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"グラフを保存しました: {save_path}")
        
        plt.show()
    
    def plot_portfolio_evolution(self, result: Dict[str, Any], save_path: str = None):
        """
        ポートフォリオの進化をプロット
        
        Args:
            result: バックテスト結果
            save_path: 保存パス
        """
        if "portfolio_values" not in result or "dates" not in result:
            print("ポートフォリオ進化データがありません")
            return
        
        portfolio_values = result["portfolio_values"]
        dates = result["dates"]
        
        if not portfolio_values or not dates:
            print("データが空です")
            return
        
        # 日付を変換
        date_objects = pd.to_datetime(dates)
        
        # グラフを作成
        plt.figure(figsize=(12, 6))
        plt.plot(date_objects, portfolio_values, linewidth=2)
        plt.title(f"{result.get('strategy', 'Unknown')} 戦略 - ポートフォリオ進化")
        plt.xlabel("日付")
        plt.ylabel("ポートフォリオ価値")
        plt.grid(True, alpha=0.3)
        
        # 投資額の累積をプロット
        if "total_invested" in result:
            total_invested = result["total_invested"]
            plt.axhline(y=total_invested, color='red', linestyle='--', 
                       label=f'累積投資額: {total_invested:,.0f}円')
            plt.legend()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"ポートフォリオ進化グラフを保存しました: {save_path}")
        
        plt.show()
    
    def generate_report(self, strategy: str = None, output_file: str = None):
        """
        分析レポートを生成
        
        Args:
            strategy: 戦略名
            output_file: 出力ファイル
        """
        results = self.load_results(strategy)
        
        if not results:
            print("結果が見つかりません")
            return
        
        # 分析実行
        analysis = self.analyze_performance(results)
        
        # レポート生成
        report = []
        report.append("=" * 60)
        report.append("Project Chimera バックテスト分析レポート")
        report.append("=" * 60)
        report.append(f"分析日時: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"対象戦略: {strategy if strategy else '全戦略'}")
        report.append(f"結果数: {analysis.get('count', 0)}")
        report.append("")
        
        # パフォーマンス統計
        report.append("📊 パフォーマンス統計")
        report.append("-" * 30)
        
        for metric, stats in analysis.items():
            if metric == "count":
                continue
            
            report.append(f"{metric.upper()}:")
            report.append(f"  平均: {stats['mean']:.2%}")
            report.append(f"  最小: {stats['min']:.2%}")
            report.append(f"  最大: {stats['max']:.2%}")
            report.append(f"  標準偏差: {stats['std']:.2%}")
            report.append("")
        
        # 個別結果
        report.append("📋 個別結果")
        report.append("-" * 30)
        
        for i, result in enumerate(results[:10]):  # 最新10件
            report.append(f"{i+1}. {result.get('strategy', 'Unknown')}戦略")
            report.append(f"   総リターン: {result.get('total_return', 0):.2%}")
            report.append(f"   年率リターン: {result.get('annual_return', 0):.2%}")
            report.append(f"   最大ドローダウン: {result.get('max_drawdown', 0):.2%}")
            
            if "metadata" in result:
                timestamp = result["metadata"].get("timestamp", "")
                if timestamp:
                    report.append(f"   実行日時: {timestamp}")
            report.append("")
        
        # レポート出力
        report_text = "\n".join(report)
        print(report_text)
        
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(report_text)
            print(f"レポートを保存しました: {output_file}")

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description="Project Chimera バックテスト分析")
    parser.add_argument("--strategy", help="分析する戦略")
    parser.add_argument("--plot", action="store_true", help="グラフを表示")
    parser.add_argument("--portfolio-evolution", help="ポートフォリオ進化をプロット（結果ファイル名）")
    parser.add_argument("--report", help="レポートを生成（出力ファイル名）")
    parser.add_argument("--save-plot", help="グラフを保存（ファイル名）")
    
    args = parser.parse_args()
    
    analyzer = BacktestAnalyzer()
    
    if args.portfolio_evolution:
        # ポートフォリオ進化をプロット
        results = analyzer.load_results()
        for result in results:
            if result.get("strategy") == args.portfolio_evolution:
                analyzer.plot_portfolio_evolution(result, args.save_plot)
                break
        else:
            print(f"戦略 '{args.portfolio_evolution}' の結果が見つかりません")
    
    elif args.plot:
        # パフォーマンス比較グラフ
        results = analyzer.load_results(args.strategy)
        analyzer.plot_performance_comparison(results, args.save_plot)
    
    elif args.report:
        # レポート生成
        analyzer.generate_report(args.strategy, args.report)
    
    else:
        # デフォルト: レポート生成
        analyzer.generate_report(args.strategy)

if __name__ == "__main__":
    main()
