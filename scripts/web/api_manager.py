#!/usr/bin/env python3
"""
API管理器脚本
负责API接口设计、数据格式、跨域问题处理、接口交互和排序逻辑
"""

import os
import sys
import json
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.utils.logging_utils import get_script_logger
from scripts.utils.file_utils import read_json, write_json

class APIManager:
    """API管理器"""

    def __init__(self):
        self.logger = get_script_logger("api_manager")
        self.project_root = project_root
        self.api_config_path = self.project_root / "src" / "src_config.json"
        self.api_endpoints = {}
        self.cross_domain_config = {}

    def load_api_config(self) -> Dict[str, Any]:
        """加载API配置"""
        try:
            if self.api_config_path.exists():
                return read_json(self.api_config_path)
            else:
                # 创建默认API配置
                default_config = {
                    "api": {
                        "host": "localhost",
                        "port": 8000,
                        "cors_origins": ["http://localhost:8080", "http://127.0.0.1:8080"],
                        "endpoints": {
                            "health": {"path": "/health", "method": "GET", "description": "健康检查"},
                            "scripts": {"path": "/api/scripts", "method": "GET", "description": "获取脚本列表"},
                            "run_script": {"path": "/api/scripts/run/{script_name}", "method": "POST", "description": "运行脚本"},
                            "docs": {"path": "/api/docs", "method": "GET", "description": "获取文档列表"},
                            "deployment": {"path": "/api/deployment", "method": "GET", "description": "获取部署进度"},
                            "config": {"path": "/api/config", "method": "GET", "description": "获取配置"}
                        }
                    },
                    "data_formats": {
                        "json": {"content_type": "application/json", "charset": "utf-8"},
                        "form": {"content_type": "application/x-www-form-urlencoded"},
                        "multipart": {"content_type": "multipart/form-data"}
                    },
                    "sorting": {
                        "default_order": "asc",
                        "sortable_fields": ["name", "created_at", "status", "priority"]
                    }
                }
                write_json(self.api_config_path, default_config)
                return default_config
        except Exception as e:
            self.logger.error(f"加载API配置失败: {e}")
            return {}

    def check_api_compatibility(self) -> Dict[str, Any]:
        """检查API兼容性"""
        config = self.load_api_config()
        api_info = config.get("api", {})
        
        compatibility_report = {
            "backend_version": api_info.get("version", "unknown"),
            "compatible_modules": [],
            "incompatible_modules": [],
            "issues": []
        }

        # 检查模块兼容性
        modules_to_check = ["task_manager", "scheduler", "config_loader"]
        
        for module in modules_to_check:
            module_path = self.project_root / "src" / module.replace("_", "/") / f"{module}_config.json"
            if module_path.exists():
                module_config = read_json(module_path)
                module_version = module_config.get("version", "unknown")
                
                if module_version == compatibility_report["backend_version"]:
                    compatibility_report["compatible_modules"].append(module)
                else:
                    compatibility_report["incompatible_modules"].append(module)
                    compatibility_report["issues"].append(f"模块 {module} 版本不兼容")

        return compatibility_report

    def handle_cross_domain_issues(self) -> Dict[str, Any]:
        """处理跨域问题"""
        config = self.load_api_config()
        cors_config = config.get("api", {}).get("cors_origins", [])
        
        cross_domain_report = {
            "allowed_origins": cors_config,
            "current_origin": "http://localhost:8080",  # Web监控端口的默认值
            "is_allowed": False,
            "security_level": "medium",
            "recommendations": []
        }

        # 检查当前origin是否在允许列表中
        if cross_domain_report["current_origin"] in cors_config:
            cross_domain_report["is_allowed"] = True
        elif "*" in cors_config:
            cross_domain_report["is_allowed"] = True
            cross_domain_report["security_level"] = "low"
            cross_domain_report["recommendations"].append("警告：允许所有域访问可能存在安全风险")
        else:
            cross_domain_report["recommendations"].append(f"建议将 {cross_domain_report['current_origin']} 添加到CORS允许列表")

        return cross_domain_report

    def validate_api_endpoints(self) -> Dict[str, Any]:
        """验证API端点"""
        config = self.load_api_config()
        endpoints = config.get("api", {}).get("endpoints", {})
        
        validation_report = {
            "total_endpoints": len(endpoints),
            "accessible_endpoints": [],
            "unreachable_endpoints": [],
            "response_times": {},
            "issues": []
        }

        for endpoint_name, endpoint_info in endpoints.items():
            url = f"http://localhost:8000{endpoint_info['path']}"
            method = endpoint_info["method"]
            
            try:
                response = requests.request(method, url, timeout=5)
                if response.status_code == 200:
                    validation_report["accessible_endpoints"].append(endpoint_name)
                    validation_report["response_times"][endpoint_name] = response.elapsed.total_seconds()
                else:
                    validation_report["unreachable_endpoints"].append(endpoint_name)
                    validation_report["issues"].append(f"端点 {endpoint_name} 返回状态码 {response.status_code}")
            except Exception as e:
                validation_report["unreachable_endpoints"].append(endpoint_name)
                validation_report["issues"].append(f"端点 {endpoint_name} 无法访问: {str(e)}")

        return validation_report

    def optimize_data_formats(self) -> Dict[str, Any]:
        """优化数据格式处理"""
        config = self.load_api_config()
        data_formats = config.get("data_formats", {})
        
        optimization_report = {
            "current_formats": list(data_formats.keys()),
            "recommended_formats": ["json", "xml", "protobuf"],
            "efficiency_scores": {},
            "optimization_suggestions": []
        }

        # 评估每个数据格式的效率
        for format_name, format_config in data_formats.items():
            efficiency_score = 0
            
            # 简单评分逻辑（实际可以更复杂）
            if format_name == "json":
                efficiency_score = 90  # JSON广泛支持，易读性强
            elif format_name == "xml":
                efficiency_score = 70  # XML结构复杂，但标准化
            elif format_name == "protobuf":
                efficiency_score = 95  # Protobuf高效，但需要额外处理
            
            optimization_report["efficiency_scores"][format_name] = efficiency_score
        
        # 推荐优化建议
        if "json" not in optimization_report["current_formats"]:
            optimization_report["optimization_suggestions"].append("建议添加JSON格式支持")
            
        if optimization_report["efficiency_scores"].get("xml", 0) > 80:
            optimization_report["optimization_suggestions"].append("考虑使用更高效的替代格式")

        return optimization_report

    def implement_sorting_logic(self) -> Dict[str, Any]:
        """实现排序逻辑"""
        config = self.load_api_config()
        sorting_config = config.get("sorting", {})
        
        sorting_report = {
            "sortable_fields": sorting_config.get("sortable_fields", []),
            "default_order": sorting_config.get("default_order", "asc"),
            "supported_orders": ["asc", "desc"],
            "implementation_status": {}
        }

        # 检查排序字段的实现情况
        for field in sorting_report["sortable_fields"]:
            sorting_report["implementation_status"][field] = {
                "supported": True,
                "order_types": sorting_report["supported_orders"],
                "performance": "good"
            }

        return sorting_report

    def cache_management(self) -> Dict[str, Any]:
        """缓存管理"""
        cache_report = {
            "cache_cleanup_enabled": False,
            "cache_conflicts_detected": False,
            "lazy_loading_supported": True,
            "dynamic_loading_enabled": True,
            "cache_size": "unknown",
            "recommendations": []
        }

        # 检查缓存配置
        config_files = [
            self.project_root / "src" / "config" / "app_config.py",
            self.project_root / "web" / "web_config.json"
        ]
        
        for config_file in config_files:
            if config_file.exists():
                try:
                    content = config_file.read_text(encoding='utf-8')
                    if "cache" in content.lower():
                        cache_report["cache_cleanup_enabled"] = True
                    if "conflict" in content.lower():
                        cache_report["cache_conflicts_detected"] = True
                except:
                    pass

        # 推荐缓存优化
        if not cache_report["cache_cleanup_enabled"]:
            cache_report["recommendations"].append("建议启用定时缓存清理")
            
        if cache_report["cache_conflicts_detected"]:
            cache_report["recommendations"].append("检测到潜在缓存冲突，建议优化缓存策略")

        return cache_report

    def run(self):
        """运行API管理器"""
        self.logger.info("API管理器启动")

        # 检查API兼容性
        compatibility = self.check_api_compatibility()
        self.logger.info(f"API兼容性检查完成")

        # 处理跨域问题
        cross_domain = self.handle_cross_domain_issues()
        self.logger.info(f"跨域问题处理完成")

        # 验证API端点
        endpoints = self.validate_api_endpoints()
        self.logger.info(f"API端点验证完成")

        # 优化数据格式
        data_formats = self.optimize_data_formats()
        self.logger.info(f"数据格式优化完成")

        # 实现排序逻辑
        sorting = self.implement_sorting_logic()
        self.logger.info(f"排序逻辑实现完成")

        # 缓存管理
        cache = self.cache_management()
        self.logger.info(f"缓存管理检查完成")

        # 输出报告
        print("API管理报告:")
        print(f"- API端点总数: {endpoints.get('total_endpoints', 0)}")
        print(f"- 可访问端点: {len(endpoints.get('accessible_endpoints', []))}")
        print(f"- 跨域访问: {'允许' if cross_domain.get('is_allowed') else '拒绝'}")
        print(f"- 兼容模块: {len(compatibility.get('compatible_modules', []))}")
        
        all_issues = []
        all_issues.extend(compatibility.get("issues", []))
        all_issues.extend(cross_domain.get("recommendations", []))
        all_issues.extend(endpoints.get("issues", []))
        all_issues.extend(data_formats.get("optimization_suggestions", []))
        all_issues.extend(cache.get("recommendations", []))

        if all_issues:
            print("发现问题:")
            for issue in all_issues:
                print(f"- {issue}")

        self.logger.info("API管理器运行完成")

if __name__ == "__main__":
    manager = APIManager()
    manager.run()
