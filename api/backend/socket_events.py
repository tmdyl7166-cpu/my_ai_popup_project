"""
Socket.IO事件处理器
负责处理WebSocket事件
"""
import json
from typing import Dict, Any

class SocketEventHandler:
    """Socket.IO事件处理器"""
    
    def __init__(self, sio, app):
        self.sio = sio
        self.app = app
    
    def setup_socket_events(self):
        """设置Socket.IO事件"""
        @self.sio.event
        async def connect(sid, environ):
            print(f"客户端连接: {sid}")
            await self.sio.emit('status_update', self.app.script_manager.get_scripts_status(), to=sid)
        
        @self.sio.event
        async def disconnect(sid):
            print(f"客户端断开: {sid}")
        
        @self.sio.event
        async def request_status(sid):
            """请求状态更新"""
            await self.sio.emit('status_update', self.app.script_manager.get_scripts_status(), to=sid)
        
        @self.sio.event
        async def run_script(sid, script_name):
            """运行脚本"""
            result = await self.app.script_manager.run_script_async(script_name)
            await self.sio.emit('script_result', {
                'script': script_name,
                'result': result
            }, to=sid)
