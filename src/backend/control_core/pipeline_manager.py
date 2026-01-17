#!/usr/bin/env python3
"""
my_ai_popup_project 管道管理器

负责管理处理管道的创建、执行和监控。
"""

import asyncio
import threading
import time
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum

from ...utils.logger import get_logger


class PipelineStatus(Enum):
    """管道状态枚举"""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class PipelineTask:
    """管道任务"""
    id: str
    name: str
    status: TaskStatus = TaskStatus.PENDING
    progress: float = 0.0
    result: Any = None
    error: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    dependencies: List[str] = field(default_factory=list)
    callback: Optional[Callable] = None


@dataclass
class ProcessingPipeline:
    """处理管道"""
    id: str
    name: str
    status: PipelineStatus = PipelineStatus.CREATED
    tasks: Dict[str, PipelineTask] = field(default_factory=dict)
    progress: float = 0.0
    result: Any = None
    error: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class PipelineManager:
    """管道管理器"""

    def __init__(self):
        self.logger = get_logger(__name__)
        self._lock = threading.RLock()

        # 管道存储
        self.pipelines: Dict[str, ProcessingPipeline] = {}

        # 运行中的管道
        self._running_pipelines: Dict[str, asyncio.Task] = {}

        # 统计信息
        self.stats = {
            "total_pipelines": 0,
            "running_pipelines": 0,
            "completed_pipelines": 0,
            "failed_pipelines": 0,
        }

    async def create_pipeline(
        self,
        pipeline_id: str,
        name: str,
        tasks: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> ProcessingPipeline:
        """创建处理管道"""
        with self._lock:
            if pipeline_id in self.pipelines:
                raise ValueError(f"管道 {pipeline_id} 已存在")

            pipeline = ProcessingPipeline(
                id=pipeline_id,
                name=name,
                metadata=metadata or {}
            )

            # 创建任务
            for task_data in tasks:
                task = PipelineTask(
                    id=task_data["id"],
                    name=task_data["name"],
                    dependencies=task_data.get("dependencies", []),
                    callback=task_data.get("callback")
                )
                pipeline.tasks[task.id] = task

            self.pipelines[pipeline_id] = pipeline
            self.stats["total_pipelines"] += 1

            self.logger.info(f"创建管道: {pipeline_id} ({name})")
            return pipeline

    async def execute_pipeline(self, pipeline_id: str) -> Any:
        """执行管道"""
        with self._lock:
            if pipeline_id not in self.pipelines:
                raise ValueError(f"管道 {pipeline_id} 不存在")

            pipeline = self.pipelines[pipeline_id]
            if pipeline.status != PipelineStatus.CREATED:
                raise ValueError(f"管道 {pipeline_id} 状态不允许执行: {pipeline.status.value}")

            pipeline.status = PipelineStatus.RUNNING
            pipeline.start_time = time.time()
            self.stats["running_pipelines"] += 1

        try:
            # 创建异步任务
            task = asyncio.create_task(self._execute_pipeline_async(pipeline))
            self._running_pipelines[pipeline_id] = task

            # 等待执行完成
            result = await task

            with self._lock:
                pipeline.status = PipelineStatus.COMPLETED
                pipeline.end_time = time.time()
                pipeline.result = result
                pipeline.progress = 100.0
                self.stats["running_pipelines"] -= 1
                self.stats["completed_pipelines"] += 1

            self.logger.info(f"管道 {pipeline_id} 执行完成")
            return result

        except Exception as e:
            with self._lock:
                pipeline.status = PipelineStatus.FAILED
                pipeline.end_time = time.time()
                pipeline.error = str(e)
                self.stats["running_pipelines"] -= 1
                self.stats["failed_pipelines"] += 1

            self.logger.error(f"管道 {pipeline_id} 执行失败: {e}")
            raise

    async def _execute_pipeline_async(self, pipeline: ProcessingPipeline) -> Any:
        """异步执行管道"""
        # 拓扑排序任务
        sorted_tasks = self._topological_sort(pipeline.tasks)

        results = {}

        for task in sorted_tasks:
            # 检查依赖
            if not self._check_dependencies(task, results):
                raise ValueError(f"任务 {task.id} 的依赖未满足")

            try:
                task.status = TaskStatus.RUNNING
                task.start_time = time.time()

                # 执行任务
                if task.callback:
                    result = await self._execute_task_callback(task, results)
                else:
                    result = await self._execute_default_task(task, results)

                task.status = TaskStatus.COMPLETED
                task.end_time = time.time()
                task.result = result
                task.progress = 100.0

                results[task.id] = result

                # 更新管道进度
                completed_tasks = sum(1 for t in pipeline.tasks.values()
                                    if t.status == TaskStatus.COMPLETED)
                pipeline.progress = (completed_tasks / len(pipeline.tasks)) * 100

            except Exception as e:
                task.status = TaskStatus.FAILED
                task.end_time = time.time()
                task.error = str(e)
                raise

        # 返回最终结果
        return results

    def _topological_sort(self, tasks: Dict[str, PipelineTask]) -> List[PipelineTask]:
        """拓扑排序任务"""
        # 简化的拓扑排序实现
        sorted_tasks = []
        visited = set()
        visiting = set()

        def visit(task: PipelineTask):
            if task.id in visiting:
                raise ValueError(f"检测到循环依赖: {task.id}")
            if task.id in visited:
                return

            visiting.add(task.id)

            for dep_id in task.dependencies:
                if dep_id in tasks:
                    visit(tasks[dep_id])

            visiting.remove(task.id)
            visited.add(task.id)
            sorted_tasks.append(task)

        for task in tasks.values():
            if task.id not in visited:
                visit(task)

        return sorted_tasks

    def _check_dependencies(self, task: PipelineTask, results: Dict[str, Any]) -> bool:
        """检查任务依赖"""
        for dep_id in task.dependencies:
            if dep_id not in results:
                return False
        return True

    async def _execute_task_callback(self, task: PipelineTask, results: Dict[str, Any]) -> Any:
        """执行任务回调"""
        # 准备参数
        kwargs = {}
        for dep_id in task.dependencies:
            if dep_id in results:
                kwargs[dep_id] = results[dep_id]

        # 执行回调
        if asyncio.iscoroutinefunction(task.callback):
            return await task.callback(**kwargs)
        else:
            # 在线程池中执行同步函数
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, task.callback, **kwargs)

    async def _execute_default_task(self, task: PipelineTask, results: Dict[str, Any]) -> Any:
        """执行默认任务"""
        # 默认任务实现
        self.logger.info(f"执行默认任务: {task.name}")

        # 模拟处理时间
        await asyncio.sleep(0.1)

        return f"默认任务结果: {task.name}"

    async def cancel_pipeline(self, pipeline_id: str) -> bool:
        """取消管道执行"""
        with self._lock:
            if pipeline_id not in self._running_pipelines:
                return False

            task = self._running_pipelines[pipeline_id]
            task.cancel()

            pipeline = self.pipelines[pipeline_id]
            pipeline.status = PipelineStatus.CANCELLED
            pipeline.end_time = time.time()

            # 取消所有运行中的任务
            for task_obj in pipeline.tasks.values():
                if task_obj.status == TaskStatus.RUNNING:
                    task_obj.status = TaskStatus.CANCELLED
                    task_obj.end_time = time.time()

            del self._running_pipelines[pipeline_id]
            self.stats["running_pipelines"] -= 1

            self.logger.info(f"管道 {pipeline_id} 已取消")
            return True

    async def pause_pipeline(self, pipeline_id: str) -> bool:
        """暂停管道执行"""
        with self._lock:
            if pipeline_id not in self.pipelines:
                return False

            pipeline = self.pipelines[pipeline_id]
            if pipeline.status != PipelineStatus.RUNNING:
                return False

            pipeline.status = PipelineStatus.PAUSED
            self.logger.info(f"管道 {pipeline_id} 已暂停")
            return True

    async def resume_pipeline(self, pipeline_id: str) -> bool:
        """恢复管道执行"""
        with self._lock:
            if pipeline_id not in self.pipelines:
                return False

            pipeline = self.pipelines[pipeline_id]
            if pipeline.status != PipelineStatus.PAUSED:
                return False

            pipeline.status = PipelineStatus.RUNNING
            self.logger.info(f"管道 {pipeline_id} 已恢复")
            return True

    def get_pipeline(self, pipeline_id: str) -> Optional[ProcessingPipeline]:
        """获取管道"""
        return self.pipelines.get(pipeline_id)

    def get_all_pipelines(self) -> Dict[str, ProcessingPipeline]:
        """获取所有管道"""
        with self._lock:
            return self.pipelines.copy()

    def get_pipeline_status(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        """获取管道状态"""
        pipeline = self.get_pipeline(pipeline_id)
        if not pipeline:
            return None

        return {
            "id": pipeline.id,
            "name": pipeline.name,
            "status": pipeline.status.value,
            "progress": pipeline.progress,
            "start_time": pipeline.start_time,
            "end_time": pipeline.end_time,
            "error": pipeline.error,
            "tasks": {
                task_id: {
                    "name": task.name,
                    "status": task.status.value,
                    "progress": task.progress,
                    "error": task.error
                }
                for task_id, task in pipeline.tasks.items()
            }
        }

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self._lock:
            return self.stats.copy()

    async def cleanup_completed_pipelines(self, max_age: int = 3600):
        """清理已完成的管道"""
        current_time = time.time()
        to_remove = []

        with self._lock:
            for pipeline_id, pipeline in self.pipelines.items():
                if (pipeline.status in [PipelineStatus.COMPLETED, PipelineStatus.FAILED, PipelineStatus.CANCELLED]
                    and pipeline.end_time
                    and current_time - pipeline.end_time > max_age):
                    to_remove.append(pipeline_id)

            for pipeline_id in to_remove:
                del self.pipelines[pipeline_id]
                self.logger.info(f"清理管道: {pipeline_id}")


# 全局管道管理器实例
pipeline_manager = PipelineManager()
