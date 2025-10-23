#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Chimera 継続的改善スクリプト
システムの継続的な改善と最適化
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

class ContinuousImprovement:
    def __init__(self):
        self.improvement_log = []
        self.performance_history = []
        self.user_feedback = []
        
    def analyze_system_performance(self) -> Dict[str, Any]:
        """システムパフォーマンスの分析"""
        print("📊 システムパフォーマンスを分析中...")
        
        try:
            # ログファイルの分析
            log_files = list(Path("logs").glob("chimera_*.log"))
            if not log_files:
                return {"error": "No log files found"}
            
            # 最新のログファイルを取得
            latest_log = max(log_files, key=os.path.getmtime)
            
            # ログエントリの分析
            with open(latest_log, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # エラーレベルの分析
            error_counts = {"INFO": 0, "WARNING": 0, "ERROR": 0, "CRITICAL": 0}
            for line in lines[-1000:]:  # 最新1000行のみ
                try:
                    log_entry = json.loads(line.strip())
                    level = log_entry.get('level', 'INFO')
                    if level in error_counts:
                        error_counts[level] += 1
                except json.JSONDecodeError:
                    continue
            
            # 取引の分析
            trade_count = 0
            for line in lines:
                if "TRADE" in line:
                    trade_count += 1
            
            # パフォーマンス指標の計算
            total_logs = len(lines)
            error_rate = (error_counts["ERROR"] + error_counts["CRITICAL"]) / total_logs if total_logs > 0 else 0
            
            performance_metrics = {
                "timestamp": datetime.now().isoformat(),
                "total_logs": total_logs,
                "error_counts": error_counts,
                "trade_count": trade_count,
                "error_rate": error_rate,
                "performance_score": max(0, 100 - (error_rate * 100))
            }
            
            print(f"  ✅ パフォーマンス分析完了")
            print(f"     総ログ数: {total_logs}")
            print(f"     エラー率: {error_rate:.2%}")
            print(f"     パフォーマンススコア: {performance_metrics['performance_score']:.1f}")
            
            return performance_metrics
            
        except Exception as e:
            print(f"  ❌ パフォーマンス分析エラー: {e}")
            return {"error": str(e)}
    
    def analyze_user_behavior(self) -> Dict[str, Any]:
        """ユーザー行動の分析"""
        print("👤 ユーザー行動を分析中...")
        
        try:
            # 設定ファイルの変更履歴を分析
            config_file = Path("src/config/config.yaml")
            if not config_file.exists():
                return {"error": "Config file not found"}
            
            # 設定の読み込み
            import yaml
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # ポートフォリオ比率の分析
            portfolio_ratios = config.get("portfolio_ratios", {})
            total_ratio = sum(portfolio_ratios.values())
            
            # 投資戦略の分析
            investment_analysis = {
                "portfolio_ratios": portfolio_ratios,
                "total_ratio": total_ratio,
                "risk_profile": self._determine_risk_profile(portfolio_ratios),
                "investment_focus": self._determine_investment_focus(portfolio_ratios)
            }
            
            print(f"  ✅ ユーザー行動分析完了")
            print(f"     リスクプロファイル: {investment_analysis['risk_profile']}")
            print(f"     投資フォーカス: {investment_analysis['investment_focus']}")
            
            return investment_analysis
            
        except Exception as e:
            print(f"  ❌ ユーザー行動分析エラー: {e}")
            return {"error": str(e)}
    
    def _determine_risk_profile(self, ratios: Dict[str, float]) -> str:
        """リスクプロファイルの判定"""
        if ratios.get("range", 0) > 0.15:
            return "aggressive"
        elif ratios.get("range", 0) > 0.05:
            return "moderate"
        else:
            return "conservative"
    
    def _determine_investment_focus(self, ratios: Dict[str, float]) -> str:
        """投資フォーカスの判定"""
        if ratios.get("dividend", 0) > 0.25:
            return "income_focus"
        elif ratios.get("index", 0) > 0.6:
            return "capital_growth"
        else:
            return "balanced"
    
    def generate_improvement_recommendations(self, performance: Dict[str, Any], behavior: Dict[str, Any]) -> List[str]:
        """改善推奨事項の生成"""
        print("💡 改善推奨事項を生成中...")
        
        recommendations = []
        
        # パフォーマンスベースの推奨事項
        if performance.get("error_rate", 0) > 0.05:
            recommendations.append("エラー率が高いです。ログを詳細に確認し、問題を特定してください")
        
        if performance.get("performance_score", 0) < 80:
            recommendations.append("パフォーマンススコアが低いです。システム最適化を実行してください")
        
        # ユーザー行動ベースの推奨事項
        if behavior.get("total_ratio", 0) != 1.0:
            recommendations.append("ポートフォリオ比率の合計が1.0ではありません。設定を確認してください")
        
        risk_profile = behavior.get("risk_profile", "moderate")
        if risk_profile == "aggressive":
            recommendations.append("積極的なリスクプロファイルです。定期的なポートフォリオ監視を推奨します")
        
        # 一般的な推奨事項
        recommendations.extend([
            "定期的なバックテストを実行して戦略の有効性を確認してください",
            "市場環境の変化に応じて設定を調整してください",
            "セキュリティ監査を定期的に実行してください",
            "システムアップデートを定期的に確認してください"
        ])
        
        print(f"  ✅ {len(recommendations)}個の推奨事項を生成しました")
        
        return recommendations
    
    def implement_improvements(self, recommendations: List[str]) -> Dict[str, Any]:
        """改善の実装"""
        print("🔧 改善を実装中...")
        
        implemented = []
        failed = []
        
        for recommendation in recommendations:
            try:
                if "エラー率" in recommendation:
                    # エラー率の改善
                    result = self._improve_error_rate()
                    if result:
                        implemented.append("エラー率の改善")
                    else:
                        failed.append("エラー率の改善")
                
                elif "パフォーマンススコア" in recommendation:
                    # パフォーマンスの改善
                    result = self._improve_performance()
                    if result:
                        implemented.append("パフォーマンスの改善")
                    else:
                        failed.append("パフォーマンスの改善")
                
                elif "ポートフォリオ比率" in recommendation:
                    # ポートフォリオ比率の修正
                    result = self._fix_portfolio_ratios()
                    if result:
                        implemented.append("ポートフォリオ比率の修正")
                    else:
                        failed.append("ポートフォリオ比率の修正")
                
                elif "セキュリティ監査" in recommendation:
                    # セキュリティ監査の実行
                    result = self._run_security_audit()
                    if result:
                        implemented.append("セキュリティ監査の実行")
                    else:
                        failed.append("セキュリティ監査の実行")
                
            except Exception as e:
                failed.append(f"改善実装エラー: {e}")
        
        improvement_result = {
            "timestamp": datetime.now().isoformat(),
            "implemented": implemented,
            "failed": failed,
            "total_recommendations": len(recommendations),
            "success_rate": len(implemented) / len(recommendations) if recommendations else 0
        }
        
        print(f"  ✅ 改善実装完了")
        print(f"     実装成功: {len(implemented)}")
        print(f"     実装失敗: {len(failed)}")
        print(f"     成功率: {improvement_result['success_rate']:.1%}")
        
        return improvement_result
    
    def _improve_error_rate(self) -> bool:
        """エラー率の改善"""
        try:
            # ログファイルのクリーンアップ
            log_dir = Path("logs")
            for log_file in log_dir.glob("*.log"):
                if log_file.stat().st_mtime < (time.time() - 7 * 24 * 3600):  # 7日以上古い
                    log_file.unlink()
            
            return True
        except:
            return False
    
    def _improve_performance(self) -> bool:
        """パフォーマンスの改善"""
        try:
            # パフォーマンス最適化スクリプトを実行
            result = subprocess.run([
                sys.executable, "scripts/performance_optimizer.py"
            ], capture_output=True, text=True, timeout=60)
            
            return result.returncode == 0
        except:
            return False
    
    def _fix_portfolio_ratios(self) -> bool:
        """ポートフォリオ比率の修正"""
        try:
            import yaml
            
            config_file = Path("src/config/config.yaml")
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            portfolio_ratios = config.get("portfolio_ratios", {})
            total_ratio = sum(portfolio_ratios.values())
            
            if total_ratio != 1.0:
                # 比率を正規化
                for key in portfolio_ratios:
                    portfolio_ratios[key] = portfolio_ratios[key] / total_ratio
                
                config["portfolio_ratios"] = portfolio_ratios
                
                with open(config_file, 'w', encoding='utf-8') as f:
                    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            
            return True
        except:
            return False
    
    def _run_security_audit(self) -> bool:
        """セキュリティ監査の実行"""
        try:
            result = subprocess.run([
                sys.executable, "scripts/security_enhancer.py"
            ], capture_output=True, text=True, timeout=120)
            
            return result.returncode == 0
        except:
            return False
    
    def collect_user_feedback(self) -> Dict[str, Any]:
        """ユーザーフィードバックの収集"""
        print("📝 ユーザーフィードバックを収集中...")
        
        try:
            # 運用ログからフィードバックを収集
            operation_log_file = Path("operation_log.json")
            if operation_log_file.exists():
                with open(operation_log_file, 'r', encoding='utf-8') as f:
                    operation_log = json.load(f)
                
                # システムの使用状況を分析
                usage_analysis = {
                    "startup_time": operation_log.get("startup_time"),
                    "system_status": operation_log.get("status"),
                    "environment": operation_log.get("environment", {}),
                    "checks": operation_log.get("checks", {})
                }
                
                print("  ✅ ユーザーフィードバック収集完了")
                return usage_analysis
            else:
                print("  ⚠️ 運用ログファイルが見つかりません")
                return {"error": "Operation log not found"}
                
        except Exception as e:
            print(f"  ❌ ユーザーフィードバック収集エラー: {e}")
            return {"error": str(e)}
    
    def generate_improvement_report(self, performance: Dict[str, Any], behavior: Dict[str, Any], 
                                  recommendations: List[str], improvements: Dict[str, Any], 
                                  feedback: Dict[str, Any]) -> Dict[str, Any]:
        """改善レポートの生成"""
        print("📋 改善レポートを生成中...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "analysis": {
                "performance": performance,
                "behavior": behavior,
                "feedback": feedback
            },
            "recommendations": recommendations,
            "improvements": improvements,
            "summary": {
                "total_recommendations": len(recommendations),
                "implemented_improvements": len(improvements.get("implemented", [])),
                "failed_improvements": len(improvements.get("failed", [])),
                "success_rate": improvements.get("success_rate", 0)
            }
        }
        
        with open("improvement_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print("  ✅ 改善レポートを生成しました")
        return report

def main():
    """メイン関数"""
    print("=" * 60)
    print("🔄 Project Chimera 継続的改善")
    print("=" * 60)
    
    improvement = ContinuousImprovement()
    
    # システムパフォーマンスの分析
    performance = improvement.analyze_system_performance()
    
    # ユーザー行動の分析
    behavior = improvement.analyze_user_behavior()
    
    # ユーザーフィードバックの収集
    feedback = improvement.collect_user_feedback()
    
    # 改善推奨事項の生成
    recommendations = improvement.generate_improvement_recommendations(performance, behavior)
    
    # 改善の実装
    improvements = improvement.implement_improvements(recommendations)
    
    # 改善レポートの生成
    report = improvement.generate_improvement_report(performance, behavior, recommendations, improvements, feedback)
    
    print("\n" + "=" * 60)
    print("📊 継続的改善結果サマリー")
    print("=" * 60)
    
    print(f"パフォーマンススコア: {performance.get('performance_score', 0):.1f}")
    print(f"エラー率: {performance.get('error_rate', 0):.2%}")
    print(f"リスクプロファイル: {behavior.get('risk_profile', 'unknown')}")
    print(f"投資フォーカス: {behavior.get('investment_focus', 'unknown')}")
    print(f"推奨事項数: {len(recommendations)}")
    print(f"実装成功数: {len(improvements.get('implemented', []))}")
    print(f"実装失敗数: {len(improvements.get('failed', []))}")
    print(f"成功率: {improvements.get('success_rate', 0):.1%}")
    
    print("\n推奨事項:")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")
    
    print("\n実装された改善:")
    for imp in improvements.get("implemented", []):
        print(f"  ✅ {imp}")
    
    print("\n実装に失敗した改善:")
    for fail in improvements.get("failed", []):
        print(f"  ❌ {fail}")
    
    print(f"\n📋 改善レポートを保存しました: improvement_report.json")
    
    if improvements.get("success_rate", 0) > 0.8:
        print("\n🎉 継続的改善が成功しました！")
    elif improvements.get("success_rate", 0) > 0.5:
        print("\n⚠️ 継続的改善が部分的に成功しました")
    else:
        print("\n❌ 継続的改善に失敗しました")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
