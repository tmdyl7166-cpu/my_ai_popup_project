#!/usr/bin/env python3
"""
my_ai_popup_project 统一路径配置模块

功能:
    - 提供项目路径的动态检测和统一管理
    - 支持环境变量覆盖默认配置
    - 提供绝对路径和相对路径的转换
    - 缓存路径信息以提高性能

使用方式:
    from scripts.path_config import PROJECT_ROOT, SCRIPTS_DIR, get_engine_path

    # 获取项目根目录
    root = PROJECT_ROOT

    # 获取特定引擎路径
    engine_path = get_engine_path("deep_live_cam")

    # 获取配置路径
    config_path = get_config_path("model_config.json")
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional, Union
from dataclasses import dataclass, field


# ============================================================================
# 常量定义
# ============================================================================

# 脚本目录 (当前文件所在目录)
_SCRIPT_DIR = Path(__file__).parent.resolve()

# 项目根目录 (脚本目录的父目录)
PROJECT_ROOT = _SCRIPT_DIR.parent.resolve()

# ============================================================================
# 路径配置类
# ============================================================================


@dataclass(frozen=True)
class PathConfig:
    """
    路径配置数据类

     Attributes:
        project_root: 项目根目录绝对路径
        scripts_dir: 脚本目录
        src_dir: 源码目录
        frontend_dir: 前端目录
        backend_dir: 后端目录
        processing_dir: 处理引擎目录
        integrations_dir: 集成目录
        config_dir: 配置文件目录
        rules_dir: 规则目录
        assets_dir: 资源目录
        docs_dir: 文档目录
        logs_dir: 日志目录
        web_dir: Web监控目录
        tests_dir: 测试目录
    """

    project_root: Path = PROJECT_ROOT
    scripts_dir: Path = _SCRIPT_DIR
    src_dir: Path = PROJECT_ROOT / "src"
    frontend_dir: Path = PROJECT_ROOT / "src" / "frontend"
    backend_dir: Path = PROJECT_ROOT / "src" / "backend"
    processing_dir: Path = PROJECT_ROOT / "src" / "processing"
    integrations_dir: Path = PROJECT_ROOT / "src" / "integrations"
    config_dir: Path = PROJECT_ROOT / "rules"
    rules_dir: Path = PROJECT_ROOT / "rules"
    assets_dir: Path = PROJECT_ROOT / "assets"
    docs_dir: Path = PROJECT_ROOT / "docs"
    logs_dir: Path = PROJECT_ROOT / "logs"
    web_dir: Path = PROJECT_ROOT / "web"
    tests_dir: Path = PROJECT_ROOT / "tests"

    # 第三方集成子目录
    deep_live_cam_dir: Path = assets_dir / "Deep-Live-Cam-main"
    facefusion_dir: Path = assets_dir / "facefusion-master"
    iroop_dir: Path = assets_dir / "iRoopDeepFaceCam-main"


# 全局路径配置实例
PATH_CONFIG = PathConfig()


# ============================================================================
# 路径检测函数
# ============================================================================


def get_project_root() -> Path:
    """
    获取项目根目录

    Returns:
        Path: 项目根目录绝对路径

    优先级:
        1. 环境变量 MY_AI_POPUP_PROJECT_ROOT
        2. 当前脚本的父目录的父目录
    """
    # 优先使用环境变量
    env_root = os.environ.get("MY_AI_POPUP_PROJECT_ROOT")
    if env_root:
        path = Path(env_root).resolve()
        if path.exists() and path.is_dir():
            return path

    return PROJECT_ROOT


def get_scripts_dir() -> Path:
    """
    获取脚本目录

    Returns:
        Path: 脚本目录绝对路径
    """
    return _SCRIPT_DIR


def get_src_dir() -> Path:
    """
    获取源码目录

    Returns:
        Path: 源码目录绝对路径
    """
    return get_project_root() / "src"


def get_frontend_dir() -> Path:
    """
    获取前端目录

    Returns:
        Path: 前端目录绝对路径
    """
    return get_project_root() / "src" / "frontend"


def get_backend_dir() -> Path:
    """
    获取后端目录

    Returns:
        Path: 后端目录绝对路径
    """
    return get_project_root() / "src" / "backend"


def get_processing_dir() -> Path:
    """
    获取处理引擎目录

    Returns:
        Path: 处理引擎目录绝对路径
    """
    return get_project_root() / "src" / "processing"


def get_integrations_dir() -> Path:
    """
    获取集成目录

    Returns:
        Path: 集成目录绝对路径
    """
    return get_project_root() / "src" / "integrations"


def get_config_dir() -> Path:
    """
    获取配置文件目录

    Returns:
        Path: 配置目录绝对路径 (rules目录)
    """
    return get_project_root() / "rules"


def get_rules_dir() -> Path:
    """
    获取规则目录

    Returns:
        Path: 规则目录绝对路径
    """
    return get_project_root() / "rules"


def get_assets_dir() -> Path:
    """
    获取资源目录

    Returns:
        Path: 资源目录绝对路径
    """
    return get_project_root() / "assets"


def get_docs_dir() -> Path:
    """
    获取文档目录

    Returns:
        Path: 文档目录绝对路径
    """
    return get_project_root() / "docs"


def get_logs_dir() -> Path:
    """
    获取日志目录

    Returns:
        Path: 日志目录绝对路径
    """
    return get_project_root() / "logs"


def get_web_dir() -> Path:
    """
    获取Web监控目录

    Returns:
        Path: Web监控目录绝对路径
    """
    return get_project_root() / "web"


def get_tests_dir() -> Path:
    """
    获取测试目录

    Returns:
        Path: 测试目录绝对路径
    """
    return get_project_root() / "tests"


# ============================================================================
# 引擎路径函数
# ============================================================================


def get_engine_path(engine_name: str) -> Optional[Path]:
    """
    获取指定引擎的路径

    Args:
        engine_name: 引擎名称 (deeplivecam, facefusion, iroop)

    Returns:
        Path: 引擎目录路径，不存在返回None
    """
    engine_name = engine_name.lower().replace("-", "").replace("_", "")

    engine_map = {
        "deeplivecam": get_project_root() / "assets" / "Deep-Live-Cam-main",
        "facefusion": get_project_root() / "assets" / "facefusion-master",
        "iroop": get_project_root() / "assets" / "iRoopDeepFaceCam-main",
    }

    path = engine_map.get(engine_name)
    if path and path.exists():
        return path
    return None


def get_deep_live_cam_path() -> Path:
    """
    获取Deep-Live-Cam引擎路径

    Returns:
        Path: Deep-Live-Cam目录
    """
    return get_project_root() / "assets" / "Deep-Live-Cam-main"


def get_facefusion_path() -> Path:
    """
    获取FaceFusion引擎路径

    Returns:
        Path: FaceFusion目录
    """
    return get_project_root() / "assets" / "facefusion-master"


def get_iroop_path() -> Path:
    """
    获取iRoop引擎路径

    Returns:
        Path: iRoop目录
    """
    return get_project_root() / "assets" / "iRoopDeepFaceCam-main"


# ============================================================================
# 配置文件路径函数
# ============================================================================


def get_config_path(config_name: str) -> Path:
    """
    获取配置文件路径

    Args:
        config_name: 配置文件名

    Returns:
        Path: 配置文件绝对路径
    """
    return get_config_dir() / config_name


def get_rules_config_path(config_name: str) -> Path:
    """
    获取规则配置文件路径

    Args:
        config_name: 规则配置文件名

    Returns:
        Path: 规则配置文件绝对路径
    """
    return get_rules_dir() / config_name


def get_project_config_path() -> Path:
    """
    获取项目配置文件路径

    Returns:
        Path: 项目配置文件
    """
    return get_project_root() / "project_config.json"


def get_requirements_path() -> Path:
    """
    获取依赖文件路径

    Returns:
        Path: requirements.txt文件
    """
    return get_project_root() / "requirements.txt"


# ============================================================================
# 路径验证函数
# ============================================================================


def check_path_exists(path: Union[str, Path]) -> bool:
    """
    检查路径是否存在

    Args:
        path: 要检查的路径

    Returns:
        bool: 路径是否存在
    """
    return Path(path).exists()


def ensure_dir_exists(path: Union[str, Path]) -> Path:
    """
    确保目录存在，如果不存在则创建

    Args:
        path: 目录路径

    Returns:
        Path: 目录路径
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_relative_path(
    absolute_path: Union[str, Path], base_path: Optional[Path] = None
) -> Path:
    """
    获取相对路径

    Args:
        absolute_path: 绝对路径
        base_path: 基准路径，默认为项目根目录

    Returns:
        Path: 相对路径
    """
    if base_path is None:
        base_path = get_project_root()

    absolute_path = Path(absolute_path).resolve()
    base_path = base_path.resolve()

    try:
        return absolute_path.relative_to(base_path)
    except ValueError:
        # 如果无法计算相对路径，返回绝对路径
        return absolute_path


