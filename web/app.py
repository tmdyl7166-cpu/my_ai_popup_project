#!/usr/bin/env python3
"""
AI弹窗项目Web管理界面
提供统一的脚本监控、API调试、部署进度查看等功能
"""

import os
import sys
import json
import time
import asyncio
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import subprocess
import threading
import schedule

# ========================================
# Sentry SDK 初始化 (必须在 FastAPI 导入之前)
# ========================================
import sentry_sdk

sentry_sdk.init(
    dsn="https://4d6820ea296e34011b2e4db3e747b87d@o4510728365015040.ingest.us.sentry.io/4510728434483200",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)

# ========================================
# FastAPI 和相关导入
# ========================================
import os
import uvicorn
from fastapi import FastAPI, Request, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import socketio
import psutil

# 导入安全模块
try:
    from .security import (
        SecurityHeadersMiddleware,
        HostValidationMiddleware,
        RateLimitMiddleware,
        RequestLoggingMiddleware,
        verify_api_key,
        ScriptRunRequest,
        ConfigUpdateRequest,
        check_security_config
    )
except ImportError:
    from security import (
        SecurityHeadersMiddleware,
        HostValidationMiddleware,
        RateLimitMiddleware,
        RequestLoggingMiddleware,
        verify_api_key,
        ScriptRunRequest,
        ConfigUpdateRequest,
        check_security_config
    )

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/web_app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class WebMonitorApp:
    """Web监控应用主类"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.web_root = Path(__file__).parent

        # 应用状态
        self.script_status = {}
        self.monitoring_active = False
        self.scheduled_tasks = {}

        # 初始化FastAPI应用
        self.app = FastAPI(title="AI弹窗项目监控中心", version="1.0.0")

        # 添加安全中间件（按顺序：先日志，再速率限制，然后主机验证，最后安全头）
        self.app.add_middleware(RequestLoggingMiddleware)
        self.app.add_middleware(RateLimitMiddleware)
        self.app.add_middleware(HostValidationMiddleware)
        self.app.add_middleware(SecurityHeadersMiddleware)

        # Socket.IO for real-time updates
        self.sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
        self.socket_app = socketio.ASGIApp(self.sio, self.app)

        # 模板和静态文件
        self.templates = Jinja2Templates(directory=str(self.web_root / "templates"))

        # 挂载静态文件
        self.app.mount("/static", StaticFiles(directory=str(self.web_root / "static")), name="static")

        # 注册路由
        self.setup_routes()

        # 注册Socket.IO事件
        self.setup_socket_events()

        logger.info("Web监控应用初始化完成")

    def setup_routes(self):
        """设置路由"""

        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard(request: Request):
            """主仪表板"""
            return self.templates.TemplateResponse("dashboard.html", {
                "request": request,
                "title": "AI弹窗项目监控中心"
            })

        @self.app.get("/api/health")
        async def health_check():
            """健康检查"""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0"
            }

        @self.app.get("/api/project/status")
        async def project_status():
            """项目整体状态"""
            return await self.get_project_status()

        @self.app.get("/api/scripts/status")
        async def scripts_status():
            """脚本运行状态"""
            return self.get_scripts_status()

        @self.app.get("/api/scripts/list")
        async def scripts_list():
            """脚本列表"""
            return self.get_scripts_list()

        @self.app.post("/api/scripts/run/{script_name}")
        async def run_script(script_name: str, background_tasks: BackgroundTasks):
            """运行指定脚本"""
            return await self.run_script_async(script_name, background_tasks)

        @self.app.post("/api/scripts/stop/{script_name}")
        async def stop_script(script_name: str):
            """停止指定脚本"""
            return self.stop_script(script_name)

        @self.app.get("/api/logs/{script_name}")
        async def get_script_logs(script_name: str, lines: int = 100):
            """获取脚本日志"""
            return self.get_script_logs(script_name, lines)

        @self.app.get("/api/config/{component}")
        async def get_config(component: str):
            """获取配置信息"""
            return self.get_component_config(component)

        @self.app.post("/api/config/{component}")
        async def update_config(component: str, config: Dict[str, Any]):
            """更新配置"""
            return self.update_component_config(component, config)

        @self.app.get("/api/deployment/progress")
        async def deployment_progress():
            """部署进度"""
            return self.get_deployment_progress()

        @self.app.get("/api/system/resources")
        async def system_resources():
            """系统资源使用情况"""
            return self.get_system_resources()

        # 仅在调试/开发环境暴露 Sentry 测试路由，避免在生产环境中增加攻击面和污染 Sentry 数据
        if os.getenv("APP_ENV", "development") in {"development", "dev", "local"} or os.getenv("DEBUG", "0") == "1":
            @self.app.get("/sentry-debug")
            async def trigger_error():
                """Sentry SDK 验证路由 - 故意触发错误以测试监控（仅开发环境启用）"""
                # 故意触发异常，用于验证 Sentry 捕获能力
                1 / 0

        @self.app.websocket("/ws/monitoring")
        async def monitoring_websocket(websocket: WebSocket):
            """监控WebSocket"""
            await websocket.accept()
            try:
                while True:
                    data = await websocket.receive_text()
                    # 处理监控数据
                    response = await self.handle_monitoring_message(data)
                    await websocket.send_text(json.dumps(response))
            except WebSocketDisconnect:
                logger.info("监控WebSocket连接断开")

    def setup_socket_events(self):
        """设置Socket.IO事件"""

        @self.sio.event
        async def connect(sid, environ):
            logger.info(f"客户端连接: {sid}")
            await self.sio.emit('status_update', self.get_scripts_status(), to=sid)

        @self.sio.event
        async def disconnect(sid):
            logger.info(f"客户端断开: {sid}")

        @self.sio.event
        async def request_status(sid):
            """请求状态更新"""
            await self.sio.emit('status_update', self.get_scripts_status(), to=sid)

        @self.sio.event
        async def run_script(sid, script_name):
            """运行脚本"""
            result = await self.run_script_async(script_name)
            await self.sio.emit('script_result', {
                'script': script_name,
                'result': result
            }, to=sid)

    async def get_project_status(self) -> Dict[str, Any]:
        """获取项目整体状态"""
        status = {
            'project_name': 'AI弹窗项目',
            'version': '1.0.0',
            'status': 'running',
            'components': {},
            'last_updated': datetime.now().isoformat()
        }

        # 检查各组件状态
        components = ['frontend', 'backend', 'ai', 'processing', 'integrations']
        for component in components:
            status['components'][component] = await self.check_component_status(component)

        return status

    async def check_component_status(self, component: str) -> Dict[str, Any]:
        """检查组件状态"""
        # 这里可以实现具体的组件状态检查逻辑
        return {
            'name': component,
            'status': 'healthy',
            'last_check': datetime.now().isoformat(),
            'details': {}
        }

    def get_scripts_status(self) -> Dict[str, Any]:
        """获取脚本运行状态"""
        return {
            'scripts': self.script_status,
            'monitoring_active': self.monitoring_active,
            'timestamp': datetime.now().isoformat()
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
                logger.error(f"读取脚本配置失败: {e}")

        return []

    async def run_script_async(self, script_name: str, background_tasks: Optional[BackgroundTasks] = None) -> Dict[str, Any]:
        """异步运行脚本"""
        try:
            # 更新脚本状态
            self.script_status[script_name] = 'running'
            self.script_status[f"{script_name}_start_time"] = datetime.now().isoformat()

            # 广播状态更新
            await self.sio.emit('status_update', self.get_scripts_status())

            # 构造脚本路径
            script_path = self.project_root / 'scripts' / 'health_monitor' / script_name

            if not script_path.exists():
                raise FileNotFoundError(f"脚本文件不存在: {script_path}")

            # 运行脚本
            if background_tasks is not None:
                background_tasks.add_task(self._run_script_background, script_name, str(script_path))
                return {'status': 'started', 'message': f'脚本 {script_name} 已开始运行'}
            else:
                return await self._run_script_direct(script_name, str(script_path))

        except Exception as e:
            logger.error(f"运行脚本失败 {script_name}: {e}")
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

            self.script_status[f"{script_name}_last_run"] = datetime.now().isoformat()

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
            logger.error(f"后台脚本执行失败 {script_name}: {e}")
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

    def get_component_config(self, component: str) -> Dict[str, Any]:
        """获取组件配置"""
        config_paths = {
            'project': 'project_config.json',
            'frontend': 'src/frontend/frontend_config.json',
            'backend': 'src/backend/backend_config.json',
            'scripts': 'scripts/scripts_config.json'
        }

        if component in config_paths:
            config_path = self.project_root / config_paths[component]
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as e:
                    return {'error': str(e)}

        return {'error': '组件配置不存在'}

    def update_component_config(self, component: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """更新组件配置"""
        # 这里可以实现配置更新逻辑
        return {'status': 'success', 'message': f'{component} 配置已更新'}

    def get_deployment_progress(self) -> Dict[str, Any]:
        """获取部署进度"""
        progress_dir = self.project_root / 'docs' / 'deployment_progress'

        if not progress_dir.exists():
            return {'status': 'not_found', 'message': '部署进度目录不存在'}

        # 查找所有以数字序号开头的部署进度文件
        progress_files = list(progress_dir.glob('[0-9][0-9]-*.md'))

        if progress_files:
            # 使用最新的文件（按修改时间排序）
            latest_file = max(progress_files, key=lambda f: f.stat().st_mtime)
            try:
                with open(latest_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {
                    'status': 'success',
                    'content': content,
                    'file': latest_file.name
                }
            except Exception as e:
                return {'status': 'error', 'message': str(e)}

        return {'status': 'not_found', 'message': '未找到部署进度文件'}

    def get_system_resources(self) -> Dict[str, Any]:
        """获取系统资源使用情况"""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory': {
                    'total': psutil.virtual_memory().total,
                    'available': psutil.virtual_memory().available,
                    'percent': psutil.virtual_memory().percent
                },
                'disk': {
                    'total': psutil.disk_usage('/').total,
                    'free': psutil.disk_usage('/').free,
                    'percent': psutil.disk_usage('/').percent
                },
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e)}

    async def handle_monitoring_message(self, message: str) -> Dict[str, Any]:
        """处理监控消息"""
        try:
            data = json.loads(message)
            action = data.get('action')

            if action == 'get_status':
                return self.get_scripts_status()
            elif action == 'run_script':
                script_name = data.get('script')
                if script_name:
                    result = await self.run_script_async(script_name)
                    return {'action': 'script_result', 'script': script_name, 'result': result}

            return {'error': '未知操作'}

        except Exception as e:
            return {'error': str(e)}

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
        logger.info("监控调度器已启动")

    async def run_scheduled_scripts(self):
        """运行定时脚本"""
        # 这里可以实现定时脚本运行逻辑
        pass

    def run(self, host: str = "0.0.0.0", port: int = 8080):
        """运行应用"""
        logger.info(f"启动Web监控应用: http://{host}:{port}")

        # 启动监控调度器
        self.start_monitoring_scheduler()

        # 启动服务器
        uvicorn.run(
            self.socket_app,
            host=host,
            port=port,
            log_level="info"
        )

# 创建应用实例
app_instance = WebMonitorApp()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='AI弹窗项目Web监控中心')
    parser.add_argument('--host', default='0.0.0.0', help='监听地址')
    parser.add_argument('--port', type=int, default=8080, help='监听端口')

    args = parser.parse_args()

    app_instance.run(host=args.host, port=args.port)
