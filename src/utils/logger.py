"""
日志工具模块
提供统一的日志记录功能
"""
import sys
from pathlib import Path
from loguru import logger
from datetime import datetime
from typing import Optional

# 导入路径解析器
from src.utils.path_resolver import PathResolver


class Logger:
    """日志管理器"""
    
    _instance: Optional["Logger"] = None
    _initialized: bool = False
    
    def __new__(cls) -> "Logger":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not Logger._initialized:
            self._setup_logger()
            Logger._initialized = True
    
    def _setup_logger(self):
        """配置日志器"""
        # 移除默认处理器
        logger.remove()
        
        # 获取日志级别
        log_level = "INFO"
        
        # 控制台输出
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{message}</cyan>",
            level=log_level,
            colorize=True
        )
        
        # 文件输出 - 使用路径解析器获取日志目录
        log_dir = PathResolver.get_logs_dir()
        
        log_file = log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
        
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
            level="DEBUG",
            rotation="10 MB",
            retention="10 days",
            compression="gz"
        )
    
    def get_logger(self):
        """获取日志器实例"""
        return logger
    
    def log(self, level: str, message: str, **kwargs):
        """记录日志"""
        getattr(logger, level.lower())(message, **kwargs)
    
    def info(self, message: str, **kwargs):
        self.log("INFO", message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        self.log("DEBUG", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self.log("WARNING", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self.log("ERROR", message, **kwargs)


# 全局日志器实例
_log_instance = Logger()


def get_logger(name: str = "app"):
    """获取日志器"""
    return _log_instance.get_logger().bind(name=name)


def log_info(message: str, **kwargs):
    _log_instance.info(message, **kwargs)


def log_error(message: str, **kwargs):
    _log_instance.error(message, **kwargs)


def log_warning(message: str, **kwargs):
    _log_instance.warning(message, **kwargs)


def log_debug(message: str, **kwargs):
    _log_instance.debug(message, **kwargs)