# ============================================================================
# 环境检测函数
# ============================================================================


def is_virtual_environment() -> bool:
    """
    检查是否在虚拟环境中运行

    Returns:
        bool: 是否在虚拟环境中
    """
    return (
        hasattr(sys, "real_prefix")
        or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)
        or os.environ.get("VIRTUAL_ENV") is not None
    )


def get_virtual_env_path() -> Optional[Path]:
    """
    获取虚拟环境路径

    Returns:
        Path: 虚拟环境路径，不存在返回None
    """
    venv_path = os.environ.get("VIRTUAL_ENV")
    if venv_path:
        return Path(venv_path).resolve()

    # 检查常见的虚拟环境位置
    common_venvs = [
        get_project_root() / "ai_popup_env",
        get_project_root() / "venv",
        get_project_root() / ".venv",
    ]

    for venv in common_venvs:
        if venv.exists() and (venv / "bin" / "python").exists():
            return venv

    return None


def is_display_available() -> bool:
    """
    检查是否可用显示（GUI环境）

    Returns:
        bool: 是否可用显示
    """
    display = os.environ.get("DISPLAY", "")
    return bool(display) and display != ""


def is_headless() -> bool:
    """
    检查是否在无头环境中运行

    Returns:
        bool: 是否在无头环境
    """
    return not is_display_available()


