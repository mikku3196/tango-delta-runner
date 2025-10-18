import os
from dotenv import load_dotenv

class EnvLoader:
    def __init__(self, env_path=".env"):
        """環墁E��数ローダーの初期匁E""
        self.env_path = env_path
        self.load_env()
    
    def load_env(self):
        """環墁E��数ファイルを読み込む"""
        try:
            # .envファイルが存在するかチェチE��
            if os.path.exists(self.env_path):
                load_dotenv(self.env_path)
                print(f"環墁E��数ファイルを読み込みました: {self.env_path}")
            else:
                print(f"警呁E 環墁E��数ファイルが見つかりません: {self.env_path}")
                print("代わりにシスチE��環墁E��数を使用しまぁE)
        except Exception as e:
            print(f"環墁E��数ファイルの読み込みエラー: {e}")
    
    def get(self, key, default=None):
        """環墁E��数の値を取征E""
        return os.getenv(key, default)
    
    def get_required(self, key):
        """忁E���E環墁E��数の値を取得（存在しなぁE��合�Eエラー�E�E""
        value = os.getenv(key)
        if value is None:
            raise ValueError(f"忁E���E環墁E��数が設定されてぁE��せん: {key}")
        return value
    
    def get_ib_main_account_id(self):
        """IB証券メイン口座IDを取征E""
        return self.get_required("IB_MAIN_ACCOUNT_ID")
    
    def get_ib_nisa_account_id(self):
        """IB証券NISA口座IDを取征E""
        return self.get_required("IB_NISA_ACCOUNT_ID")
    
    def get_discord_webhook_url(self):
        """Discord Webhook URLを取征E""
        return self.get_required("DISCORD_WEBHOOK_URL")
    
    def get_log_level(self):
        """ログレベルを取得（デフォルチE INFO�E�E""
        return self.get("LOG_LEVEL", "INFO")
    
    def validate_required_vars(self):
        """忁E���E環墁E��数がすべて設定されてぁE��かチェチE��"""
        required_vars = [
            "IB_MAIN_ACCOUNT_ID",
            "IB_NISA_ACCOUNT_ID", 
            "DISCORD_WEBHOOK_URL"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"以下�E忁E��環墁E��数が設定されてぁE��せん: {', '.join(missing_vars)}")
        
        return True
