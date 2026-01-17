"""
路径解析工具模块
提供统一的路径解析功能，确保所有路径都相对于项目根目录 my_ai_popup_project
"""
import os
from pathlib import Path
from typing import Optional


class PathResolver:
    """
    路径解析器类
    确保项目中的所有路径都相对于项目根目录
    """
    
    # 项目根目录（my_ai_popup_project）
    PROJECT_ROOT: Optional[Path] = None
    
    @classmethod
    def initialize(cls, project_root: Optional[Path] = None) -> None:
        """
        初始化路径解析器
        
        Args:
            project_root: 项目根目录路径，如果为None则自动检测
        """
        if project_root is not None:
            cls.PROJECT_ROOT = Path(project_root)
            return
        
        # 自动检测项目根目录
        # 向上查找直到找到 my_ai_popup_project 目录
        current_path = Path(__file__).resolve()
        
        # 从当前文件位置向上查找
        for parent in current_path.parents:
            if parent.name == 'my_ai_popup_project':
                cls.PROJECT_ROOT = parent
                break
        else:
            # 如果没找到，使用默认逻辑
            # 假设当前文件位于 my_ai_popup_project/src/utils/ 中
            cls.PROJECT_ROOT = current_path.parent.parent.parent
    
    @classmethod
    def get_project_root(cls) -> Path:
        """获取项目根目录"""
        if cls.PROJECT_ROOT is None:
            cls.initialize()
        assert cls.PROJECT_ROOT is not None, "项目根目录未初始化"
        return cls.PROJECT_ROOT
    
    @classmethod
    def get_assets_dir(cls) -> Path:
        """获取资源目录"""
        return cls.get_project_root() / 'assets'
    
    @classmethod
    def get_models_dir(cls) -> Path:
        """获取模型目录"""
        return cls.get_assets_dir() / 'models'
    
    @classmethod
    def get_images_dir(cls) -> Path:
        """获取图片资源目录"""
        return cls.get_assets_dir() / 'images'
    
    @classmethod
    def get_videos_dir(cls) -> Path:
        """获取视频资源目录"""
        return cls.get_assets_dir() / 'videos'
    
    @classmethod
    def get_output_dir(cls) -> Path:
        """获取输出目录"""
        return cls.get_videos_dir() / 'output'
    
    @classmethod
    def get_logs_dir(cls) -> Path:
        """获取日志目录"""
        return cls.get_project_root() / 'logs'
    
    @classmethod
    def get_src_dir(cls) -> Path:
        """获取源代码目录"""
        return cls.get_project_root() / 'src'
    
    @classmethod
    def get_config_dir(cls) -> Path:
        """获取配置目录"""
        return cls.get_src_dir() / 'config'
    
    @classmethod
    def get_deep_live_cam_dir(cls) -> Path:
        """获取 Deep-Live-Cam 目录"""
        return cls.get_project_root() / 'assets' / 'Deep-Live-Cam-main'
    
    @classmethod
    def get_facefusion_dir(cls) -> Path:
        """获取 Facefusion 目录"""
        return cls.get_project_root() / 'assets' / 'facefusion-master'
    
    @classmethod
    def get_iroop_deepfacecam_dir(cls) -> Path:
        """获取 iRoopDeepFaceCam 目录"""
        return cls.get_project_root() / 'assets' / 'iRoopDeepFaceCam-main'
    
    @classmethod
    def resolve(cls, *paths: str) -> Path:
        """
        解析相对于项目根目录的路径
        
        Args:
            *paths: 路径部分
            
        Returns:
            完整的绝对路径
        """
        return cls.get_project_root().joinpath(*paths)
    
    @classmethod
    def resolve_assets(cls, *paths: str) -> Path:
        """
        解析相对于资源目录的路径
        
        Args:
            *paths: 路径部分
            
        Returns:
            完整的绝对路径
        """
        return cls.get_assets_dir().joinpath(*paths)
    
    @classmethod
    def resolve_models(cls, *paths: str) -> Path:
        """
        解析相对于模型目录的路径
        
        Args:
            *paths: 路径部分
            
        Returns:
            完整的绝对路径
        """
        return cls.get_models_dir().joinpath(*paths)
    
    @classmethod
    def resolve_output(cls, *paths: str) -> Path:
        """
        解析相对于输出目录的路径
        
        Args:
            *paths: 路径部分
            
        Returns:
            完整的绝对路径
        """
        return cls.get_output_dir().joinpath(*paths)
    
    @classmethod
    def resolve_logs(cls, *paths: str) -> Path:
        """
        解析相对于日志目录的路径
        
        Args:
            *paths: 路径部分
            
        Returns:
            完整的绝对路径
        """
        return cls.get_logs_dir().joinpath(*paths)
    
    @classmethod
    def get_temp_dir(cls) -> Path:
        """获取临时文件目录"""
        temp_dir = cls.get_project_root() / 'temp'
        temp_dir.mkdir(parents=True, exist_ok=True)
        return temp_dir
    
    @classmethod
    def ensure_dir_exists(cls, path: Path) -> Path:
        """
        确保目录存在
        
        Args:
            path: 目录路径
            
        Returns:
            创建的目录路径
        """
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @classmethod
    def get_test_data_dir(cls) -> Path:
        """获取测试数据目录"""
        return cls.get_project_root() / 'tests' / 'test_data'


# 便捷函数
def get_project_root() -> Path:
    """获取项目根目录"""
    return PathResolver.get_project_root()


def resolve_path(*paths: str) -> Path:
    """解析相对于项目根目录的路径"""
    return PathResolver.resolve(*paths)


def ensure_project_structure() -> None:
    """
    确保项目目录结构完整
    """
    required_dirs = [
        PathResolver.get_assets_dir(),
        PathResolver.get_models_dir(),
        PathResolver.get_images_dir(),
        PathResolver.get_videos_dir(),
        PathResolver.get_output_dir(),
        PathResolver.get_logs_dir(),
        PathResolver.get_src_dir(),
        PathResolver.get_config_dir(),
        PathResolver.get_temp_dir(),
    ]
    
    for dir_path in required_dirs:
        PathResolver.ensure_dir_exists(dir_path)


# 初始化路径解析器
PathResolver.initialize()

