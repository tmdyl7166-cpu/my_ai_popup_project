"""
日志中间件
记录API请求和响应
"""
import time
import logging
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse

from src.utils.logger import get_logger

logger = get_logger(__name__)


class LoggingMiddleware:
    """API日志中间件"""

    def __init__(self, app: Callable):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # 记录请求开始
        start_time = time.time()
        method = scope["method"]
        path = scope["path"]
        query_string = scope.get("query_string", b"").decode("utf-8")

        logger.info(f"API请求开始: {method} {path} {query_string}")

        # 处理请求
        response_started = False
        response_status = None

        async def send_wrapper(message):
            nonlocal response_started, response_status

            if message["type"] == "http.response.start":
                response_started = True
                response_status = message["status"]

            await send(message)

            if message["type"] == "http.response.body" and response_started:
                # 记录请求完成
                duration = time.time() - start_time
                logger.info(f"API请求完成: {method} {path} 状态码: {response_status} 耗时: {duration:.3f}s")

        await self.app(scope, receive, send_wrapper)


async def log_requests(request: Request, call_next):
    """FastAPI中间件函数"""
    start_time = time.time()

    # 记录请求
    logger.info(f"API请求: {request.method} {request.url}")

    try:
        response = await call_next(request)

        # 记录响应
        duration = time.time() - start_time
        logger.info(f"API响应: {request.method} {request.url} 状态码: {response.status_code} 耗时: {duration:.3f}s")

        return response

    except Exception as e:
        # 记录错误
        duration = time.time() - start_time
        logger.error(f"API错误: {request.method} {request.url} 错误: {str(e)} 耗时: {duration:.3f}s")
        raise


class RequestLoggingMiddleware:
    """请求日志中间件类"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        # 提取请求信息
        method = scope.get("method", "")
        path = scope.get("path", "")
        query = scope.get("query_string", b"").decode("utf-8")
        headers = dict(scope.get("headers", []))

        # 记录请求开始
        logger.info(f"HTTP请求: {method} {path}{'?' + query if query else ''}")

        # 处理请求
        start_time = time.time()

        async def logging_send(message):
            if message["type"] == "http.response.start":
                status_code = message["status"]
                duration = time.time() - start_time
                logger.info(f"HTTP响应: {method} {path} 状态码: {status_code} 耗时: {duration:.3f}s")

            await send(message)

        await self.app(scope, receive, logging_send)
