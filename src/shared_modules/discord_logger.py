import requests
import json
from datetime import datetime

class DiscordLogger:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
    
    def send_message(self, title, description, color=0x3498db, fields=None):
        """Discordにメッセージを送信"""
        embed = {
            "title": title,
            "description": description,
            "color": color,
            "timestamp": datetime.utcnow().isoformat(),
            "fields": fields or []
        }
        
        payload = {"embeds": [embed]}
        
        try:
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Discord通知エラー: {e}")
            return False
    
    def info(self, message, fields=None):
        """情報レベルのメッセージ（青色）"""
        return self.send_message("ℹ️ INFO", message, 0x3498db, fields)
    
    def success(self, message, fields=None):
        """成功レベルのメッセージ（緑色）"""
        return self.send_message("✅ SUCCESS", message, 0x2ecc71, fields)
    
    def warning(self, message, fields=None):
        """警告レベルのメッセージ（黄色）"""
        return self.send_message("⚠️ WARNING", message, 0xf39c12, fields)
    
    def error(self, message, fields=None):
        """エラーレベルのメッセージ（赤色）"""
        return self.send_message("❌ ERROR", message, 0xe74c3c, fields)
    
    def trade_notification(self, action, symbol, quantity, price=None, order_id=None):
        """取引通知専用メッセージ"""
        fields = [
            {"name": "銘柄", "value": symbol, "inline": True},
            {"name": "数量", "value": str(quantity), "inline": True},
        ]
        
        if price:
            fields.append({"name": "価格", "value": f"¥{price:,.0f}", "inline": True})
        
        if order_id:
            fields.append({"name": "注文ID", "value": str(order_id), "inline": True})
        
        action_emoji = "🟢" if action == "BUY" else "🔴"
        color = 0x2ecc71 if action == "BUY" else 0xe74c3c
        
        return self.send_message(
            f"{action_emoji} {action} 注文実行",
            f"{action}注文が実行されました",
            color,
            fields
        )
