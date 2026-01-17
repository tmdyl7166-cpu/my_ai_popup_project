#!/usr/bin/env python3
"""
全局上下文监控器脚本
监控整个项目的全局上下文关联性，确保所有路径和文件的关联性检查
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.utils.logging_utils import get_script_logger
from scripts.utils.file_utils import read_json, write_json

class GlobalContextMonitor:
    """全局上下文监控器"""

    def __init__(self):
        self.logger = get_script_logger("global_context_monitor")
        self.project_root = project_root
        self.context_config_path = self.project_root / "scripts" / "health" / "global_context_config.json"

        # 定义需要监控的关键路径
        self.critical_paths = {
            "src": self.project_root / "src",
            "web": self.project_root / "web",
            "scripts": self.project_root / "scripts",
            "docs": self.project_root / "docs",
            "assets": self.project_root / "assets",
            "rules": self.project_root / "rules",
            "logs": self.project_root / "logs",
            "tests": self.project_root / "tests"
        }

        # 定义文件关联映射
        self.file_associations = {
            ".py": ["__init__.py", "config.json", "_config.json", "_README.md"],
            ".js": [".min.js", ".map", ".config.js"],
            ".json": [".schema.json", "_config.json"],
            ".md": ["_README.md", ".md.template"],
            ".html": [".css", ".js"],
            ".css": [".min.css", ".map"]
        }

    def load_context_config(self) -> Dict[str, Any]:
        """加载上下文配置"""
        try:
            if self.context_config_path.exists():
                return read_json(self.context_config_path)
            else:
                default_config = {
                    "version": "1.0.0",
                    "last_scan": None,
                    "scan_interval": 3600,  # 1小时
                    "critical_paths": list(self.critical_paths.keys()),
                    "file_associations": self.file_associations,
                    "exclusions": [".git", "__pycache__", ".pytest_cache", "node_modules"],
                    "monitoring": {
                        "enabled": True,
                        "real_time": False,
                        "alerts": True
                    }
                }
                write_json(self.context_config_path, default_config)
                return default_config
        except Exception as e:
            self.logger.error(f"加载上下文配置失败: {e}")
            return {}

    def scan_project_structure(self) -> Dict[str, Any]:
        """扫描项目结构"""
        scan_result = {
            "timestamp": datetime.now().isoformat(),
            "total_files": 0,
            "total_dirs": 0,
            "path_status": {},
            "file_associations": {},
            "orphaned_files": [],
            "missing_associations": [],
            "integrity_issues": []
        }

        config = self.load_context_config()
        exclusions = set(config.get("exclusions", []))

        for path_name, path_obj in self.critical_paths.items():
            if not path_obj.exists():
                scan_result["path_status"][path_name] = "missing"
                scan_result["integrity_issues"].append(f"关键路径不存在: {path_name}")
                continue

            scan_result["path_status"][path_name] = "exists"

            # 递归扫描路径
            for root, dirs, files in os.walk(path_obj):
                # 排除不需要的目录
                dirs[:] = [d for d in dirs if d not in exclusions]

                scan_result["total_dirs"] += len(dirs)
                scan_result["total_files"] += len(files)

                # 检查文件关联性
                for file in files:
                    file_path = Path(root) / file
                    self.check_file_associations(file_path, scan_result)

        return scan_result

    def check_file_associations(self, file_path: Path, scan_result: Dict[str, Any]):
        """检查文件关联性"""
        file_ext = file_path.suffix
        file_name = file_path.name
        dir_path = file_path.parent

        # 检查关联文件
        expected_associations = self.file_associations.get(file_ext, [])

        for assoc in expected_associations:
            if assoc.startswith("."):
                # 扩展名关联
                expected_file = file_path.with_suffix(assoc)
            else:
                # 文件名关联
                expected_file = dir_path / assoc

            if not expected_file.exists():
                scan_result["missing_associations"].append({
                    "file": str(file_path),
                    "expected": str(expected_file),
                    "type": "association"
                })

        # 检查孤立文件
        if self.is_orphaned_file(file_path):
            scan_result["orphaned_files"].append(str(file_path))

    def is_orphaned_file(self, file_path: Path) -> bool:
        """检查是否为孤立文件"""
        # 检查是否有对应的配置文件
        if file_path.suffix == ".py":
            config_file = file_path.with_suffix("_config.json")
            readme_file = file_path.with_suffix("_README.md")
            if not config_file.exists() and not readme_file.exists():
                return True

        # 检查是否有对应的源文件
        if file_path.suffix in [".min.js", ".min.css", ".map"]:
            base_name = file_path.name.split(".")[0]
            source_file = file_path.parent / f"{base_name}{file_path.suffix.replace('.min', '').replace('.map', '')}"
            if not source_file.exists():
                return True

        return False

    def check_global_context_integrity(self) -> Dict[str, Any]:
        """检查全局上下文完整性"""
        integrity_report = {
            "config_consistency": {},
            "path_references": {},
            "import_dependencies": {},
            "cross_references": {},
            "issues": []
        }

        # 检查配置文件一致性
        config_files = [
            "project_config.json",
            "src/src_config.json",
            "web/web_config.json",
            "scripts/scripts_config.json"
        ]

        for config_file in config_files:
            config_path = self.project_root / config_file
            if config_path.exists():
                try:
                    config = read_json(config_path)
                    integrity_report["config_consistency"][config_file] = "valid"

                    # 检查路径引用
                    self.check_path_references(config, config_file, integrity_report)

                except Exception as e:
                    integrity_report["config_consistency"][config_file] = f"invalid: {e}"
                    integrity_report["issues"].append(f"配置文件损坏: {config_file}")

        # 检查Python导入依赖
        self.check_python_imports(integrity_report)

        # 检查跨引用
        self.check_cross_references(integrity_report)

        return integrity_report

    def check_path_references(self, config: Dict[str, Any], config_file: str, integrity_report: Dict[str, Any]):
        """检查路径引用"""
        def check_paths(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    if isinstance(value, (str, Path)) and str(value).startswith("/"):
                        full_path = self.project_root / str(value).lstrip("/")
                        if not full_path.exists():
                            integrity_report["path_references"][f"{config_file}:{current_path}"] = "broken"
                        else:
                            integrity_report["path_references"][f"{config_file}:{current_path}"] = "valid"
                    else:
                        check_paths(value, current_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_paths(item, f"{path}[{i}]")

        check_paths(config)

    def check_python_imports(self, integrity_report: Dict[str, Any]):
        """检查Python导入依赖"""
        python_files = list(self.project_root.rglob("*.py"))

        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 查找导入语句
                import_lines = []
                for line in content.split('\n'):
                    line = line.strip()
                    if line.startswith(('import ', 'from ')):
                        import_lines.append(line)

                # 分析导入依赖
                for import_line in import_lines:
                    if 'from src.' in import_line or 'from scripts.' in import_line:
                        # 检查相对导入
                        module_path = import_line.split('from ')[1].split(' import')[0]
                        if not self.check_module_exists(module_path):
                            integrity_report["import_dependencies"][str(py_file)] = f"missing: {module_path}"

            except Exception as e:
                self.logger.warning(f"检查导入失败: {py_file}")

    def check_module_exists(self, module_path: str) -> bool:
        """检查模块是否存在"""
        try:
            parts = module_path.split('.')
            current_path = self.project_root

            for part in parts:
                current_path = current_path / part
                if not current_path.exists():
                    return False

                # 检查是否有__init__.py
                if current_path.is_dir() and not (current_path / "__init__.py").exists():
                    return False

            return True
        except:
            return False

    def check_cross_references(self, integrity_report: Dict[str, Any]):
        """检查跨引用"""
        # 检查文档引用
        docs_path = self.project_root / "docs"
        if docs_path.exists():
            for md_file in docs_path.rglob("*.md"):
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 查找文件引用
                    import re
                    refs = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
                    for text, link in refs:
                        if link.startswith(('../', './', '/')):
                            # 相对路径引用
                            full_path = (md_file.parent / link).resolve()
                            if not full_path.exists():
                                integrity_report["cross_references"][str(md_file)] = f"broken_link: {link}"

                except Exception as e:
                    self.logger.warning(f"检查文档引用失败: {md_file}")

    def generate_integrity_report(self) -> Dict[str, Any]:
        """生成完整性报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "structure_scan": self.scan_project_structure(),
            "context_integrity": self.check_global_context_integrity(),
            "summary": {}
        }

        # 生成摘要
        structure = report["structure_scan"]
        integrity = report["context_integrity"]

        report["summary"] = {
            "total_files": structure["total_files"],
            "total_dirs": structure["total_dirs"],
            "missing_paths": len([p for p in structure["path_status"].values() if p == "missing"]),
            "orphaned_files": len(structure["orphaned_files"]),
            "missing_associations": len(structure["missing_associations"]),
            "broken_references": len(integrity.get("path_references", {})),
            "import_issues": len(integrity.get("import_dependencies", {})),
            "cross_ref_issues": len(integrity.get("cross_references", {})),
            "overall_health": "good"
        }

        # 计算整体健康度
        issues_count = (
            report["summary"]["missing_paths"] +
            report["summary"]["orphaned_files"] +
            report["summary"]["missing_associations"] +
            report["summary"]["broken_references"] +
            report["summary"]["import_issues"] +
            report["summary"]["cross_ref_issues"]
        )

        if issues_count > 10:
            report["summary"]["overall_health"] = "critical"
        elif issues_count > 5:
            report["summary"]["overall_health"] = "warning"
        else:
            report["summary"]["overall_health"] = "good"

        return report

    def run(self):
        """运行全局上下文监控器"""
        self.logger.info("全局上下文监控器启动")

        print("=" * 60)
        print("🔍 AI弹窗项目全局上下文监控器")
        print("=" * 60)

        # 生成完整性报告
        report = self.generate_integrity_report()

        print(f"扫描时间: {report['timestamp']}")
        print(f"项目健康度: {report['summary']['overall_health'].upper()}")

        print("\n📊 结构统计:")
        print(f"- 总文件数: {report['summary']['total_files']}")
        print(f"- 总目录数: {report['summary']['total_dirs']}")
        print(f"- 缺失路径: {report['summary']['missing_paths']}")
        print(f"- 孤立文件: {report['summary']['orphaned_files']}")
        print(f"- 缺失关联: {report['summary']['missing_associations']}")

        print("\n🔗 引用检查:")
        print(f"- 断开引用: {report['summary']['broken_references']}")
        print(f"- 导入问题: {report['summary']['import_issues']}")
        print(f"- 跨引用问题: {report['summary']['cross_ref_issues']}")

        # 显示问题详情
        issues = []
        issues.extend(report["structure_scan"].get("integrity_issues", []))
        issues.extend(report["context_integrity"].get("issues", []))

        if issues:
            print("\n⚠️ 发现问题:")
            for issue in issues[:10]:  # 只显示前10个问题
                print(f"- {issue}")
            if len(issues) > 10:
                print(f"- ... 还有 {len(issues) - 10} 个问题")

        # 保存报告
        report_path = self.project_root / "logs" / f"context_integrity_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        write_json(report_path, report)

        print(f"\n✅ 完整性报告已保存: {report_path}")

        self.logger.info("全局上下文监控器运行完成")

if __name__ == "__main__":
    monitor = GlobalContextMonitor()
    monitor.run()
