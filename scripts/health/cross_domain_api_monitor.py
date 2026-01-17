#!/usr/bin/env python3
"""
跨域和API监控器脚本
监控跨域问题、API设计、数据格式、模板引擎和动态渲染
"""

import os
import sys
import json
import requests
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from urllib.parse import urlparse

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.utils.logging_utils import get_script_logger
from scripts.utils.file_utils import read_json, write_json

class CrossDomainAPIMonitor:
    """跨域和API监控器"""

    def __init__(self):
        self.logger = get_script_logger("cross_domain_api_monitor")
        self.project_root = project_root
        self.api_config_path = self.project_root / "scripts" / "health" / "cross_domain_api_config.json"

        # 常见的跨域配置检查
        self.cors_headers = [
            'Access-Control-Allow-Origin',
            'Access-Control-Allow-Methods',
            'Access-Control-Allow-Headers',
            'Access-Control-Allow-Credentials',
            'Access-Control-Max-Age'
        ]

        # 支持的数据格式
        self.supported_formats = {
            'json': ['application/json', 'text/json'],
            'xml': ['application/xml', 'text/xml'],
            'form': ['application/x-www-form-urlencoded', 'multipart/form-data'],
            'text': ['text/plain', 'text/html']
        }

    def load_api_config(self) -> Dict[str, Any]:
        """加载API配置"""
        try:
            if self.api_config_path.exists():
                return read_json(self.api_config_path)
            else:
                default_config = {
                    "version": "1.0.0",
                    "api_endpoints": {
                        "base_url": "http://localhost:8000",
                        "endpoints": [
                            "/health",
                            "/api/scripts",
                            "/api/docs",
                            "/api/config"
                        ]
                    },
                    "cors_policy": {
                        "allowed_origins": ["http://localhost:8080", "http://127.0.0.1:8080"],
                        "allowed_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                        "allowed_headers": ["Content-Type", "Authorization", "X-Requested-With"],
                        "allow_credentials": True
                    },
                    "data_formats": {
                        "preferred": "json",
                        "fallback": "xml",
                        "compression": ["gzip", "deflate"]
                    },
                    "template_engines": {
                        "supported": ["jinja2", "django", "mustache"],
                        "default": "jinja2"
                    }
                }
                write_json(self.api_config_path, default_config)
                return default_config
        except Exception as e:
            self.logger.error(f"加载API配置失败: {e}")
            return {}

    def check_cors_configuration(self) -> Dict[str, Any]:
        """检查CORS配置"""
        cors_report = {
            "server_configured": False,
            "headers_present": {},
            "origins_allowed": [],
            "methods_allowed": [],
            "credentials_allowed": False,
            "preflight_support": False,
            "issues": []
        }

        # 检查后端CORS配置
        backend_files = [
            self.project_root / "src" / "main.py",
            self.project_root / "web" / "app.py"
        ]

        for backend_file in backend_files:
            if backend_file.exists():
                try:
                    with open(backend_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查CORS中间件
                    if 'CORSMiddleware' in content or 'cors' in content.lower():
                        cors_report["server_configured"] = True

                    # 检查允许的源
                    origin_matches = re.findall(r'allow_origins["\']?\s*:\s*\[([^\]]+)\]', content, re.IGNORECASE)
                    for match in origin_matches:
                        origins = [o.strip().strip('"\''') for o in match.split(',')]
                        cors_report["origins_allowed"].extend(origins)

                    # 检查允许的方法
                    method_matches = re.findall(r'allow_methods["\']?\s*:\s*\[([^\]]+)\]', content, re.IGNORECASE)
                    for match in method_matches:
                        methods = [m.strip().strip('"\''') for m in match.split(',')]
                        cors_report["methods_allowed"].extend(methods)

                    # 检查凭据
                    if 'allow_credentials' in content and 'True' in content:
                        cors_report["credentials_allowed"] = True

                except Exception as e:
                    self.logger.warning(f"检查后端CORS配置失败: {backend_file}")

        # 检查前端CORS处理
        frontend_files = [
            self.project_root / "web" / "static" / "js" / "modules" / "api.js"
        ]

        for frontend_file in frontend_files:
            if frontend_file.exists():
                try:
                    with open(frontend_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查预检请求处理
                    if 'OPTIONS' in content or 'preflight' in content.lower():
                        cors_report["preflight_support"] = True

                except Exception as e:
                    self.logger.warning(f"检查前端CORS配置失败: {frontend_file}")

        # 验证CORS配置
        if not cors_report["server_configured"]:
            cors_report["issues"].append("未检测到服务器端CORS配置")

        if not cors_report["origins_allowed"]:
            cors_report["issues"].append("未配置允许的源域名")

        if not cors_report["methods_allowed"]:
            cors_report["issues"].append("未配置允许的HTTP方法")

        return cors_report

    def test_api_endpoints(self) -> Dict[str, Any]:
        """测试API端点"""
        api_report = {
            "endpoints_tested": [],
            "successful_requests": [],
            "failed_requests": [],
            "response_times": {},
            "status_codes": {},
            "data_formats": {},
            "issues": []
        }

        config = self.load_api_config()
        base_url = config.get("api_endpoints", {}).get("base_url", "http://localhost:8000")
        endpoints = config.get("api_endpoints", {}).get("endpoints", [])

        for endpoint in endpoints:
            full_url = f"{base_url}{endpoint}"
            api_report["endpoints_tested"].append(full_url)

            try:
                start_time = datetime.now()
                response = requests.get(full_url, timeout=10)
                response_time = (datetime.now() - start_time).total_seconds()

                api_report["response_times"][full_url] = response_time
                api_report["status_codes"][full_url] = response.status_code

                # 检查响应格式
                content_type = response.headers.get('content-type', '').lower()
                api_report["data_formats"][full_url] = content_type

                if response.status_code == 200:
                    api_report["successful_requests"].append(full_url)

                    # 验证数据格式
                    if 'json' in content_type:
                        try:
                            response.json()
                        except:
                            api_report["issues"].append(f"{full_url}: 无效的JSON响应")
                    elif 'xml' in content_type:
                        if not response.text.strip().startswith('<'):
                            api_report["issues"].append(f"{full_url}: 无效的XML响应")
                else:
                    api_report["failed_requests"].append({
                        "url": full_url,
                        "status_code": response.status_code,
                        "error": response.text[:200]
                    })

            except requests.exceptions.RequestException as e:
                api_report["failed_requests"].append({
                    "url": full_url,
                    "error": str(e)
                })
                api_report["issues"].append(f"{full_url}: 请求失败 - {str(e)}")

        return api_report

    def analyze_data_formats(self) -> Dict[str, Any]:
        """分析数据格式"""
        format_report = {
            "formats_used": {},
            "format_consistency": {},
            "compression_support": {},
            "serialization_efficiency": {},
            "issues": []
        }

        # 检查配置文件中的数据格式定义
        config_files = [
            self.project_root / "src" / "src_config.json",
            self.project_root / "web" / "web_config.json"
        ]

        for config_file in config_files:
            if config_file.exists():
                try:
                    config = read_json(config_file)
                    self.analyze_config_data_formats(config, str(config_file), format_report)
                except Exception as e:
                    self.logger.warning(f"分析配置文件数据格式失败: {config_file}")

        # 检查代码中的数据格式使用
        code_files = [
            self.project_root / "src" / "main.py",
            self.project_root / "web" / "app.py"
        ]

        for code_file in code_files:
            if code_file.exists():
                try:
                    with open(code_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查JSON使用
                    if 'json.dumps' in content or 'json.loads' in content:
                        format_report["formats_used"]["json"] = format_report["formats_used"].get("json", 0) + 1

                    # 检查XML使用
                    if 'xml' in content.lower() or 'etree' in content:
                        format_report["formats_used"]["xml"] = format_report["formats_used"].get("xml", 0) + 1

                    # 检查压缩
                    if 'gzip' in content or 'compress' in content:
                        format_report["compression_support"]["gzip"] = True

                except Exception as e:
                    self.logger.warning(f"分析代码数据格式失败: {code_file}")

        # 验证格式一致性
        formats_used = list(format_report["formats_used"].keys())
        if len(formats_used) > 1:
            format_report["format_consistency"]["multiple_formats"] = True
            format_report["issues"].append("项目中使用了多种数据格式，建议统一")

        return format_report

    def analyze_config_data_formats(self, config: Dict[str, Any], config_file: str, report: Dict[str, Any]):
        """分析配置中的数据格式"""
        def check_formats(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    if isinstance(value, str):
                        for format_name, mime_types in self.supported_formats.items():
                            if any(mime in value.lower() for mime in mime_types):
                                report["formats_used"][format_name] = report["formats_used"].get(format_name, 0) + 1
                    check_formats(value, current_path)

        check_formats(config)

    def check_template_engines(self) -> Dict[str, Any]:
        """检查模板引擎"""
        template_report = {
            "engines_detected": {},
            "template_files": [],
            "dynamic_rendering": {},
            "caching_mechanisms": {},
            "issues": []
        }

        # 检查模板文件
        template_dirs = [
            self.project_root / "web" / "templates",
            self.project_root / "docs"
        ]

        for template_dir in template_dirs:
            if template_dir.exists():
                template_files = list(template_dir.rglob("*.html")) + list(template_dir.rglob("*.md"))
                template_report["template_files"].extend([str(f) for f in template_files])

                for template_file in template_files:
                    try:
                        with open(template_file, 'r', encoding='utf-8') as f:
                            content = f.read()

                        # 检查模板语法
                        if '{{' in content and '}}' in content:
                            template_report["engines_detected"]["jinja2"] = True

                        if '{%' in content and '%}' in content:
                            template_report["engines_detected"]["django"] = True

                        if '{{{' in content and '}}}' in content:
                            template_report["engines_detected"]["mustache"] = True

                        # 检查动态渲染
                        if 'render_template' in content or 'render' in content:
                            template_report["dynamic_rendering"][str(template_file)] = True

                    except Exception as e:
                        self.logger.warning(f"检查模板文件失败: {template_file}")

        # 检查模板引擎配置
        config_files = [
            self.project_root / "web" / "app.py",
            self.project_root / "src" / "main.py"
        ]

        for config_file in config_files:
            if config_file.exists():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查模板引擎导入
                    if 'jinja2' in content:
                        template_report["engines_detected"]["jinja2"] = True

                    if 'django' in content.lower():
                        template_report["engines_detected"]["django"] = True

                    # 检查缓存机制
                    if 'cache' in content.lower() or 'memoize' in content:
                        template_report["caching_mechanisms"]["template_cache"] = True

                except Exception as e:
                    self.logger.warning(f"检查模板引擎配置失败: {config_file}")

        # 验证模板引擎配置
        if not template_report["engines_detected"]:
            template_report["issues"].append("未检测到模板引擎配置")

        if len(template_report["engines_detected"]) > 1:
            template_report["issues"].append("检测到多个模板引擎，建议统一使用一个")

        return template_report

    def check_dynamic_rendering(self) -> Dict[str, Any]:
        """检查动态渲染"""
        rendering_report = {
            "server_side_rendering": False,
            "client_side_rendering": False,
            "hybrid_rendering": False,
            "rendering_performance": {},
            "lazy_loading": False,
            "issues": []
        }

        # 检查服务器端渲染
        backend_files = [
            self.project_root / "src" / "main.py",
            self.project_root / "web" / "app.py"
        ]

        for backend_file in backend_files:
            if backend_file.exists():
                try:
                    with open(backend_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    if 'render_template' in content or 'TemplateResponse' in content:
                        rendering_report["server_side_rendering"] = True

                    if 'jsonify' in content or 'JSONResponse' in content:
                        rendering_report["server_side_rendering"] = True

                except Exception as e:
                    self.logger.warning(f"检查服务器端渲染失败: {backend_file}")

        # 检查客户端渲染
        frontend_files = [
            self.project_root / "web" / "static" / "js" / "modules"
        ]

        for frontend_dir in frontend_files:
            if frontend_dir.exists():
                js_files = list(frontend_dir.rglob("*.js"))
                for js_file in js_files:
                    try:
                        with open(js_file, 'r', encoding='utf-8') as f:
                            content = f.read()

                        if 'render' in content or 'append' in content or 'html(' in content:
                            rendering_report["client_side_rendering"] = True

                        if 'lazy' in content.lower() or 'intersection' in content:
                            rendering_report["lazy_loading"] = True

                    except Exception as e:
                        self.logger.warning(f"检查客户端渲染失败: {js_file}")

        # 检查混合渲染
        if rendering_report["server_side_rendering"] and rendering_report["client_side_rendering"]:
            rendering_report["hybrid_rendering"] = True

        # 验证渲染配置
        if not rendering_report["server_side_rendering"] and not rendering_report["client_side_rendering"]:
            rendering_report["issues"].append("未检测到渲染机制")

        return rendering_report

    def generate_cross_domain_api_report(self) -> Dict[str, Any]:
        """生成跨域和API报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "cors_configuration": self.check_cors_configuration(),
            "api_endpoints": self.test_api_endpoints(),
            "data_formats": self.analyze_data_formats(),
            "template_engines": self.check_template_engines(),
            "dynamic_rendering": self.check_dynamic_rendering(),
            "summary": {}
        }

        # 生成摘要
        cors = report["cors_configuration"]
        api = report["api_endpoints"]
        formats = report["data_formats"]
        templates = report["template_engines"]
        rendering = report["dynamic_rendering"]

        report["summary"] = {
            "cors_configured": cors["server_configured"],
            "api_endpoints_tested": len(api["endpoints_tested"]),
            "api_endpoints_successful": len(api["successful_requests"]),
            "api_endpoints_failed": len(api["failed_requests"]),
            "data_formats_used": len(formats["formats_used"]),
            "template_engines_detected": len(templates["engines_detected"]),
            "server_side_rendering": rendering["server_side_rendering"],
            "client_side_rendering": rendering["client_side_rendering"],
            "lazy_loading_enabled": rendering["lazy_loading"],
            "total_issues": (
                len(cors.get("issues", [])) +
                len(api.get("issues", [])) +
                len(formats.get("issues", [])) +
                len(templates.get("issues", [])) +
                len(rendering.get("issues", []))
            ),
            "overall_api_health": "good"
        }

        # 计算整体API健康度
        issues_count = report["summary"]["total_issues"]
        failed_endpoints = report["summary"]["api_endpoints_failed"]

        if issues_count > 5 or failed_endpoints > 2:
            report["summary"]["overall_api_health"] = "critical"
        elif issues_count > 2 or failed_endpoints > 0:
            report["summary"]["overall_api_health"] = "warning"
        else:
            report["summary"]["overall_api_health"] = "good"

        return report

    def run(self):
        """运行跨域和API监控器"""
        self.logger.info("跨域和API监控器启动")

        print("=" * 60)
        print("🌐 AI弹窗项目跨域和API监控器")
        print("=" * 60)

        # 生成报告
        report = self.generate_cross_domain_api_report()

        print(f"检查时间: {report['timestamp']}")
        print(f"API整体健康度: {report['summary']['overall_api_health'].upper()}")

        print("\n🔒 CORS配置:")
        cors = report["cors_configuration"]
        print(f"- 服务器配置: {'✓' if cors['server_configured'] else '✗'}")
        print(f"- 允许源数量: {len(cors['origins_allowed'])}")
        print(f"- 允许方法数量: {len(cors['methods_allowed'])}")
        print(f"- 凭据支持: {'✓' if cors['credentials_allowed'] else '✗'}")
        print(f"- 预检支持: {'✓' if cors['preflight_support'] else '✗'}")

        print("\n🔗 API端点:")
        api = report["api_endpoints"]
        print(f"- 测试端点数: {len(api['endpoints_tested'])}")
        print(f"- 成功请求: {len(api['successful_requests'])}")
        print(f"- 失败请求: {len(api['failed_requests'])}")

        print("\n📄 数据格式:")
        formats = report["data_formats"]
        print(f"- 使用的格式: {', '.join(formats['formats_used'].keys()) or '无'}")
        print(f"- 格式一致性: {'✓' if len(formats['formats_used']) <= 1 else '✗'}")

        print("\n🎨 模板引擎:")
        templates = report["template_engines"]
        print(f"- 检测到的引擎: {', '.join(templates['engines_detected'].keys()) or '无'}")
        print(f"- 模板文件数: {len(templates['template_files'])}")

        print("\n⚡ 动态渲染:")
        rendering = report["dynamic_rendering"]
        print(f"- 服务器端渲染: {'✓' if rendering['server_side_rendering'] else '✗'}")
        print(f"- 客户端渲染: {'✓' if rendering['client_side_rendering'] else '✗'}")
        print(f"- 混合渲染: {'✓' if rendering['hybrid_rendering'] else '✗'}")
        print(f"- 懒加载: {'✓' if rendering['lazy_loading'] else '✗'}")

        # 显示问题
        all_issues = []
        all_issues.extend(cors.get("issues", []))
        all_issues.extend(api.get("issues", []))
        all_issues.extend(formats.get("issues", []))
        all_issues.extend(templates.get("issues", []))
        all_issues.extend(rendering.get("issues", []))

        if all_issues:
            print("\n⚠️ 发现问题:")
            for issue in all_issues[:10]:
                print(f"- {issue}")
            if len(all_issues) > 10:
                print(f"- ... 还有 {len(all_issues) - 10} 个问题")

        # 保存报告
        report_path = self.project_root / "logs" / f"cross_domain_api_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        write_json(report_path, report)

        print(f"\n✅ 监控报告已保存: {report_path}")

        self.logger.info("跨域和API监控器运行完成")

if __name__ == "__main__":
    monitor = CrossDomainAPIMonitor()
    monitor.run()
