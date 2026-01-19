#!/usr/bin/env python3
"""
统一引擎管理器
统一管理Deep-Live-Cam、FaceFusion、iRoop三大换脸引擎
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

from .engine_base import (
    BaseEngineAdapter,
    EngineType,
    EngineStatus,
    EngineInfo,
    EngineResult
)

logger = logging.getLogger(__name__)


@dataclass
class EngineRegistry:
    """引擎注册信息"""
    name: str
    engine_class: type
    type: EngineType
    path: str
    enabled: bool = True


class UnifiedEngineManager:
    """统一引擎管理器"""
    
    # 引擎注册表
    ENGINES = {
        'deep_live_cam': {
            'name': 'Deep-Live-Cam',
            'type': EngineType.DEEP_LIVE_CAM,
            'path': 'assets/Deep-Live-Cam-main',
            'enabled': True
        },
        'facefusion': {
            'name': 'FaceFusion',
            'type': EngineType.FACE_FUSION,
            'path': 'assets/facefusion-master',
            'enabled': True
        },
        'iroop_deepfacecam': {
            'name': 'iRoopDeepFaceCam',
            'type': EngineType.IROOP_DEEPCAM,
            'path': 'assets/iRoopDeepFaceCam-main',
            'enabled': True
        }
    }
    
    def __init__(self):
        self.active_engines: Dict[str, BaseEngineAdapter] = {}
        self._engine_cache: Dict[str, Optional[BaseEngineAdapter]] = {}
        
    def get_available_engines(self) -> List[Dict[str, Any]]:
        """获取可用的引擎列表"""
        available = []
        for name, config in self.ENGINES.items():
            if not config['enabled']:
                continue
                
            engine = self._get_engine_instance(name)
            if engine and engine.is_available:
                available.append({
                    'id': name,
                    'name': config['name'],
                    'type': config['type'].value,
                    'status': engine.status.value,
                    'info': self._engine_to_dict(engine.get_info())
                })
        return available
    
    def get_all_engines(self) -> List[Dict[str, Any]]:
        """获取所有已注册引擎信息"""
        engines = []
        for name, config in self.ENGINES.items():
            engine = self._get_engine_instance(name)
            info = engine.get_info() if engine else None
            engines.append({
                'id': name,
                'name': config['name'],
                'type': config['type'].value,
                'enabled': config['enabled'],
                'available': engine.is_available if engine else False,
                'status': engine.status.value if engine else EngineStatus.UNKNOWN.value,
                'info': self._engine_to_dict(info) if info else None
            })
        return engines
    
    def initialize_engine(self, engine_name: str, **kwargs) -> Dict[str, Any]:
        """初始化指定引擎"""
        if engine_name not in self.ENGINES:
            return {'success': False, 'error': f'未知引擎: {engine_name}'}
        
        if engine_name in self.active_engines:
            return {
                'success': True, 
                'message': f'引擎 {engine_name} 已初始化',
                'status': self.active_engines[engine_name].status.value
            }
        
        engine = self._get_engine_instance(engine_name)
        if not engine:
            return {'success': False, 'error': f'无法创建引擎实例: {engine_name}'}
        
        if not engine.is_available:
            return {'success': False, 'error': f'引擎 {engine_name} 不可用'}
        
        try:
            engine.status = EngineStatus.INITIALIZING
            if engine.initialize(**kwargs):
                self.active_engines[engine_name] = engine
                return {
                    'success': True,
                    'message': f'引擎 {engine_name} 初始化成功',
                    'status': engine.status.value,
                    'info': self._engine_to_dict(engine.get_info())
                }
            else:
                return {'success': False, 'error': f'引擎 {engine_name} 初始化失败'}
        except Exception as e:
            logger.error(f'初始化引擎 {engine_name} 失败: {e}')
            return {'success': False, 'error': str(e)}
    
    def get_engine(self, engine_name: str) -> Optional[BaseEngineAdapter]:
        """获取已初始化的引擎"""
        return self.active_engines.get(engine_name)
    
    def process_with_engine(
        self, 
        engine_name: str, 
        source: str, 
        target: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """使用指定引擎处理换脸"""
        engine = self.get_engine(engine_name)
        if not engine:
            return {
                'success': False,
                'error': f'引擎 {engine_name} 未初始化'
            }
        
        try:
            result = engine.process(source, target, **kwargs)
            return {
                'success': result.success,
                'output_path': result.output_path,
                'error_message': result.error_message,
                'processing_time': result.processing_time,
                'metrics': result.metrics
            }
        except Exception as e:
            logger.error(f'引擎处理失败: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    def shutdown_engine(self, engine_name: str) -> Dict[str, Any]:
        """关闭指定引擎"""
        if engine_name not in self.active_engines:
            return {'success': True, 'message': f'引擎 {engine_name} 未运行'}
        
        try:
            engine = self.active_engines[engine_name]
            engine.shutdown()
            del self.active_engines[engine_name]
            return {'success': True, 'message': f'引擎 {engine_name} 已关闭'}
        except Exception as e:
            logger.error(f'关闭引擎 {engine_name} 失败: {e}')
            return {'success': False, 'error': str(e)}
    
    def shutdown_all(self) -> Dict[str, Any]:
        """关闭所有引擎"""
        closed = []
        errors = []
        
        for engine_name in list(self.active_engines.keys()):
            result = self.shutdown_engine(engine_name)
            if result['success']:
                closed.append(engine_name)
            else:
                errors.append({engine_name: result.get('error')})
        
        return {
            'success': len(errors) == 0,
            'closed_engines': closed,
            'errors': errors
        }
    
    def get_engine_models(self, engine_name: str) -> List[Dict[str, Any]]:
        """获取引擎可用模型列表"""
        engine = self._get_engine_instance(engine_name)
        if not engine:
            return []
        
        models = engine.get_models()
        return [
            {
                'name': model.get('name', '未知'),
                'path': model.get('path', ''),
                'size_mb': model.get('size', 0) / (1024 * 1024)
            }
            for model in models
        ]
    
    def _get_engine_instance(self, engine_name: str) -> Optional[BaseEngineAdapter]:
        """获取引擎实例（懒加载）"""
        if engine_name in self._engine_cache:
            return self._engine_cache[engine_name]
        
        if engine_name not in self.ENGINES:
            self._engine_cache[engine_name] = None
            return None
        
        config = self.ENGINES[engine_name]
        
        # 根据引擎类型创建对应实例
        try:
            if config['type'] == EngineType.DEEP_LIVE_CAM:
                from .deep_live_cam_adapter import DeepLiveCamAdapter
                instance = DeepLiveCamAdapter()
            elif config['type'] == EngineType.FACE_FUSION:
                from .facefusion_adapter import FaceFusionAdapter
                instance = FaceFusionAdapter()
            elif config['type'] == EngineType.IROOP_DEEPCAM:
                from .iroop_adapter import IRoopAdapter
                instance = IRoopAdapter()
            else:
                instance = None
            
            self._engine_cache[engine_name] = instance
            return instance
        except ImportError as e:
            logger.warning(f'无法导入引擎适配器 {engine_name}: {e}')
            self._engine_cache[engine_name] = None
            return None
    
    def _engine_to_dict(self, info: EngineInfo) -> Dict[str, Any]:
        """将引擎信息转换为字典"""
        if not info:
            return {}
        
        return {
            'name': info.name,
            'type': info.type.value,
            'version': info.version,
            'status': info.status.value,
            'capabilities': info.capabilities,
            'gpu_memory_mb': info.gpu_memory_mb,
            'model_count': info.model_count
        }
    
    def get_status_summary(self) -> Dict[str, Any]:
        """获取状态摘要"""
        return {
            'total_engines': len(self.ENGINES),
            'active_engines': len(self.active_engines),
            'engines': self.get_all_engines()
        }


# 全局单例
_engine_manager: Optional[UnifiedEngineManager] = None


def get_engine_manager() -> UnifiedEngineManager:
    """获取全局引擎管理器单例"""
    global _engine_manager
    if _engine_manager is None:
        _engine_manager = UnifiedEngineManager()
    return _engine_manager

