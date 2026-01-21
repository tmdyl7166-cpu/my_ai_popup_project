#!/usr/bin/env python3
"""
统一引擎管理器
统一管理Deep-Live-Cam、FaceFusion、iRoop三大换脸引擎
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass, field
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import threading

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

        # 并发控制
        self._processing_lock = asyncio.Lock()
        self._active_processes: Dict[str, asyncio.Task] = {}
        self._executor = ThreadPoolExecutor(max_workers=3)  # 限制并发引擎处理数

        # 资源监控
        self._resource_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_processing_time': 0.0,
            'peak_concurrent_processes': 0,
            'last_health_check': time.time()
        }

        # 健康监控
        self._health_monitor_task: Optional[asyncio.Task] = None
        self._health_check_interval = 60  # 每60秒检查一次健康状态
        
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

    async def process_with_engine_async(
        self,
        engine_name: str,
        source: str,
        target: str,
        **kwargs
    ) -> Dict[str, Any]:
        """异步使用指定引擎处理换脸（支持并发）"""
        async with self._processing_lock:
            # 检查并发限制
            if len(self._active_processes) >= 3:
                return {
                    'success': False,
                    'error': '并发处理数已达上限，请稍后再试'
                }

            # 更新统计信息
            self._resource_stats['total_requests'] += 1
            current_concurrent = len(self._active_processes) + 1
            self._resource_stats['peak_concurrent_processes'] = max(
                self._resource_stats['peak_concurrent_processes'],
                current_concurrent
            )

        engine = self.get_engine(engine_name)
        if not engine:
            async with self._processing_lock:
                self._resource_stats['failed_requests'] += 1
            return {
                'success': False,
                'error': f'引擎 {engine_name} 未初始化'
            }

        # 创建处理任务
        task_id = f"{engine_name}_{int(time.time() * 1000)}"
        task = asyncio.create_task(self._execute_engine_process(task_id, engine, source, target, **kwargs))
        self._active_processes[task_id] = task

        try:
            result = await task
            async with self._processing_lock:
                if result['success']:
                    self._resource_stats['successful_requests'] += 1
                else:
                    self._resource_stats['failed_requests'] += 1

                # 更新平均处理时间
                if result.get('processing_time'):
                    current_avg = self._resource_stats['average_processing_time']
                    total_requests = self._resource_stats['successful_requests'] + self._resource_stats['failed_requests']
                    self._resource_stats['average_processing_time'] = (
                        (current_avg * (total_requests - 1)) + result['processing_time']
                    ) / total_requests

            return result
        finally:
            # 清理已完成的任务
            if task_id in self._active_processes:
                del self._active_processes[task_id]

    async def _execute_engine_process(
        self,
        task_id: str,
        engine: BaseEngineAdapter,
        source: str,
        target: str,
        **kwargs
    ) -> Dict[str, Any]:
        """执行引擎处理（带重试机制）"""
        max_retries = kwargs.get('max_retries', 2)
        retry_delay = kwargs.get('retry_delay', 1.0)

        for attempt in range(max_retries + 1):
            try:
                start_time = time.time()

                # 使用线程池执行同步处理
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    self._executor,
                    engine.process,
                    source,
                    target,
                    kwargs
                )

                processing_time = time.time() - start_time

                # 增强结果信息
                enhanced_result = {
                    'success': result.success,
                    'output_path': result.output_path,
                    'error_message': result.error_message,
                    'processing_time': processing_time,
                    'metrics': result.metrics or {},
                    'attempt': attempt + 1,
                    'engine_name': engine.__class__.__name__
                }

                if result.success:
                    logger.info(f"引擎处理成功: {task_id}, 用时: {processing_time:.2f}秒")
                    return enhanced_result
                else:
                    logger.warning(f"引擎处理失败: {task_id}, 尝试 {attempt + 1}/{max_retries + 1}")

            except Exception as e:
                logger.error(f"引擎处理异常: {task_id}, 尝试 {attempt + 1}/{max_retries + 1}, 错误: {e}")

                if attempt == max_retries:
                    return {
                        'success': False,
                        'error': f'处理失败，已重试 {max_retries + 1} 次: {str(e)}',
                        'processing_time': time.time() - start_time,
                        'attempt': attempt + 1
                    }

            # 等待后重试
            if attempt < max_retries:
                await asyncio.sleep(retry_delay * (2 ** attempt))  # 指数退避

        return {
            'success': False,
            'error': '所有重试均失败',
            'attempt': max_retries + 1
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

