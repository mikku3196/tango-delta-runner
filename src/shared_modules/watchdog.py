#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Chimera Watchdog機能
システム監視と自動再起動機能
"""

import os
import time
import threading
import subprocess
import signal
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable
from pathlib import Path

from src.shared_modules.config_loader import ConfigLoader
from src.shared_modules.discord_logger import DiscordLogger
from src.shared_modules.detailed_logger import get_detailed_logger

class Watchdog:
    def __init__(self, config: ConfigLoader, discord: DiscordLogger):
        """
        Watchdogの初期化
        
        Args:
            config: 設定ローダー
            discord: Discord通知ロガー
        """
        self.config = config
        self.discord = discord
        self.detailed_logger = get_detailed_logger()
        
        # 監視設定
        self.check_interval = 600  # 10分ごと
        self.max_restart_attempts = 3
        self.restart_cooldown = 300  # 5分間のクールダウン
        
        # 監視対象プロセス
        self.monitored_processes = {}
        self.restart_counts = {}
        self.last_restart_times = {}
        
        # 監視状態
        self.is_monitoring = False
        self.monitor_thread = None
        
        # 停止フラグ
        self.stop_flag_file = "STOP.flag"
        
        # ハートビート設定
        self.heartbeat_interval = 86400  # 24時間ごと
        self.last_heartbeat = datetime.now()
        
        self.detailed_logger.log_event("INFO", "WATCHDOG", "Watchdog initialized", {
            "check_interval": self.check_interval,
            "max_restart_attempts": self.max_restart_attempts,
            "restart_cooldown": self.restart_cooldown
        })
    
    def register_process(self, name: str, process_func: Callable, 
                        restart_func: Optional[Callable] = None, 
                        health_check_func: Optional[Callable] = None):
        """
        監視対象プロセスを登録
        
        Args:
            name: プロセス名
            process_func: プロセス実行関数
            restart_func: 再起動関数（Noneの場合はprocess_funcを使用）
            health_check_func: ヘルスチェック関数
        """
        self.monitored_processes[name] = {
            "process_func": process_func,
            "restart_func": restart_func or process_func,
            "health_check_func": health_check_func,
            "is_running": False,
            "process": None,
            "thread": None
        }
        
        self.restart_counts[name] = 0
        self.last_restart_times[name] = None
        
        self.detailed_logger.log_event("INFO", "WATCHDOG", f"Process registered: {name}", {
            "process_name": name,
            "has_health_check": health_check_func is not None
        })
    
    def start_monitoring(self):
        """監視を開始"""
        if self.is_monitoring:
            self.detailed_logger.log_warning("WATCHDOG", "Monitoring already started")
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        self.detailed_logger.log_event("INFO", "WATCHDOG", "Monitoring started")
        self.discord.info("Watchdog監視を開始しました")
    
    def stop_monitoring(self):
        """監視を停止"""
        self.is_monitoring = False
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        
        # 監視対象プロセスを停止
        for name, process_info in self.monitored_processes.items():
            self._stop_process(name)
        
        self.detailed_logger.log_event("INFO", "WATCHDOG", "Monitoring stopped")
        self.discord.info("Watchdog監視を停止しました")
    
    def _monitor_loop(self):
        """監視ループ"""
        while self.is_monitoring:
            try:
                # STOP.flagのチェック
                if self._check_stop_flag():
                    self.detailed_logger.log_event("CRITICAL", "WATCHDOG", "STOP.flag detected")
                    self.discord.error("【CRITICAL】STOP.flagが検出されました。監視を停止します。")
                    break
                
                # 各プロセスの監視
                for name in list(self.monitored_processes.keys()):
                    self._check_process_health(name)
                
                # ハートビートチェック
                self._check_heartbeat()
                
                # 次のチェックまで待機
                time.sleep(self.check_interval)
                
            except Exception as e:
                self.detailed_logger.log_error("WATCHDOG", e, "Monitor loop error")
                self.discord.error(f"Watchdog監視ループでエラーが発生しました: {str(e)}")
                time.sleep(60)  # エラー時は1分待機
    
    def _check_stop_flag(self) -> bool:
        """STOP.flagの存在をチェック"""
        return os.path.exists(self.stop_flag_file)
    
    def _check_process_health(self, name: str):
        """プロセスのヘルスチェック"""
        process_info = self.monitored_processes.get(name)
        if not process_info:
            return
        
        try:
            # ヘルスチェック関数がある場合は実行
            if process_info["health_check_func"]:
                is_healthy = process_info["health_check_func"]()
                if not is_healthy:
                    self.detailed_logger.log_event("WARNING", "WATCHDOG", 
                                                 f"Process {name} failed health check")
                    self._restart_process(name)
                    return
            
            # プロセスが停止している場合は再起動
            if not process_info["is_running"]:
                self.detailed_logger.log_event("WARNING", "WATCHDOG", 
                                             f"Process {name} is not running")
                self._restart_process(name)
                
        except Exception as e:
            self.detailed_logger.log_error("WATCHDOG", e, f"Health check for {name}")
            self._restart_process(name)
    
    def _restart_process(self, name: str):
        """プロセスを再起動"""
        process_info = self.monitored_processes.get(name)
        if not process_info:
            return
        
        # クールダウンチェック
        if self._is_in_cooldown(name):
            return
        
        # 最大再起動回数チェック
        if self.restart_counts[name] >= self.max_restart_attempts:
            self.detailed_logger.log_event("CRITICAL", "WATCHDOG", 
                                         f"Process {name} exceeded max restart attempts")
            self.discord.error(f"【FATAL】プロセス {name} が最大再起動回数を超過しました。システムを停止します。")
            self._emergency_shutdown()
            return
        
        try:
            # 既存のプロセスを停止
            self._stop_process(name)
            
            # プロセスを再起動
            self._start_process(name)
            
            # 再起動回数を増加
            self.restart_counts[name] += 1
            self.last_restart_times[name] = datetime.now()
            
            self.detailed_logger.log_event("INFO", "WATCHDOG", 
                                         f"Process {name} restarted", {
                                             "restart_count": self.restart_counts[name],
                                             "max_attempts": self.max_restart_attempts
                                         })
            
            self.discord.warning(f"プロセス {name} を再起動しました (試行 {self.restart_counts[name]}/{self.max_restart_attempts})")
            
        except Exception as e:
            self.detailed_logger.log_error("WATCHDOG", e, f"Restart process {name}")
            self.discord.error(f"プロセス {name} の再起動に失敗しました: {str(e)}")
    
    def _is_in_cooldown(self, name: str) -> bool:
        """クールダウン期間中かチェック"""
        last_restart = self.last_restart_times.get(name)
        if not last_restart:
            return False
        
        cooldown_end = last_restart + timedelta(seconds=self.restart_cooldown)
        return datetime.now() < cooldown_end
    
    def _start_process(self, name: str):
        """プロセスを開始"""
        process_info = self.monitored_processes.get(name)
        if not process_info:
            return
        
        try:
            # プロセス実行関数をスレッドで実行
            process_info["thread"] = threading.Thread(
                target=self._run_process, 
                args=(name, process_info["process_func"]),
                daemon=True
            )
            process_info["thread"].start()
            process_info["is_running"] = True
            
            self.detailed_logger.log_event("INFO", "WATCHDOG", f"Process {name} started")
            
        except Exception as e:
            self.detailed_logger.log_error("WATCHDOG", e, f"Start process {name}")
            raise
    
    def _stop_process(self, name: str):
        """プロセスを停止"""
        process_info = self.monitored_processes.get(name)
        if not process_info:
            return
        
        try:
            process_info["is_running"] = False
            
            # スレッドの終了を待機
            if process_info["thread"] and process_info["thread"].is_alive():
                process_info["thread"].join(timeout=5)
            
            self.detailed_logger.log_event("INFO", "WATCHDOG", f"Process {name} stopped")
            
        except Exception as e:
            self.detailed_logger.log_error("WATCHDOG", e, f"Stop process {name}")
    
    def _run_process(self, name: str, process_func: Callable):
        """プロセス実行関数をラップ"""
        try:
            self.detailed_logger.log_event("INFO", "WATCHDOG", f"Process {name} execution started")
            process_func()
        except Exception as e:
            self.detailed_logger.log_error("WATCHDOG", e, f"Process {name} execution")
            self.monitored_processes[name]["is_running"] = False
        finally:
            self.detailed_logger.log_event("INFO", "WATCHDOG", f"Process {name} execution ended")
    
    def _check_heartbeat(self):
        """ハートビートチェック"""
        now = datetime.now()
        if now - self.last_heartbeat >= timedelta(seconds=self.heartbeat_interval):
            self._send_heartbeat()
            self.last_heartbeat = now
    
    def _send_heartbeat(self):
        """ハートビートを送信"""
        try:
            # 監視対象プロセスの状態を取得
            process_status = {}
            for name, process_info in self.monitored_processes.items():
                process_status[name] = {
                    "is_running": process_info["is_running"],
                    "restart_count": self.restart_counts[name],
                    "last_restart": self.last_restart_times[name].isoformat() if self.last_restart_times[name] else None
                }
            
            self.detailed_logger.log_event("INFO", "WATCHDOG", "Heartbeat sent", {
                "process_status": process_status,
                "uptime": (datetime.now() - self.last_heartbeat).total_seconds()
            })
            
            self.discord.info("🔄 Watchdog ハートビート", "システムは正常に稼働中です", 
                            fields=[
                                {"name": "監視対象プロセス", "value": str(len(self.monitored_processes)), "inline": True},
                                {"name": "稼働時間", "value": f"{self.heartbeat_interval // 3600}時間", "inline": True}
                            ])
            
        except Exception as e:
            self.detailed_logger.log_error("WATCHDOG", e, "Send heartbeat")
    
    def _emergency_shutdown(self):
        """緊急シャットダウン"""
        try:
            self.detailed_logger.log_event("CRITICAL", "WATCHDOG", "Emergency shutdown initiated")
            self.discord.error("【FATAL】Watchdogが緊急シャットダウンを実行します")
            
            # 監視を停止
            self.stop_monitoring()
            
            # STOP.flagを作成
            with open(self.stop_flag_file, "w", encoding="utf-8") as f:
                f.write(json.dumps({
                    "reason": "watchdog_emergency_shutdown",
                    "timestamp": datetime.now().isoformat(),
                    "executed_by": "watchdog.py"
                }, ensure_ascii=False))
            
            # プロセス終了
            os._exit(1)
            
        except Exception as e:
            self.detailed_logger.log_error("WATCHDOG", e, "Emergency shutdown")
            os._exit(1)
    
    def get_status(self) -> Dict[str, Any]:
        """Watchdogの状態を取得"""
        return {
            "is_monitoring": self.is_monitoring,
            "check_interval": self.check_interval,
            "max_restart_attempts": self.max_restart_attempts,
            "restart_cooldown": self.restart_cooldown,
            "monitored_processes": {
                name: {
                    "is_running": info["is_running"],
                    "restart_count": self.restart_counts[name],
                    "last_restart": self.last_restart_times[name].isoformat() if self.last_restart_times[name] else None
                }
                for name, info in self.monitored_processes.items()
            },
            "last_heartbeat": self.last_heartbeat.isoformat()
        }

# グローバルWatchdogインスタンス
watchdog_instance = None

def get_watchdog() -> Optional[Watchdog]:
    """Watchdogインスタンスを取得"""
    return watchdog_instance

def initialize_watchdog(config: ConfigLoader, discord: DiscordLogger) -> Watchdog:
    """Watchdogを初期化"""
    global watchdog_instance
    watchdog_instance = Watchdog(config, discord)
    return watchdog_instance

if __name__ == "__main__":
    # テスト実行
    from src.shared_modules.config_loader import ConfigLoader
    from src.shared_modules.discord_logger import DiscordLogger
    
    config = ConfigLoader()
    discord = DiscordLogger(config.get("discord_webhook_url"))
    
    watchdog = Watchdog(config, discord)
    
    # テストプロセスを登録
    def test_process():
        print("Test process running...")
        time.sleep(30)
        print("Test process finished")
    
    def test_health_check():
        return True  # 常に健康
    
    watchdog.register_process("test_process", test_process, health_check_func=test_health_check)
    
    # 監視開始
    watchdog.start_monitoring()
    
    try:
        # テスト実行
        time.sleep(60)
    except KeyboardInterrupt:
        print("Stopping watchdog...")
        watchdog.stop_monitoring()
