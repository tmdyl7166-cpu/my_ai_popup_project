#!/usr/bin/env python3
"""
文件操作工具模块
提供统一的文件操作接口
"""

import os
import json
import yaml
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import hashlib

class FileUtils:
    """文件操作工具类"""

    @staticmethod
    def ensure_dir(path: Union[str, Path]) -> Path:
        """确保目录存在"""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def read_json(path: Union[str, Path], encoding: str = 'utf-8') -> Dict[str, Any]:
        """读取JSON文件"""
        with open(path, 'r', encoding=encoding) as f:
            return json.load(f)

    @staticmethod
    def write_json(path: Union[str, Path], data: Dict[str, Any], encoding: str = 'utf-8') -> None:
        """写入JSON文件"""
        FileUtils.ensure_dir(Path(path).parent)
        with open(path, 'w', encoding=encoding) as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def read_yaml(path: Union[str, Path], encoding: str = 'utf-8') -> Dict[str, Any]:
        """读取YAML文件"""
        try:
            import yaml
            with open(path, 'r', encoding=encoding) as f:
                return yaml.safe_load(f)
        except ImportError:
            raise ImportError("需要安装PyYAML: pip install PyYAML")

    @staticmethod
    def write_yaml(path: Union[str, Path], data: Dict[str, Any], encoding: str = 'utf-8') -> None:
        """写入YAML文件"""
        try:
            import yaml
            FileUtils.ensure_dir(Path(path).parent)
            with open(path, 'w', encoding=encoding) as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        except ImportError:
            raise ImportError("需要安装PyYAML: pip install PyYAML")

    @staticmethod
    def read_text(path: Union[str, Path], encoding: str = 'utf-8') -> str:
        """读取文本文件"""
        with open(path, 'r', encoding=encoding) as f:
            return f.read()

    @staticmethod
    def write_text(path: Union[str, Path], content: str, encoding: str = 'utf-8') -> None:
        """写入文本文件"""
        FileUtils.ensure_dir(Path(path).parent)
        with open(path, 'w', encoding=encoding) as f:
            f.write(content)

    @staticmethod
    def list_files(path: Union[str, Path], pattern: str = "*", recursive: bool = False) -> List[Path]:
        """列出文件"""
        path = Path(path)
        if recursive:
            return list(path.rglob(pattern))
        else:
            return list(path.glob(pattern))

    @staticmethod
    def get_file_info(path: Union[str, Path]) -> Dict[str, Any]:
        """获取文件信息"""
        path = Path(path)
        stat = path.stat()

        return {
            'name': path.name,
            'path': str(path),
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'is_file': path.is_file(),
            'is_dir': path.is_dir(),
            'exists': path.exists()
        }

    @staticmethod
    def calculate_hash(path: Union[str, Path], algorithm: str = 'md5') -> str:
        """计算文件哈希"""
        hash_func = getattr(hashlib, algorithm)()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        return hash_func.hexdigest()

    @staticmethod
    def copy_file(src: Union[str, Path], dst: Union[str, Path]) -> None:
        """复制文件"""
        FileUtils.ensure_dir(Path(dst).parent)
        shutil.copy2(src, dst)

    @staticmethod
    def move_file(src: Union[str, Path], dst: Union[str, Path]) -> None:
        """移动文件"""
        FileUtils.ensure_dir(Path(dst).parent)
        shutil.move(src, dst)

    @staticmethod
    def remove_file(path: Union[str, Path]) -> None:
        """删除文件或目录"""
        path = Path(path)
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)

    @staticmethod
    def find_files_by_extension(path: Union[str, Path], extensions: List[str], recursive: bool = True) -> List[Path]:
        """按扩展名查找文件"""
        files = []
        for ext in extensions:
            pattern = f"*.{ext}" if not ext.startswith('.') else f"*{ext}"
            files.extend(FileUtils.list_files(path, pattern, recursive))
        return files

    @staticmethod
    def get_directory_tree(path: Union[str, Path], max_depth: int = 3) -> Dict[str, Any]:
        """获取目录树结构"""
        path = Path(path)

        def _build_tree(current_path: Path, current_depth: int = 0) -> Dict[str, Any]:
            if current_depth > max_depth:
                return {'type': 'truncated'}

            if current_path.is_file():
                return {
                    'type': 'file',
                    'name': current_path.name,
                    'size': current_path.stat().st_size,
                    'modified': datetime.fromtimestamp(current_path.stat().st_mtime).isoformat()
                }
            elif current_path.is_dir():
                children = {}
                try:
                    for item in sorted(current_path.iterdir()):
                        if not item.name.startswith('.'):  # 跳过隐藏文件
                            children[item.name] = _build_tree(item, current_depth + 1)
                except PermissionError:
                    pass

                return {
                    'type': 'directory',
                    'name': current_path.name,
                    'children': children
                }
            else:
                return {'type': 'unknown', 'name': current_path.name}

        return _build_tree(path)

# 便捷函数
def ensure_dir(path: Union[str, Path]) -> Path:
    """确保目录存在"""
    return FileUtils.ensure_dir(path)

def read_json(path: Union[str, Path]) -> Dict[str, Any]:
    """读取JSON文件"""
    return FileUtils.read_json(path)

def write_json(path: Union[str, Path], data: Dict[str, Any]) -> None:
    """写入JSON文件"""
    FileUtils.write_json(path, data)

def read_text(path: Union[str, Path]) -> str:
    """读取文本文件"""
    return FileUtils.read_text(path)

def write_text(path: Union[str, Path], content: str) -> None:
    """写入文本文件"""
    FileUtils.write_text(path, content)
