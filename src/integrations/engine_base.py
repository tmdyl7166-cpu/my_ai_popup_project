#!/usr/bin/env python3
"""
引擎适配器基类
定义第三方引擎的通用接口和规范
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging
import time

logger = logging.getLogger(__name__)


class EngineType(Enum):
    """引擎类型枚举"""
    DEEP_LIVE_CAM = "deep_live_cam"
    FACE_FUSION = "facefusion"
    IROOP_DEEPCAM = "iroop_deepfacecam"


class EngineStatus(Enum):
    """引擎状态枚举"""
    UNKNOWN = "unknown"
    AVAILABLE = "available"
    INITIALIZING = "initializing"
    READY = "ready"
    PROCESSING = "processing"
    ERROR = "error"
    UNAVAILABLE = "unavailable"


@dataclass
class EngineResult:
    """引擎处理结果"""
    success: bool
    output_path: Optional[str] = None
    error_message: Optional[str] = None
    processing_time: float = 0.0
    metrics: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metrics is None:
            self.metrics = dict()


@dataclass
class EngineInfo:
    """引擎信息"""
    name: str
    type: EngineType
    version: str
    status: EngineStatus
    capabilities: list
    gpu_memory_mb: float = 0.0
    model_count: int = 0


class BaseEngineAdapter(ABC):
    """引擎适配器基类"""
    
    # 子类必须覆盖
    ENGINE_TYPE = EngineType.DEEP_LIVE_CAM
    ENGINE_NAME = "Base Engine"
    
    def __init__(self):
        self.status = EngineStatus.UNKNOWN
        self._initialized = False
        self._start_time = None
        
    @property
    def is_available(self) -> bool:
        """检查引擎是否可用"""
        try:
            return self._check_availability()
        except Exception as e:
            logger.error(f"检查引擎可用性失败: {e}")
            return False
    
    @property
    def is_initialized(self) -> bool:
        """检查引擎是否已初始化"""
        return self._initialized
    
    @abstractmethod
    def _check_availability(self) -> bool:
        """检查引擎是否可用（子类实现）"""
        pass
    
    @abstractmethod
    def initialize(self, **kwargs) -> bool:
        """初始化引擎"""
        pass
    
    @abstractmethod
    def process(self, source: str, target: str, **kwargs) -> EngineResult:
        """处理换脸"""
        pass
    
    @abstractmethod
    def shutdown(self):
        """关闭引擎"""
        pass
    
    @abstractmethod
    def get_info(self) -> EngineInfo:
        """获取引擎信息"""
        pass
    
    @abstractmethod
    def get_models(self) -> list:
        """获取可用模型列表"""
        pass
    
    def _measure_time(self, func):
        """测量函数执行时间"""
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            return result, elapsed
        return wrapper
    
    def _validate_paths(self, source: str, target: str) -> bool:
        """验证路径有效性"""
        import os
        if not os.path.exists(source):
            logger.error(f"源文件不存在: {source}")
            return False
        if not os.path.exists(target):
            logger.error(f"目标文件不存在: {target}")
            return False
        return True

