"""
脚本注册管理器
负责脚本模块的注册、发现和元数据管理
"""
from pathlib import Path
from typing import Dict, List, Any, Optional
import importlib
import importlib.util
import inspect
import logging

logger = logging.getLogger(__name__)

class ScriptRegistry:
    """脚本注册管理器"""

    def __init__(self, scripts_root: Path):
        self.scripts_root = scripts_root
        self.registered_modules: Dict[str, Dict[str, Any]] = {}
        self.discovered_scripts: Dict[str, Dict[str, Any]] = {}

    def register_module(self, name: str, module_path: str, class_name: str, description: str = "") -> None:
        """注册脚本模块"""
        self.registered_modules[name] = {
            'name': name,
            'module_path': module_path,
            'class_name': class_name,
            'description': description,
            'status': 'registered'
        }
        logger.info(f"模块已注册: {name}")

    def discover_scripts(self) -> Dict[str, Dict[str, Any]]:
        """自动发现脚本"""
        # 扫描scripts目录下的所有Python文件
        for py_file in self.scripts_root.rglob('*.py'):
            if py_file.name.startswith('__'):
                continue

            relative_path = py_file.relative_to(self.scripts_root)
            module_name = str(relative_path).replace('.py', '').replace('/', '.')

            try:
                # 尝试导入模块
                spec = importlib.util.spec_from_file_location(module_name, py_file)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # 检查是否有主类
                    main_class = None
                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and hasattr(obj, 'run'):
                            main_class = name
                            break

                    if main_class:
                        script_info = {
                            'name': module_name,
                            'file_path': str(py_file),
                            'module_path': module_name,
                            'class_name': main_class,
                            'description': getattr(module, '__doc__', '').strip() if module.__doc__ else '',
                            'status': 'discovered'
                        }
                        self.discovered_scripts[module_name] = script_info
                        logger.debug(f"发现脚本: {module_name}")

            except Exception as e:
                logger.warning(f"无法加载脚本 {module_name}: {e}")

        return self.discovered_scripts

    def get_registered_modules(self) -> Dict[str, Dict[str, Any]]:
        """获取已注册的模块"""
        return self.registered_modules.copy()

    def get_discovered_scripts(self) -> Dict[str, Dict[str, Any]]:
        """获取已发现的脚本"""
        return self.discovered_scripts.copy()

    def get_module_info(self, module_name: str) -> Optional[Dict[str, Any]]:
        """获取模块信息"""
        if module_name in self.registered_modules:
            return self.registered_modules[module_name]
        if module_name in self.discovered_scripts:
            return self.discovered_scripts[module_name]
        return None

    def list_available_modules(self) -> List[str]:
        """列出所有可用模块"""
        return list(set(list(self.registered_modules.keys()) + list(self.discovered_scripts.keys())))
