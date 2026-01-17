#!/usr/bin/env python3
"""
菜单互动性监控器脚本
监控主菜单和子菜单的分离互动性，确保菜单层级和事件处理的正确性
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.utils.logging_utils import get_script_logger
from scripts.utils.file_utils import read_json, write_json

class MenuInteractivityMonitor:
    """菜单互动性监控器"""

    def __init__(self):
        self.logger = get_script_logger("menu_interactivity_monitor")
        self.project_root = project_root
        self.menu_config_path = self.project_root / "scripts" / "health" / "menu_interactivity_config.json"

        # 定义需要检查的文件类型
        self.checkable_files = {
            "html": [".html"],
            "javascript": [".js"],
            "python": [".py"],
            "css": [".css"]
        }

    def load_menu_config(self) -> Dict[str, Any]:
        """加载菜单配置"""
        try:
            if self.menu_config_path.exists():
                return read_json(self.menu_config_path)
            else:
                default_config = {
                    "version": "1.0.0",
                    "menu_structure": {
                        "main_menu_selectors": [".main-menu", "#main-nav", ".navbar"],
                        "submenu_selectors": [".submenu", ".dropdown-menu", ".sub-nav"],
                        "menu_item_selectors": [".menu-item", ".nav-item", "li"],
                        "active_selectors": [".active", ".current", ".selected"]
                    },
                    "interactivity_patterns": {
                        "event_prevention": ["preventDefault", "stopPropagation", "stopImmediatePropagation"],
                        "menu_toggle": ["toggle", "show", "hide", "slideToggle", "fadeToggle"],
                        "state_management": ["addClass", "removeClass", "toggleClass", "attr", "data"]
                    },
                    "nesting_rules": {
                        "max_depth": 3,
                        "event_bubbling_check": True,
                        "z_index_management": True
                    }
                }
                write_json(self.menu_config_path, default_config)
                return default_config
        except Exception as e:
            self.logger.error(f"加载菜单配置失败: {e}")
            return {}

    def analyze_menu_structure(self) -> Dict[str, Any]:
        """分析菜单结构"""
        structure_report = {
            "html_files": [],
            "menu_elements": {},
            "submenu_elements": {},
            "interactivity_issues": [],
            "structure_violations": []
        }

        # 查找HTML文件
        web_templates = self.project_root / "web" / "templates"
        if web_templates.exists():
            html_files = list(web_templates.rglob("*.html"))
            structure_report["html_files"] = [str(f) for f in html_files]

            for html_file in html_files:
                self.analyze_html_menu_structure(html_file, structure_report)

        return structure_report

    def analyze_html_menu_structure(self, html_file: Path, report: Dict[str, Any]):
        """分析HTML菜单结构"""
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查菜单元素
            menu_selectors = ["nav", "menu", ".menu", ".navbar", "#nav", "#menu"]
            for selector in menu_selectors:
                if selector in content:
                    if selector not in report["menu_elements"]:
                        report["menu_elements"][selector] = []
                    report["menu_elements"][selector].append(str(html_file))

            # 检查子菜单元素
            submenu_patterns = [
                r'class="[^"]*submenu[^"]*"',
                r'class="[^"]*dropdown[^"]*"',
                r'class="[^"]*sub-menu[^"]*"',
                r'<ul[^>]*class="[^"]*sub[^"]*">'
            ]

            for pattern in submenu_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    if str(html_file) not in report["submenu_elements"]:
                        report["submenu_elements"][str(html_file)] = []
                    report["submenu_elements"][str(html_file)].extend(matches)

            # 检查结构违规
            self.check_menu_structure_violations(content, html_file, report)

        except Exception as e:
            self.logger.warning(f"分析HTML文件失败: {html_file}")

    def check_menu_structure_violations(self, content: str, html_file: Path, report: Dict[str, Any]):
        """检查菜单结构违规"""
        # 检查嵌套深度
        nested_ul_pattern = r'<ul[^>]*>.*?<ul[^>]*>.*?</ul>.*?</ul>'
        if re.search(nested_ul_pattern, content, re.DOTALL):
            report["structure_violations"].append({
                "file": str(html_file),
                "type": "deep_nesting",
                "description": "检测到过深的菜单嵌套"
            })

        # 检查缺少关闭标签
        open_ul = content.count('<ul')
        close_ul = content.count('</ul>')
        if open_ul != close_ul:
            report["structure_violations"].append({
                "file": str(html_file),
                "type": "unclosed_tags",
                "description": f"UL标签不匹配: {open_ul} 个打开, {close_ul} 个关闭"
            })

    def analyze_javascript_interactivity(self) -> Dict[str, Any]:
        """分析JavaScript互动性"""
        js_report = {
            "js_files": [],
            "event_handlers": {},
            "menu_functions": {},
            "interactivity_patterns": {},
            "issues": []
        }

        # 查找JavaScript文件
        js_paths = [
            self.project_root / "web" / "static" / "js",
            self.project_root / "src" / "frontend"
        ]

        for js_path in js_paths:
            if js_path.exists():
                js_files = list(js_path.rglob("*.js"))
                js_report["js_files"].extend([str(f) for f in js_files])

                for js_file in js_files:
                    self.analyze_js_file(js_file, js_report)

        return js_report

    def analyze_js_file(self, js_file: Path, report: Dict[str, Any]):
        """分析JavaScript文件"""
        try:
            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查事件处理器
            event_patterns = [
                r'\.on\(',
                r'\.click\(',
                r'\.hover\(',
                r'\.mouseenter\(',
                r'\.mouseleave\(',
                r'addEventListener\('
            ]

            for pattern in event_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    event_type = pattern.replace('\\', '').replace('(', '')
                    if event_type not in report["event_handlers"]:
                        report["event_handlers"][event_type] = []
                    report["event_handlers"][event_type].append(str(js_file))

            # 检查菜单相关函数
            menu_functions = [
                "toggleMenu",
                "showMenu",
                "hideMenu",
                "openSubmenu",
                "closeSubmenu"
            ]

            for func in menu_functions:
                if func in content:
                    if func not in report["menu_functions"]:
                        report["menu_functions"][func] = []
                    report["menu_functions"][func].append(str(js_file))

            # 检查互动性模式
            interactivity_patterns = [
                "preventDefault",
                "stopPropagation",
                "stopImmediatePropagation",
                "toggleClass",
                "addClass",
                "removeClass"
            ]

            for pattern in interactivity_patterns:
                if pattern in content:
                    if pattern not in report["interactivity_patterns"]:
                        report["interactivity_patterns"][pattern] = []
                    report["interactivity_patterns"][pattern].append(str(js_file))

            # 检查问题
            self.check_js_interactivity_issues(content, js_file, report)

        except Exception as e:
            self.logger.warning(f"分析JS文件失败: {js_file}")

    def check_js_interactivity_issues(self, content: str, js_file: Path, report: Dict[str, Any]):
        """检查JavaScript互动性问题"""
        # 检查事件冒泡问题
        if ".on(" in content and "stopPropagation" not in content:
            report["issues"].append({
                "file": str(js_file),
                "type": "missing_stopPropagation",
                "description": "事件处理器可能缺少stopPropagation调用"
            })

        # 检查嵌套菜单事件冲突
        nested_menu_pattern = r'\.menu.*\.on\(.*\..*\.on\('
        if re.search(nested_menu_pattern, content, re.DOTALL):
            report["issues"].append({
                "file": str(js_file),
                "type": "nested_event_conflict",
                "description": "检测到嵌套菜单事件可能冲突"
            })

    def analyze_css_styling(self) -> Dict[str, Any]:
        """分析CSS样式"""
        css_report = {
            "css_files": [],
            "menu_styles": {},
            "submenu_styles": {},
            "responsive_rules": {},
            "z_index_issues": []
        }

        # 查找CSS文件
        css_paths = [
            self.project_root / "web" / "static" / "css",
            self.project_root / "src" / "frontend" / "styles"
        ]

        for css_path in css_paths:
            if css_path.exists():
                css_files = list(css_path.rglob("*.css"))
                css_report["css_files"].extend([str(f) for f in css_files])

                for css_file in css_files:
                    self.analyze_css_file(css_file, css_report)

        return css_report

    def analyze_css_file(self, css_file: Path, report: Dict[str, Any]):
        """分析CSS文件"""
        try:
            with open(css_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查菜单样式
            menu_selectors = [
                ".menu", ".navbar", ".nav", ".main-menu",
                ".submenu", ".dropdown-menu", ".sub-menu"
            ]

            for selector in menu_selectors:
                if selector in content:
                    if selector not in report["menu_styles"]:
                        report["menu_styles"][selector] = []
                    report["menu_styles"][selector].append(str(css_file))

            # 检查响应式规则
            media_queries = re.findall(r'@media[^{]*\{[^}]*\}', content, re.DOTALL)
            if media_queries:
                report["responsive_rules"][str(css_file)] = len(media_queries)

            # 检查z-index问题
            z_index_pattern = r'z-index:\s*(\d+)'
            z_indices = re.findall(z_index_pattern, content)
            high_z_indices = [int(z) for z in z_indices if int(z) > 1000]
            if high_z_indices:
                report["z_index_issues"].append({
                    "file": str(css_file),
                    "high_z_indices": high_z_indices
                })

        except Exception as e:
            self.logger.warning(f"分析CSS文件失败: {css_file}")

    def check_menu_separation(self) -> Dict[str, Any]:
        """检查菜单分离"""
        separation_report = {
            "main_sub_separation": True,
            "event_isolation": True,
            "css_isolation": True,
            "js_isolation": True,
            "issues": []
        }

        # 检查HTML分离
        structure = self.analyze_menu_structure()
        main_menus = len(structure.get("menu_elements", {}))
        sub_menus = sum(len(items) for items in structure.get("submenu_elements", {}).values())

        if main_menus == 0:
            separation_report["main_sub_separation"] = False
            separation_report["issues"].append("未检测到主菜单元素")

        if sub_menus == 0:
            separation_report["main_sub_separation"] = False
            separation_report["issues"].append("未检测到子菜单元素")

        # 检查JavaScript事件隔离
        js_analysis = self.analyze_javascript_interactivity()
        event_handlers = js_analysis.get("event_handlers", {})
        menu_functions = js_analysis.get("menu_functions", {})

        if not event_handlers and not menu_functions:
            separation_report["js_isolation"] = False
            separation_report["issues"].append("未检测到菜单相关的事件处理或函数")

        # 检查CSS样式隔离
        css_analysis = self.analyze_css_styling()
        menu_styles = css_analysis.get("menu_styles", {})

        if not menu_styles:
            separation_report["css_isolation"] = False
            separation_report["issues"].append("未检测到菜单相关的CSS样式")

        return separation_report

    def generate_interactivity_report(self) -> Dict[str, Any]:
        """生成互动性报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "menu_structure": self.analyze_menu_structure(),
            "javascript_interactivity": self.analyze_javascript_interactivity(),
            "css_styling": self.analyze_css_styling(),
            "menu_separation": self.check_menu_separation(),
            "summary": {}
        }

        # 生成摘要
        structure = report["menu_structure"]
        js_analysis = report["javascript_interactivity"]
        css_analysis = report["css_styling"]
        separation = report["menu_separation"]

        report["summary"] = {
            "html_files_checked": len(structure["html_files"]),
            "js_files_checked": len(js_analysis["js_files"]),
            "css_files_checked": len(css_analysis["css_files"]),
            "menu_elements_found": len(structure.get("menu_elements", {})),
            "submenu_elements_found": len(structure.get("submenu_elements", {})),
            "event_handlers_found": len(js_analysis.get("event_handlers", {})),
            "menu_functions_found": len(js_analysis.get("menu_functions", {})),
            "interactivity_patterns": len(js_analysis.get("interactivity_patterns", {})),
            "css_menu_styles": len(css_analysis.get("menu_styles", {})),
            "responsive_rules": sum(css_analysis.get("responsive_rules", {}).values()),
            "structure_violations": len(structure.get("structure_violations", [])),
            "js_issues": len(js_analysis.get("issues", [])),
            "z_index_issues": len(css_analysis.get("z_index_issues", [])),
            "separation_issues": len(separation.get("issues", [])),
            "overall_interactivity": "good"
        }

        # 计算整体互动性
        issues_count = (
            report["summary"]["structure_violations"] +
            report["summary"]["js_issues"] +
            report["summary"]["z_index_issues"] +
            report["summary"]["separation_issues"]
        )

        if issues_count > 5:
            report["summary"]["overall_interactivity"] = "poor"
        elif issues_count > 2:
            report["summary"]["overall_interactivity"] = "fair"
        else:
            report["summary"]["overall_interactivity"] = "good"

        return report

    def run(self):
        """运行菜单互动性监控器"""
        self.logger.info("菜单互动性监控器启动")

        print("=" * 60)
        print("🎯 AI弹窗项目菜单互动性监控器")
        print("=" * 60)

        # 生成互动性报告
        report = self.generate_interactivity_report()

        print(f"检查时间: {report['timestamp']}")
        print(f"整体互动性: {report['summary']['overall_interactivity'].upper()}")

        print("\n📊 文件统计:")
        print(f"- HTML文件: {report['summary']['html_files_checked']}")
        print(f"- JS文件: {report['summary']['js_files_checked']}")
        print(f"- CSS文件: {report['summary']['css_files_checked']}")

        print("\n🎨 菜单元素:")
        print(f"- 主菜单元素: {report['summary']['menu_elements_found']}")
        print(f"- 子菜单元素: {report['summary']['submenu_elements_found']}")
        print(f"- 菜单样式: {report['summary']['css_menu_styles']}")

        print("\n⚡ 互动性:")
        print(f"- 事件处理器: {report['summary']['event_handlers_found']}")
        print(f"- 菜单函数: {report['summary']['menu_functions_found']}")
        print(f"- 互动模式: {report['summary']['interactivity_patterns']}")
        print(f"- 响应式规则: {report['summary']['responsive_rules']}")

        print("\n🔍 问题统计:")
        print(f"- 结构违规: {report['summary']['structure_violations']}")
        print(f"- JS问题: {report['summary']['js_issues']}")
        print(f"- Z-index问题: {report['summary']['z_index_issues']}")
        print(f"- 分离问题: {report['summary']['separation_issues']}")

        # 显示详细问题
        all_issues = []
        all_issues.extend(report["menu_structure"].get("structure_violations", []))
        all_issues.extend(report["javascript_interactivity"].get("issues", []))
        all_issues.extend(report["menu_separation"].get("issues", []))

        if all_issues:
            print("\n⚠️ 发现问题:")
            for issue in all_issues[:10]:  # 只显示前10个问题
                if isinstance(issue, dict):
                    print(f"- [{issue.get('type', 'unknown')}] {issue.get('description', 'no description')}")
                else:
                    print(f"- {issue}")
            if len(all_issues) > 10:
                print(f"- ... 还有 {len(all_issues) - 10} 个问题")

        # 保存报告
        report_path = self.project_root / "logs" / f"menu_interactivity_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        write_json(report_path, report)

        print(f"\n✅ 互动性报告已保存: {report_path}")

        self.logger.info("菜单互动性监控器运行完成")

if __name__ == "__main__":
    monitor = MenuInteractivityMonitor()
    monitor.run()
