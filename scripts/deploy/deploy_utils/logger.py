#!/usr/bin/env python3
"""
部署系统日志工具
提供日志记录功能
"""

import os
import sys
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from functools import wraps


# 日志配置
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DIR = Path(__file__).parent.parent.parent / "logs" / "deploy"


class LoggerManager:
    """日志管理器"""
    
    _loggers: Dict[str, logging.Logger] = {}
    _initialized = False
    
    @classmethod
    def initialize(cls, log_dir: Optional[Path] = None, level: int = logging.DEBUG):
        """初始化日志系统"""
        if cls._initialized:
            return
        
        global LOG_DIR
        if log_dir:
            LOG_DIR = log_dir
        
        # 创建日志目录
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        
        # 配置根日志器
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        
        # 清除现有处理器
        root_logger.handlers.clear()
        
        # 添加文件处理器
        today = datetime.now().strftime('%Y-%m-%d')
        file_handler = logging.handlers.RotatingFileHandler(
            LOG_DIR / f"deploy_{today}.log",
            maxBytes=10 * 1024 * 1024,
            backupCount=10,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # 添加控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # 格式
        formatter = logging.Formatter(LOG_FORMAT)
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        cls._initialized = True
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """获取日志记录器"""
        if name in cls._loggers:
            return cls._loggers[name]
        
        logger = logging.getLogger(f"deploy.{name}")
        cls._loggers[name] = logger
        return logger


def setup_global_logging():
    """设置全局日志"""
    LoggerManager.initialize()


def get_logger(name: str) -> logging.Logger:
    """获取日志记录器"""
    return LoggerManager.get_logger(name)


def log_execution(logger: Optional[logging.Logger] = None, level: int = logging.INFO):
    """记录函数执行的装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            log = logger or get_logger(func.__module__)
            log.log(level, f"开始执行: {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                log.log(level, f"执行成功: {func.__name__}")
                return result
            except Exception as e:
                log.exception(f"执行失败: {func.__name__} - {e}")
                raise
        
        return wrapper
    return decorator


class ExecutionLogger:
    """执行日志器"""
    
    def __init__(self, name: str, log_dir: Optional[Path] = None):
        self.name = name
        self.log_dir = log_dir or LOG_DIR
        self.logger = get_logger(name)
        self.start_time: Optional[datetime] = None
    
    def __enter__(self):
        """进入上下文"""
        self.start_time = datetime.now()
        self.logger.info(f"开始执行: {self.name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文"""
        if self.start_time is None:
            duration = 0.0
        else:
            duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type is None:
            self.logger.info(f"执行完成: {self.name} (耗时: {duration:.2f}s)")
        else:
            self.logger.error(f"执行失败: {self.name} (耗时: {duration:.2f}s) - {exc_val}")
        
        return False  # 不抑制异常
    
    def log(self, level: int, message: str, **kwargs):
        """记录日志"""
        extra_info = " ".join(f"{k}={v}" for k, v in kwargs.items())
        if extra_info:
            message = f"{message} ({extra_info})"
        
        self.logger.log(level, message)


# 导出
__all__ = [
    'LoggerManager',
    'setup_global_logging',
    'get_logger',
    'log_execution',
    'ExecutionLogger'
]

