#!/usr/bin/env python3
"""
FaceFusion 引擎适配器
实现与 FaceFusion 项目的集成
"""

import os
import logging
from typing import Optional
from pathlib import Path

from .engine_base import (
    BaseEngineAdapter,
    EngineType,
    EngineStatus,
    EngineInfo,
    EngineResult
)

logger = logging.getLogger(__name__)


class FaceFusionAdapter(BaseEngineAdapter):
    """FaceFusion 引擎适配器"""
    
    ENGINE_TYPE = EngineType.FACE_FUSION
    ENGINE_NAME = "FaceFusion"
    
    def __init__(self):
        super().__init__()
        self.project_path = None
        self._weights_dir = None
        
    def _check_availability(self) -> bool:
        """检查 FaceFusion 是否可用"""
        # 检查项目目录
        base_path = Path(__file__).parent.parent.parent
        self.project_path = base_path / "assets" / "facefusion-master"
        
        if not self.project_path.exists():
            logger.warning(f"FaceFusion 目录不存在: {self.project_path}")
            return False
        
        # 检查权重目录
        self._weights_dir = self.project_path / "weights"
        if not self._weights_dir.exists():
            logger.warning(f"FaceFusion 权重目录不存在: {self._weights_dir}")
        
        logger.info(f"FaceFusion 可用: {self.project_path}")
        return True
    
    def initialize(self, **kwargs) -> bool:
        """初始化 FaceFusion"""
        try:
            self.status = EngineStatus.INITIALIZING
            
            # 检查 GPU
            try:
                import torch
                has_cuda = torch.cuda.is_available()
                logger.info(f"CUDA 可用: {has_cuda}")
            except ImportError:
                logger.warning("PyTorch 未安装，GPU 加速不可用")
            
            self.status = EngineStatus.READY
            self._initialized = True
            logger.info("FaceFusion 初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"初始化 FaceFusion 失败: {e}")
            self.status = EngineStatus.ERROR
            return False
    
    def process(self, source: str, target: str, **kwargs) -> EngineResult:
        """执行人脸融合处理"""
        import time
        start_time = time.time()
        
        if not self._initialized:
            return EngineResult(
                success=False,
                error_message="引擎未初始化",
                processing_time=time.time() - start_time
            )
        
        if not self._validate_paths(source, target):
            return EngineResult(
                success=False,
                error_message="文件路径无效",
                processing_time=time.time() - start_time
            )
        
        try:
            self.status = EngineStatus.PROCESSING
            
            # TODO: 实现实际的融合逻辑
            # 这里模拟处理过程
            time.sleep(1.5)  # 模拟处理时间
            
            output_path = f"/tmp/facefusion_output_{int(start_time)}.mp4"
            
            result = EngineResult(
                success=True,
                output_path=output_path,
                processing_time=time.time() - start_time,
                metrics={
                    "source": source,
                    "target": target,
                    "engine": "facefusion"
                }
            )
            
            self.status = EngineStatus.READY
            return result
            
        except Exception as e:
            logger.error(f"FaceFusion 处理失败: {e}")
            self.status = EngineStatus.ERROR
            return EngineResult(
                success=False,
                error_message=str(e),
                processing_time=time.time() - start_time
            )
    
    def shutdown(self):
        """关闭 FaceFusion"""
        self._initialized = False
        self.status = EngineStatus.UNKNOWN
        logger.info("FaceFusion 已关闭")
    
    def get_info(self) -> EngineInfo:
        """获取引擎信息"""
        model_count = len(list(self._weights_dir.glob("**/*"))) if self._weights_dir and self._weights_dir.exists() else 0
        
        return EngineInfo(
            name=self.ENGINE_NAME,
            type=self.ENGINE_TYPE,
            version="2.0.0",
            status=self.status,
            capabilities=[
                "人脸融合",
                "高质量输出",
                "批量处理",
                "GPU加速"
            ],
            gpu_memory_mb=6144.0,
            model_count=model_count
        )
    
    def get_models(self) -> list:
        """获取可用模型列表"""
        if not self._weights_dir or not self._weights_dir.exists():
            return []
        
        models = []
        for root, dirs, files in os.walk(self._weights_dir):
            for file in files:
                model_path = Path(root) / file
                models.append({
                    'name': model_path.name,
                    'path': str(model_path),
                    'size': model_path.stat().st_size
                })
        
        return models

