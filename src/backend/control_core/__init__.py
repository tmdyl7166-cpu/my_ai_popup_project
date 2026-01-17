"""
my_ai_popup_project 控制核心模块

此模块包含系统的核心控制逻辑，包括服务器、状态管理、管道管理等。
"""

from .server import *
from .state_manager import *
from .pipeline_manager import *

__version__ = "1.0.0"
__all__ = ["server", "state_manager", "pipeline_manager"]
