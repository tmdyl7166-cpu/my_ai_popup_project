"""
脚本管理器
负责脚本的运行、状态管理和调度
"""
import os
import sys
import json
import time
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
import threading
import schedule

class ScriptManager:
    """脚本管理器"""
    
    def __init__(self, project_root: Path, sio, script_status: Dict[str, Any]):
        self.project_root = project_root
        self.sio = sio
        self.script_status = script_status
        self.monitoring_active = False
        self.scheduled_tasks = {}
    
    def get_scripts_status(self) -> Dict[str, Any]:
        """获取脚本运行状态"""
        return {
            'scripts': self.script_status,
            'monitoring_active': self.monitoring_active,
            'timestamp': time.time()
        }
    
    def get_scripts_list(self) -> List[Dict[str, Any]]:
        """获取脚本列表"""
        scripts_config_path = self.project_root / 'scripts' / 'scripts_config.json'
        if scripts_config_path.exists():
            try:
                with open(scripts_config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                scripts = []
                sub_scripts = config.get('structure', {}).get('scripts/health_monitor/', {}).get('subScripts', {})
                for script_name, script_info in sub_scripts.items():
                    scripts.append({
                        'name': script_name,
                        'display_name': script_info.get('name', script_name),
                        'description': script_info.get('description', ''),
                        'status': self.script_status.get(script_name, 'idle'),
                        'last_run': self.script_status.get(f"{script_name}_last_run"),
                        'frequency': script_info.get('execution', {}).get('frequency', 'manual')
                    })
                return scripts
            except Exception as e:
                print(f"读取脚本配置失败: {e}")
        return []
    
    async def run_script_async(self, script_name: str, background_tasks = None) -> Dict[str, Any]:
        """异步运行脚本"""
        try:
            # 更新脚本状态
            self.script_status[script_name] = 'running'
            self.script_status[f"{script_name}_start_time"] = time.time()
            # 广播状态更新
            await self.sio.emit('status_update', self.get_scripts_status())
            # 构造脚本路径
            script_path = self.project_root / 'scripts' / 'health_monitor' / script_name
            if not script_path.exists():
                raise FileNotFoundError(f"脚本文件不存在: {script_path}")
            # 运行脚本
            if background_tasks:
                background_tasks.add_task(self._run_script_background, script_name, str(script_path))
                return {'status': 'started', 'message': f'脚本 {script_name} 已开始运行'}
            else:
                return await self._run_script_direct(script_name, str(script_path))
        except Exception as e:
            print(f"运行脚本失败 {script_name}: {e}")
            self.script_status[script_name] = 'failed'
            await self.sio.emit('status_update', self.get_scripts_status())
            return {'status': 'error', 'message': str(e)}
    
    async def _run_script_direct(self, script_name: str, script_path: str) -> Dict[str, Any]:
        """直接运行脚本"""
        try:
            # 使用subprocess运行脚本
            result = subprocess.run(
                [sys.executable, script_path, '--quiet'],
                capture_output=True,
                text=True,
                timeout=300,  # 5分钟超时
                cwd=str(self.project_root)
            )
            # 更新状态
            if result.returncode == 0:
                self.script_status[script_name] = 'completed'
                status = 'success'
            else:
                self.script_status[script_name] = 'failed'
                status = 'failed'
            self.script_status[f"{script_name}_last_run"] = time.time()
            # 广播状态更新
            await self.sio.emit('status_update', self.get_scripts_status())
            return {
                'status': status,
                'return_code': result.returncode,
                'stdout': result.stdout[-1000:],  # 最后1000字符
                'stderr': result.stderr[-1000:] if result.stderr else ''
            }
        except subprocess.TimeoutExpired:
            self.script_status[script_name] = 'timeout'
            await self.sio.emit('status_update', self.get_scripts_status())
            return {'status': 'timeout', 'message': '脚本执行超时'}
        except Exception as e:
            self.script_status[script_name] = 'error'
            await self.sio.emit('status_update', self.get_scripts_status())
            return {'status': 'error', 'message': str(e)}
    
    async def _run_script_background(self, script_name: str, script_path: str):
        """后台运行脚本"""
        try:
            result = await self._run_script_direct(script_name, script_path)
            # 发送结果通知
            await self.sio.emit('script_completed', {
                'script': script_name,
                'result': result
            })
        except Exception as e:
            print(f"后台脚本执行失败 {script_name}: {e}")
            await self.sio.emit('script_error', {
                'script': script_name,
                'error': str(e)
            })
    
    def stop_script(self, script_name: str) -> Dict[str, Any]:
        """停止脚本"""
        # 这里可以实现脚本停止逻辑
        self.script_status[script_name] = 'stopped'
        return {'status': 'stopped', 'message': f'脚本 {script_name} 已停止'}
    
    def get_script_logs(self, script_name: str, lines: int = 100) -> Dict[str, Any]:
        """获取脚本日志"""
        log_file = self.project_root / 'logs' / f'{script_name}.log'
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    all_lines = f.readlines()
                    recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                return {
                    'status': 'success',
                    'logs': recent_lines,
                    'total_lines': len(all_lines),
                    'returned_lines': len(recent_lines)
                }
            except Exception as e:
                return {'status': 'error', 'message': str(e)}
        return {'status': 'not_found', 'message': '日志文件不存在'}
    
    def start_monitoring_scheduler(self):
        """启动监控调度器"""
        def run_scheduled_scripts():
            """运行定时脚本"""
            asyncio.create_task(self.run_scheduled_scripts())
        # 每小时检查一次
        schedule.every().hour.do(run_scheduled_scripts)
        def scheduler_loop():
            while self.monitoring_active:
                schedule.run_pending()
                time.sleep(60)
        self.monitoring_active = True
        scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
        scheduler_thread.start()
        print("监控调度器已启动")
    
    async def run_scheduled_scripts(self):
        """运行定时脚本"""
        # 这里可以实现定时脚本运行逻辑
        pass
