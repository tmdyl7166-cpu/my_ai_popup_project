#!/usr/bin/env python3
"""
跨平台兼容层
处理不同操作系统之间的差异
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from enum import Enum
import logging

# 设置日志
logger = logging.getLogger("deploy.platform")


class OSType(Enum):
    """操作系统类型"""
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "darwin"
    UNKNOWN = "unknown"


class PlatformInfo:
    """平台信息"""
    
    def __init__(self):
        self.os_type = self._detect_os()
        self.is_64bit = sys.maxsize > 2**32
        self.python_version = tuple(map(int, platform.python_version().split('.')))
        self.home_dir = Path.home()
        
    def _detect_os(self) -> OSType:
        """检测操作系统类型"""
        system = platform.system().lower()
        if system == "windows":
            return OSType.WINDOWS
        elif system == "darwin":
            return OSType.MACOS
        elif system == "linux":
            return OSType.LINUX
        return OSType.UNKNOWN
    
    @property
    def is_windows(self) -> bool:
        return self.os_type == OSType.WINDOWS
    
    @property
    def is_linux(self) -> bool:
        return self.os_type == OSType.LINUX
    
    @property
    def is_macos(self) -> bool:
        return self.os_type == OSType.MACOS
    
    def __repr__(self):
        return f"PlatformInfo(os={self.os_type.value}, python={platform.python_version()}, 64bit={self.is_64bit})"


class PathResolver:
    """路径解析器"""
    
    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or Path.cwd()
        self.platform = PlatformInfo()
    
    def to_native(self, path: str) -> str:
        """转换为本地路径格式"""
        if self.platform.is_windows:
            return path.replace("/", "\\")
        return path.replace("\\", "/")
    
    def to_unix(self, path: str) -> str:
        """转换为Unix路径格式"""
        return path.replace("\\", "/")
    
    def join(self, *parts) -> Path:
        """跨平台路径拼接"""
        return self.base_path.joinpath(*parts)
    
    def relative_to(self, path: Path, base: Optional[Path] = None) -> Path:
        """获取相对路径"""
        base = base or self.base_path
        try:
            return path.relative_to(base)
        except ValueError:
            return path
    
    def expanduser(self, path: str) -> Path:
        """展开用户目录"""
        return Path(path).expanduser()
    
    def which(self, command: str) -> Optional[Path]:
        """查找命令路径"""
        try:
            result = shutil.which(command)
            if result:
                return Path(result)
        except Exception:
            pass
        return None


class CommandBuilder:
    """命令构建器"""
    
    def __init__(self):
        self.platform = PlatformInfo()
        self._command_parts: List[str] = []
    
    def append(self, part: str) -> 'CommandBuilder':
        """添加命令部分"""
        self._command_parts.append(part)
        return self
    
    def extend(self, parts: List[str]) -> 'CommandBuilder':
        """批量添加命令部分"""
        self._command_parts.extend(parts)
        return self
    
    def build(self, shell: bool = True) -> str:
        """构建命令字符串"""
        return " ".join(self._command_parts)
    
    @staticmethod
    def python(script: str, args: List[str] = None, module: bool = False) -> 'CommandBuilder':
        """构建Python命令"""
        builder = CommandBuilder()
        builder.append(sys.executable)
        
        if module:
            builder.append("-m")
        
        if script:
            if module:
                builder.append(script)
            else:
                builder.append(script)
        
        if args:
            builder.extend(args)
        
        return builder
    
    @staticmethod
    def pip(args: List[str]) -> 'CommandBuilder':
        """构建pip命令"""
        builder = CommandBuilder()
        builder.append(sys.executable)
        builder.append("-m")
        builder.append("pip")
        builder.extend(args)
        return builder
    
    @staticmethod
    def shell(script: str) -> 'CommandBuilder':
        """构建Shell命令"""
        builder = CommandBuilder()
        
        if PlatformInfo().is_windows:
            builder.append("cmd /c")
            builder.append(f'"{script}"')
        else:
            builder.append("bash")
            builder.append("-c")
            builder.append(f'"{script}"')
        
        return builder
    
    def run(self, timeout: int = 300, capture: bool = True) -> subprocess.CompletedProcess:
        """运行命令"""
        cmd_str = self.build()
        logger.info(f"执行命令: {cmd_str}")
        
        try:
            result = subprocess.run(
                cmd_str,
                shell=shell,
                timeout=timeout,
                capture_output=capture,
                text=True,
                cwd=str(Path.cwd())
            )
            
            if result.returncode == 0:
                logger.info(f"命令执行成功")
            else:
                logger.warning(f"命令执行失败，返回码: {result.returncode}")
                if result.stderr:
                    logger.error(f"错误输出: {result.stderr}")
            
            return result
            
        except subprocess.TimeoutExpired:
            logger.error("命令执行超时")
            raise
    
    def __str__(self):
        return self.build()


class EnvironmentUtils:
    """环境工具类"""
    
    @staticmethod
    def get_env(key: str, default: str = "") -> str:
        """获取环境变量"""
        return os.environ.get(key, default)
    
    @staticmethod
    def set_env(key: str, value: str):
        """设置环境变量"""
        os.environ[key] = value
    
    @staticmethod
    def get_python_path() -> Path:
        """获取Python路径"""
        return Path(sys.executable)
    
    @staticmethod
    def get_site_packages_path() -> Path:
        """获取site-packages路径"""
        import site
        return Path(site.getsitepackages()[0])
    
    @staticmethod
    def get_virtualenv_path() -> Optional[Path]:
        """获取虚拟环境路径"""
        # 检查常见的虚拟环境位置
        venv_names = ['ai_popup_env', 'venv', '.venv', 'env']
        
        for venv_name in venv_names:
            venv_path = Path.cwd() / venv_name
            if venv_path.exists():
                # 检查是否包含Python可执行文件
                python_path = venv_path / "bin" / "python" if not PlatformInfo().is_windows else venv_path / "Scripts" / "python.exe"
                if python_path.exists():
                    return venv_path
        
        return None
    
    @staticmethod
    def is_virtualenv() -> bool:
        """是否在虚拟环境中"""
        return EnvironmentUtils.get_virtualenv_path() is not None
    
    @staticmethod
    def check_command(command: str) -> bool:
        """检查命令是否存在"""
        return shutil.which(command) is not None


class FileOperations:
    """文件操作工具"""
    
    @staticmethod
    def read_file(path: Path, encoding: str = 'utf-8') -> str:
        """读取文件"""
        with open(path, 'r', encoding=encoding) as f:
            return f.read()
    
    @staticmethod
    def write_file(path: Path, content: str, encoding: str = 'utf-8'):
        """写入文件"""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding=encoding) as f:
            f.write(content)
    
    @staticmethod
    def copy(src: Path, dst: Path):
        """复制文件或目录"""
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)
    
    @staticmethod
    def move(src: Path, dst: Path):
        """移动文件或目录"""
        shutil.move(str(src), str(dst))
    
    @staticmethod
    def delete(path: Path):
        """删除文件或目录"""
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
    
    @staticmethod
    def create_backup(path: Path, backup_dir: Path) -> Path:
        """创建备份"""
        backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = backup_dir / f"{path.name}_{timestamp}"
        
        if path.is_dir():
            shutil.make_archive(
                str(backup_path).replace('.tar.gz', ''),
                'gztar',
                str(path)
            )
            return Path(str(backup_path) + '.tar.gz')
        else:
            shutil.copy2(path, backup_path)
            return backup_path


class Registry:
    """跨平台注册表操作（仅Windows）"""
    
    @staticmethod
    def get_value(key: str, value_name: str) -> Optional[str]:
        """获取注册表值"""
        if not PlatformInfo().is_windows:
            return None
        
        try:
            import winreg
            with winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER) as reg:
                with winreg.OpenKey(reg, key, 0, winreg.KEY_READ) as key_handle:
                    value, regtype = winreg.QueryValueEx(key_handle, value_name)
                    return value
        except Exception as e:
            logger.warning(f"读取注册表失败: {e}")
            return None
    
    @staticmethod
    def set_value(key: str, value_name: str, value: str):
        """设置注册表值"""
        if not PlatformInfo().is_windows:
            return
        
        try:
            import winreg
            with winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER) as reg:
                with winreg.OpenKey(reg, key, 0, winreg.KEY_WRITE) as key_handle:
                    winreg.SetValueEx(key_handle, value_name, 0, winreg.REG_SZ, value)
        except Exception as e:
            logger.error(f"写入注册表失败: {e}")


# 导出常用工具
__all__ = [
    'OSType',
    'PlatformInfo',
    'PathResolver',
    'CommandBuilder',
    'EnvironmentUtils',
    'FileOperations',
    'Registry'
]

