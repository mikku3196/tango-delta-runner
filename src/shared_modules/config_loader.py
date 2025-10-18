import yaml
import os
from src.shared_modules.env_loader import EnvLoader

class ConfigLoader:
    def __init__(self, config_path="src/config/config.yaml"):
        self.config_path = config_path
        self.env_loader = EnvLoader()
        self.config = self.load_config()
    
    def load_config(self):
        """設定ファイルを読み込む"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as file:
                config = yaml.safe_load(file)
            
            # 環墁E��数から機寁E��報を取得して設定に追加
            config["ib_account"] = {
                "main_account_id": self.env_loader.get_ib_main_account_id(),
                "nisa_account_id": self.env_loader.get_ib_nisa_account_id(),
                "host": self.config.get("ib_gateway", {}).get("host", "127.0.0.1"),
                "port": self.config.get("ib_gateway", {}).get("port", 5000),
                "client_id": self.config.get("ib_gateway", {}).get("client_id", 1)
            }
            
            config["discord_webhook_url"] = self.env_loader.get_discord_webhook_url()
            
            return config
            
        except FileNotFoundError:
            print(f"設定ファイルが見つかりません: {self.config_path}")
            return {}
        except yaml.YAMLError as e:
            print(f"設定ファイルの解析エラー: {e}")
            return {}
        except Exception as e:
            print(f"設定読み込みエラー: {e}")
            return {}
    
    def get(self, key, default=None):
        """設定値を取得する（ドチE��記法対応！E""
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def reload(self):
        """設定ファイルを�E読み込み"""
        self.config = self.load_config()
        return self.config
    
    def validate_config(self):
        """設定�E妥当性をチェチE��"""
        try:
            # 忁E���E環墁E��数をチェチE��
            self.env_loader.validate_required_vars()
            
            # 忁E���E設定頁E��をチェチE��
            required_configs = [
                "portfolio_ratios.index",
                "portfolio_ratios.dividend", 
                "portfolio_ratios.range",
                "index_bot.ticker",
                "index_bot.monthly_investment"
            ]
            
            for config_key in required_configs:
                if self.get(config_key) is None:
                    raise ValueError(f"忁E���E設定頁E��が不足してぁE��ぁE {config_key}")
            
            return True
            
        except Exception as e:
            print(f"設定検証エラー: {e}")
            return False
