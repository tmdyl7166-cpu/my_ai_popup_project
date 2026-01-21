"""
后端日志配置
Backend Logging Configuration
"""

import json
import logging
import logging.handlers
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent


class StructuredFormatter(logging.Formatter):
    """结构化日志格式化器"""

    def format(self, record: logging.LogRecord) -> str:
        # 基础日志信息
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 添加额外字段
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id

        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id

        if hasattr(record, "api_endpoint"):
            log_entry["api_endpoint"] = record.api_endpoint

        if hasattr(record, "response_time"):
            log_entry["response_time"] = record.response_time

        if hasattr(record, "status_code"):
            log_entry["status_code"] = record.status_code

        # 添加异常信息
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # 添加额外数据
        if hasattr(record, "extra_data"):
            log_entry.update(record.extra_data)

        return json.dumps(log_entry, ensure_ascii=False, default=str)


class APILogFilter(logging.Filter):
    """API日志过滤器"""

    def filter(self, record: logging.LogRecord) -> bool:
        # 过滤掉健康检查的详细日志
        if hasattr(record, "api_endpoint") and record.api_endpoint == "/health":
            return record.levelno >= logging.WARNING

        return True


class LogBubbleHandler(logging.Handler):
    """日志气泡处理器 - 用于UI通知"""

    def __init__(self, level=logging.WARNING):
        super().__init__(level)
        self.bubbles: list = []

    def emit(self, record: logging.LogRecord) -> None:
        """发出日志气泡"""
        bubble = {
            "id": f"{record.created}_{record.levelno}",
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "title": f"{record.levelname}: {record.module}",
            "message": record.getMessage(),
            "category": getattr(record, "category", "system"),
            "auto_close": record.levelno < logging.ERROR,
            "duration": 5000 if record.levelno < logging.ERROR else 10000,
        }

        # 添加到气泡列表
        self.bubbles.append(bubble)

        # 保持最多50个气泡
        if len(self.bubbles) > 50:
            self.bubbles.pop(0)

        # 在控制台输出（用于调试）
        print(f"🔔 气泡通知: {bubble['title']} - {bubble['message']}", file=sys.stderr)


def setup_logging(
    log_level: str = "INFO",
    log_to_file: bool = True,
    log_to_console: bool = True,
    enable_bubbles: bool = True,
) -> Dict[str, logging.Logger]:
    """
    设置日志配置

    Args:
        log_level: 日志级别
        log_to_file: 是否记录到文件
        log_to_console: 是否输出到控制台
        enable_bubbles: 是否启用气泡通知

    Returns:
        日志器字典
    """
    # 创建日志目录
    log_dir = PROJECT_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)

    # 根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # 清除现有处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 结构化格式化器
    structured_formatter = StructuredFormatter()

    # 控制台处理器
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(structured_formatter)
        console_handler.addFilter(APILogFilter())
        root_logger.addHandler(console_handler)

    # 文件处理器
    if log_to_file:
        # 主要日志文件
        main_log_file = log_dir / f"backend_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            main_log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(structured_formatter)
        root_logger.addHandler(file_handler)

        # 错误日志文件
        error_log_file = (
            log_dir / f"backend_error_{datetime.now().strftime('%Y%m%d')}.log"
        )
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding="utf-8",
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(structured_formatter)
        root_logger.addHandler(error_handler)

    # 气泡处理器
    if enable_bubbles:
        bubble_handler = LogBubbleHandler()
        bubble_handler.setLevel(logging.WARNING)
        root_logger.addHandler(bubble_handler)

    # 创建专用日志器
    loggers = {
        "api": logging.getLogger("api"),
        "auth": logging.getLogger("auth"),
        "database": logging.getLogger("database"),
        "websocket": logging.getLogger("websocket"),
        "health": logging.getLogger("health"),
        "performance": logging.getLogger("performance"),
        "security": logging.getLogger("security"),
        "user_action": logging.getLogger("user_action"),
    }

    # 为API日志器添加额外配置
    api_logger = loggers["api"]
    api_logger.setLevel(logging.DEBUG)

    # API专用文件处理器
    api_log_file = log_dir / f"api_{datetime.now().strftime('%Y%m%d')}.log"
    api_file_handler = logging.handlers.RotatingFileHandler(
        api_log_file, maxBytes=20 * 1024 * 1024, backupCount=7, encoding="utf-8"  # 20MB
    )
    api_file_handler.setLevel(logging.DEBUG)
    api_file_handler.setFormatter(structured_formatter)
    api_logger.addHandler(api_file_handler)

    # 性能日志器
    perf_logger = loggers["performance"]
    perf_log_file = log_dir / f"performance_{datetime.now().strftime('%Y%m%d')}.log"
    perf_file_handler = logging.handlers.RotatingFileHandler(
        perf_log_file,
        maxBytes=50 * 1024 * 1024,  # 50MB
        backupCount=3,
        encoding="utf-8",
    )
    perf_file_handler.setLevel(logging.DEBUG)
    perf_file_handler.setFormatter(structured_formatter)
    perf_logger.addHandler(perf_file_handler)

    return loggers


