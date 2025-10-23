#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Chimera パフォーマンス最適化
システムのパフォーマンス監視と最適化
"""

import os
import sys
import time
import psutil
import threading
import queue
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import json

class PerformanceMonitor:
    def __init__(self):
        self.metrics_queue = queue.Queue()
        self.is_monitoring = False
        self.monitor_thread = None
        self.metrics_history = []
        self.max_history_size = 1000
        
    def start_monitoring(self):
        """パフォーマンス監視を開始"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("📊 パフォーマンス監視を開始しました")
    
    def stop_monitoring(self):
        """パフォーマンス監視を停止"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        print("📊 パフォーマンス監視を停止しました")
    
    def _monitor_loop(self):
        """監視ループ"""
        while self.is_monitoring:
            try:
                metrics = self._collect_metrics()
                self.metrics_queue.put(metrics)
                self._update_history(metrics)
                time.sleep(5)  # 5秒ごとに監視
            except Exception as e:
                print(f"パフォーマンス監視エラー: {e}")
                time.sleep(10)
    
    def _collect_metrics(self) -> Dict[str, Any]:
        """メトリクスを収集"""
        try:
            # システムメトリクス
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # プロセスメトリクス
            chimera_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent', 'create_time']):
                try:
                    if proc.info['cmdline'] and any('main_controller.py' in cmd for cmd in proc.info['cmdline']):
                        chimera_processes.append({
                            'pid': proc.info['pid'],
                            'cpu_percent': proc.info['cpu_percent'],
                            'memory_percent': proc.info['memory_percent'],
                            'uptime': time.time() - proc.info['create_time']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # ネットワークメトリクス
            network = psutil.net_io_counters()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'system': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_used': memory.used,
                    'memory_total': memory.total,
                    'disk_percent': disk.percent,
                    'disk_used': disk.used,
                    'disk_total': disk.total
                },
                'processes': chimera_processes,
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                }
            }
        except Exception as e:
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def _update_history(self, metrics: Dict[str, Any]):
        """メトリクス履歴を更新"""
        self.metrics_history.append(metrics)
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history = self.metrics_history[-self.max_history_size:]
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """現在のメトリクスを取得"""
        try:
            return self.metrics_queue.get_nowait()
        except queue.Empty:
            return self._collect_metrics()
    
    def get_metrics_history(self, minutes: int = 60) -> List[Dict[str, Any]]:
        """指定時間のメトリクス履歴を取得"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        return [
            m for m in self.metrics_history 
            if datetime.fromisoformat(m['timestamp']) > cutoff_time
        ]
    
    def analyze_performance(self) -> Dict[str, Any]:
        """パフォーマンス分析"""
        if not self.metrics_history:
            return {'error': 'No metrics available'}
        
        recent_metrics = self.get_metrics_history(60)  # 過去1時間
        
        if not recent_metrics:
            return {'error': 'No recent metrics available'}
        
        # CPU使用率分析
        cpu_values = [m['system']['cpu_percent'] for m in recent_metrics if 'system' in m]
        cpu_avg = sum(cpu_values) / len(cpu_values) if cpu_values else 0
        cpu_max = max(cpu_values) if cpu_values else 0
        
        # メモリ使用率分析
        memory_values = [m['system']['memory_percent'] for m in recent_metrics if 'system' in m]
        memory_avg = sum(memory_values) / len(memory_values) if memory_values else 0
        memory_max = max(memory_values) if memory_values else 0
        
        # ディスク使用率分析
        disk_values = [m['system']['disk_percent'] for m in recent_metrics if 'system' in m]
        disk_avg = sum(disk_values) / len(disk_values) if disk_values else 0
        disk_max = max(disk_values) if disk_values else 0
        
        # プロセス数分析
        process_counts = [len(m.get('processes', [])) for m in recent_metrics]
        process_avg = sum(process_counts) / len(process_counts) if process_counts else 0
        
        return {
            'analysis_period': '60 minutes',
            'cpu': {
                'average': cpu_avg,
                'maximum': cpu_max,
                'status': 'high' if cpu_avg > 80 else 'normal' if cpu_avg < 50 else 'moderate'
            },
            'memory': {
                'average': memory_avg,
                'maximum': memory_max,
                'status': 'high' if memory_avg > 80 else 'normal' if memory_avg < 50 else 'moderate'
            },
            'disk': {
                'average': disk_avg,
                'maximum': disk_max,
                'status': 'high' if disk_avg > 90 else 'normal' if disk_avg < 70 else 'moderate'
            },
            'processes': {
                'average_count': process_avg,
                'status': 'normal' if process_avg > 0 else 'stopped'
            },
            'recommendations': self._generate_recommendations(cpu_avg, memory_avg, disk_avg, process_avg)
        }
    
    def _generate_recommendations(self, cpu_avg: float, memory_avg: float, disk_avg: float, process_avg: float) -> List[str]:
        """推奨事項を生成"""
        recommendations = []
        
        if cpu_avg > 80:
            recommendations.append("CPU使用率が高いです。不要なプロセスを終了するか、システムリソースを増強してください。")
        
        if memory_avg > 80:
            recommendations.append("メモリ使用率が高いです。メモリリークがないか確認し、必要に応じてメモリを増強してください。")
        
        if disk_avg > 90:
            recommendations.append("ディスク使用率が高いです。古いログファイルを削除するか、ディスク容量を増強してください。")
        
        if process_avg == 0:
            recommendations.append("Project Chimeraプロセスが停止しています。サービスを再起動してください。")
        
        if not recommendations:
            recommendations.append("システムは正常に動作しています。")
        
        return recommendations

