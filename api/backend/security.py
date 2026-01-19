#!/usr/bin/env python3
"""
Web安全中间件模块
提供输入验证、API密钥认证、速率限制、安全头等安全功能
"""

import os
import time
import logging
from typing import Dict, Any, Optional
from collections import defaultdict
from dataclasses import dataclass
from fastapi import Request, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader, APIKeyQuery
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)

# ========================================
# 配置
# ========================================
class SecurityConfig:
    """安全配置"""
    # API密钥
    API_KEY: str = os.getenv("API_KEY", "dev-api-key-change-in-production")
    
    # 速率限制
    RATE_LIMIT_MAX_REQUESTS: int = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "100"))
    RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
    
    # CORS配置
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")
    CORS_METHODS: list = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_HEADERS: list = ["X-API-Key", "Content-Type", "Authorization"]
    
    # 允许的主机
    ALLOWED_HOSTS: list = os.getenv("ALLOWED_HOSTS", "*").split(",")
    
    # 调试模式
    DEBUG: bool = os.getenv("DEBUG", "0") == "1"
    APP_ENV: str = os.getenv("APP_ENV", "development")


# ========================================
# 输入验证模型
# ========================================
from pydantic import BaseModel, Field, validator
from typing import List, Optional

class ScriptRunRequest(BaseModel):
    """脚本运行请求验证"""
    script_name: str = Field(
        ..., 
        min_length=1, 
        max_length=100, 
        pattern=r'^[a-zA-Z0-9_-]+$',
        description="脚本名称，只能包含字母、数字、下划线和连字符"
    )
    timeout: Optional[int] = Field(
        default=300, 
        ge=1, 
        le=3600,
        description="超时时间（秒）"
    )
    parameters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="脚本参数"
    )

class ConfigUpdateRequest(BaseModel):
    """配置更新请求验证"""
    component: str = Field(
        ..., 
        min_length=1, 
        max_length=50,
        pattern=r'^[a-zA-Z0-9_-]+$',
        description="组件名称"
    )
    config: Dict[str, Any] = Field(
        ...,
        description="配置数据"
    )
    
    @validator('component')
    def validate_component(cls, v):
        allowed_components = {'project', 'frontend', 'backend', 'scripts', 'web'}
        if v not in allowed_components:
            raise ValueError(f'组件必须为以下之一: {allowed_components}')
        return v

class PaginationParams(BaseModel):
    """分页参数"""
    page: int = Field(default=1, ge=1, description="页码")
    limit: int = Field(default=50, ge=1, le=100, description="每页数量")


# ========================================
# 速率限制器
# ========================================
class RateLimiter:
    """速率限制器"""
    
    def __init__(self, max_requests: int = 100, window: int = 60):
        self.max_requests = max_requests
        self.window = window
        self.requests: defaultdict[str, list] = defaultdict(list)
    
    def is_allowed(self, key: str) -> tuple[bool, int]:
        """
        检查是否允许请求
        
        Returns:
            (是否允许, 剩余请求数)
        """
        now = time.time()
        window_start = now - self.window
        
        # 清理旧请求记录
        self.requests[key] = [t for t in self.requests[key] if t > window_start]
        
        remaining = self.max_requests - len(self.requests[key])
        
        if len(self.requests[key]) >= self.max_requests:
            logger.warning(f"速率限制触发: {key}, 剩余请求: 0")
            return False, 0
        
        # 记录当前请求
        self.requests[key].append(now)
        
        return True, remaining - 1
    
    def get_remaining(self, key: str) -> int:
        """获取剩余请求数"""
        now = time.time()
        window_start = now - self.window
        self.requests[key] = [t for t in self.requests[key] if t > window_start]
        return max(0, self.max_requests - len(self.requests[key]))
    
    def reset(self, key: str):
        """重置指定key的计数"""
        self.requests[key] = []


# 全局速率限制器实例
rate_limiter = RateLimiter(
    max_requests=SecurityConfig.RATE_LIMIT_MAX_REQUESTS,
    window=SecurityConfig.RATE_LIMIT_WINDOW_SECONDS
)


# ========================================
# API密钥认证
# ========================================
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
api_key_query = APIKeyQuery(name="api_key", auto_error=False)


async def verify_api_key(
    api_key: Optional[str] = Security(api_key_header),
    query_key: Optional[str] = Security(api_key_query)
) -> str:
    """验证API密钥"""
    key = api_key or query_key
    
    if not key:
        raise HTTPException(
            status_code=403,
            detail="缺少API密钥，请提供 X-API-Key 请求头或 api_key 查询参数"
        )
    
    if key != SecurityConfig.API_KEY:
        logger.warning(f"无效的API密钥尝试: {key[:8]}...")
        raise HTTPException(
            status_code=403,
            detail="无效的API密钥"
        )
    
    return key


# 依赖注入的认证依赖
require_api_key = Depends(verify_api_key)


# ========================================
# 安全头中间件
# ========================================
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """安全头中间件 - 添加HTTP安全响应头"""
    
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        
        # 安全相关响应头
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response


