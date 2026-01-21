#!/usr/bin/env python3
"""
速率限制中间件
提供API速率限制功能，防止滥用
"""

import time
import asyncio
from collections import defaultdict
from typing import Dict, Tuple, Optional
import logging

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from src.utils.logger import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """速率限制器"""

    def __init__(self):
        # 存储请求记录: {client_key: [(timestamp, count), ...]}
        self.requests: Dict[str, list] = defaultdict(list)

        # 速率限制配置
        self.rate_limits = {
            "default": (100, 60),  # 每60秒最多100个请求
            "strict": (10, 60),    # 每60秒最多10个请求
            "login": (5, 300),     # 每5分钟最多5次登录尝试
        }

        # 清理过期记录的间隔（秒）
        self.cleanup_interval = 300  # 5分钟
        self.last_cleanup = time.time()

    def _get_client_key(self, request: Request, use_ip: bool = True) -> str:
        """
        获取客户端标识符

        Args:
            request: FastAPI请求对象
            use_ip: 是否使用IP地址作为标识符

        Returns:
            str: 客户端键
        """
        if use_ip:
            # 使用IP地址
            client_ip = request.client.host if request.client else "unknown"
            return f"ip:{client_ip}"
        else:
            # 使用用户ID（如果已认证）
            # 这里可以扩展为使用用户ID
            client_ip = request.client.host if request.client else "unknown"
            return f"ip:{client_ip}"

    def _cleanup_old_requests(self):
        """清理过期的请求记录"""
        current_time = time.time()
        if current_time - self.last_cleanup < self.cleanup_interval:
            return

        cutoff_time = current_time - max(limit[1] for limit in self.rate_limits.values())

        for client_key in list(self.requests.keys()):
            self.requests[client_key] = [
                (timestamp, count) for timestamp, count in self.requests[client_key]
                if timestamp > cutoff_time
            ]

            # 如果没有记录了，删除键
            if not self.requests[client_key]:
                del self.requests[client_key]

        self.last_cleanup = current_time

    def _is_rate_limited(self, client_key: str, limit: Tuple[int, int]) -> Tuple[bool, float]:
        """
        检查是否超过速率限制

        Args:
            client_key: 客户端键
            limit: (最大请求数, 时间窗口秒数)

        Returns:
            Tuple[bool, float]: (是否限制, 剩余等待时间)
        """
        max_requests, window_seconds = limit
        current_time = time.time()

        # 获取该客户端的请求记录
        client_requests = self.requests[client_key]

        # 过滤出时间窗口内的请求
        window_start = current_time - window_seconds
        recent_requests = [
            (timestamp, count) for timestamp, count in client_requests
            if timestamp > window_start
        ]

        # 计算总请求数
        total_requests = sum(count for _, count in recent_requests)

        if total_requests >= max_requests:
            # 计算最早可以再次请求的时间
            if recent_requests:
                oldest_request_time = min(timestamp for timestamp, _ in recent_requests)
                wait_time = window_seconds - (current_time - oldest_request_time)
                return True, max(0, wait_time)
            else:
                return True, window_seconds

        return False, 0.0

    def check_rate_limit(self, request: Request, limit_type: str = "default") -> None:
        """
        检查速率限制

        Args:
            request: FastAPI请求对象
            limit_type: 限制类型

        Raises:
            HTTPException: 超过速率限制
        """
        # 清理过期记录
        self._cleanup_old_requests()

        # 获取限制配置
        if limit_type not in self.rate_limits:
            limit_type = "default"
        limit = self.rate_limits[limit_type]

        # 获取客户端键
        client_key = self._get_client_key(request)

        # 检查是否超过限制
        is_limited, wait_time = self._is_rate_limited(client_key, limit)

        if is_limited:
            logger.warning(f"速率限制触发: {client_key}, 等待时间: {wait_time:.1f}秒")
            raise HTTPException(
                status_code=429,
                detail=f"请求过于频繁，请在 {wait_time:.1f} 秒后重试"
            )

        # 记录请求
        current_time = time.time()
        self.requests[client_key].append((current_time, 1))

        logger.debug(f"请求记录: {client_key}, 当前计数: {sum(count for _, count in self.requests[client_key])}")


# 全局速率限制器实例
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """获取速率限制器实例（单例模式）"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


async def rate_limit_middleware(request: Request, call_next):
    """
    速率限制中间件

    Args:
        request: FastAPI请求对象
        call_next: 下一个中间件/处理函数

    Returns:
        Response: 响应对象
    """
    # 获取路径对应的限制类型
    path = request.url.path

    # 根据路径设置不同的限制
    if path.startswith("/api/auth/login"):
        limit_type = "login"
    elif path.startswith("/api/admin"):
        limit_type = "strict"
    else:
        limit_type = "default"

    # 检查速率限制
    rate_limiter = get_rate_limiter()
    rate_limiter.check_rate_limit(request, limit_type)

    # 继续处理请求
    response = await call_next(request)
    return response


def create_rate_limited_response() -> JSONResponse:
    """创建速率限制响应"""
    return JSONResponse(
        status_code=429,
        content={
            "detail": "请求过于频繁，请稍后再试",
            "type": "rate_limit_exceeded"
        }
    )


__all__ = [
    "RateLimiter",
    "get_rate_limiter",
    "rate_limit_middleware",
    "create_rate_limited_response"
]
