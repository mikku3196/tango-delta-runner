#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Chimera 詳細ロギングシステム
JSONL形式での詳細ログ記録とローテーション
"""

import os
import json
import logging
import logging.handlers
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pathlib import Path

class JSONLFormatter(logging.Formatter):
    """JSONL形式のログフォーマッター"""
    
    def format(self, record):
        """ログレコードをJSONL形式でフォーマット"""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "component": getattr(record, "component", "UNKNOWN"), # <-- ここも 'component' に修正
            "event": record.getMessage(),
            "details": getattr(record, "details", {})
        }
        
        return json.dumps(log_entry, ensure_ascii=False)

class DetailedLogger:
    def __init__(self, log_dir: str = "logs", max_days: int = 7, max_size_mb: int = 50):
        """
        詳細ロガーの初期化
        
        Args:
            log_dir: ログディレクトリ
            max_days: ログ保持日数
            max_size_mb: ログファイル最大サイズ（MB）
        """
        self.log_dir = Path(log_dir)
        self.max_days = max_days
        self.max_size_bytes = max_size_mb * 1024 * 1024
        
        self.log_dir.mkdir(exist_ok=True)
        
        self.log_filename = self.log_dir / f"chimera_{datetime.now().strftime('%Y-%m-%d')}.log"
        
        self._setup_rotation()
        
        self.logger = logging.getLogger("chimera")
        self.logger.setLevel(logging.DEBUG)
        
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        self._setup_jsonl_handler()
    
    def _setup_rotation(self):
        self._cleanup_old_logs()
        if self.log_filename.exists() and self.log_filename.stat().st_size > self.max_size_bytes:
            self._rotate_log_file()
    
    def _cleanup_old_logs(self):
        cutoff_date = datetime.now() - timedelta(days=self.max_days)
        for log_file in self.log_dir.glob("chimera_*.log"):
            try:
                date_str = log_file.stem.split("_")[1]
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                if file_date < cutoff_date:
                    log_file.unlink()
            except (ValueError, IndexError):
                continue
    
    def _rotate_log_file(self):
        if self.log_filename.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            rotated_name = self.log_dir / f"chimera_{datetime.now().strftime('%Y-%m-%d')}_{timestamp}.log"
            self.log_filename.rename(rotated_name)
    
    def _setup_jsonl_handler(self):
        handler = logging.FileHandler(self.log_filename, encoding='utf-8')
        handler.setLevel(logging.DEBUG)
        formatter = JSONLFormatter()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    # --- ここから下のメソッドが、クラスの中に正しく配置されました ---

    def log_event(self, level: str, module: str, event: str, details: Dict[str, Any] = None):
        """
        イベントをログに記録
        """
        if details is None:
            details = {}
        
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(event, extra={
            "component": module,  # <-- 'module' を 'component' に変更！
            "event": event,
            "details": details
        })

    def log_trade(self, action: str, symbol: str, quantity: int, price: float, 
                  account: str, details: Dict[str, Any] = None):
        """
        取引イベントをログに記録
        """
        if details is None:
            details = {}
        
        trade_details = {
            "action": action, "symbol": symbol, "quantity": quantity,
            "price": price, "account": account, **details
        }
        self.log_event("INFO", "TRADE", f"{action} {symbol}", trade_details)
    
    def log_portfolio_change(self, strategy: str, old_value: float, new_value: float, 
                           change_percent: float, details: Dict[str, Any] = None):
        """
        ポートフォリオ変更をログに記録
        """
        if details is None:
            details = {}
        
        portfolio_details = {
            "strategy": strategy, "old_value": old_value, "new_value": new_value,
            "change_percent": change_percent, **details
        }
        self.log_event("INFO", "PORTFOLIO", f"Portfolio change: {strategy}", portfolio_details)
    
    def log_nisa_usage(self, annual_used: float, lifetime_used: float, 
                      annual_limit: float, lifetime_limit: float, details: Dict[str, Any] = None):
        """
        NISA使用状況をログに記録
        """
        if details is None:
            details = {}
        
        nisa_details = {
            "annual_used": annual_used, "lifetime_used": lifetime_used,
            "annual_limit": annual_limit, "lifetime_limit": lifetime_limit,
            "annual_usage_percent": (annual_used / annual_limit) * 100,
            "lifetime_usage_percent": (lifetime_used / lifetime_limit) * 100,
            **details
        }
        self.log_event("INFO", "NISA", "NISA usage update", nisa_details)
    
    def log_error(self, module: str, error: Exception, context: str = "", details: Dict[str, Any] = None):
        """
        エラーをログに記録
        """
        if details is None:
            details = {}
        
        error_details = {
            "error_type": type(error).__name__, "error_message": str(error),
            "context": context, **details
        }
        self.log_event("ERROR", module, f"Error in {context}", error_details)
    
    def get_log_stats(self) -> Dict[str, Any]:
        """ログ統計情報を取得"""
        stats = {"log_dir": str(self.log_dir), "current_log_file": str(self.log_filename),
                 "log_file_size": self.log_filename.stat().st_size if self.log_filename.exists() else 0,
                 "max_days": self.max_days, "max_size_mb": self.max_size_bytes // (1024 * 1024),
                 "log_files": []}
        
        for log_file in self.log_dir.glob("chimera_*.log"):
            stats["log_files"].append({
                "name": log_file.name, "size": log_file.stat().st_size,
                "modified": datetime.fromtimestamp(log_file.stat().st_mtime).isoformat()
            })
        return stats

# --- ここから下は、クラスの外にあるのが正しいです ---

detailed_logger = DetailedLogger()

def get_detailed_logger() -> DetailedLogger:
    return detailed_logger

# ... (log_info, log_warningなどのヘルパー関数) ...