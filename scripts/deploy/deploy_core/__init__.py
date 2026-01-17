#!/usr/bin/env python3
"""
部署系统核心模块
提供跨平台兼容、执行器和回滚机制
"""

import os
import sys
import subprocess
import shutil
import platform
import tempfile
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from enum import Enum
import logging

# 导入工具模块
from deploy_utils.logger import get_logger as get_deploy_logger
from deploy_utils.config import ConfigManager as DeployConfig


class PlatformType(Enum):
    """平台类型枚举"""
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "darwin"


class DeployStatus(Enum):
    """部署状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"


class DeployContext:
    """部署上下文"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.start_time = datetime.now()
        self.status = DeployStatus.PENDING
        self.steps: List[Dict[str, Any]] = []
        self.artifacts: Dict[str, Any] = {}
        # 设置环境变量
        self.backup_path: Optional[Path] = None
        self._start_time = datetime.now()
        
    def add_step(self, name: str, status: str, message: str = ""):
        """添加部署步骤"""
        step = {
            "name": name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.steps.append(step)
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "project_root": str(self.project_root),
            "start_time": self.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "status": self.status.value,
            "steps": self.steps,
            "artifacts": self.artifacts
        }


class PlatformDetector:
    """平台检测器"""
    
    @staticmethod
    def detect() -> PlatformType:
        """检测当前平台"""
        system = platform.system().lower()
        if system == "windows":
            return PlatformType.WINDOWS
        elif system == "darwin":
            return PlatformType.MACOS
        else:
            return PlatformType.LINUX
    
    @staticmethod
    def is_windows() -> bool:
        """是否Windows平台"""
        return PlatformDetector.detect() == PlatformType.WINDOWS
    
    @staticmethod
    def is_linux() -> bool:
        """是否Linux平台"""
        return PlatformDetector.detect() == PlatformType.LINUX
    
    @staticmethod
    def is_macos() -> bool:
        """是否macOS平台"""
        return PlatformDetector.detect() == PlatformType.MACOS
    
    @staticmethod
    def get_path_separator() -> str:
        """获取路径分隔符"""
        return "\\" if PlatformDetector.is_windows() else "/"
    
    @staticmethod
    def normalize_path(path: str) -> str:
        """规范化路径"""
        if PlatformDetector.is_windows():
            return path.replace("/", "\\")
        else:
            return path.replace("\\", "/")
    
    @staticmethod
    def get_shell_executable() -> str:
        """获取Shell执行器"""
        if PlatformDetector.is_windows():
            return "cmd.exe"
        else:
            return "bash"
    
    @staticmethod
    def get_script_extension() -> str:
        """获取脚本扩展名"""
        return ".bat" if PlatformDetector.is_windows() else ".sh"


class PathUtils:
    """路径工具类"""
    
    @staticmethod
    def ensure_dir(path: Path) -> bool:
        """确保目录存在"""
        try:
            path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            return False
    
    @staticmethod
    def backup_file(file_path: Path, backup_dir: Path) -> Optional[Path]:
        """备份文件"""
        try:
            backup_dir.mkdir(parents=True, exist_ok=True)
            backup_path = backup_dir / f"{file_path.name}.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(file_path, backup_path)
            return backup_path
        except Exception as e:
            return None
    
    @staticmethod
    def cleanup_dir(path: Path) -> bool:
        """清理目录"""
        try:
            if path.exists():
                shutil.rmtree(path)
            return True
        except Exception as e:
            return False


class BaseDeployModule(ABC):
    """部署模块基类"""
    
    def __init__(self, name: str, context: DeployContext):
        self.name = name
        self.context = context
        self.logger = get_deploy_logger(name)
        self.config = DeployConfig()
    
    @abstractmethod
    def check_prerequisites(self) -> bool:
        """检查前置条件"""
        pass
    
    @abstractmethod
    def execute(self) -> bool:
        """执行部署"""
        pass
    
    @abstractmethod
    def rollback(self) -> bool:
        """回滚"""
        pass
    
    def run(self) -> bool:
        """运行完整的部署流程"""
        self.context.add_step(self.name, "running", "开始执行")
        
        # 检查前置条件
        if not self.check_prerequisites():
            self.context.add_step(self.name, "failed", "前置条件检查失败")
            return False
        
        # 执行部署
        if self.execute():
            self.context.add_step(self.name, "success", "执行成功")
            return True
        else:
            self.context.add_step(self.name, "failed", "执行失败")
            # 尝试回滚
            if self.rollback():
                self.context.add_step(self.name, "rolled_back", "已回滚")
            else:
                self.context.add_step(self.name, "failed", "回滚也失败")
            return False


