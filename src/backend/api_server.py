"""API服务器模块

提供统一的API服务器接口，封装control_core中的FastAPI应用。
支持结构化日志、API请求记录和性能监控。
"""

import os
import sys
import time
import uuid
import logging
from datetime import datetime
from typing import Optional

# 添加项目根目录到路径
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, PROJECT_ROOT)

# 导入日志配置
try:
    from src.backend.logging_config import (
        setup_logging,
        log_api_request,
        log_performance_metric,
        get_request_logger,
        StructuredFormatter,
    )

    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False

# 尝试导入uvicorn
try:
    import uvicorn

    UVICORN_AVAILABLE = True
except ImportError:
    UVICORN_AVAILABLE = False

# 导入FastAPI应用
try:
    from src.backend.control_core.server import app, main as run_server

    FASTAPI_AVAILABLE = True
except ImportError as e:
    FASTAPI_AVAILABLE = False
    app = None
    run_server = None
    print(f"警告: 无法导入FastAPI应用: {e}")


class APIServer:
    """API服务器封装类"""

    def __init__(self, host="0.0.0.0", port=8000, reload=False, log_level="INFO"):
        """
        初始化API服务器

        Args:
            host: 监听地址
            port: 监听端口
            reload: 是否启用热重载
            log_level: 日志级别
        """
        self.host = host
        self.port = port
        self.reload = reload
        self.log_level = log_level

        # 设置日志
        self._setup_logging()

        # 获取日志器
        self.logger = logging.getLogger("api_server")
        self.logger.info(f"API服务器初始化: {host}:{port}")

        # 配置FastAPI日志
        if FASTAPI_AVAILABLE and app is not None:
            self._configure_fastapi_logging()

    def _setup_logging(self):
        """设置日志配置"""
        if LOGGING_AVAILABLE:
            loggers = setup_logging(
                log_level=self.log_level,
                log_to_file=True,
                log_to_console=True,
                enable_bubbles=True,
            )
            self.api_logger = loggers.get("api")
            self.perf_logger = loggers.get("performance")
        else:
            # 使用标准日志
            logging.basicConfig(
                level=getattr(logging, self.log_level.upper(), logging.INFO),
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            )
            self.api_logger = None
            self.perf_logger = None

    def _configure_fastapi_logging(self):
        """配置FastAPI日志"""
        # 配置访问日志
        access_logger = logging.getLogger("uvicorn.access")
        if access_logger:
            access_logger.setLevel(logging.DEBUG)

            # 添加文件处理器
            log_dir = os.path.join(PROJECT_ROOT, "logs")
            os.makedirs(log_dir, exist_ok=True)

            from logging.handlers import RotatingFileHandler

            # 访问日志文件
            access_log_file = os.path.join(
                log_dir, f"access_{datetime.now().strftime('%Y%m%d')}.log"
            )
            access_handler = RotatingFileHandler(
                access_log_file,
                maxBytes=20 * 1024 * 1024,  # 20MB
                backupCount=7,
                encoding="utf-8",
            )
            access_handler.setLevel(logging.DEBUG)
            access_handler.setFormatter(StructuredFormatter())
            access_logger.addHandler(access_handler)

    def _add_request_logging_middleware(self):
        """添加请求日志中间件"""
        if app is None:
            return

        @app.middleware("http")
        async def log_requests(request: dict, call_next):
            """记录每个API请求"""
            start_time = time.time()

            # 生成请求ID
            request_id = str(uuid.uuid4())[:8]

            # 获取请求信息
            method = request.get("method", "UNKNOWN")
            endpoint = request.get("url", {}).get("path", "/")
            client_ip = request.get("client", {}).get("host", "unknown")
            user_agent = request.get("headers", {}).get("user-agent", "unknown")

            try:
                # 处理请求
                response = await call_next(request)
                status_code = (
                    response.status_code if hasattr(response, "status_code") else 200
                )
            except Exception as e:
                status_code = 500
                if self.api_logger:
                    self.api_logger.error(f"请求处理错误: {endpoint} - {str(e)}")
                raise
            finally:
                # 计算响应时间
                response_time = time.time() - start_time

                # 记录API请求
                if self.api_logger:
                    log_api_request(
                        self.api_logger,
                        method=method,
                        endpoint=endpoint,
                        status_code=status_code,
                        response_time=response_time,
                        client_ip=client_ip,
                        user_agent=user_agent,
                    )

                # 记录性能指标
                if self.perf_logger:
                    log_performance_metric(
                        self.perf_logger,
                        metric_name="api_response_time",
                        value=response_time * 1000,  # 转换为毫秒
                        unit="ms",
                        tags={
                            "endpoint": endpoint,
                            "method": method,
                            "status": str(status_code),
                        },
                    )

            return response

    def start(self):
        """启动服务器"""
        if not UVICORN_AVAILABLE:
            print("错误: uvicorn 未安装，请运行: pip install uvicorn")
            return False

        if not FASTAPI_AVAILABLE or app is None:
            print("错误: FastAPI 应用未加载")
            return False

        self.logger.info(f"启动API服务器: {self.host}:{self.port}")

        # 启动浏览器（如果配置了AUTO_BROWSER）
        if os.environ.get("AUTO_BROWSER", "false").lower() == "true":
            import webbrowser

            webbrowser.open(f"http://{self.host}:{self.port}")
            self.logger.info("自动打开浏览器")

        # 配置uvicorn日志
        log_config = uvicorn.config.LOGGING_CONFIG
        log_config["formatters"]["default"][
            "fmt"
        ] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        log_config["formatters"]["access"][
            "fmt"
        ] = '%(asctime)s - %(levelname)s - %(client_addr)s - "%(request_line)s" %(status_code)s'

        # 启动服务器
        uvicorn.run(
            app,
            host=self.host,
            port=self.port,
            reload=self.reload,
            log_level=self.log_level.lower(),
            log_config=log_config,
        )

        return True


def create_server(
    host="0.0.0.0", port=8000, reload=False, log_level="INFO"
) -> APIServer:
    """
    创建API服务器实例

    Args:
        host: 监听地址
        port: 监听端口
        reload: 是否启用热重载
        log_level: 日志级别

    Returns:
        APIServer实例
    """
    return APIServer(host=host, port=port, reload=reload, log_level=log_level)


# 导出
__all__ = ["app", "run_server", "APIServer", "create_server"]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="API服务器")
    parser.add_argument("--host", default="0.0.0.0", help="监听地址")
    parser.add_argument("--port", type=int, default=8000, help="监听端口")
    parser.add_argument("--reload", action="store_true", help="启用热重载")
    parser.add_argument(
        "--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"]
    )

    args = parser.parse_args()

    server = create_server(
        host=args.host, port=args.port, reload=args.reload, log_level=args.log_level
    )
    server.start()
