"""
文件工具模块
提供文件操作和路径管理的功能
"""
import os
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime


class FileUtils:
    """文件工具类"""
    
    # 支持的图片格式
    IMAGE_FORMATS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}
    
    # 支持的视频格式
    VIDEO_FORMATS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
    
    # 支持的模型格式
    MODEL_FORMATS = {".pt", ".pth", ".onnx", ".h5", ".bin", ".safetensors"}
    
    @staticmethod
    def get_file_extension(file_path: str) -> str:
        """获取文件扩展名"""
        return Path(file_path).suffix.lower()
    
    @staticmethod
    def is_image(file_path: str) -> bool:
        """检查是否为图片文件"""
        return FileUtils.get_file_extension(file_path) in FileUtils.IMAGE_FORMATS
    
    @staticmethod
    def is_video(file_path: str) -> bool:
        """检查是否为视频文件"""
        return FileUtils.get_file_extension(file_path) in FileUtils.VIDEO_FORMATS
    
    @staticmethod
    def is_model(file_path: str) -> bool:
        """检查是否为模型文件"""
        return FileUtils.get_file_extension(file_path) in FileUtils.MODEL_FORMATS
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """获取文件大小（字节）"""
        return Path(file_path).stat().st_size
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} PB"
    
    @staticmethod
    def list_files(
        directory: str,
        extensions: Optional[set] = None,
        recursive: bool = False
    ) -> List[Path]:
        """列出目录中的文件"""
        dir_path = Path(directory)
        if not dir_path.exists():
            return []
        
        files = []
        
        if recursive:
            for root, _, filenames in os.walk(dir_path):
                for filename in filenames:
                    if extensions is None or Path(filename).suffix.lower() in extensions:
                        files.append(Path(root) / filename)
        else:
            for item in dir_path.iterdir():
                if item.is_file():
                    if extensions is None or item.suffix.lower() in extensions:
                        files.append(item)
        
        return files
    
    @staticmethod
    def list_directories(directory: str) -> List[Path]:
        """列出目录中的子目录"""
        dir_path = Path(directory)
        if not dir_path.exists():
            return []
        
        return [item for item in dir_path.iterdir() if item.is_dir()]
    
    @staticmethod
    def create_directory(path: str, exist_ok: bool = True) -> Path:
        """创建目录"""
        dir_path = Path(path)
        dir_path.mkdir(parents=True, exist_ok=exist_ok)
        return dir_path
    
    @staticmethod
    def ensure_directory_exists(path: str) -> Path:
        """确保目录存在"""
        return FileUtils.create_directory(path, exist_ok=True)
    
    @staticmethod
    def copy_file(src: str, dst: str, overwrite: bool = False) -> bool:
        """复制文件"""
        src_path = Path(src)
        dst_path = Path(dst)
        
        if not src_path.exists():
            return False
        
        if dst_path.exists() and not overwrite:
            return False
        
        shutil.copy2(src_path, dst_path)
        return True
    
    @staticmethod
    def move_file(src: str, dst: str) -> bool:
        """移动文件"""
        src_path = Path(src)
        dst_path = Path(dst)
        
        if not src_path.exists():
            return False
        
        shutil.move(str(src_path), str(dst_path))
        return True
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """删除文件"""
        path = Path(file_path)
        if path.exists():
            path.unlink()
            return True
        return False
    
    @staticmethod
    def get_file_info(file_path: str) -> Dict[str, Any]:
        """获取文件信息"""
        path = Path(file_path)
        
        if not path.exists():
            return {}
        
        stat = path.stat()
        
        return {
            "path": str(path.absolute()),
            "name": path.name,
            "extension": path.suffix.lower(),
            "size": stat.st_size,
            "size_formatted": FileUtils.format_file_size(stat.st_size),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "is_image": FileUtils.is_image(file_path),
            "is_video": FileUtils.is_video(file_path),
            "is_model": FileUtils.is_model(file_path),
        }
    
    @staticmethod
    def clean_directory(directory: str, keep_patterns: Optional[List[str]] = None) -> int:
        """清理目录中的临时文件"""
        dir_path = Path(directory)
        if not dir_path.exists():
            return 0
        
        deleted = 0
        keep_patterns = keep_patterns or []
        
        for item in dir_path.iterdir():
            if item.is_file():
                should_keep = False
                for pattern in keep_patterns:
                    if pattern in item.name:
                        should_keep = True
                        break
                
                if not should_keep:
                    item.unlink()
                    deleted += 1
        
        return deleted
    
    @staticmethod
    def get_unique_path(base_path: str) -> str:
        """生成唯一的文件路径"""
        path = Path(base_path)
        
        if not path.exists():
            return str(path)
        
        parent = path.parent
        stem = path.stem
        suffix = path.suffix
        
        counter = 1
        while True:
            new_name = f"{stem}_{counter}{suffix}"
            new_path = parent / new_name
            if not new_path.exists():
                return str(new_path)
            counter += 1

