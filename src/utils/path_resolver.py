#!/usr/bin/env python3
"""
AI弹窗项目路径解析器
提供统一的路径管理和解析功能
"""

import os
import sys
from pathlib import Path
from typing import Dict


class PathResolver:
    """路径解析器 - 统一管理项目路径"""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._project_root = self._get_project_root()
            self._paths = {}
            self._init_paths()
            self.__class__._initialized = True

    @staticmethod
    def _get_project_root() -> Path:
        """获取项目根目录"""
        # 尝试多种方式确定项目根目录
        current_file = Path(__file__).resolve()

        # 方法1: 通过当前文件位置向上查找
        for parent in current_file.parents:
            if (parent / 'project_config.json').exists() or (parent / '.blackboxrules').exists():
                return parent

        # 方法2: 通过环境变量
        env_root = os.getenv('AI_POPUP_PROJECT_ROOT')
        if env_root and Path(env_root).exists():
            return Path(env_root)

        # 方法3: 通过PYTHONPATH
        for path_str in sys.path:
            path = Path(path_str)
            if (path / 'project_config.json').exists():
                return path

        # 方法4: 默认使用当前工作目录
        cwd = Path.cwd()
        if (cwd / 'project_config.json').exists():
            return cwd

        # 最后的后备方案
        return current_file.parent.parent.parent

    def _init_paths(self):
        """初始化所有路径"""
        root = self._project_root

        # 基础目录
        self._paths.update({
            'project_root': root,
            'src': root / 'src',
            'scripts': root / 'scripts',
            'web': root / 'web',
            'docs': root / 'docs',
            'assets': root / 'assets',
            'logs': root / 'logs',
            'tests': root / 'tests',
            'build': root / 'build',
            'backup': root / 'backup',
        })

        # 子模块目录
        self._paths.update({
            'backend': root / 'src' / 'backend',
            'frontend': root / 'src' / 'frontend',
            'ai': root / 'src' / 'ai',
            'processing': root / 'src' / 'processing',
            'integrations': root / 'src' / 'integrations',
            'utils': root / 'src' / 'utils',
            'config': root / 'src' / 'config',
        })

        # 资产子目录
        self._paths.update({
            'deep_live_cam': root / 'assets' / 'Deep-Live-Cam-main',
            'facefusion': root / 'assets' / 'facefusion-master',
            'iroop_deepfacecam': root / 'assets' / 'iRoopDeepFaceCam-main',
            'obs_studio': root / 'assets' / 'obs-studio-master',
        })

        # 动态目录（运行时创建）
        self._paths.update({
            'temp': root / 'temp',
            'output': root / 'output',
            'cache': root / 'cache',
            'models': root / 'models',
            'images': root / 'images',
            'videos': root / 'videos',
        })

    @property
    def project_root(self) -> Path:
        """获取项目根目录"""
        return self._project_root

    def get_path(self, name: str) -> Path:
        """获取指定路径"""
        if name not in self._paths:
            raise ValueError(f"未知路径名称: {name}")
        return self._paths[name]

    def get_project_root(self) -> Path:
        """获取项目根目录"""
        return self.get_path('project_root')

    def get_src_dir(self) -> Path:
        """获取源代码目录"""
        return self.get_path('src')

    def get_scripts_dir(self) -> Path:
        """获取脚本目录"""
        return self.get_path('scripts')

    def get_assets_dir(self) -> Path:
        """获取资产目录"""
        return self.get_path('assets')

    def get_models_dir(self) -> Path:
        """获取模型目录"""
        return self.get_path('models')

    def get_images_dir(self) -> Path:
        """获取图片目录"""
        return self.get_path('images')

    def get_videos_dir(self) -> Path:
        """获取视频目录"""
        return self.get_path('videos')

    def get_output_dir(self) -> Path:
        """获取输出目录"""
        return self.get_path('output')

    def get_logs_dir(self) -> Path:
        """获取日志目录"""
        return self.get_path('logs')

    def get_temp_dir(self) -> Path:
        """获取临时目录"""
        return self.get_path('temp')

    def get_deep_live_cam_dir(self) -> Path:
        """获取Deep-Live-Cam目录"""
        return self.get_path('deep_live_cam')

    def get_facefusion_dir(self) -> Path:
        """获取FaceFusion目录"""
        return self.get_path('facefusion')

    def get_iroop_deepfacecam_dir(self) -> Path:
        """获取iRoopDeepFaceCam目录"""
        return self.get_path('iroop_deepfacecam')

    def get_obs_studio_dir(self) -> Path:
        """获取OBS Studio目录"""
        return self.get_path('obs_studio')

    def ensure_path_exists(self, name: str) -> Path:
        """确保路径存在，如果不存在则创建"""
        path = self.get_path(name)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_config_file(self, name: str) -> Path:
        """获取配置文件路径"""
        config_files = {
            'project': self.project_root / 'project_config.json',
            'src': self.project_root / 'src' / 'src_config.json',
            'scripts': self.project_root / 'scripts' / 'scripts_config.json',
            'web': self.project_root / 'web' / 'web_config.json',
            'docs': self.project_root / 'docs' / 'docs_config.json',
            'assets': self.project_root / 'assets' / 'assets_config.json',
        }

        if name not in config_files:
            raise ValueError(f"未知配置文件: {name}")

        return config_files[name]

    def get_all_paths(self) -> Dict[str, Path]:
        """获取所有路径"""
        return self._paths.copy()

    def validate_paths(self) -> Dict[str, bool]:
        """验证路径存在性"""
        results = {}
        for name, path in self._paths.items():
            results[name] = path.exists()
        return results


def ensure_project_structure():
    """确保项目结构完整"""
    resolver = PathResolver()

    # 需要确保存在的关键目录
    critical_dirs = [
        'logs', 'temp', 'output', 'cache',
        'models', 'images', 'videos'
    ]

    for dir_name in critical_dirs:
        try:
            resolver.ensure_path_exists(dir_name)
        except Exception as e:
            print(f"警告: 无法创建目录 {dir_name}: {e}")

    # 验证关键路径
    validation = resolver.validate_paths()
    missing_paths = [name for name, exists in validation.items() if not exists]

    if missing_paths:
        print(f"警告: 以下路径不存在: {missing_paths}")
        return False

    return True


# 全局实例
path_resolver = PathResolver()

# 便捷函数
def get_project_root() -> Path:
    return path_resolver.get_project_root()


def get_src_dir() -> Path:
    return path_resolver.get_src_dir()


def get_assets_dir() -> Path:
    return path_resolver.get_assets_dir()


def get_logs_dir() -> Path:
    return path_resolver.get_logs_dir()


if __name__ == "__main__":
    # 测试路径解析器
    resolver = PathResolver()

    print("项目路径解析器测试:")
    print(f"项目根目录: {resolver.get_project_root()}")
    print(f"源代码目录: {resolver.get_src_dir()}")
    print(f"资产目录: {resolver.get_assets_dir()}")
    print(f"日志目录: {resolver.get_logs_dir()}")

    print("\n路径验证:")
    validation = resolver.validate_paths()
    for name, exists in validation.items():
        status = "✓" if exists else "✗"
        print(f"  {status} {name}: {resolver.get_path(name)}")

    print(f"\n项目结构完整性: {'✓' if ensure_project_structure() else '✗'}")
