#!/usr/bin/env python3
"""
脚本注册表
统一管理所有自动化脚本的注册和发现
"""

import os
import sys
import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Type
import pkgutil

from scripts.utils.logging_utils import get_script_logger
from scripts.utils.file_utils import read_json


class ScriptRegistry:
    """脚本注册表"""

    def __init__(self, scripts_dir: Path):
        self.scripts_dir = Path(scripts_dir)
        self.logger = get_script_logger("script_registry")
        self.modules = {}  # 模块名称 -> 模块信息
        self.classes = {}  # 类名 -> 类对象
        self.instances = {}  # 实例名 -> 实例对象

        # 确保脚本目录存在
        self.scripts_dir.mkdir(parents=True, exist_ok=True)

        # 添加脚本目录到Python路径
        if str(self.scripts_dir) not in sys.path:
            sys.path.insert(0, str(self.scripts_dir))

    def discover_scripts(self) -> Dict[str, Any]:
        """发现并注册所有脚本"""
        self.logger.info(f"开始发现脚本，目录: {self.scripts_dir}")

        discovered = {"modules": [], "classes": [], "errors": []}

        # 扫描所有Python文件
        for py_file in self.scripts_dir.rglob("*.py"):
            if py_file.name.startswith("__"):
                continue

            try:
                # 计算相对路径作为模块名
                relative_path = py_file.relative_to(self.scripts_dir)
                module_name = str(relative_path.with_suffix("")).replace(os.sep, ".")

                # 尝试导入模块
                module = importlib.import_module(module_name)

                # 注册模块
                self._register_module(module_name, module, py_file)

                discovered["modules"].append(module_name)

                # 发现模块中的类
                classes = self._discover_classes_in_module(module)
                discovered["classes"].extend(classes)

            except Exception as e:
                error_info = {
                    "file": str(py_file),
                    "module": module_name,
                    "error": str(e),
                }
                discovered["errors"].append(error_info)
                self.logger.warning(f"加载模块失败 {module_name}: {e}")

        self.logger.info(
            f"脚本发现完成，发现 {len(discovered['modules'])} 个模块，{len(discovered['classes'])} 个类"
        )
        return discovered

    def _register_module(self, module_name: str, module: Any, file_path: Path) -> None:
        """注册模块"""
        module_info = {
            "name": module_name,
            "module": module,
            "file_path": file_path,
            "classes": [],
            "functions": [],
            "last_modified": file_path.stat().st_mtime,
        }

        # 发现模块成员
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and not name.startswith("_"):
                module_info["classes"].append(name)
                self.classes[f"{module_name}.{name}"] = obj
            elif inspect.isfunction(obj) and not name.startswith("_"):
                module_info["functions"].append(name)

        self.modules[module_name] = module_info

    def _discover_classes_in_module(self, module: Any) -> List[str]:
        """发现模块中的类"""
        classes = []
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and not name.startswith("_"):
                full_name = f"{module.__name__}.{name}"
                classes.append(full_name)
        return classes

    def get_module_info(self, module_name: str) -> Optional[Dict[str, Any]]:
        """获取模块信息"""
        return self.modules.get(module_name)

    def get_class(self, class_name: str) -> Optional[Type]:
        """获取类对象"""
        return self.classes.get(class_name)

    def create_instance(self, class_name: str, *args, **kwargs) -> Optional[Any]:
        """创建类实例"""
        cls = self.get_class(class_name)
        if cls:
            try:
                instance = cls(*args, **kwargs)
                instance_name = f"{class_name}_{id(instance)}"
                self.instances[instance_name] = instance
                return instance
            except Exception as e:
                self.logger.error(f"创建实例失败 {class_name}: {e}")
        return None

    def list_available_modules(self) -> List[str]:
        """列出所有可用模块"""
        return list(self.modules.keys())

    def list_available_classes(self) -> List[str]:
        """列出所有可用类"""
        return list(self.classes.keys())

    def execute_module_function(
        self, module_name: str, function_name: str, *args, **kwargs
    ) -> Any:
        """执行模块函数"""
        module_info = self.get_module_info(module_name)
        if not module_info:
            raise ValueError(f"模块不存在: {module_name}")

        module = module_info["module"]
        if not hasattr(module, function_name):
            raise ValueError(f"函数不存在: {module_name}.{function_name}")

        func = getattr(module, function_name)
        if not callable(func):
            raise ValueError(f"不是可调用对象: {module_name}.{function_name}")

        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"执行函数失败 {module_name}.{function_name}: {e}")
            raise

    def reload_module(self, module_name: str) -> bool:
        """重新加载模块"""
        if module_name not in self.modules:
            return False

        try:
            # 从sys.modules中移除
            if module_name in sys.modules:
                del sys.modules[module_name]

            # 重新导入
            module = importlib.import_module(module_name)

            # 更新注册信息
            module_info = self.modules[module_name]
            self._register_module(module_name, module, module_info["file_path"])

            self.logger.info(f"模块重新加载成功: {module_name}")
            return True

        except Exception as e:
            self.logger.error(f"重新加载模块失败 {module_name}: {e}")
            return False

    def get_module_dependencies(self, module_name: str) -> List[str]:
        """获取模块依赖"""
        module_info = self.get_module_info(module_name)
        if not module_info:
            return []

        dependencies = []
        module = module_info["module"]

        # 检查导入语句
        try:
            source = inspect.getsource(module)
            lines = source.split("\n")

            for line in lines:
                line = line.strip()
                if line.startswith("import ") or line.startswith("from "):
                    # 简单解析导入语句
                    if " import " in line:
                        parts = line.split(" import ")
                        if len(parts) >= 1:
                            dep_module = parts[0].replace("from ", "").strip()
                            dependencies.append(dep_module)
        except Exception:
            pass

        return dependencies

    def validate_module(self, module_name: str) -> Dict[str, Any]:
        """验证模块"""
        result = {"valid": True, "errors": [], "warnings": []}

        module_info = self.get_module_info(module_name)
        if not module_info:
            result["valid"] = False
            result["errors"].append(f"模块不存在: {module_name}")
            return result

        module = module_info["module"]
        file_path = module_info["file_path"]

        # 检查文件是否存在
        if not file_path.exists():
            result["valid"] = False
            result["errors"].append(f"模块文件不存在: {file_path}")

        # 检查语法
        try:
            compile(
                open(file_path, "r", encoding="utf-8").read(), str(file_path), "exec"
            )
        except SyntaxError as e:
            result["valid"] = False
            result["errors"].append(f"语法错误: {e}")

        # 检查依赖
        dependencies = self.get_module_dependencies(module_name)
        for dep in dependencies:
            try:
                importlib.import_module(dep)
            except ImportError:
                result["warnings"].append(f"依赖模块不可用: {dep}")

        return result

    def get_registry_stats(self) -> Dict[str, Any]:
        """获取注册表统计信息"""
        return {
            "total_modules": len(self.modules),
            "total_classes": len(self.classes),
            "total_instances": len(self.instances),
            "scripts_directory": str(self.scripts_dir),
        }

    def cleanup_instances(self) -> int:
        """清理实例"""
        count = len(self.instances)
        self.instances.clear()
        self.logger.info(f"清理了 {count} 个实例")
        return count

    def export_registry(self, output_file: str) -> None:
        """导出注册表信息"""
        from scripts.utils.file_utils import write_json

        export_data = {
            "stats": self.get_registry_stats(),
            "modules": {},
            "classes": list(self.classes.keys()),
            "instances": list(self.instances.keys()),
        }

        for name, info in self.modules.items():
            export_data["modules"][name] = {
                "file_path": str(info["file_path"]),
                "classes": info["classes"],
                "functions": info["functions"],
                "last_modified": info["last_modified"],
            }

        write_json(output_file, export_data)
        self.logger.info(f"注册表信息已导出到: {output_file}")