def get_request_logger(request_id: str, api_endpoint: str) -> logging.LoggerAdapter:
    """
    获取请求专用日志器

    Args:
        request_id: 请求ID
        api_endpoint: API端点

    Returns:
        日志器适配器
    """
    logger = logging.getLogger("api")

    class RequestAdapter(logging.LoggerAdapter):
        def process(self, msg, kwargs):
            extra = kwargs.get("extra", {})
            extra.update({"request_id": request_id, "api_endpoint": api_endpoint})
            kwargs["extra"] = extra
            return msg, kwargs

    return RequestAdapter(logger, {})


def log_api_request(
    logger: logging.LoggerAdapter,
    method: str,
    endpoint: str,
    status_code: int,
    response_time: float,
    user_id: Optional[str] = None,
    client_ip: Optional[str] = None,
    user_agent: Optional[str] = None,
):
    """
    记录API请求

    Args:
        logger: 日志器
        method: HTTP方法
        endpoint: 端点
        status_code: 状态码
        response_time: 响应时间(秒)
        user_id: 用户ID
        client_ip: 客户端IP
        user_agent: 用户代理
    """
    level = (
        logging.INFO
        if status_code < 400
        else logging.WARNING if status_code < 500 else logging.ERROR
    )

    extra_data = {
        "method": method,
        "status_code": status_code,
        "response_time": response_time,
        "category": "api_request",
    }

    if user_id:
        extra_data["user_id"] = user_id
    if client_ip:
        extra_data["client_ip"] = client_ip
    if user_agent:
        extra_data["user_agent"] = user_agent

    logger.log(
        level,
        f"API请求: {method} {endpoint} -> {status_code} ({response_time:.3f}s)",
        extra={"extra_data": extra_data},
    )


def log_user_action(
    logger: logging.Logger,
    user_id: str,
    action: str,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
):
    """
    记录用户操作

    Args:
        logger: 日志器
        user_id: 用户ID
        action: 操作类型
        details: 操作详情
        ip_address: IP地址
    """
    extra_data = {"user_id": user_id, "action": action, "category": "user_action"}

    if details:
        extra_data.update(details)
    if ip_address:
        extra_data["ip_address"] = ip_address

    logger.info(f"用户操作: {user_id} - {action}", extra={"extra_data": extra_data})


def log_performance_metric(
    logger: logging.Logger,
    metric_name: str,
    value: float,
    unit: str = "ms",
    tags: Optional[Dict[str, str]] = None,
):
    """
    记录性能指标

    Args:
        logger: 日志器
        metric_name: 指标名称
        value: 数值
        unit: 单位
        tags: 标签
    """
    extra_data = {
        "metric_name": metric_name,
        "value": value,
        "unit": unit,
        "category": "performance",
    }

    if tags:
        extra_data.update(tags)

    logger.info(
        f"性能指标: {metric_name} = {value} {unit}", extra={"extra_data": extra_data}
    )


def log_security_event(
    logger: logging.Logger,
    event_type: str,
    severity: str,
    details: Dict[str, Any],
    ip_address: Optional[str] = None,
    user_id: Optional[str] = None,
):
    """
    记录安全事件

    Args:
        logger: 日志器
        event_type: 事件类型
        severity: 严重程度
        details: 事件详情
        ip_address: IP地址
        user_id: 用户ID
    """
    level = getattr(logging, severity.upper(), logging.WARNING)

    extra_data = {
        "event_type": event_type,
        "severity": severity,
        "category": "security",
    }

    if ip_address:
        extra_data["ip_address"] = ip_address
    if user_id:
        extra_data["user_id"] = user_id

    extra_data.update(details)

    logger.log(
        level, f"安全事件: {event_type} ({severity})", extra={"extra_data": extra_data}
    )


# 全局日志器实例
_loggers = None


def get_loggers() -> Dict[str, logging.Logger]:
    """获取日志器实例"""
    global _loggers
    if _loggers is None:
        _loggers = setup_logging()
    return _loggers
