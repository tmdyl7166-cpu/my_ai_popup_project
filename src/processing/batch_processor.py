"""
批量处理器
处理批量任务和队列管理
"""
import asyncio
import time
from typing import List, Optional, Dict, Any, Callable
from pathlib import Path
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

from src.config.app_config import get_config
from src.utils.logger import get_logger

logger = get_logger(__name__)
config = get_config()


@dataclass
class BatchTask:
    """批量任务"""
    id: str
    task_type: str
    source_path: str
    target_path: str
    output_path: Optional[str] = None
    priority: int = 1
    parameters: Optional[Dict[str, Any]] = None


@dataclass
class BatchProcessingResult:
    """批量处理结果"""
    success: bool
    completed_tasks: int = 0
    failed_tasks: int = 0
    total_tasks: int = 0
    processing_time: float = 0.0
    error_message: Optional[str] = None
    results: Optional[List[Dict[str, Any]]] = None


class BatchProcessor:
    """批量处理器 - Mock实现"""

    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=config.max_workers)
        self.processing_stats = {
            "batches_processed": 0,
            "total_tasks_processed": 0,
            "average_batch_time": 0.0,
            "total_batch_time": 0.0
        }

    async def process_batch(self,
                          tasks: List[BatchTask],
                          progress_callback: Optional[Callable[[int, int], None]] = None,
                          **kwargs) -> BatchProcessingResult:
        """
        处理批量任务

        Args:
            tasks: 任务列表
            progress_callback: 进度回调函数
            **kwargs: 其他参数

        Returns:
            BatchProcessingResult: 批量处理结果
        """
        start_time = time.time()
        total_tasks = len(tasks)

        logger.info(f"开始批量处理: {total_tasks} 个任务")

        try:
            completed_tasks = 0
            failed_tasks = 0
            results = []

            # 并发处理任务
            semaphore = asyncio.Semaphore(config.max_workers)

            async def process_single_task(task: BatchTask) -> Dict[str, Any]:
                async with semaphore:
                    try:
                        # Mock: 模拟处理单个任务
                        await asyncio.sleep(1.0)  # 模拟处理时间

                        # 模拟成功处理
                        result = {
                            "task_id": task.id,
                            "success": True,
                            "output_path": self._generate_output_path(task),
                            "processing_time": 1.0,
                            "metadata": {
                                "operation": task.task_type,
                                "source_path": task.source_path,
                                "target_path": task.target_path
                            }
                        }

                        nonlocal completed_tasks
                        completed_tasks += 1

                        if progress_callback:
                            progress_callback(completed_tasks, total_tasks)

                        return result

                    except Exception as e:
                        nonlocal failed_tasks
                        failed_tasks += 1

                        logger.error(f"任务处理失败 {task.id}: {e}")
                        return {
                            "task_id": task.id,
                            "success": False,
                            "error_message": str(e)
                        }

            # 并发执行所有任务
            task_coroutines = [process_single_task(task) for task in tasks]
            results = await asyncio.gather(*task_coroutines, return_exceptions=True)

            # 处理异常结果
            clean_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    failed_tasks += 1
                    clean_results.append({
                        "task_id": tasks[i].id,
                        "success": False,
                        "error_message": str(result)
                    })
                else:
                    clean_results.append(result)

            # 更新统计信息
            processing_time = time.time() - start_time
            self._update_stats(processing_time, total_tasks)

            batch_result = BatchProcessingResult(
                success=failed_tasks == 0,
                completed_tasks=completed_tasks,
                failed_tasks=failed_tasks,
                total_tasks=total_tasks,
                processing_time=processing_time,
                results=clean_results
            )

            logger.info(f"批量处理完成: {completed_tasks}/{total_tasks} 成功, 耗时: {processing_time:.2f}s")
            return batch_result

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"批量处理失败: {e}")
            return BatchProcessingResult(
                success=False,
                error_message=str(e),
                processing_time=processing_time,
                total_tasks=total_tasks
            )

    def _generate_output_path(self, task: BatchTask) -> str:
        """生成输出路径"""
        timestamp = int(time.time())

        if task.task_type.startswith("image"):
            output_dir = Path(config.output_dir) / "images"
        else:
            output_dir = Path(config.output_dir) / "videos"

        output_dir.mkdir(parents=True, exist_ok=True)

        target_path_obj = Path(task.target_path)
        output_name = f"{target_path_obj.stem}_batch_{task.id}_{timestamp}{target_path_obj.suffix}"
        return str(output_dir / output_name)

    def _update_stats(self, processing_time: float, task_count: int):
        """更新统计信息"""
        self.processing_stats["batches_processed"] += 1
        self.processing_stats["total_tasks_processed"] += task_count
        self.processing_stats["total_batch_time"] += processing_time

        if self.processing_stats["batches_processed"] > 0:
            self.processing_stats["average_batch_time"] = (
                self.processing_stats["total_batch_time"] /
                self.processing_stats["batches_processed"]
            )

    def get_stats(self) -> Dict[str, Any]:
        """获取批量处理统计信息"""
        return {
            "batches_processed": self.processing_stats["batches_processed"],
            "total_tasks_processed": self.processing_stats["total_tasks_processed"],
            "average_batch_time": round(self.processing_stats["average_batch_time"], 3),
            "total_batch_time": round(self.processing_stats["total_batch_time"], 3),
            "max_concurrent_tasks": config.max_workers
        }

    async def validate_batch_tasks(self, tasks: List[BatchTask]) -> Dict[str, Any]:
        """
        验证批量任务

        Args:
            tasks: 任务列表

        Returns:
            Dict[str, Any]: 验证结果
        """
        validation_result = {
            "valid": True,
            "total_tasks": len(tasks),
            "valid_tasks": 0,
            "invalid_tasks": 0,
            "errors": []
        }

        for task in tasks:
            is_valid, error = await self._validate_single_task(task)
            if is_valid:
                validation_result["valid_tasks"] += 1
            else:
                validation_result["invalid_tasks"] += 1
                validation_result["errors"].append({
                    "task_id": task.id,
                    "error": error
                })

        if validation_result["invalid_tasks"] > 0:
            validation_result["valid"] = False

        return validation_result

    async def _validate_single_task(self, task: BatchTask) -> tuple[bool, Optional[str]]:
        """
        验证单个任务

        Args:
            task: 任务对象

        Returns:
            tuple[bool, Optional[str]]: (是否有效, 错误信息)
        """
        # 检查必需字段
        if not task.source_path or not task.target_path:
            return False, "源路径和目标路径不能为空"

        # 检查文件是否存在
        if not Path(task.source_path).exists():
            return False, f"源文件不存在: {task.source_path}"

        if not Path(task.target_path).exists():
            return False, f"目标文件不存在: {task.target_path}"

        # 检查任务类型
        supported_types = ["image_to_image", "image_to_video", "video_to_video"]
        if task.task_type not in supported_types:
            return False, f"不支持的任务类型: {task.task_type}"

        return True, None


# 全局批量处理器实例
_batch_processor: Optional[BatchProcessor] = None


def get_batch_processor() -> BatchProcessor:
    """获取批量处理器实例（单例模式）"""
    global _batch_processor
    if _batch_processor is None:
        _batch_processor = BatchProcessor()
    return _batch_processor
