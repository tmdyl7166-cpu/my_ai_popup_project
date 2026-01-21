#!/usr/bin/env python3
"""
文件工具模块
提供文件操作的统一接口
"""

import os
import json
import yaml
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
import shutil
import tempfile


def read_json(file_path: Union[str, Path]) -> Dict[str, Any]:
    """读取JSON文件"""
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(
    file_path: Union[str, Path], data: Dict[str, Any], indent: int = 2
) -> None:
    """写入JSON文件"""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def read_yaml(file_path: Union[str, Path]) -> Dict[str, Any]:
    """读取YAML文件"""
    try:
        import yaml
    except ImportError:
        raise ImportError("需要安装 PyYAML: pip install PyYAML")

    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def write_yaml(file_path: Union[str, Path], data: Dict[str, Any]) -> None:
    """写入YAML文件"""
    try:
        import yaml
    except ImportError:
        raise ImportError("需要安装 PyYAML: pip install PyYAML")

    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)


def read_text(file_path: Union[str, Path], encoding: str = "utf-8") -> str:
    """读取文本文件"""
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    with open(file_path, "r", encoding=encoding) as f:
        return f.read()


def write_text(
    file_path: Union[str, Path], content: str, encoding: str = "utf-8"
) -> None:
    """写入文本文件"""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding=encoding) as f:
        f.write(content)


def calculate_file_hash(file_path: Union[str, Path], algorithm: str = "md5") -> str:
    """计算文件哈希值"""
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    hash_func = getattr(hashlib, algorithm)()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)

    return hash_func.hexdigest()


def get_file_info(file_path: Union[str, Path]) -> Dict[str, Any]:
    """获取文件信息"""
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    stat = file_path.stat()
    return {
        "path": str(file_path),
        "name": file_path.name,
        "size": stat.st_size,
        "modified": stat.st_mtime,
        "created": stat.st_ctime,
        "is_file": file_path.is_file(),
        "is_dir": file_path.is_dir(),
        "extension": file_path.suffix,
        "hash_md5": calculate_file_hash(file_path, "md5"),
        "hash_sha256": calculate_file_hash(file_path, "sha256"),
    }


def find_files_by_pattern(
    directory: Union[str, Path], pattern: str, recursive: bool = True
) -> List[Path]:
    """按模式查找文件"""
    directory = Path(directory)
    if not directory.exists():
        return []

    if recursive:
        return list(directory.rglob(pattern))
    else:
        return list(directory.glob(pattern))


def copy_file(src: Union[str, Path], dst: Union[str, Path]) -> None:
    """复制文件"""
    src, dst = Path(src), Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def move_file(src: Union[str, Path], dst: Union[str, Path]) -> None:
    """移动文件"""
    src, dst = Path(src), Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(src, dst)


def create_backup(file_path: Union[str, Path], suffix: str = ".backup") -> Path:
    """创建文件备份"""
    file_path = Path(file_path)
    backup_path = file_path.with_suffix(f"{file_path.suffix}{suffix}")
    copy_file(file_path, backup_path)
    return backup_path


def safe_write_file(
    file_path: Union[str, Path], content: str, encoding: str = "utf-8"
) -> None:
    """安全写入文件（先写入临时文件再替换）"""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # 创建临时文件
    with tempfile.NamedTemporaryFile(
        mode="w", dir=file_path.parent, encoding=encoding, delete=False, suffix=".tmp"
    ) as temp_file:
        temp_file.write(content)
        temp_path = Path(temp_file.name)

    # 原子性替换
    temp_path.replace(file_path)


def ensure_directory(path: Union[str, Path]) -> Path:
    """确保目录存在"""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_directory_size(directory: Union[str, Path]) -> int:
    """计算目录大小"""
    directory = Path(directory)
    if not directory.exists():
        return 0

    total_size = 0
    for file_path in directory.rglob("*"):
        if file_path.is_file():
            total_size += file_path.stat().st_size

    return total_size


def clean_directory(
    directory: Union[str, Path], patterns: List[str] = None
) -> Dict[str, int]:
    """清理目录"""
    if patterns is None:
        patterns = ["*.tmp", "*.log", "__pycache__", "*.pyc"]

    directory = Path(directory)
    if not directory.exists():
        return {}

    cleaned = {}
    for pattern in patterns:
        for path in directory.rglob(pattern):
            try:
                if path.is_file():
                    path.unlink()
                    cleaned[pattern] = cleaned.get(pattern, 0) + 1
                elif path.is_dir():
                    shutil.rmtree(path)
                    cleaned[pattern] = cleaned.get(pattern, 0) + 1
            except Exception:
                pass  # 忽略删除失败的文件

    return cleaned
