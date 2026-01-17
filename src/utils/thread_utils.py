"""
线程工具模块
提供异步任务管理和线程控制功能
"""
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable, Any, Optional, Dict, List
from queue import Queue
import time


class ThreadUtils:
    """线程工具类"""
    
    _instance: Optional["ThreadUtils"] = None
    _executor: Optional[ThreadPoolExecutor] = None
    
    def __new__(cls) -> "ThreadUtils":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, max_workers: int = 4):
        if ThreadUtils._executor is None:
            ThreadUtils._executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def run_in_background(
        self,
        func: Callable,
        callback: Optional[Callable] = None,
        error_callback: Optional[Callable] = None,
        **kwargs
    ) -> Future:
        """在后台线程中运行函数"""
        future = ThreadUtils._executor.submit(func, **kwargs)
        
        if callback:
            future.add_done_callback(
                lambda f: callback(f.result()) if not f.exception() else None
            )
        
        if error_callback:
            future.add_done_callback(
                lambda f: error_callback(f.exception()) if f.exception() else None
            )
        
        return future
    
    def run_async(self, coro):
        """运行异步协程"""
        loop = asyncio.new_event_loop()
        return loop.run_until_complete(coro)
    
    @staticmethod
    def create_worker(func: Callable, daemon: bool = True) -> threading.Thread:
        """创建工作线程"""
        thread = threading.Thread(target=func, daemon=daemon)
        return thread
    
    @staticmethod
    def create_timer(interval: float, func: Callable, daemon: bool = True) -> threading.Timer:
        """创建定时器"""
        return threading.Timer(interval, func, daemon=daemon)


class TaskQueue:
    """任务队列"""
    
    def __init__(self, max_size: int = 100):
        self.queue = Queue(maxsize=max_size)
        self.workers: List[threading.Thread] = []
        self.running = False
    
    def start(self, num_workers: int = 4):
        """启动工作线程"""
        self.running = True
        
        for i in range(num_workers):
            worker = threading.Thread(target=self._worker, daemon=True)
            worker.start()
            self.workers.append(worker)
    
    def stop(self):
        """停止工作线程"""
        self.running = False
        
        # 清空队列
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
            except:
                pass
        
        # 等待工作线程结束
        for worker in self.workers:
            worker.join(timeout=1.0)
        
        self.workers.clear()
    
    def add_task(self, task: Callable, *args, **kwargs) -> bool:
        """添加任务"""
        if not self.running:
            return False
        
        try:
            self.queue.put((task, args, kwargs), block=False)
            return True
        except:
            return False
    
    def _worker(self):
        """工作线程函数"""
        while self.running:
            try:
                task, args, kwargs = self.queue.get(timeout=1.0)
                task(*args, **kwargs)
            except Exception:
                pass  # 忽略异常


class ProgressTracker:
    """进度追踪器"""
    
    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = time.time()
        self.last_update = self.start_time
        self.lock = threading.Lock()
        self.callbacks: List[Callable] = []
    
    def add_callback(self, callback: Callable):
        """添加进度回调"""
        self.callbacks.append(callback)
    
    def update(self, n: int = 1, status: str = ""):
        """更新进度"""
        with self.lock:
            self.current += n
            elapsed = time.time() - self.start_time
            percentage = (self.current / self.total) * 100 if self.total > 0 else 0
            
            if self.current >= self.total:
                status = "Complete"
            
            # 触发回调
            for callback in self.callbacks:
                try:
                    callback(
                        current=self.current,
                        total=self.total,
                        percentage=percentage,
                        elapsed=elapsed,
                        status=status
                    )
                except:
                    pass
    
    def set_total(self, total: int):
        """设置总进度"""
        with self.lock:
            self.total = total
    
    @property
    def progress(self) -> float:
        """获取进度百分比"""
        with self.lock:
            return (self.current / self.total) * 100 if self.total > 0 else 0
    
    @property
    def elapsed(self) -> float:
        """获取已用时间"""
        return time.time() - self.start_time
    
    def get_eta(self) -> float:
        """获取预计剩余时间"""
        with self.lock:
            if self.current <= 0:
                return 0
            
            elapsed = self.elapsed
            rate = self.current / elapsed
            remaining = self.total - self.current
            
            return remaining / rate if rate > 0 else 0

