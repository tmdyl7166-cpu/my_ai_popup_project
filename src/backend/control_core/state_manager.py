#!/usr/bin/env python3
"""
my_ai_popup_project 状态管理器

负责管理系统状态、配置状态、任务状态等全局状态信息。
"""

import asyncio
import json
import os
import threading
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from ...utils.logger import get_logger


@dataclass
class SystemStatus:
    """系统状态"""
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    gpu_usage: Optional[float] = None
    network_status: str = "unknown"
    last_updated: float = field(default_factory=time.time)


@dataclass
class ServiceStatus:
    """服务状态"""
    name: str
    status: str  # running, stopped, error
    pid: Optional[int] = None
    port: Optional[int] = None
    start_time: Optional[float] = None
    last_heartbeat: Optional[float] = None


class StateManager:
    """状态管理器"""

    def __init__(self):
        self.logger = get_logger(__name__)
        self._lock = threading.RLock()

        # 系统状态
        self.system_status = SystemStatus()

        # 服务状态
        self.services: Dict[str, ServiceStatus] = {}

        # 配置状态
        self.config_status = {
            "last_loaded": None,
            "version": None,
            "valid": False,
            "errors": []
        }

        # 运行状态
        self.is_initialized = False
        self.start_time = time.time()

    async def initialize(self):
        """初始化状态管理器"""
        try:
            self.logger.info("初始化状态管理器...")

            # 加载持久化状态
            await self._load_persistent_state()

            # 启动状态监控
            asyncio.create_task(self._status_monitor())

            self.is_initialized = True
            self.logger.info("状态管理器初始化完成")

        except Exception as e:
            self.logger.error(f"状态管理器初始化失败: {e}")
            raise

    async def cleanup(self):
        """清理资源"""
        try:
            self.logger.info("清理状态管理器资源...")

            # 保存状态
            await self._save_persistent_state()

            self.logger.info("状态管理器清理完成")

        except Exception as e:
            self.logger.error(f"状态管理器清理失败: {e}")

    async def _status_monitor(self):
        """状态监控协程"""
        while True:
            try:
                await self._update_system_status()
                await self._check_service_health()
                await asyncio.sleep(30)  # 每30秒更新一次

            except Exception as e:
                self.logger.error(f"状态监控异常: {e}")
                await asyncio.sleep(60)

    async def _update_system_status(self):
        """更新系统状态"""
        try:
            # CPU使用率
            import psutil
            self.system_status.cpu_usage = psutil.cpu_percent(interval=1)

            # 内存使用率
            memory = psutil.virtual_memory()
            self.system_status.memory_usage = memory.percent

            # 磁盘使用率
            disk = psutil.disk_usage('/')
            self.system_status.disk_usage = disk.percent

            # GPU使用率 (如果可用)
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                if gpus:
                    self.system_status.gpu_usage = gpus[0].load * 100
            except ImportError:
                self.system_status.gpu_usage = None

            # 网络状态
            self.system_status.network_status = await self._check_network_status()

            self.system_status.last_updated = time.time()

        except Exception as e:
            self.logger.error(f"更新系统状态失败: {e}")

    async def _check_network_status(self) -> str:
        """检查网络状态"""
        try:
            # 简单的网络连接检查
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return "connected"
        except:
            return "disconnected"

    async def _check_service_health(self):
        """检查服务健康状态"""
        for service_name, service in self.services.items():
            try:
                if service.status == "running":
                    # 检查进程是否还在运行
                    if service.pid and not self._is_process_running(service.pid):
                        service.status = "stopped"
                        self.logger.warning(f"服务 {service_name} 进程已停止")

                    # 检查端口是否开放
                    elif service.port and not await self._is_port_open(service.port):
                        service.status = "error"
                        self.logger.error(f"服务 {service_name} 端口 {service.port} 无响应")

                    else:
                        service.last_heartbeat = time.time()

            except Exception as e:
                self.logger.error(f"检查服务 {service_name} 健康状态失败: {e}")

    def _is_process_running(self, pid: int) -> bool:
        """检查进程是否运行"""
        try:
            import psutil
            return psutil.pid_exists(pid)
        except:
            return False

    async def _is_port_open(self, port: int) -> bool:
        """检查端口是否开放"""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result == 0
        except:
            return False

    def register_service(self, name: str, port: Optional[int] = None, pid: Optional[int] = None):
        """注册服务"""
        with self._lock:
            self.services[name] = ServiceStatus(
                name=name,
                status="starting",
                port=port,
                pid=pid,
                start_time=time.time()
            )
            self.logger.info(f"注册服务: {name}")

    def update_service_status(self, name: str, status: str):
        """更新服务状态"""
        with self._lock:
            if name in self.services:
                self.services[name].status = status
                self.services[name].last_heartbeat = time.time()
                self.logger.info(f"服务 {name} 状态更新为: {status}")

    def unregister_service(self, name: str):
        """注销服务"""
        with self._lock:
            if name in self.services:
                del self.services[name]
                self.logger.info(f"注销服务: {name}")

    def get_service_status(self, name: str) -> Optional[ServiceStatus]:
        """获取服务状态"""
        return self.services.get(name)

    def get_all_services(self) -> Dict[str, ServiceStatus]:
        """获取所有服务状态"""
        with self._lock:
            return self.services.copy()

    def update_config_status(self, version: str, valid: bool, errors: List[str] = None):
        """更新配置状态"""
        with self._lock:
            self.config_status.update({
                "last_loaded": time.time(),
                "version": version,
                "valid": valid,
                "errors": errors or []
            })

    def get_config_status(self) -> Dict[str, Any]:
        """获取配置状态"""
        with self._lock:
            return self.config_status.copy()

    def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        return {
            "cpu_usage": self.system_status.cpu_usage,
            "memory_usage": self.system_status.memory_usage,
            "disk_usage": self.system_status.disk_usage,
            "gpu_usage": self.system_status.gpu_usage,
            "network_status": self.system_status.network_status,
            "uptime": time.time() - self.start_time,
            "services_count": len(self.services),
            "active_services": len([s for s in self.services.values() if s.status == "running"])
        }

    async def _load_persistent_state(self):
        """加载持久化状态"""
        try:
            state_file = Path("logs/state_manager.json")
            if state_file.exists():
                with open(state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 恢复服务状态
                services_data = data.get("services", {})
                for name, service_data in services_data.items():
                    self.services[name] = ServiceStatus(**service_data)

                self.logger.info("持久化状态加载完成")

        except Exception as e:
            self.logger.error(f"加载持久化状态失败: {e}")

    async def _save_persistent_state(self):
        """保存持久化状态"""
        try:
            state_file = Path("logs/state_manager.json")
            state_file.parent.mkdir(parents=True, exist_ok=True)

            # 准备保存的数据
            services_data = {}
            for name, service in self.services.items():
                services_data[name] = {
                    "name": service.name,
                    "status": service.status,
                    "pid": service.pid,
                    "port": service.port,
                    "start_time": service.start_time,
                    "last_heartbeat": service.last_heartbeat
                }

            data = {
                "timestamp": time.time(),
                "services": services_data
            }

            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.logger.info("持久化状态保存完成")

        except Exception as e:
            self.logger.error(f"保存持久化状态失败: {e}")


# 全局状态管理器实例
state_manager = StateManager()