# ============================================================================
# 导出配置
# ============================================================================

__all__ = [
    # 路径常量
    "PROJECT_ROOT",
    "PATH_CONFIG",
    # 路径检测函数
    "get_project_root",
    "get_scripts_dir",
    "get_src_dir",
    "get_frontend_dir",
    "get_backend_dir",
    "get_processing_dir",
    "get_integrations_dir",
    "get_config_dir",
    "get_rules_dir",
    "get_assets_dir",
    "get_docs_dir",
    "get_logs_dir",
    "get_web_dir",
    "get_tests_dir",
    # 引擎路径函数
    "get_engine_path",
    "get_deep_live_cam_path",
    "get_facefusion_path",
    "get_iroop_path",
    # 配置文件路径函数
    "get_config_path",
    "get_rules_config_path",
    "get_project_config_path",
    "get_requirements_path",
    # 路径验证函数
    "check_path_exists",
    "ensure_dir_exists",
    "get_relative_path",
    # 环境检测函数
    "is_virtual_environment",
    "get_virtual_env_path",
    "is_display_available",
    "is_headless",
    # 数据类
    "PathConfig",
]


if __name__ == "__main__":
    # 演示路径配置模块的使用
    print("=" * 60)
    print("my_ai_popup_project 路径配置模块测试")
    print("=" * 60)

    print(f"\n项目根目录: {get_project_root()}")
    print(f"脚本目录: {get_scripts_dir()}")
    print(f"源码目录: {get_src_dir()}")
    print(f"前端目录: {get_frontend_dir()}")
    print(f"后端目录: {get_backend_dir()}")
    print(f"处理目录: {get_processing_dir()}")
    print(f"配置目录: {get_config_dir()}")
    print(f"规则目录: {get_rules_dir()}")
    print(f"资源目录: {get_assets_dir()}")
    print(f"文档目录: {get_docs_dir()}")
    print(f"日志目录: {get_logs_dir()}")
    print(f"Web目录: {get_web_dir()}")

    print("\n引擎路径:")
    print(f"  Deep-Live-Cam: {get_deep_live_cam_path()}")
    print(f"  FaceFusion: {get_facefusion_path()}")
    print(f"  iRoop: {get_iroop_path()}")

    print("\n环境检测:")
    print(f"  虚拟环境: {is_virtual_environment()}")
    print(f"  虚拟环境路径: {get_virtual_env_path()}")
    print(f"  显示可用: {is_display_available()}")
    print(f"  无头环境: {is_headless()}")

    print("\n" + "=" * 60)