# ========================================
# 主机验证中间件
# ========================================
class HostValidationMiddleware(BaseHTTPMiddleware):
    """主机验证中间件 - 防止主机头攻击"""
    
    async def dispatch(self, request: Request, call_next):
        # 获取请求的主机头
        host = request.headers.get("host", "")
        
        # 在生产环境中验证主机
        if SecurityConfig.APP_ENV == "production" and SecurityConfig.ALLOWED_HOSTS != ["*"]:
            if host not in SecurityConfig.ALLOWED_HOSTS:
                logger.warning(f"主机头验证失败: {host}")
                raise HTTPException(
                    status_code=400,
                    detail="无效的请求主机"
                )
        
        response = await call_next(request)
        return response


# ========================================
# 速率限制中间件
# ========================================
class RateLimitMiddleware(BaseHTTPMiddleware):
    """速率限制中间件"""
    
    async def dispatch(self, request: Request, call_next):
        # 获取客户端IP作为限流key
        client_ip = request.client.host if request.client else "unknown"
        rate_limit_key = f"{client_ip}:{request.url.path}"
        
        allowed, remaining = rate_limiter.is_allowed(rate_limit_key)
        
        # 添加速率限制响应头
        headers = {
            "X-RateLimit-Limit": str(SecurityConfig.RATE_LIMIT_MAX_REQUESTS),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Window": str(SecurityConfig.RATE_LIMIT_WINDOW_SECONDS)
        }
        
        if not allowed:
            return Response(
                content="Too Many Requests",
                status_code=429,
                headers=headers
            )
        
        response = await call_next(request)
        
        # 添加响应头
        for key, value in headers.items():
            response.headers[key] = value
        
        return response


# ========================================
# 请求日志中间件
# ========================================
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # 记录请求
        logger.info(f"请求: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            
            # 记录响应
            logger.info(
                f"响应: {request.method} {request.url.path} - "
                f"状态:{response.status_code} - 耗时:{duration:.3f}s"
            )
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"错误: {request.method} {request.url.path} - "
                f"错误:{str(e)} - 耗时:{duration:.3f}s"
            )
            raise


# ========================================
# 安全工具函数
# ========================================
def sanitize_input(input_str: str) -> str:
    """清理输入字符串，防止注入攻击"""
    import re
    # 移除可能的恶意模式
    sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', input_str)
    sanitized = re.sub(r'<[^>]*>', '', sanitized)  # 移除HTML标签
    sanitized = re.sub(r'[\'";\-\-]', '', sanitized)  # 移除SQL注入特征
    return sanitized.strip()


def validate_file_path(file_path: str, allowed_dir: str) -> bool:
    """验证文件路径安全"""
    import os
    
    # 转换为绝对路径
    abs_path = os.path.abspath(os.path.join(allowed_dir, file_path))
    
    # 确保路径在允许的目录内
    if not abs_path.startswith(os.path.abspath(allowed_dir)):
        return False
    
    # 检查路径遍历攻击
    if '..' in file_path or file_path.startswith('/'):
        return False
    
    return True


def generate_api_key(length: int = 32) -> str:
    """生成安全的API密钥"""
    import secrets
    import string
    
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


# ========================================
# 安全配置检查
# ========================================
def check_security_config() -> Dict[str, Any]:
    """检查安全配置状态"""
    issues = []
    
    # 检查API密钥是否使用默认值
    if SecurityConfig.API_KEY == "dev-api-key-change-in-production":
        issues.append({
            "severity": "high",
            "message": "API密钥使用默认值，请在生产环境中修改"
        })
    
    # 检查是否在生产环境使用调试模式
    if SecurityConfig.APP_ENV == "production" and SecurityConfig.DEBUG:
        issues.append({
            "severity": "high",
            "message": "生产环境不应启用调试模式"
        })
    
    # 检查CORS配置
    if "*" in SecurityConfig.CORS_ORIGINS and SecurityConfig.APP_ENV == "production":
        issues.append({
            "severity": "medium",
            "message": "生产环境CORS应限制特定来源"
        })
    
    return {
        "status": "secure" if not issues else "warning",
        "issues": issues,
        "environment": SecurityConfig.APP_ENV,
        "debug": SecurityConfig.DEBUG
    }


# ========================================
# 导出
# ========================================
__all__ = [
    # 配置
    "SecurityConfig",
    "SecurityConfig",
    
    # 验证模型
    "ScriptRunRequest",
    "ConfigUpdateRequest",
    "PaginationParams",
    
    # 认证
    "verify_api_key",
    "require_api_key",
    
    # 速率限制
    "RateLimiter",
    "rate_limiter",
    
    # 中间件
    "SecurityHeadersMiddleware",
    "HostValidationMiddleware",
    "RateLimitMiddleware",
    "RequestLoggingMiddleware",
    
    # 工具函数
    "sanitize_input",
    "validate_file_path",
    "generate_api_key",
    "check_security_config",
]

