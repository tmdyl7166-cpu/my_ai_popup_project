#!/usr/bin/env python3
"""
部署系统工具模块
提供日志和配置功能
"""

import os
import sys
import json
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from logging.handlers import RotatingFileHandler


# 全局日志配置
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DIR = Path(__file__).parent.parent.parent / "logs" / "deploy"


class DeployLogger:
    """部署日志记录器"""
    
    _instances: Dict[str, logging.Logger] = {}
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """获取日志记录器"""
        if name in cls._instances:
            return cls._instances[name]
        
        logger = logging.getLogger(f"deploy.{name}")
        
        # 确保日志目录存在
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        
        # 文件处理器
        log_file = LOG_DIR / f"{name}.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 格式
        formatter = logging.Formatter(LOG_FORMAT)
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.setLevel(logging.DEBUG)
        
        cls._instances[name] = logger
        return logger


def get_deploy_logger(name: str) -> logging.Logger:
    """获取部署日志记录器"""
    return DeployLogger.get_logger(name)


class DeployConfig:
    """部署配置类"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.config_file = self.project_root / "project_config.json"
        self._config: Optional[Dict[str, Any]] = None
    
    def load(self) -> Dict[str, Any]:
        """加载配置"""
        if self._config is None:
            if self.config_file.exists():
                try:
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        self._config = json.load(f)
                except Exception as e:
                    print(f"加载配置失败: {e}")
                    self._config = self._get_default_config()
            else:
                self._config = self._get_default_config()
        return self._config if self._config is not None else {}
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "deployment": {
                "environment": "development",
                "retry": {
                    "max_attempts": 3,
                    "delay": 5,
                    "backoff": 2
                },
                "timeout": 300
            },
            "python": {
                "min_version": "3.10",
                "venv_name": "ai_popup_env"
            },
            "paths": {
                "logs": "./logs",
                "data": "./data",
                "assets": "./assets"
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        config = self.load()
        
        # 支持点号分隔的键
        keys = key.split('.')
        value = config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        
        return value if value is not None else default
    
    def save(self, config: Dict[str, Any]):
        """保存配置"""
        self._config = config
        
        # 确保目录存在
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    @property
    def environment(self) -> str:
        """获取部署环境"""
        return self.get("deployment.environment", "development")
    
    @property
    def max_retries(self) -> int:
        """获取最大重试次数"""
        return self.get("deployment.retry.max_attempts", 3)
    
    @property
    def retry_delay(self) -> int:
        """获取重试延迟（秒）"""
        return self.get("deployment.retry.delay", 5)
    
    @property
    def venv_name(self) -> str:
        """获取虚拟环境名称"""
        return self.get("python.venv_name", "ai_popup_env")

