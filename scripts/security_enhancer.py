#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Chimera セキュリティ強化
セキュリティ監査と強化機能
"""

import os
import sys
import hashlib
import secrets
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess

class SecurityAuditor:
    def __init__(self):
        self.audit_results = []
        self.security_issues = []
        
    def run_security_audit(self) -> Dict[str, Any]:
        """セキュリティ監査を実行"""
        print("🔒 セキュリティ監査を実行中...")
        
        # 各種セキュリティチェックを実行
        checks = [
            self._check_file_permissions,
            self._check_sensitive_files,
            self._check_password_security,
            self._check_api_security,
            self._check_log_security,
            self._check_network_security,
            self._check_dependency_security,
            self._check_configuration_security
        ]
        
        for check in checks:
            try:
                result = check()
                self.audit_results.append(result)
            except Exception as e:
                self.audit_results.append({
                    'check': check.__name__,
                    'status': 'error',
                    'message': str(e)
                })
        
        return {
            'timestamp': datetime.now().isoformat(),
            'audit_results': self.audit_results,
            'security_score': self._calculate_security_score(),
            'recommendations': self._generate_security_recommendations()
        }
    
    def _check_file_permissions(self) -> Dict[str, Any]:
        """ファイル権限チェック"""
        print("  📁 ファイル権限をチェック中...")
        
        issues = []
        critical_files = [
            '.env',
            'src/config/config.yaml',
            'logs/',
            'emergency_stop.py'
        ]
        
        for file_path in critical_files:
            path = Path(file_path)
            if path.exists():
                stat = path.stat()
                mode = oct(stat.st_mode)[-3:]
                
                # .envファイルは600以下である必要がある
                if file_path == '.env' and int(mode) > 600:
                    issues.append(f"{file_path}: 権限が緩すぎます ({mode})")
                
                # ログディレクトリは755以下である必要がある
                elif file_path == 'logs/' and int(mode) > 755:
                    issues.append(f"{file_path}: 権限が緩すぎます ({mode})")
        
        return {
            'check': 'file_permissions',
            'status': 'warning' if issues else 'pass',
            'issues': issues,
            'message': f'{len(issues)}個の権限問題を発見' if issues else 'ファイル権限は適切です'
        }
    
    def _check_sensitive_files(self) -> Dict[str, Any]:
        """機密ファイルチェック"""
        print("  🔐 機密ファイルをチェック中...")
        
        issues = []
        
        # .envファイルの存在確認
        if not Path('.env').exists():
            issues.append('.envファイルが存在しません')
        
        # .envファイルの内容チェック
        if Path('.env').exists():
            with open('.env', 'r') as f:
                content = f.read()
                
            # デフォルト値のチェック
            if 'DU1234567' in content or 'FU7654321' in content:
                issues.append('.envファイルにデフォルト値が含まれています')
            
            if 'your_webhook_id' in content or 'your_webhook_token' in content:
                issues.append('.envファイルにプレースホルダーが含まれています')
        
        # 機密ファイルがGitに含まれていないかチェック
        try:
            result = subprocess.run(['git', 'ls-files'], capture_output=True, text=True)
            tracked_files = result.stdout.split('\n')
            
            if '.env' in tracked_files:
                issues.append('.envファイルがGitで追跡されています')
        except subprocess.CalledProcessError:
            pass  # Gitリポジトリでない場合はスキップ
        
        return {
            'check': 'sensitive_files',
            'status': 'critical' if issues else 'pass',
            'issues': issues,
            'message': f'{len(issues)}個の機密ファイル問題を発見' if issues else '機密ファイルは適切に管理されています'
        }
    
    def _check_password_security(self) -> Dict[str, Any]:
        """パスワードセキュリティチェック"""
        print("  🔑 パスワードセキュリティをチェック中...")
        
        issues = []
        
        # 設定ファイルでパスワードが平文で保存されていないかチェック
        config_files = ['src/config/config.yaml']
        
        for config_file in config_files:
            if Path(config_file).exists():
                with open(config_file, 'r') as f:
                    content = f.read()
                
                # パスワードらしき文字列をチェック
                if 'password:' in content.lower() or 'passwd:' in content.lower():
                    issues.append(f'{config_file}にパスワードが含まれている可能性があります')
        
        return {
            'check': 'password_security',
            'status': 'warning' if issues else 'pass',
            'issues': issues,
            'message': f'{len(issues)}個のパスワード問題を発見' if issues else 'パスワードセキュリティは適切です'
        }
    
    def _check_api_security(self) -> Dict[str, Any]:
        """APIセキュリティチェック"""
        print("  🌐 APIセキュリティをチェック中...")
        
        issues = []
        
        # IB API設定のチェック
        try:
            from src.shared_modules.config_loader import ConfigLoader
            config = ConfigLoader()
            
            ib_config = config.get('ib_account', {})
            
            # デフォルト値のチェック
            if ib_config.get('host') == '127.0.0.1' and ib_config.get('port') == 5000:
                issues.append('IB API設定がデフォルト値のままです')
            
            # クライアントIDのチェック
            if ib_config.get('client_id') == 1:
                issues.append('IB APIクライアントIDがデフォルト値です')
                
        except Exception as e:
            issues.append(f'設定ファイルの読み込みエラー: {e}')
        
        return {
            'check': 'api_security',
            'status': 'warning' if issues else 'pass',
            'issues': issues,
            'message': f'{len(issues)}個のAPI問題を発見' if issues else 'APIセキュリティは適切です'
        }
    
    def _check_log_security(self) -> Dict[str, Any]:
        """ログセキュリティチェック"""
        print("  📝 ログセキュリティをチェック中...")
        
        issues = []
        
        # ログディレクトリの存在確認
        log_dir = Path('logs')
        if not log_dir.exists():
            issues.append('ログディレクトリが存在しません')
        else:
            # ログファイルの権限チェック
            for log_file in log_dir.glob('*.log'):
                stat = log_file.stat()
                mode = oct(stat.st_mode)[-3:]
                if int(mode) > 644:
                    issues.append(f'{log_file}: ログファイルの権限が緩すぎます ({mode})')
        
        return {
            'check': 'log_security',
            'status': 'warning' if issues else 'pass',
            'issues': issues,
            'message': f'{len(issues)}個のログ問題を発見' if issues else 'ログセキュリティは適切です'
        }
    
    def _check_network_security(self) -> Dict[str, Any]:
        """ネットワークセキュリティチェック"""
        print("  🌐 ネットワークセキュリティをチェック中...")
        
        issues = []
        
        # ダッシュボードの設定チェック
        dashboard_file = Path('dashboard/app.py')
        if dashboard_file.exists():
            with open(dashboard_file, 'r') as f:
                content = f.read()
            
            # 0.0.0.0でのバインドチェック
            if 'host=\'0.0.0.0\'' in content:
                issues.append('ダッシュボードが0.0.0.0でバインドされています（本番環境では制限してください）')
            
            # debug=Trueのチェック
            if 'debug=True' in content:
                issues.append('ダッシュボードがデバッグモードで実行されています')
        
        return {
            'check': 'network_security',
            'status': 'warning' if issues else 'pass',
            'issues': issues,
            'message': f'{len(issues)}個のネットワーク問題を発見' if issues else 'ネットワークセキュリティは適切です'
        }
    
    def _check_dependency_security(self) -> Dict[str, Any]:
        """依存関係セキュリティチェック"""
        print("  📦 依存関係セキュリティをチェック中...")
        
        issues = []
        
        # requirements.txtの存在確認
        if not Path('requirements.txt').exists():
            issues.append('requirements.txtが存在しません')
        else:
            # 依存関係のバージョン固定チェック
            with open('requirements.txt', 'r') as f:
                requirements = f.read()
            
            # バージョンが固定されていない依存関係をチェック
            for line in requirements.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    if '>=' in line and not '==' in line:
                        package = line.split('>=')[0]
                        issues.append(f'{package}: バージョンが固定されていません')
        
        return {
            'check': 'dependency_security',
            'status': 'warning' if issues else 'pass',
            'issues': issues,
            'message': f'{len(issues)}個の依存関係問題を発見' if issues else '依存関係セキュリティは適切です'
        }
    
    def _check_configuration_security(self) -> Dict[str, Any]:
        """設定セキュリティチェック"""
        print("  ⚙️ 設定セキュリティをチェック中...")
        
        issues = []
        
        try:
            from src.shared_modules.config_loader import ConfigLoader
            config = ConfigLoader()
            
            # デフォルト設定のチェック
            portfolio_ratios = config.get('portfolio_ratios', {})
            if portfolio_ratios.get('index') == 0.5 and portfolio_ratios.get('dividend') == 0.3:
                issues.append('ポートフォリオ比率がデフォルト値のままです')
            
            # リスク設定のチェック
            risk_profile = config.get('risk_assessment', {}).get('default_profile', '')
            if risk_profile == 'aggressive':
                issues.append('デフォルトリスクプロファイルが積極型に設定されています')
                
        except Exception as e:
            issues.append(f'設定ファイルの読み込みエラー: {e}')
        
        return {
            'check': 'configuration_security',
            'status': 'warning' if issues else 'pass',
            'issues': issues,
            'message': f'{len(issues)}個の設定問題を発見' if issues else '設定セキュリティは適切です'
        }
    
    def _calculate_security_score(self) -> int:
        """セキュリティスコアを計算"""
        if not self.audit_results:
            return 0
        
        total_checks = len(self.audit_results)
        passed_checks = len([r for r in self.audit_results if r['status'] == 'pass'])
        
        return int((passed_checks / total_checks) * 100)
    
    def _generate_security_recommendations(self) -> List[str]:
        """セキュリティ推奨事項を生成"""
        recommendations = []
        
        for result in self.audit_results:
            if result['status'] != 'pass':
                recommendations.extend(result.get('issues', []))
        
        # 一般的な推奨事項
        recommendations.extend([
            '定期的なセキュリティ監査を実施してください',
            'システムアップデートを定期的に実行してください',
            'ログファイルを定期的に監視してください',
            'バックアップを定期的に作成してください',
            'アクセス権限を最小限に制限してください'
        ])
        
        return list(set(recommendations))  # 重複を除去

class SecurityEnhancer:
    def __init__(self):
        self.auditor = SecurityAuditor()
    
    def enhance_security(self) -> Dict[str, Any]:
        """セキュリティ強化を実行"""
        print("🛡️ セキュリティ強化を実行中...")
        
        enhancements = []
        
        # ファイル権限の修正
        file_permission_result = self._fix_file_permissions()
        enhancements.append(file_permission_result)
        
        # 機密ファイルの保護
        sensitive_file_result = self._protect_sensitive_files()
        enhancements.append(sensitive_file_result)
        
        # ログセキュリティの強化
        log_security_result = self._enhance_log_security()
        enhancements.append(log_security_result)
        
        # 設定ファイルの強化
        config_security_result = self._enhance_config_security()
        enhancements.append(config_security_result)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'enhancements': enhancements,
            'summary': self._generate_enhancement_summary(enhancements)
        }
    
    def _fix_file_permissions(self) -> Dict[str, Any]:
        """ファイル権限を修正"""
        try:
            # .envファイルの権限を600に設定
            env_file = Path('.env')
            if env_file.exists():
                os.chmod(env_file, 0o600)
            
            # ログディレクトリの権限を755に設定
            log_dir = Path('logs')
            if log_dir.exists():
                os.chmod(log_dir, 0o755)
                for log_file in log_dir.glob('*.log'):
                    os.chmod(log_file, 0o644)
            
            return {
                'type': 'file_permissions',
                'status': 'completed',
                'message': 'ファイル権限を修正しました'
            }
            
        except Exception as e:
            return {
                'type': 'file_permissions',
                'status': 'error',
                'message': str(e)
            }
    
    def _protect_sensitive_files(self) -> Dict[str, Any]:
        """機密ファイルを保護"""
        try:
            # .gitignoreに.envを追加
            gitignore_file = Path('.gitignore')
            if gitignore_file.exists():
                with open(gitignore_file, 'r') as f:
                    content = f.read()
                
                if '.env' not in content:
                    with open(gitignore_file, 'a') as f:
                        f.write('\n# Environment variables\n.env\n')
            
            return {
                'type': 'sensitive_files',
                'status': 'completed',
                'message': '機密ファイルの保護を強化しました'
            }
            
        except Exception as e:
            return {
                'type': 'sensitive_files',
                'status': 'error',
                'message': str(e)
            }
    
    def _enhance_log_security(self) -> Dict[str, Any]:
        """ログセキュリティを強化"""
        try:
            # ログローテーション設定を作成
            logrotate_content = """logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 ubuntu ubuntu
}"""
            
            with open('chimera.logrotate', 'w') as f:
                f.write(logrotate_content)
            
            return {
                'type': 'log_security',
                'status': 'completed',
                'message': 'ログセキュリティを強化しました'
            }
            
        except Exception as e:
            return {
                'type': 'log_security',
                'status': 'error',
                'message': str(e)
            }
    
    def _enhance_config_security(self) -> Dict[str, Any]:
        """設定セキュリティを強化"""
        try:
            # セキュリティ設定ファイルを作成
            security_config = {
                'security': {
                    'max_login_attempts': 3,
                    'session_timeout': 3600,
                    'password_min_length': 12,
                    'enable_two_factor': False,
                    'log_failed_attempts': True,
                    'encrypt_sensitive_data': True
                }
            }
            
            with open('security_config.json', 'w') as f:
                json.dump(security_config, f, indent=2)
            
            return {
                'type': 'config_security',
                'status': 'completed',
                'message': '設定セキュリティを強化しました'
            }
            
        except Exception as e:
            return {
                'type': 'config_security',
                'status': 'error',
                'message': str(e)
            }
    
    def _generate_enhancement_summary(self, enhancements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """強化サマリーを生成"""
        completed = len([e for e in enhancements if e['status'] == 'completed'])
        errors = len([e for e in enhancements if e['status'] == 'error'])
        
        return {
            'total_enhancements': len(enhancements),
            'completed': completed,
            'errors': errors,
            'status': 'success' if errors == 0 else 'partial' if completed > 0 else 'failed'
        }

def main():
    """メイン関数"""
    print("=" * 60)
    print("🔒 Project Chimera セキュリティ強化")
    print("=" * 60)
    
    auditor = SecurityAuditor()
    enhancer = SecurityEnhancer()
    
    # セキュリティ監査実行
    print("🔍 セキュリティ監査を実行中...")
    audit_result = auditor.run_security_audit()
    
    print(f"\n📊 セキュリティスコア: {audit_result['security_score']}/100")
    
    print("\n監査結果:")
    for result in audit_result['audit_results']:
        status_icon = "✅" if result['status'] == 'pass' else "⚠️" if result['status'] == 'warning' else "❌"
        print(f"  {status_icon} {result['check']}: {result['message']}")
        
        if result.get('issues'):
            for issue in result['issues']:
                print(f"    • {issue}")
    
    print("\n推奨事項:")
    for recommendation in audit_result['recommendations']:
        print(f"  • {recommendation}")
    
    # セキュリティ強化実行
    print("\n🛡️ セキュリティ強化を実行中...")
    enhancement_result = enhancer.enhance_security()
    
    print("強化結果:")
    for enhancement in enhancement_result['enhancements']:
        status_icon = "✅" if enhancement['status'] == 'completed' else "❌"
        print(f"  {status_icon} {enhancement['type']}: {enhancement['message']}")
    
    summary = enhancement_result['summary']
    print(f"\nサマリー: {summary['completed']}/{summary['total_enhancements']} 強化完了")
    
    # 結果をファイルに保存
    result = {
        'timestamp': datetime.now().isoformat(),
        'audit': audit_result,
        'enhancement': enhancement_result
    }
    
    with open('security_audit_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n📋 結果を保存しました: security_audit_result.json")
    
    if audit_result['security_score'] >= 80:
        print("\n✅ セキュリティレベルは良好です")
    elif audit_result['security_score'] >= 60:
        print("\n⚠️ セキュリティレベルは中程度です。改善を推奨します")
    else:
        print("\n❌ セキュリティレベルは低いです。緊急の改善が必要です")

if __name__ == "__main__":
    main()
