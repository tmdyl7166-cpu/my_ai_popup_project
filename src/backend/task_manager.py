"""
任务管理器
负责创建、管理和跟踪任务的生命周期
"""
import asyncio
import time
import uuid
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor

from src.config.app_config import get_config
from src.utils.logger import get_logger

logger = get_logger(__name__)
config = get_config()


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"           # 待处理
    RESOURCE_LOADING = "resource_loading"  # 资源加载中
    AI_PROCESSING = "ai_processing"     # AI处理中
    SYNTHESIZING = "synthesizing"      # 合成中
    OUTPUT_GENERATING = "output_generating" # 输出生成中
    COMPLETED = "completed"         # 已完成
    FAILED = "failed"             # 失败
    CANCELLED = "cancelled"         # 已取消
    PAUSED = "paused"             # 已暂停


class TaskPriority(Enum):
    """任务优先级枚举"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class Task:
    """任务类"""
    id: str
    task_type: str
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None

    # 任务参数
    source_path: Optional[str] = None
    target_path: Optional[str] = None
    output_path: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)

    # 进度和结果
    progress: float = 0.0
    progress_message: str = ""
    result: Optional[Any] = None
    error_message: Optional[str] = None

    # 回调函数
    on_progress: Optional[Callable[[float, str], None]] = None
    on_complete: Optional[Callable[[Any], None]] = None
    on_error: Optional[Callable[[str], None]] = None

    def update_progress(self, progress: float, message: str = ""):
        """更新进度"""
        self.progress = max(0.0, min(100.0, progress))
        self.progress_message = message
        self.updated_at = time.time()

        if self.on_progress:
            self.on_progress(self.progress, self.progress_message)

    def complete(self, result: Any = None):
        """完成任务"""
        self.status = TaskStatus.COMPLETED
        self.completed_at = time.time()
        self.updated_at = time.time()
        self.result = result
        self.progress = 100.0

        if self.on_complete:
            self.on_complete(result)

    def fail(self, error_message: str):
        """任务失败"""
        self.status = TaskStatus.FAILED
        self.error_message = error_message
        self.updated_at = time.time()

        if self.on_error:
            self.on_error(error_message)

    def cancel(self):
        """取消任务"""
        self.status = TaskStatus.CANCELLED
        self.updated_at = time.time()

    def pause(self):
        """暂停任务"""
        self.status = TaskStatus.PAUSED
        self.updated_at = time.time()

    def resume(self):
        """恢复任务"""
        self.status = TaskStatus.PENDING
        self.updated_at = time.time()

    def is_active(self) -> bool:
        """检查任务是否活跃"""
        return self.status in [
            TaskStatus.PENDING,
            TaskStatus.RESOURCE_LOADING,
            TaskStatus.AI_PROCESSING,
            TaskStatus.SYNTHESIZING,
            TaskStatus.OUTPUT_GENERATING
        ]

    def is_finished(self) -> bool:
        """检查任务是否完成"""
        return self.status in [
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
            TaskStatus.CANCELLED
        ]


class TaskManager:
    """任务管理器"""

    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.executor = ThreadPoolExecutor(max_workers=config.max_workers)
        self.task_queue = asyncio.Queue()
        self.stats = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "cancelled_tasks": 0,
            "active_tasks": 0,
            "average_completion_time": 0.0
        }

    async def create_task(self,
                         task_type: str,
                         priority: TaskPriority = TaskPriority.NORMAL,
                         **kwargs) -> str:
        """
        创建新任务

        Args:
            task_type: 任务类型
            priority: 任务优先级
            **kwargs: 任务参数

        Returns:
            str: 任务ID
        """
        task_id = str(uuid.uuid4())

        task = Task(
            id=task_id,
            task_type=task_type,
            priority=priority,
            source_path=kwargs.get('source_path'),
            target_path=kwargs.get('target_path'),
            output_path=kwargs.get('output_path'),
            parameters=kwargs.get('parameters', {})
        )

        self.tasks[task_id] = task
        self.stats["total_tasks"] += 1

        logger.info(f"创建任务: {task_id} 类型: {task_type} 优先级: {priority.name}")

        # 将任务加入队列
        await self.task_queue.put(task)

        return task_id

    async def get_task(self, task_id: str) -> Optional[Task]:
        """
        获取任务

        Args:
            task_id: 任务ID

        Returns:
            Optional[Task]: 任务对象
        """
        return self.tasks.get(task_id)

    async def execute_task(self, task: Task) -> None:
        """
        执行任务

        Args:
            task: 任务对象
        """
        try:
            task.started_at = time.time()
            task.status = TaskStatus.RESOURCE_LOADING
            task.update_progress(5.0, "开始加载资源")

            logger.info(f"开始执行任务: {task.id}")

            # 根据任务类型执行相应处理
            if task.task_type == "image_to_camera":
                await self._execute_image_to_camera(task)
            elif task.task_type == "image_to_video":
                await self._execute_image_to_video(task)
            elif task.task_type == "video_to_camera":
                await self._execute_video_to_camera(task)
            elif task.task_type == "image_to_image":
                await self._execute_image_to_image(task)
            elif task.task_type == "ai_analyze":
                await self._execute_ai_analyze(task)
            else:
                raise ValueError(f"不支持的任务类型: {task.task_type}")

            task.complete()
            self.stats["completed_tasks"] += 1

            logger.info(f"任务完成: {task.id}")

        except Exception as e:
            error_msg = f"任务执行失败: {str(e)}"
            task.fail(error_msg)
            self.stats["failed_tasks"] += 1

            logger.error(f"任务失败: {task.id} - {error_msg}")

        finally:
            # 从活跃任务中移除
            if task.id in self.active_tasks:
                del self.active_tasks[task.id]

            # 更新统计信息
            self._update_stats()

    async def cancel_task(self, task_id: str) -> bool:
        """
        取消任务

        Args:
            task_id: 任务ID

        Returns:
            bool: 是否成功取消
        """
        task = self.tasks.get(task_id)
        if not task:
            return False

        if task.is_finished():
            return False

        task.cancel()
        self.stats["cancelled_tasks"] += 1

        # 取消活跃任务
        if task_id in self.active_tasks:
            self.active_tasks[task_id].cancel()
            del self.active_tasks[task_id]

        logger.info(f"任务已取消: {task_id}")
        return True

    async def pause_task(self, task_id: str) -> bool:
        """
        暂停任务

        Args:
            task_id: 任务ID

        Returns:
            bool: 是否成功暂停
        """
        task = self.tasks.get(task_id)
        if not task or not task.is_active():
            return False

        task.pause()
        logger.info(f"任务已暂停: {task_id}")
        return True

    async def resume_task(self, task_id: str) -> bool:
        """
        恢复任务

        Args:
            task_id: 任务ID

        Returns:
            bool: 是否成功恢复
        """
        task = self.tasks.get(task_id)
        if not task or task.status != TaskStatus.PAUSED:
            return False

        task.resume()

        # 重新加入队列
        await self.task_queue.put(task)

        logger.info(f"任务已恢复: {task_id}")
        return True

    async def cleanup_completed_tasks(self, max_age: int = 3600) -> int:
        """
        清理已完成的任务

        Args:
            max_age: 最大保留时间（秒）

        Returns:
            int: 清理的任务数量
        """
        current_time = time.time()
        cleaned_count = 0

        tasks_to_remove = []
        for task_id, task in self.tasks.items():
            if (task.is_finished() and
                current_time - task.updated_at > max_age):
                tasks_to_remove.append(task_id)

        for task_id in tasks_to_remove:
            del self.tasks[task_id]
            cleaned_count += 1

        if cleaned_count > 0:
            logger.info(f"清理了 {cleaned_count} 个过期任务")

        return cleaned_count

    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息

        Returns:
            Dict[str, Any]: 统计数据
        """
        return {
            "total_tasks": self.stats["total_tasks"],
            "completed_tasks": self.stats["completed_tasks"],
            "failed_tasks": self.stats["failed_tasks"],
            "cancelled_tasks": self.stats["cancelled_tasks"],
            "active_tasks": len(self.active_tasks),
            "pending_tasks": self.task_queue.qsize(),
            "average_completion_time": self.stats["average_completion_time"]
        }

    def _update_stats(self):
        """更新统计信息"""
        self.stats["active_tasks"] = len(self.active_tasks)

        # 计算平均完成时间
        completed_tasks = [t for t in self.tasks.values()
                          if t.status == TaskStatus.COMPLETED and t.completed_at and t.started_at]

        if completed_tasks:
            total_time = sum(t.completed_at - t.started_at for t in completed_tasks)
            self.stats["average_completion_time"] = total_time / len(completed_tasks)

    # 任务执行方法（Mock实现）
    async def _execute_image_to_camera(self, task: Task):
        """执行图片到摄像头任务"""
        task.status = TaskStatus.AI_PROCESSING
        task.update_progress(20.0, "AI分析图片")

        await asyncio.sleep(1.0)  # 模拟AI处理

        task.status = TaskStatus.SYNTHESIZING
        task.update_progress(60.0, "实时合成")

        await asyncio.sleep(2.0)  # 模拟合成

        task.status = TaskStatus.OUTPUT_GENERATING
        task.update_progress(90.0, "输出到虚拟摄像头")

        await asyncio.sleep(0.5)  # 模拟输出

    async def _execute_image_to_video(self, task: Task):
        """执行图片到视频任务"""
        task.status = TaskStatus.AI_PROCESSING
        task.update_progress(10.0, "AI分析图片")

        await asyncio.sleep(1.0)

        task.status = TaskStatus.SYNTHESIZING
        task.update_progress(30.0, "逐帧处理视频")

        # 模拟逐帧处理
        total_frames = 100
        for i in range(total_frames):
            await asyncio.sleep(0.01)  # 模拟每帧处理
            progress = 30.0 + (i / total_frames) * 50.0
            task.update_progress(progress, f"处理帧 {i+1}/{total_frames}")

        task.status = TaskStatus.OUTPUT_GENERATING
        task.update_progress(90.0, "生成输出视频")

        await asyncio.sleep(1.0)

    async def _execute_video_to_camera(self, task: Task):
        """执行视频到摄像头任务"""
        task.status = TaskStatus.RESOURCE_LOADING
        task.update_progress(20.0, "加载视频")

        await asyncio.sleep(0.5)

        task.status = TaskStatus.OUTPUT_GENERATING
        task.update_progress(50.0, "输出到虚拟摄像头")

        await asyncio.sleep(2.0)

    async def _execute_image_to_image(self, task: Task):
        """执行图片到图片任务"""
        task.status = TaskStatus.AI_PROCESSING
        task.update_progress(30.0, "AI分析图片")

        await asyncio.sleep(1.0)

        task.status = TaskStatus.SYNTHESIZING
        task.update_progress(70.0, "合成图片")

        await asyncio.sleep(1.0)

        task.status = TaskStatus.OUTPUT_GENERATING
        task.update_progress(90.0, "保存结果")

        await asyncio.sleep(0.5)

    async def _execute_ai_analyze(self, task: Task):
        """执行AI分析任务"""
        task.status = TaskStatus.AI_PROCESSING
        task.update_progress(50.0, "AI分析中")

        await asyncio.sleep(2.0)

        task.update_progress(100.0, "分析完成")


# 全局任务管理器实例
_task_manager: Optional[TaskManager] = None


def get_task_manager() -> TaskManager:
    """获取任务管理器实例（单例模式）"""
    global _task_manager
    if _task_manager is None:
        _task_manager = TaskManager()
    return _task_manager
