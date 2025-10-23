import yaml
import os

class ConfigLoader:
    def __init__(self, config_path="src/config/config.yaml"):
        self.config_path = config_path
        self.config = self.load_config()
    
    def load_config(self):
        """設定ファイルを読み込む"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            print(f"設定ファイルが見つかりません: {self.config_path}")
            return {}
        except yaml.YAMLError as e:
            print(f"設定ファイルの解析エラー: {e}")
            return {}
    
    def get(self, key, default=None):
        """設定値を取得する（ドット記法対応）"""
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def reload(self):
        """設定ファイルを再読み込み"""
        self.config = self.load_config()
        return self.config
