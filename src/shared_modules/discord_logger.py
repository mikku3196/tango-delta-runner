import requests
import json
from datetime import datetime

class DiscordLogger:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
    
    def send_message(self, title, description, color=0x3498db, fields=None):
        """Discord縺ｫ繝｡繝・そ繝ｼ繧ｸ繧帝∽ｿ｡"""
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
            print(f"Discord騾夂衍繧ｨ繝ｩ繝ｼ: {e}")
            return False
    
    def info(self, message, fields=None):
        """諠・ｱ繝ｬ繝吶Ν縺ｮ繝｡繝・そ繝ｼ繧ｸ・磯搨濶ｲ・・""
        return self.send_message("邃ｹ・・INFO", message, 0x3498db, fields)
    
    def success(self, message, fields=None):
        """謌仙粥繝ｬ繝吶Ν縺ｮ繝｡繝・そ繝ｼ繧ｸ・育ｷ題牡・・""
        return self.send_message("笨・SUCCESS", message, 0x2ecc71, fields)
    
    def warning(self, message, fields=None):
        """隴ｦ蜻翫Ξ繝吶Ν縺ｮ繝｡繝・そ繝ｼ繧ｸ・磯ｻ・牡・・""
        return self.send_message("笞・・WARNING", message, 0xf39c12, fields)
    
    def error(self, message, fields=None):
        """繧ｨ繝ｩ繝ｼ繝ｬ繝吶Ν縺ｮ繝｡繝・そ繝ｼ繧ｸ・郁ｵ､濶ｲ・・""
        return self.send_message("笶・ERROR", message, 0xe74c3c, fields)
    
    def trade_notification(self, action, symbol, quantity, price=None, order_id=None):
        """蜿門ｼ暮夂衍蟆ら畑繝｡繝・そ繝ｼ繧ｸ"""
        fields = [
            {"name": "驫俶氛", "value": symbol, "inline": True},
            {"name": "謨ｰ驥・, "value": str(quantity), "inline": True},
        ]
        
        if price:
            fields.append({"name": "萓｡譬ｼ", "value": f"ﾂ･{price:,.0f}", "inline": True})
        
        if order_id:
            fields.append({"name": "豕ｨ譁⑩D", "value": str(order_id), "inline": True})
        
        action_emoji = "泙" if action == "BUY" else "閥"
        color = 0x2ecc71 if action == "BUY" else 0xe74c3c
        
        return self.send_message(
            f"{action_emoji} {action} 豕ｨ譁・ｮ溯｡・,
            f"{action}豕ｨ譁・′螳溯｡後＆繧後∪縺励◆",
            color,
            fields
        )
