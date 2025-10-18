#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
リスク許容度診断モジュール
"""

import json
from typing import Dict, List, Tuple
from src.shared_modules.config_loader import ConfigLoader

class RiskAssessor:
    def __init__(self, config_loader: ConfigLoader):
        self.config = config_loader
        self.risk_profiles = self.config.get("risk_assessment.profiles", {})
    
    def conduct_risk_assessment(self) -> str:
        """リスク許容度診断を実行し、�Eロファイルを返す"""
        print("リスク許容度診断を開始しまぁE..")
        
        # 診断質啁E        questions = self._get_risk_questions()
        answers = []
        
        print("\\n=== リスク許容度診断 ===")
        print("吁E��問に1-5の数字で回答してください�E�E: 最も低い、E: 最も高い�E�E)
        
        for i, question in enumerate(questions, 1):
            print(f"\\n質問{i}: {question['question']}")
            print(f"選択肢: {question['options']}")
            
            while True:
                try:
                    answer = int(input("回筁E(1-5): "))
                    if 1 <= answer <= 5:
                        answers.append(answer)
                        break
                    else:
                        print("1-5の数字で入力してください")
                except ValueError:
                    print("数字で入力してください")
        
        # スコア計箁E        total_score = sum(answers)
        risk_profile = self._calculate_risk_profile(total_score)
        
        print(f"\\n診断結果: {risk_profile}")
        print(f"総スコア: {total_score}/25")
        
        return risk_profile
    
    def _get_risk_questions(self) -> List[Dict]:
        """リスク診断質問を取征E""
        return [
            {
                "question": "投賁E��間�Eどの程度を想定してぁE��すか�E�E,
                "options": "1: 1年未満, 2: 1-3年, 3: 3-5年, 4: 5-10年, 5: 10年以丁E
            },
            {
                "question": "投賁E�E本の損失に対する許容度は�E�E,
                "options": "1: 5%未満, 2: 5-10%, 3: 10-20%, 4: 20-30%, 5: 30%以丁E
            },
            {
                "question": "投賁E�E目皁E�E�E�E,
                "options": "1: 允E��保�E, 2: 安定収盁E 3: バランス, 4: 成長重要E 5: 積極皁E�E長"
            },
            {
                "question": "市場の変動に対する反応�E�E�E,
                "options": "1: 非常に不宁E 2: 不宁E 3: 普送E 4: 冷靁E 5: 機会と捉えめE
            },
            {
                "question": "投賁E��験�E�E�E,
                "options": "1: 初忁E��E 2: 少し経騁E 3: 中程度, 4: 経験豊寁E 5: 専門家レベル"
            }
        ]
    
    def _calculate_risk_profile(self, total_score: int) -> str:
        """総スコアからリスクプロファイルを決宁E""
        if total_score <= 10:
            return "stable"
        elif total_score <= 18:
            return "balanced"
        else:
            return "aggressive"
    
    def get_portfolio_ratios(self, profile: str) -> Dict[str, float]:
        """持E��されたプロファイルのポ�Eトフォリオ比率を取征E""
        if profile not in self.risk_profiles:
            print(f"警呁E プロファイル '{profile}' が見つかりません。デフォルトを使用します、E)
            profile = self.config.get("risk_assessment.default_profile", "aggressive")
        
        return self.risk_profiles.get(profile, self.risk_profiles["aggressive"])
    
    def update_config_with_profile(self, profile: str) -> bool:
        """設定ファイルを指定されたプロファイルで更新"""
        try:
            ratios = self.get_portfolio_ratios(profile)
            
            # 設定を更新
            self.config.config["portfolio_ratios"] = ratios
            
            print(f"ポ�Eトフォリオ比率を更新しました:")
            print(f"  インチE��クス: {ratios['index']:.1%}")
            print(f"  高�E彁E {ratios['dividend']:.1%}")
            print(f"  レンジ: {ratios['range']:.1%}")
            
            return True
            
        except Exception as e:
            print(f"設定更新エラー: {e}")
            return False
    
    def save_assessment_result(self, profile: str, answers: List[int], total_score: int):
        """診断結果をファイルに保孁E""
        try:
            result = {
                "profile": profile,
                "total_score": total_score,
                "answers": answers,
                "ratios": self.get_portfolio_ratios(profile),
                "timestamp": json.dumps({"": {"": str(int(__import__('time').time() * 1000))}})
            }
            
            with open("risk_assessment_result.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print("診断結果めErisk_assessment_result.json に保存しました")
            
        except Exception as e:
            print(f"結果保存エラー: {e}")
    
    def load_assessment_result(self) -> Dict:
        """保存された診断結果を読み込み"""
        try:
            with open("risk_assessment_result.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print("診断結果ファイルが見つかりません")
            return {}
        except Exception as e:
            print(f"結果読み込みエラー: {e}")
            return {}
    
    def get_profile_description(self, profile: str) -> str:
        """プロファイルの説明を取征E""
        descriptions = {
            "stable": "安定型: リスクを最小限に抑え、安定した賁E��形成を重要E,
            "balanced": "バランス垁E リスクとリターンのバランスを重要E,
            "aggressive": "積極垁E 高いリターンを狙ぁE��リスクを許容"
        }
        return descriptions.get(profile, "不�Eなプロファイル")
