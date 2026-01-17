"""API服务器模块

提供统一的API服务器接口，封装control_core中的FastAPI应用。
"""

from src.backend.control_core.server import app, main as run_server


class APIServer:
    """API服务器封装类"""
    
    def __init__(self, host='0.0.0.0', port=8000, reload=False):
        self.host = host
        self.port = port
        self.reload = reload
        self.app = app
    
    def start(self):
        """启动服务器"""
        import uvicorn
        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            reload=self.reload,
            log_level="info"
        )


__all__ = ["app", "run_server", "APIServer"]

