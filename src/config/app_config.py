"""
应用配置模块
负责加载和管理所有配置项
"""
import os
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv

# 导入路径解析器
from src.utils.path_resolver import PathResolver


@dataclass
class AppConfig:
    """应用配置类"""
    
    # 应用信息
    name: str = "AI弹窗项目"
    version: str = "1.0.0"
    env: str = "development"
    
    # GUI配置
    gui_theme: str = "dark"
    gui_width: int = 1280
    gui_height: int = 720
    
    # API配置
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = True
    api_workers: int = 1
    
    # AI模型配置
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    
    # 处理配置
    gpu_memory_fraction: float = 0.8
    max_workers: int = 4
    temp_dir: str = "/tmp/ai_processing"
    processing_quality: str = "high"
    
    # 虚拟摄像头配置
    virtual_camera_enabled: bool = True
    virtual_camera_device: str = "/dev/video10"
    virtual_camera_width: int = 1280
    virtual_camera_height: int = 720
    virtual_camera_fps: int = 30
    
    # 文件路径配置 - 使用路径解析器获取相对于项目根目录的路径
    project_root: str = ""
    assets_dir: str = ""
    models_dir: str = ""
    output_dir: str = ""
    
    # 日志配置
    log_level: str = "INFO"
    log_file: str = ""
    
    def __post_init__(self):
        """初始化后自动设置路径"""
        # 确保路径解析器已初始化
        if not PathResolver.PROJECT_ROOT:
            PathResolver.initialize()
        
        # 使用路径解析器设置相对路径
        self.project_root = str(PathResolver.get_project_root())
        self.assets_dir = str(PathResolver.get_assets_dir())
        self.models_dir = str(PathResolver.get_models_dir())
        self.output_dir = str(PathResolver.get_output_dir())
        # 设置日志文件路径（相对于项目根目录）
        self.log_file = str(PathResolver.get_logs_dir() / "app.log")
    
    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "AppConfig":
        """加载配置"""
        # 加载环境变量
        if config_path:
            load_dotenv(config_path)
        else:
            # 尝试加载项目根目录的.env文件
            env_path = PathResolver.get_project_root() / ".env"
            if env_path.exists():
                load_dotenv(env_path)
        
        return cls(
            name=os.getenv("APP_NAME", cls.name),
            version=os.getenv("APP_VERSION", cls.version),
            env=os.getenv("APP_ENV", cls.env),
            gui_theme=os.getenv("GUI_THEME", cls.gui_theme),
            gui_width=int(os.getenv("GUI_WIDTH", cls.gui_width)),
            gui_height=int(os.getenv("GUI_HEIGHT", cls.gui_height)),
            api_host=os.getenv("API_HOST", cls.api_host),
            api_port=int(os.getenv("API_PORT", cls.api_port)),
            api_debug=os.getenv("API_DEBUG", str(cls.api_debug)).lower() == "true",
            api_workers=int(os.getenv("API_WORKERS", cls.api_workers)),
            ollama_host=os.getenv("OLLAMA_HOST", cls.ollama_host),
            ollama_model=os.getenv("OLLAMA_MODEL", cls.ollama_model),
            gpu_memory_fraction=float(os.getenv("GPU_MEMORY_FRACTION", cls.gpu_memory_fraction)),
            max_workers=int(os.getenv("MAX_WORKERS", cls.max_workers)),
            temp_dir=os.getenv("TEMP_DIR", cls.temp_dir),
            processing_quality=os.getenv("PROCESSING_QUALITY", cls.processing_quality),
            virtual_camera_enabled=os.getenv("VIRTUAL_CAMERA_ENABLED", str(cls.virtual_camera_enabled)).lower() == "true",
            virtual_camera_device=os.getenv("VIRTUAL_CAMERA_DEVICE", cls.virtual_camera_device),
            virtual_camera_width=int(os.getenv("VIRTUAL_CAMERA_WIDTH", cls.virtual_camera_width)),
            virtual_camera_height=int(os.getenv("VIRTUAL_CAMERA_HEIGHT", cls.virtual_camera_height)),
            virtual_camera_fps=int(os.getenv("VIRTUAL_CAMERA_FPS", cls.virtual_camera_fps)),
            project_root=os.getenv("PROJECT_ROOT", cls.project_root),
            assets_dir=os.getenv("ASSETS_DIR", cls.assets_dir),
            models_dir=os.getenv("MODELS_DIR", cls.models_dir),
            output_dir=os.getenv("OUTPUT_DIR", cls.output_dir),
            log_level=os.getenv("LOG_LEVEL", cls.log_level),
            log_file=os.getenv("LOG_FILE", cls.log_file),
        )
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return getattr(self, key, default)


# 全局配置实例
_config: Optional[AppConfig] = None


def get_config(config_path: Optional[str] = None) -> AppConfig:
    """获取应用配置（单例模式）"""
    global _config
    if _config is None:
        _config = AppConfig.load(config_path)
    return _config


def reload_config(config_path: Optional[str] = None) -> AppConfig:
    """重新加载配置"""
    global _config
    _config = AppConfig.load(config_path)
    return _config

