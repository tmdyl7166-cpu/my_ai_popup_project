"""
任务调度器
负责决定任务何时执行，管理任务队列和并发控制
"""
import asyncio
import time
import heapq
from typing import List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
import logging

from src.config.app_config import get_config
from src.backend.task_manager import get_task_manager, Task, TaskPriority, TaskStatus
from src.utils.logger import get_logger

logger = get_logger(__name__)
config = get_config()


class TaskScheduler:
    """任务调度器"""

    def __init__(self):
        self.task_manager = get_task_manager()
        self.executor = ThreadPoolExecutor(max_workers=config.max_workers)
        self.running = False
        self.scheduler_task: Optional[asyncio.Task] = None

        # 优先级队列：使用heapq实现优先级调度
        self.priority_queue: List[Tuple[int, float, Task]] = []
        self.queue_lock = asyncio.Lock()

        # 性能监控
        self.last_stats_time = time.time()
        self.stats_interval = 60  # 每60秒记录一次统计信息

    async def start(self):
        """启动调度器"""
        if self.running:
            logger.warning("调度器已经在运行")
            return

        self.running = True
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        logger.info("任务调度器已启动")

    async def stop(self):
        """停止调度器"""
        if not self.running:
            return

        self.running = False
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass

        self.executor.shutdown(wait=True)
        logger.info("任务调度器已停止")

    async def _scheduler_loop(self):
        """调度器主循环"""
        logger.info("调度器主循环开始")

        while self.running:
            try:
                # 检查是否有任务需要执行
                await self._process_pending_tasks()

                # 定期清理和统计
                await self._periodic_maintenance()

                # 短暂休眠避免CPU占用过高
                await asyncio.sleep(0.1)

            except Exception as e:
                logger.error(f"调度器循环出错: {e}")
                await asyncio.sleep(1)  # 出错后稍等再试

    async def _process_pending_tasks(self):
        """处理待执行的任务"""
        # 检查当前活跃任务数量
        active_count = len(self.task_manager.active_tasks)

        if active_count >= config.max_concurrent_tasks:
            return  # 已达到最大并发数

        # 从优先级队列获取最高优先级任务
        async with self.queue_lock:
            if not self.priority_queue:
                return  # 队列为空

            # 弹出最高优先级任务（heapq是最小堆，负数优先级值越小优先级越高）
            _, _, task = heapq.heappop(self.priority_queue)

        # 检查任务是否仍然有效
        if task.status != TaskStatus.PENDING:
            logger.debug(f"跳过无效任务: {task.id} 状态: {task.status}")
            return

        # 启动任务执行
        execution_task = asyncio.create_task(self.task_manager.execute_task(task))
        self.task_manager.active_tasks[task.id] = execution_task

        logger.debug(f"启动任务执行: {task.id} 优先级: {task.priority.name}")

    async def _periodic_maintenance(self):
        """定期维护任务"""
        current_time = time.time()

        # 定期记录统计信息
        if current_time - self.last_stats_time >= self.stats_interval:
            stats = self.task_manager.get_stats()
            logger.info(f"任务统计: {stats}")
            self.last_stats_time = current_time

        # 定期清理过期任务
        if int(current_time) % 3600 == 0:  # 每小时清理一次
            cleaned_count = await self.task_manager.cleanup_completed_tasks()
            if cleaned_count > 0:
                logger.info(f"清理了 {cleaned_count} 个过期任务")

    async def submit_task(self, task_type: str, priority: TaskPriority = TaskPriority.NORMAL, **kwargs) -> str:
        """提交任务到调度器"""
        task_id = await self.task_manager.create_task(task_type, priority=priority, **kwargs)

        # 将任务加入优先级队列
        async with self.queue_lock:
            # 使用负数优先级值，因为heapq是最小堆，优先级数值越小优先级越高
            heapq.heappush(self.priority_queue, (-priority.value, time.time(), self.task_manager.tasks[task_id]))

        logger.info(f"任务已提交: {task_id} 类型: {task_type} 优先级: {priority.name}")
        return task_id

    async def get_task_status(self, task_id: str) -> Optional[Task]:
        """获取任务状态"""
        return await self.task_manager.get_task(task_id)

    async def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        success = await self.task_manager.cancel_task(task_id)
        if success:
            logger.info(f"任务已取消: {task_id}")
        return success

    async def pause_task(self, task_id: str) -> bool:
        """暂停任务"""
        success = await self.task_manager.pause_task(task_id)
        if success:
            logger.info(f"任务已暂停: {task_id}")
        return success

    async def resume_task(self, task_id: str) -> bool:
        """恢复任务"""
        success = await self.task_manager.resume_task(task_id)
        if success:
            logger.info(f"任务已恢复: {task_id}")
        return success

    def get_scheduler_stats(self) -> dict:
        """获取调度器统计信息"""
        task_stats = self.task_manager.get_stats()

        return {
            "scheduler_running": self.running,
            "task_stats": task_stats,
            "executor_workers": config.max_workers,
            "max_concurrent_tasks": config.max_concurrent_tasks,
            "queue_capacity": config.max_queue_size
        }

    async def wait_for_completion(self, task_id: str, timeout: Optional[float] = None) -> bool:
        """等待任务完成"""
        start_time = time.time()

        while True:
            task = await self.task_manager.get_task(task_id)
            if not task:
                return False  # 任务不存在

            if task.status in [task_manager.TaskStatus.COMPLETED, task_manager.TaskStatus.FAILED, task_manager.TaskStatus.CANCELLED]:
                return True  # 任务已结束

            if timeout and (time.time() - start_time) > timeout:
                return False  # 超时

            await asyncio.sleep(0.1)  # 短暂等待后重试


# 全局调度器实例
_scheduler: Optional[TaskScheduler] = None


def get_scheduler() -> TaskScheduler:
    """获取调度器实例（单例模式）"""
    global _scheduler
    if _scheduler is None:
        _scheduler = TaskScheduler()
    return _scheduler


async def start_scheduler():
    """启动全局调度器"""
    scheduler = get_scheduler()
    await scheduler.start()


async def stop_scheduler():
    """停止全局调度器"""
    scheduler = get_scheduler()
    await scheduler.stop()


# 向后兼容别名
Scheduler = TaskScheduler

__all__ = ["TaskScheduler", "Scheduler", "get_scheduler", "start_scheduler", "stop_scheduler"]

