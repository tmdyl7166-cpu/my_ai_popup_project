"""
Web监控应用主类
整合所有管理器，提供统一的监控界面
"""
import os
import sys
import json
import time
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import subprocess
import threading
import schedule

import uvicorn
from fastapi import FastAPI, Request, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import socketio
import psutil

from .script_manager import ScriptManager
from .system_monitor import SystemMonitor
from .config_manager import ConfigManager
from .deployment_monitor import DeploymentMonitor
from .socket_events import SocketEventHandler

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
        
        # 初始化FastAPI应用
        self.app = FastAPI(title="AI弹窗项目监控中心", version="1.0.0")
        
        # Socket.IO for real-time updates
        self.sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
        self.socket_app = socketio.ASGIApp(self.sio, self.app)
        
        # 模板和静态文件
        self.templates = Jinja2Templates(directory=str(self.web_root / "templates"))
        
        # 挂载静态文件
        self.app.mount("/static", StaticFiles(directory=str(self.web_root / "static")), name="static")
        
        # 初始化管理器
        self.script_manager = ScriptManager(self.project_root, self.sio, self.script_status)
        self.system_monitor = SystemMonitor()
        self.config_manager = ConfigManager(self.project_root)
        self.deployment_monitor = DeploymentMonitor(self.project_root)
        
        # 初始化Socket事件处理器
        self.socket_handler = SocketEventHandler(self.sio, self)
        
        # 注册路由
        self.setup_routes()
        
        # 注册Socket.IO事件
        self.socket_handler.setup_socket_events()
        
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
            return self.script_manager.get_scripts_status()
        
        @self.app.get("/api/scripts/list")
        async def scripts_list():
            """脚本列表"""
            return self.script_manager.get_scripts_list()
        
        @self.app.post("/api/scripts/run/{script_name}")
        async def run_script(script_name: str, background_tasks: BackgroundTasks):
            """运行指定脚本"""
            return await self.script_manager.run_script_async(script_name, background_tasks)
        
        @self.app.post("/api/scripts/stop/{script_name}")
        async def stop_script(script_name: str):
            """停止指定脚本"""
            return self.script_manager.stop_script(script_name)
        
        @self.app.get("/api/logs/{script_name}")
        async def get_script_logs(script_name: str, lines: int = 100):
            """获取脚本日志"""
            return self.script_manager.get_script_logs(script_name, lines)
        
        @self.app.get("/api/config/{component}")
        async def get_config(component: str):
            """获取配置信息"""
            return self.config_manager.get_component_config(component)
        
        @self.app.post("/api/config/{component}")
        async def update_config(component: str, config: Dict[str, Any]):
            """更新配置"""
            return self.config_manager.update_component_config(component, config)
        
        @self.app.get("/api/deployment/progress")
        async def deployment_progress():
            """部署进度"""
            return self.deployment_monitor.get_deployment_progress()
        
        @self.app.get("/api/system/resources")
        async def system_resources():
            """系统资源使用情况"""
            return self.system_monitor.get_system_resources()
        
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
    
    async def handle_monitoring_message(self, message: str) -> Dict[str, Any]:
        """处理监控消息"""
        try:
            data = json.loads(message)
            action = data.get('action')
            
            if action == 'get_status':
                return self.script_manager.get_scripts_status()
            elif action == 'run_script':
                script_name = data.get('script')
                if script_name:
                    result = await self.script_manager.run_script_async(script_name)
                    return {'action': 'script_result', 'script': script_name, 'result': result}
            
            return {'error': '未知操作'}
        
        except Exception as e:
            return {'error': str(e)}
    
    def run(self, host: str = "0.0.0.0", port: int = 8080):
        """运行应用"""
        logger.info(f"启动Web监控应用: http://{host}:{port}")
        
        # 启动监控调度器
        self.script_manager.start_monitoring_scheduler()
        
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
