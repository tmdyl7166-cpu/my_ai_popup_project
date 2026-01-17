"""
日志工具模块
提供统一的日志配置和管理功能
"""
import logging
import sys
from pathlib import Path
from typing import Optional

def setup_global_logging(level: int = logging.INFO, log_file: Optional[str] = None):
    """设置全局日志配置"""
    # 创建日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # 清除现有处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 添加控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 添加文件处理器（如果指定）
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

def get_script_logger(name: str) -> logging.Logger:
    """获取脚本专用日志器"""
    return logging.getLogger(f"scripts.{name}")

def setup_script_logging(script_name: str, project_root: Path, level: int = logging.INFO) -> logging.Logger:
    """设置脚本专用日志"""
    log_file = project_root / 'logs' / f'{script_name}.log'
    log_file.parent.mkdir(parents=True, exist_ok=True)

    setup_global_logging(level, str(log_file))
    return get_script_logger(script_name)