class CommandExecutor:
    """命令执行器"""
    
    def __init__(self, working_dir: Optional[Path] = None):
        self.working_dir = working_dir
        self.logger = get_deploy_logger("command_executor")
    
    def run(self, command: str, shell: bool = True, timeout: int = 300) -> subprocess.CompletedProcess:
        """运行命令"""
        self.logger.info(f"执行命令: {command}")
        
        try:
            if shell:
                result = subprocess.run(
                    command,
                    shell=True,
                    timeout=timeout,
                    capture_output=True,
                    text=True,
                    cwd=str(self.working_dir) if self.working_dir else None
                )
            else:
                result = subprocess.run(
                    command.split(),
                    timeout=timeout,
                    capture_output=True,
                    text=True,
                    cwd=str(self.working_dir) if self.working_dir else None
                )
            
            self.logger.info(f"命令执行完成，返回码: {result.returncode}")
            return result
            
        except subprocess.TimeoutExpired:
            self.logger.error("命令执行超时")
            raise
    
    def run_python(self, script_path: str, args: List[str] = None, timeout: int = 300) -> subprocess.CompletedProcess:
        """运行Python脚本"""
        command = [sys.executable, script_path]
        if args:
            command.extend(args)
        
        return self.run(" ".join(command), timeout=timeout)
    
    def run_shell(self, script_path: str, timeout: int = 300) -> subprocess.CompletedProcess:
        """运行Shell脚本"""
        if PlatformDetector.is_windows():
            command = f"cmd /c \"{script_path}\""
        else:
            command = f"bash \"{script_path}\""
        
        return self.run(command, timeout=timeout)


class RollbackManager:
    """回滚管理器"""
    
    def __init__(self, backup_dir: Path):
        self.backup_dir = backup_dir
        self.backup_records: List[Dict[str, Any]] = []
        self.logger = get_deploy_logger("rollback_manager")
    
    def backup(self, source: Path, description: str = "") -> bool:
        """创建备份"""
        try:
            if not source.exists():
                self.logger.warning(f"备份源不存在: {source}")
                return False
            
            # 创建带时间戳的备份文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"{source.name}_{timestamp}"
            
            # 如果是目录，压缩备份
            if source.is_dir():
                backup_file = self.backup_dir / f"{backup_name}.tar.gz"
                shutil.make_archive(
                    str(backup_file).replace('.tar.gz', ''),
                    'gztar',
                    str(source)
                )
            else:
                backup_file = self.backup_dir / backup_name
                shutil.copy2(source, backup_file)
            
            # 记录备份
            record = {
                "source": str(source),
                "backup": str(backup_file),
                "description": description,
                "timestamp": datetime.now().isoformat()
            }
            self.backup_records.append(record)
            
            self.logger.info(f"备份成功: {source} -> {backup_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"备份失败: {e}")
            return False
    
    def restore(self, backup_record: Dict[str, Any]) -> bool:
        """恢复备份"""
        try:
            backup_path = Path(backup_record["backup"])
            source = Path(backup_record["source"])
            
            if not backup_path.exists():
                self.logger.error(f"备份文件不存在: {backup_path}")
                return False
            
            # 恢复文件
            if backup_path.suffix == '.gz':
                # 解压目录备份
                extract_dir = self.backup_dir / "temp_extract"
                extract_dir.mkdir(exist_ok=True)
                shutil.unpack_archive(str(backup_path), str(extract_dir))
                
                # 移动内容到源目录
                extracted_content = list(extract_dir.iterdir())[0]
                if source.exists():
                    shutil.rmtree(source)
                shutil.move(str(extracted_content), str(source))
                
                shutil.rmtree(str(extract_dir))
            else:
                # 恢复文件备份
                if source.exists():
                    source.unlink()
                shutil.copy2(backup_path, source)
            
            self.logger.info(f"恢复成功: {backup_path} -> {source}")
            return True
            
        except Exception as e:
            self.logger.error(f"恢复失败: {e}")
            return False
    
    def rollback_all(self) -> bool:
        """回滚所有备份"""
        success = True
        # 倒序恢复
        for record in reversed(self.backup_records):
            if not self.restore(record):
                success = False
        
        return success


class DeployCore:
    """部署核心类"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.context = DeployContext(self.project_root)
        self.logger = get_deploy_logger("deploy_core")
        self.executor = CommandExecutor(self.project_root)
        
        # 初始化备份目录
        self.backup_dir = self.project_root / "backup" / "deploy"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.rollback_manager = RollbackManager(self.backup_dir)
        
    def register_module(self, module: BaseDeployModule):
        """注册部署模块"""
        # 模块注册逻辑
        self.logger.info(f"注册模块: {module.name}")
    
    def run_all(self, modules: List[BaseDeployModule]) -> bool:
        """运行所有注册的模块"""
        self.context.status = DeployStatus.RUNNING
        
        for module in modules:
            self.logger.info(f"执行模块: {module.name}")
            
            # 创建模块备份
            self.rollback_manager.backup(
                self.project_root / "requirements.txt",
                f"备份 before {module.name}"
            )
            
            if not module.run():
                self.logger.error(f"模块执行失败: {module.name}")
                
                # 回滚
                self.context.status = DeployStatus.ROLLING_BACK
                if self.rollback_manager.rollback_all():
                    self.context.status = DeployStatus.ROLLED_BACK
                
                return False
        
        self.context.status = DeployStatus.SUCCESS
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """获取部署状态"""
        return self.context.to_dict()

