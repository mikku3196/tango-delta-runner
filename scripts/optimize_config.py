#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Chimera 設定最適化スクリプト
個人のリスク許容度と投資目標に基づく設定の最適化
"""

import os
import sys
import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

class ConfigOptimizer:
    def __init__(self):
        self.config_file = Path("src/config/config.yaml")
        self.env_file = Path(".env")
        
    def load_current_config(self) -> Dict[str, Any]:
        """現在の設定を読み込み"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"設定ファイル読み込みエラー: {e}")
            return {}
    
    def save_config(self, config: Dict[str, Any]):
        """設定を保存"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            print("✅ 設定ファイルを保存しました")
            return True
        except Exception as e:
            print(f"設定ファイル保存エラー: {e}")
            return False
    
    def optimize_portfolio_ratios(self, risk_profile: str, investment_goal: str) -> Dict[str, float]:
        """ポートフォリオ比率を最適化"""
        print(f"📊 ポートフォリオ比率を最適化中... (リスク: {risk_profile}, 目標: {investment_goal})")
        
        # リスクプロファイルに基づく基本比率
        base_ratios = {
            "conservative": {"index": 0.80, "dividend": 0.15, "range": 0.05},
            "moderate": {"index": 0.60, "dividend": 0.25, "range": 0.15},
            "aggressive": {"index": 0.50, "dividend": 0.30, "range": 0.20}
        }
        
        # 投資目標に基づく調整
        goal_adjustments = {
            "capital_growth": {"index": 0.05, "dividend": -0.05, "range": 0.00},
            "income_focus": {"index": -0.05, "dividend": 0.10, "range": -0.05},
            "balanced": {"index": 0.00, "dividend": 0.00, "range": 0.00}
        }
        
        # 基本比率を取得
        base = base_ratios.get(risk_profile, base_ratios["moderate"])
        adjustment = goal_adjustments.get(investment_goal, goal_adjustments["balanced"])
        
        # 調整を適用
        optimized = {
            "index": max(0.3, min(0.8, base["index"] + adjustment["index"])),
            "dividend": max(0.1, min(0.4, base["dividend"] + adjustment["dividend"])),
            "range": max(0.05, min(0.3, base["range"] + adjustment["range"]))
        }
        
        # 合計を1.0に正規化
        total = sum(optimized.values())
        optimized = {k: v/total for k, v in optimized.items()}
        
        print(f"  最適化された比率: インデックス {optimized['index']:.1%}, 高配当 {optimized['dividend']:.1%}, レンジ {optimized['range']:.1%}")
        
        return optimized
    
    def optimize_bot_settings(self, monthly_investment: int, risk_profile: str) -> Dict[str, Any]:
        """Bot設定を最適化"""
        print(f"🤖 Bot設定を最適化中... (月次投資: {monthly_investment:,}円, リスク: {risk_profile})")
        
        # 月次投資額に基づく設定
        if monthly_investment < 50000:
            # 少額投資
            index_investment = int(monthly_investment * 0.7)
            dividend_investment = int(monthly_investment * 0.2)
            range_investment = int(monthly_investment * 0.1)
            max_holdings = 3
        elif monthly_investment < 100000:
            # 中額投資
            index_investment = int(monthly_investment * 0.6)
            dividend_investment = int(monthly_investment * 0.25)
            range_investment = int(monthly_investment * 0.15)
            max_holdings = 5
        else:
            # 高額投資
            index_investment = int(monthly_investment * 0.5)
            dividend_investment = int(monthly_investment * 0.3)
            range_investment = int(monthly_investment * 0.2)
            max_holdings = 7
        
        # リスクプロファイルに基づく調整
        if risk_profile == "conservative":
            max_holdings = min(max_holdings, 3)
        elif risk_profile == "aggressive":
            max_holdings = min(max_holdings + 2, 10)
        
        optimized = {
            "index_bot": {
                "monthly_investment": index_investment,
                "execution_day": 1,
                "execution_time": "09:30"
            },
            "dividend_bot": {
                "max_holding_stocks": max_holdings,
                "stop_loss_percentage": 0.15 if risk_profile == "conservative" else 0.20,
                "screening_day": 0,
                "screening_time": "22:00"
            },
            "range_bot": {
                "bollinger_period": 20,
                "bollinger_std_dev": 1.5 if risk_profile == "conservative" else 2.0,
                "stop_loss_percentage_on_break": 0.015 if risk_profile == "conservative" else 0.02,
                "max_position_size": min(range_investment, 100000)
            }
        }
        
        print(f"  最適化された設定:")
        print(f"    インデックス投資: {index_investment:,}円")
        print(f"    高配当株投資: {dividend_investment:,}円 (最大{max_holdings}銘柄)")
        print(f"    レンジ取引投資: {range_investment:,}円")
        
        return optimized
    
    def optimize_nisa_settings(self, annual_income: int, age: int) -> Dict[str, Any]:
        """NISA設定を最適化"""
        print(f"💰 NISA設定を最適化中... (年収: {annual_income:,}円, 年齢: {age}歳)")
        
        # 年収に基づく投資額の推奨
        if annual_income < 5000000:
            recommended_monthly = 20000
        elif annual_income < 8000000:
            recommended_monthly = 50000
        elif annual_income < 12000000:
            recommended_monthly = 100000
        else:
            recommended_monthly = 150000
        
        # 年齢に基づくリスク許容度の調整
        if age < 30:
            risk_multiplier = 1.2
        elif age < 50:
            risk_multiplier = 1.0
        else:
            risk_multiplier = 0.8
        
        # 年間投資額の計算
        annual_investment = recommended_monthly * 12
        
        # NISA枠の使用率計算
        nisa_usage_rate = annual_investment / 3600000  # 年間枠360万円
        
        optimized = {
            "nisa_settings": {
                "annual_limit": 3600000,
                "lifetime_limit": 18000000,
                "monitoring_enabled": True,
                "alert_threshold": 0.9 if nisa_usage_rate > 0.8 else 0.95,
                "report_frequency": "weekly" if nisa_usage_rate > 0.5 else "monthly"
            },
            "recommended_monthly_investment": recommended_monthly,
            "annual_investment": annual_investment,
            "nisa_usage_rate": nisa_usage_rate
        }
        
        print(f"  推奨月次投資額: {recommended_monthly:,}円")
        print(f"  年間投資額: {annual_investment:,}円")
        print(f"  NISA枠使用率: {nisa_usage_rate:.1%}")
        
        return optimized
    
    def optimize_notification_settings(self, user_preference: str) -> Dict[str, Any]:
        """通知設定を最適化"""
        print(f"📢 通知設定を最適化中... (設定: {user_preference})")
        
        if user_preference == "minimal":
            optimized = {
                "notifications": {
                    "trade_execution": False,
                    "portfolio_rebalance": True,
                    "nisa_limit_warning": True,
                    "system_errors": True,
                    "daily_summary": False,
                    "weekly_report": True,
                    "monthly_report": True
                }
            }
        elif user_preference == "detailed":
            optimized = {
                "notifications": {
                    "trade_execution": True,
                    "portfolio_rebalance": True,
                    "nisa_limit_warning": True,
                    "system_errors": True,
                    "daily_summary": True,
                    "weekly_report": True,
                    "monthly_report": True
                }
            }
        else:  # balanced
            optimized = {
                "notifications": {
                    "trade_execution": True,
                    "portfolio_rebalance": True,
                    "nisa_limit_warning": True,
                    "system_errors": True,
                    "daily_summary": False,
                    "weekly_report": True,
                    "monthly_report": True
                }
            }
        
        print(f"  通知設定: {user_preference}")
        
        return optimized
    
    def optimize_watchdog_settings(self, system_criticality: str) -> Dict[str, Any]:
        """Watchdog設定を最適化"""
        print(f"🐕 Watchdog設定を最適化中... (重要度: {system_criticality})")
        
        if system_criticality == "high":
            optimized = {
                "watchdog": {
                    "check_interval": 300,  # 5分
                    "max_restart_attempts": 5,
                    "restart_cooldown": 180,  # 3分
                    "heartbeat_interval": 43200,  # 12時間
                    "emergency_shutdown_enabled": True
                }
            }
        elif system_criticality == "low":
            optimized = {
                "watchdog": {
                    "check_interval": 1800,  # 30分
                    "max_restart_attempts": 2,
                    "restart_cooldown": 600,  # 10分
                    "heartbeat_interval": 172800,  # 48時間
                    "emergency_shutdown_enabled": True
                }
            }
        else:  # medium
            optimized = {
                "watchdog": {
                    "check_interval": 600,  # 10分
                    "max_restart_attempts": 3,
                    "restart_cooldown": 300,  # 5分
                    "heartbeat_interval": 86400,  # 24時間
                    "emergency_shutdown_enabled": True
                }
            }
        
        print(f"  Watchdog設定: {system_criticality}")
        
        return optimized
    
    def create_optimization_report(self, optimizations: Dict[str, Any]) -> Dict[str, Any]:
        """最適化レポートを作成"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "optimizations": optimizations,
            "summary": {
                "total_optimizations": len(optimizations),
                "categories": list(optimizations.keys())
            }
        }
        
        with open("config_optimization_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print("📋 最適化レポートを作成しました: config_optimization_report.json")
        
        return report

def main():
    """メイン関数"""
    print("=" * 60)
    print("⚙️ Project Chimera 設定最適化")
    print("=" * 60)
    
    optimizer = ConfigOptimizer()
    
    # 現在の設定を読み込み
    current_config = optimizer.load_current_config()
    if not current_config:
        print("❌ 設定ファイルの読み込みに失敗しました")
        return False
    
    # ユーザー入力の取得
    print("\n📝 設定最適化のための情報を入力してください")
    
    try:
        risk_profile = input("リスクプロファイル (conservative/moderate/aggressive): ").lower()
        if risk_profile not in ["conservative", "moderate", "aggressive"]:
            risk_profile = "moderate"
        
        investment_goal = input("投資目標 (capital_growth/income_focus/balanced): ").lower()
        if investment_goal not in ["capital_growth", "income_focus", "balanced"]:
            investment_goal = "balanced"
        
        monthly_investment = int(input("月次投資額 (円): ") or "50000")
        
        annual_income = int(input("年収 (円): ") or "6000000")
        
        age = int(input("年齢: ") or "35")
        
        user_preference = input("通知設定 (minimal/balanced/detailed): ").lower()
        if user_preference not in ["minimal", "balanced", "detailed"]:
            user_preference = "balanced"
        
        system_criticality = input("システム重要度 (low/medium/high): ").lower()
        if system_criticality not in ["low", "medium", "high"]:
            system_criticality = "medium"
        
    except (ValueError, KeyboardInterrupt):
        print("\n❌ 入力が中断されました")
        return False
    
    # 最適化の実行
    optimizations = {}
    
    # ポートフォリオ比率の最適化
    portfolio_ratios = optimizer.optimize_portfolio_ratios(risk_profile, investment_goal)
    optimizations["portfolio_ratios"] = portfolio_ratios
    
    # Bot設定の最適化
    bot_settings = optimizer.optimize_bot_settings(monthly_investment, risk_profile)
    optimizations.update(bot_settings)
    
    # NISA設定の最適化
    nisa_settings = optimizer.optimize_nisa_settings(annual_income, age)
    optimizations.update(nisa_settings)
    
    # 通知設定の最適化
    notification_settings = optimizer.optimize_notification_settings(user_preference)
    optimizations.update(notification_settings)
    
    # Watchdog設定の最適化
    watchdog_settings = optimizer.optimize_watchdog_settings(system_criticality)
    optimizations.update(watchdog_settings)
    
    # 設定ファイルの更新
    print("\n💾 設定ファイルを更新中...")
    
    # 最適化された設定を現在の設定にマージ
    for key, value in optimizations.items():
        if key in current_config:
            if isinstance(value, dict) and isinstance(current_config[key], dict):
                current_config[key].update(value)
            else:
                current_config[key] = value
        else:
            current_config[key] = value
    
    # 設定ファイルを保存
    if optimizer.save_config(current_config):
        print("✅ 設定ファイルが更新されました")
    else:
        print("❌ 設定ファイルの更新に失敗しました")
        return False
    
    # 最適化レポートの作成
    report = optimizer.create_optimization_report(optimizations)
    
    print("\n" + "=" * 60)
    print("📊 最適化結果サマリー")
    print("=" * 60)
    
    print(f"リスクプロファイル: {risk_profile}")
    print(f"投資目標: {investment_goal}")
    print(f"月次投資額: {monthly_investment:,}円")
    print(f"年収: {annual_income:,}円")
    print(f"年齢: {age}歳")
    print(f"通知設定: {user_preference}")
    print(f"システム重要度: {system_criticality}")
    
    print("\n最適化された設定:")
    for category, settings in optimizations.items():
        print(f"  {category}: {settings}")
    
    print("\n🎉 設定最適化が完了しました！")
    print("\n次のステップ:")
    print("1. 最適化された設定を確認")
    print("2. 必要に応じて手動で調整")
    print("3. システムを再起動")
    print("4. 新しい設定でテスト実行")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