class PerformanceOptimizer:
    def __init__(self):
        self.monitor = PerformanceMonitor()
    
    def optimize_system(self) -> Dict[str, Any]:
        """システム最適化を実行"""
        print("🔧 システム最適化を実行中...")
        
        optimizations = []
        
        # ログファイル最適化
        log_optimization = self._optimize_logs()
        optimizations.append(log_optimization)
        
        # プロセス最適化
        process_optimization = self._optimize_processes()
        optimizations.append(process_optimization)
        
        # メモリ最適化
        memory_optimization = self._optimize_memory()
        optimizations.append(memory_optimization)
        
        # ディスク最適化
        disk_optimization = self._optimize_disk()
        optimizations.append(disk_optimization)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'optimizations': optimizations,
            'summary': self._generate_optimization_summary(optimizations)
        }
    
    def _optimize_logs(self) -> Dict[str, Any]:
        """ログファイル最適化"""
        try:
            log_dir = Path("logs")
            if not log_dir.exists():
                return {'type': 'logs', 'status': 'skipped', 'message': 'Log directory not found'}
            
            # 古いログファイルを削除
            log_files = list(log_dir.glob("*.log"))
            old_files = []
            
            for log_file in log_files:
                if log_file.stat().st_mtime < (time.time() - 7 * 24 * 3600):  # 7日以上古い
                    old_files.append(log_file)
            
            freed_space = 0
            for log_file in old_files:
                freed_space += log_file.stat().st_size
                log_file.unlink()
            
            return {
                'type': 'logs',
                'status': 'completed',
                'message': f'Removed {len(old_files)} old log files',
                'freed_space': freed_space
            }
            
        except Exception as e:
            return {'type': 'logs', 'status': 'error', 'message': str(e)}
    
    def _optimize_processes(self) -> Dict[str, Any]:
        """プロセス最適化"""
        try:
            # 重複プロセスをチェック
            chimera_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['cmdline'] and any('main_controller.py' in cmd for cmd in proc.info['cmdline']):
                        chimera_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if len(chimera_processes) > 1:
                # 古いプロセスを終了
                chimera_processes.sort(key=lambda p: p.create_time())
                for proc in chimera_processes[:-1]:  # 最新以外を終了
                    proc.terminate()
                
                return {
                    'type': 'processes',
                    'status': 'completed',
                    'message': f'Terminated {len(chimera_processes) - 1} duplicate processes'
                }
            else:
                return {
                    'type': 'processes',
                    'status': 'skipped',
                    'message': 'No duplicate processes found'
                }
                
        except Exception as e:
            return {'type': 'processes', 'status': 'error', 'message': str(e)}
    
    def _optimize_memory(self) -> Dict[str, Any]:
        """メモリ最適化"""
        try:
            # Pythonのガベージコレクションを実行
            import gc
            collected = gc.collect()
            
            return {
                'type': 'memory',
                'status': 'completed',
                'message': f'Garbage collection completed, collected {collected} objects'
            }
            
        except Exception as e:
            return {'type': 'memory', 'status': 'error', 'message': str(e)}
    
    def _optimize_disk(self) -> Dict[str, Any]:
        """ディスク最適化"""
        try:
            # 一時ファイルを削除
            temp_files = []
            for root, dirs, files in os.walk('.'):
                for file in files:
                    if file.endswith('.tmp') or file.endswith('.pyc'):
                        temp_files.append(os.path.join(root, file))
            
            freed_space = 0
            for temp_file in temp_files:
                try:
                    freed_space += os.path.getsize(temp_file)
                    os.remove(temp_file)
                except OSError:
                    continue
            
            return {
                'type': 'disk',
                'status': 'completed',
                'message': f'Removed {len(temp_files)} temporary files',
                'freed_space': freed_space
            }
            
        except Exception as e:
            return {'type': 'disk', 'status': 'error', 'message': str(e)}
    
    def _generate_optimization_summary(self, optimizations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """最適化サマリーを生成"""
        completed = len([o for o in optimizations if o['status'] == 'completed'])
        errors = len([o for o in optimizations if o['status'] == 'error'])
        skipped = len([o for o in optimizations if o['status'] == 'skipped'])
        
        total_freed_space = sum(o.get('freed_space', 0) for o in optimizations)
        
        return {
            'total_optimizations': len(optimizations),
            'completed': completed,
            'errors': errors,
            'skipped': skipped,
            'total_freed_space': total_freed_space,
            'status': 'success' if errors == 0 else 'partial' if completed > 0 else 'failed'
        }

def main():
    """メイン関数"""
    print("=" * 60)
    print("⚡ Project Chimera パフォーマンス最適化")
    print("=" * 60)
    
    optimizer = PerformanceOptimizer()
    
    # パフォーマンス監視開始
    optimizer.monitor.start_monitoring()
    
    try:
        # 5秒間監視
        print("📊 システム状態を監視中...")
        time.sleep(5)
        
        # パフォーマンス分析
        print("\n📈 パフォーマンス分析を実行中...")
        analysis = optimizer.monitor.analyze_performance()
        
        print("分析結果:")
        print(f"  CPU使用率: {analysis['cpu']['average']:.1f}% ({analysis['cpu']['status']})")
        print(f"  メモリ使用率: {analysis['memory']['average']:.1f}% ({analysis['memory']['status']})")
        print(f"  ディスク使用率: {analysis['disk']['average']:.1f}% ({analysis['disk']['status']})")
        print(f"  プロセス数: {analysis['processes']['average_count']:.1f} ({analysis['processes']['status']})")
        
        print("\n推奨事項:")
        for recommendation in analysis['recommendations']:
            print(f"  • {recommendation}")
        
        # システム最適化実行
        print("\n🔧 システム最適化を実行中...")
        optimization_result = optimizer.optimize_system()
        
        print("最適化結果:")
        for opt in optimization_result['optimizations']:
            status_icon = "✅" if opt['status'] == 'completed' else "⚠️" if opt['status'] == 'skipped' else "❌"
            print(f"  {status_icon} {opt['type']}: {opt['message']}")
        
        summary = optimization_result['summary']
        print(f"\nサマリー: {summary['completed']}/{summary['total_optimizations']} 最適化完了")
        if summary['total_freed_space'] > 0:
            print(f"解放された容量: {summary['total_freed_space']:,} bytes")
        
        # 結果をファイルに保存
        result = {
            'timestamp': datetime.now().isoformat(),
            'analysis': analysis,
            'optimization': optimization_result
        }
        
        with open('performance_optimization_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n📋 結果を保存しました: performance_optimization_result.json")
        
    finally:
        # パフォーマンス監視停止
        optimizer.monitor.stop_monitoring()
    
    print("\n✅ パフォーマンス最適化が完了しました")

if __name__ == "__main__":
    main()
