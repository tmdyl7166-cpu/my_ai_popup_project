#!/usr/bin/env python3
"""
安全验证器脚本
负责数据安全、表单验证、安全漏洞检测和安全防护措施
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.utils.logging_utils import get_script_logger
from scripts.utils.file_utils import read_json, write_json

class SecurityValidator:
    """安全验证器"""

    def __init__(self):
        self.logger = get_script_logger("security_validator")
        self.project_root = project_root
        self.security_config_path = self.project_root / "project_config.json"

    def data_security_validation(self) -> Dict[str, Any]:
        """数据安全验证"""
        security_report = {
            "input_validation_enabled": False,
            "sql_injection_prevention": False,
            "xss_prevention": False,
            "csrf_protection": False,
            "data_encryption_enabled": False,
            "authentication_mechanism": "none",
            "authorization_levels": [],
            "vulnerabilities": [],
            "recommendations": []
        }

        # 检查配置文件中的安全设置
        config_files = [
            self.project_root / "src" / "config" / "app_config.py",
            self.project_root / "src" / "backend" / "middleware" / "logging_middleware.py",
            self.project_root / "web" / "web_config.json"
        ]

        for config_file in config_files:
            if config_file.exists():
                try:
                    content = config_file.read_text(encoding='utf-8')
                    
                    # 检查输入验证
                    if any(keyword in content.lower() for keyword in ["validate", "sanitize", "clean"]):
                        security_report["input_validation_enabled"] = True
                    
                    # 检查SQL注入防护
                    if any(keyword in content for keyword in ["parameter", "prepared", "escape"]):
                        security_report["sql_injection_prevention"] = True
                    
                    # 检查XSS防护
                    if "xss" in content.lower() or "escape" in content.lower():
                        security_report["xss_prevention"] = True
                    
                    # 检查CSRF保护
                    if "csrf" in content.lower() or "token" in content.lower():
                        security_report["csrf_protection"] = True
                    
                    # 检查数据加密
                    if "encrypt" in content.lower() or "hash" in content.lower():
                        security_report["data_encryption_enabled"] = True
                    
                    # 检查身份验证机制
                    if "auth" in content.lower() or "login" in content.lower():
                        security_report["authentication_mechanism"] = "basic"
                    
                except Exception as e:
                    self.logger.warning(f"检查安全配置失败: {e}")

        # 推荐安全改进
        if not security_report["input_validation_enabled"]:
            security_report["recommendations"].append("建议启用输入验证机制")
            
        if not security_report["sql_injection_prevention"]:
            security_report["recommendations"].append("建议实现SQL注入防护")
            
        if not security_report["xss_prevention"]:
            security_report["recommendations"].append("建议添加XSS攻击防护")

        return security_report

    def form_validation_compliance(self) -> Dict[str, Any]:
        """表单验证合规性检查"""
        form_report = {
            "required_fields_validation": False,
            "input_format_validation": False,
            "length_restrictions": False,
            "data_type_validation": False,
            "real_time_validation": False,
            "client_side_validation": False,
            "server_side_validation": False,
            "violations": [],
            "suggestions": []
        }

        # 检查前端表单验证
        js_files_path = self.project_root / "web" / "static" / "js" / "modules"
        if js_files_path.exists():
            try:
                for js_file in js_files_path.glob("*.js"):
                    content = js_file.read_text(encoding='utf-8')
                    
                    # 检查客户端验证
                    if any(keyword in content for keyword in ["required", "validation", "validate"]):
                        form_report["client_side_validation"] = True
                        
                    # 检查实时验证
                    if "input" in content and "event" in content:
                        form_report["real_time_validation"] = True
                        
            except Exception as e:
                self.logger.warning(f"检查JS验证文件失败: {e}")

        # 检查后端API验证
        api_files = [
            self.project_root / "src" / "main.py",
            self.project_root / "src" / "backend"
        ]

        for api_path in api_files:
            if api_path.exists():
                try:
                    if api_path.is_file():
                        content = api_path.read_text(encoding='utf-8')
                    else:
                        # 如果是目录，检查其中的Python文件
                        content = ""
                        for py_file in api_path.glob("*.py"):
                            content += py_file.read_text(encoding='utf-8')
                    
                    # 检查服务器端验证
                    if any(keyword in content for keyword in ["validation", "validate", "check"]):
                        form_report["server_side_validation"] = True
                        
                    # 检查必填字段验证
                    if "required" in content.lower():
                        form_report["required_fields_validation"] = True
                        
                    # 检查输入格式验证
                    if any(keyword in content for keyword in ["format", "pattern", "regex"]):
                        form_report["input_format_validation"] = True
                        
                    # 检查长度限制
                    if any(keyword in content for keyword in ["length", "max", "min"]):
                        form_report["length_restrictions"] = True
                        
                except Exception as e:
                    self.logger.warning(f"检查API验证失败: {e}")

        # 建议改进
        if not form_report["client_side_validation"]:
            form_report["suggestions"].append("建议添加客户端表单验证")
            
        if not form_report["server_side_validation"]:
            form_report["suggestions"].append("建议加强服务器端验证")

        return form_report

    def global_functional_linkage_check(self) -> Dict[str, Any]:
        """全局功能联动性检查"""
        linkage_report = {
            "module_interconnections": {},
            "api_interactions": {},
            "data_flow_analysis": {},
            "dependency_mapping": {},
            "circular_dependencies": [],
            "integration_issues": [],
            "optimization_suggestions": []
        }

        # 分析src目录下的模块结构
        src_path = self.project_root / "src"
        if src_path.exists():
            modules = ["ai", "backend", "config", "frontend", "integrations", "processing", "utils"]
            
            for module in modules:
                module_path = src_path / module
                if module_path.exists():
                    linkage_report["module_interconnections"][module] = {
                        "dependencies": [],
                        "dependents": [],
                        "isolation_level": "high"
                    }
                    
                    # 检查模块间的导入关系
                    try:
                        # 检查模块的依赖关系（简化版）
                        init_file = module_path / "__init__.py"
                        if init_file.exists():
                            content = init_file.read_text(encoding='utf-8')
                            # 分析导入语句
                            imports = re.findall(r'from\s+([\w\.]+)\s+import|import\s+([\w\.]+)', content)
                            for match in imports:
                                dependency = match[0] if match[0] else match[1]
                                if dependency.startswith("src."):
                                    dep_module = dependency.split(".")[1]
                                    linkage_report["module_interconnections"][module]["dependencies"].append(dep_module)
                    except Exception as e:
                        self.logger.warning(f"检查模块依赖失败: {e}")

        # 检查API交互
        endpoints_config = self.project_root / "src" / "src_config.json"
        if endpoints_config.exists():
            try:
                config = read_json(endpoints_config)
                endpoints = config.get("api", {}).get("endpoints", {})
                for endpoint_name, endpoint_info in endpoints.items():
                    linkage_report["api_interactions"][endpoint_name] = {
                        "method": endpoint_info.get("method", "GET"),
                        "path": endpoint_info.get("path", ""),
                        "consumes": [],
                        "produces": []
                    }
            except Exception as e:
                self.logger.warning(f"检查API配置失败: {e}")

        # 检测循环依赖
        for module, info in linkage_report["module_interconnections"].items():
            dependencies = info["dependencies"]
            for dep in dependencies:
                if dep in linkage_report["module_interconnections"]:
                    if module in linkage_report["module_interconnections"][dep]["dependencies"]:
                        linkage_report["circular_dependencies"].append(f"{module} <-> {dep}")

        if linkage_report["circular_dependencies"]:
            linkage_report["optimization_suggestions"].append("检测到循环依赖，建议重构模块结构")

        return linkage_report

    def error_handling_and_recovery(self) -> Dict[str, Any]:
        """错误处理和恢复机制"""
        error_report = {
            "exception_handling": False,
            "graceful_degradation": False,
            "retry_mechanism": False,
            "fallback_strategies": [],
            "logging_levels": [],
            "error_recovery": False,
            "issues": [],
            "recommendations": []
        }

        # 检查异常处理机制
        python_files_paths = [
            self.project_root / "src",
            self.project_root / "scripts"
        ]

        for path in python_files_paths:
            if path.exists():
                try:
                    for py_file in path.rglob("*.py"):
                        content = py_file.read_text(encoding='utf-8')
                        
                        # 检查异常处理
                        if "try:" in content and "except:" in content:
                            error_report["exception_handling"] = True
                            
                        # 检查重试机制
                        if "retry" in content.lower():
                            error_report["retry_mechanism"] = True
                            
                        # 检查日志记录
                        if "log" in content.lower() or "logger" in content:
                            error_report["logging_levels"].append(str(py_file))
                            
                except Exception as e:
                    self.logger.warning(f"检查错误处理失败: {e}")

        # 检查Web端错误处理
        js_files_path = self.project_root / "web" / "static" / "js"
        if js_files_path.exists():
            try:
                for js_file in js_files_path.rglob("*.js"):
                    content = js_file.read_text(encoding='utf-8')
                    
                    # 检查JavaScript异常处理
                    if "try" in content and "catch" in content:
                        error_report["graceful_degradation"] = True
                        
            except Exception as e:
                self.logger.warning(f"检查JS错误处理失败: {e}")

        # 推荐改进
        if not error_report["exception_handling"]:
            error_report["recommendations"].append("建议添加完善的异常处理机制")
            
        if not error_report["graceful_degradation"]:
            error_report["recommendations"].append("建议实施优雅降级策略")

        return error_report

    def run(self):
        """运行安全验证器"""
        self.logger.info("安全验证器启动")

        # 数据安全验证
        security = self.data_security_validation()
        self.logger.info(f"数据安全验证完成: {len(security.get('recommendations', []))} 个建议")

        # 表单验证合规性
        form_validation = self.form_validation_compliance()
        self.logger.info(f"表单验证合规性检查完成: {len(form_validation.get('suggestions', []))} 个建议")

        # 全局功能联动性检查
        linkage = self.global_functional_linkage_check()
        self.logger.info(f"全局功能联动性检查完成: {len(linkage.get('circular_dependencies', []))} 个循环依赖")

        # 错误处理和恢复机制
        error_handling = self.error_handling_and_recovery()
        self.logger.info(f"错误处理检查完成: {len(error_handling.get('recommendations', []))} 个建议")

        # 输出报告
        print("安全验证报告:")
        print(f"- 输入验证: {'启用' if security.get('input_validation_enabled') else '未启用'}")
        print(f"- SQL注入防护: {'启用' if security.get('sql_injection_prevention') else '未启用'}")
        print(f"- XSS防护: {'启用' if security.get('xss_prevention') else '未启用'}")
        print(f"- 客户端验证: {'启用' if form_validation.get('client_side_validation') else '未启用'}")
        print(f"- 服务器端验证: {'启用' if form_validation.get('server_side_validation') else '未启用'}")
        print(f"- 模块数量: {len(linkage.get('module_interconnections', {}))}")
        print(f"- 循环依赖: {len(linkage.get('circular_dependencies', []))}")

        all_recommendations = []
        all_recommendations.extend(security.get("recommendations", []))
        all_recommendations.extend(form_validation.get("suggestions", []))
        all_recommendations.extend(linkage.get("optimization_suggestions", []))
        all_recommendations.extend(error_handling.get("recommendations", []))

        if all_recommendations:
            print("改进建议:")
            for rec in all_recommendations:
                print(f"- {rec}")

        self.logger.info("安全验证器运行完成")

if __name__ == "__main__":
    validator = SecurityValidator()
    validator.run()
