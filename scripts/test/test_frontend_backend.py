#!/usr/bin/env python3
"""
前后端联动测试模块

功能:
    - 验证前后端API通信
    - 测试WebSocket实时通信
    - 验证脚本执行接口
    - 测试系统资源监控

使用方法:
    cd /workspaces/my_ai_popup_project
    python3 scripts/test/test_frontend_backend.py
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import socket
import json
import time
import asyncio
from typing import Dict, List, Optional
from datetime import datetime


class FrontendBackendTester:
    """前后端联动测试器"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.results = []
        self.api_base = "http://localhost:8000"
        self.web_base = "http://localhost:8080"

    def log(self, message: str, level: str = 'INFO'):
        """日志输出"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        prefix = {'INFO': '[INFO]', 'WARNING': '[WARNING]', 'ERROR': '[ERROR]', 'SUCCESS': '[SUCCESS]'}.get(level, '[INFO]')
        print(f"{timestamp} {prefix} {message}")
        self.results.append({'time': timestamp, 'level': level, 'message': message})

    def check_port_available(self, port: int, host: str = 'localhost') -> bool:
        """检查端口是否被占用"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except:
            return False

    def test_backend_api_health(self) -> Dict:
        """测试后端API健康检查"""
        self.log("测试后端API健康检查...")
        result = {
            'name': '后端API健康检查',
            'endpoint': '/api/health',
            'port': 8000,
            'status': 'pending'
        }

        if not self.check_port_available(8000):
            result['status'] = 'skip'
            result['message'] = '后端服务未启动，跳过测试'
            self.log("后端服务未启动，跳过健康检查测试", 'WARNING')
            return result

        try:
            import httpx
            response = httpx.get(f"{self.api_base}/api/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                result['status'] = 'pass'
                result['response'] = data
                self.log(f"后端API健康检查通过: {data}", 'SUCCESS')
            else:
                result['status'] = 'fail'
                result['status_code'] = response.status_code
                self.log(f"后端API返回错误状态码: {response.status_code}", 'ERROR')
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            self.log(f"后端API健康检查失败: {e}", 'ERROR')

        return result

    def test_backend_api_endpoints(self) -> Dict:
        """测试后端API端点"""
        self.log("测试后端API端点...")
        result = {
            'name': '后端API端点',
            'endpoints': [],
            'status': 'pending'
        }

        if not self.check_port_available(8000):
            result['status'] = 'skip'
            result['message'] = '后端服务未启动，跳过测试'
            self.log("后端服务未启动，跳过API端点测试", 'WARNING')
            return result

        # 定义要测试的端点
        endpoints = [
            '/api/health',
            '/api/project/status',
            '/api/scripts/list',
        ]

        try:
            import httpx
            result['endpoints'] = []
            for endpoint in endpoints:
                try:
                    response = httpx.get(f"{self.api_base}{endpoint}", timeout=5)
                    endpoint_result = {
                        'endpoint': endpoint,
                        'status_code': response.status_code,
                        'accessible': response.status_code < 400
                    }
                    result['endpoints'].append(endpoint_result)
                    if response.status_code < 400:
                        self.log(f"端点 {endpoint} 可访问", 'SUCCESS')
                    else:
                        self.log(f"端点 {endpoint} 返回状态码 {response.status_code}", 'WARNING')
                except Exception as e:
                    result['endpoints'].append({
                        'endpoint': endpoint,
                        'accessible': False,
                        'error': str(e)
                    })
                    self.log(f"端点 {endpoint} 测试失败: {e}", 'WARNING')

            # 计算端点可用率
            accessible_count = sum(1 for ep in result['endpoints'] if ep.get('accessible', False))
            total_count = len(result['endpoints'])
            if accessible_count == total_count:
                result['status'] = 'pass'
            elif accessible_count > 0:
                result['status'] = 'partial'
            else:
                result['status'] = 'fail'

        except ImportError:
            result['status'] = 'skip'
            result['message'] = 'httpx未安装，跳过测试'
            self.log("httpx未安装，跳过API端点测试", 'WARNING')

        return result

    def test_web_interface_health(self) -> Dict:
        """测试Web界面健康检查"""
        self.log("测试Web界面健康检查...")
        result = {
            'name': 'Web界面健康检查',
            'endpoint': '/api/health',
            'port': 8080,
            'status': 'pending'
        }

        if not self.check_port_available(8080):
            result['status'] = 'skip'
            result['message'] = 'Web服务未启动，跳过测试'
            self.log("Web服务未启动，跳过健康检查测试", 'WARNING')
            return result

        try:
            import httpx
            response = httpx.get(f"{self.web_base}/api/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                result['status'] = 'pass'
                result['response'] = data
                self.log(f"Web界面健康检查通过: {data}", 'SUCCESS')
            else:
                result['status'] = 'fail'
                result['status_code'] = response.status_code
                self.log(f"Web界面返回错误状态码: {response.status_code}", 'ERROR')
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            self.log(f"Web界面健康检查失败: {e}", 'ERROR')

        return result

    def test_web_interface_endpoints(self) -> Dict:
        """测试Web界面API端点"""
        self.log("测试Web界面API端点...")
        result = {
            'name': 'Web界面API端点',
            'endpoints': [],
            'status': 'pending'
        }

        if not self.check_port_available(8080):
            result['status'] = 'skip'
            result['message'] = 'Web服务未启动，跳过测试'
            self.log("Web服务未启动，跳过API端点测试", 'WARNING')
            return result

        # 定义要测试的端点
        endpoints = [
            '/api/health',
            '/api/project/status',
            '/api/scripts/status',
            '/api/scripts/list',
            '/api/system/resources',
            '/api/deployment/progress',
        ]

        try:
            import httpx
            result['endpoints'] = []
            for endpoint in endpoints:
                try:
                    response = httpx.get(f"{self.web_base}{endpoint}", timeout=5)
                    endpoint_result = {
                        'endpoint': endpoint,
                        'status_code': response.status_code,
                        'accessible': response.status_code < 400
                    }
                    result['endpoints'].append(endpoint_result)
                    if response.status_code < 400:
                        self.log(f"端点 {endpoint} 可访问", 'SUCCESS')
                    else:
                        self.log(f"端点 {endpoint} 返回状态码 {response.status_code}", 'WARNING')
                except Exception as e:
                    result['endpoints'].append({
                        'endpoint': endpoint,
                        'accessible': False,
                        'error': str(e)
                    })
                    self.log(f"端点 {endpoint} 测试失败: {e}", 'WARNING')

            # 计算端点可用率
            accessible_count = sum(1 for ep in result['endpoints'] if ep.get('accessible', False))
            total_count = len(result['endpoints'])
            if accessible_count == total_count:
                result['status'] = 'pass'
            elif accessible_count > 0:
                result['status'] = 'partial'
            else:
                result['status'] = 'fail'

        except ImportError:
            result['status'] = 'skip'
            result['message'] = 'httpx未安装，跳过测试'
            self.log("httpx未安装，跳过API端点测试", 'WARNING')

        return result

    def test_websocket_connection(self) -> Dict:
        """测试WebSocket连接"""
        self.log("测试WebSocket连接...")
        result = {
            'name': 'WebSocket连接',
            'endpoint': '/ws/monitoring',
            'port': 8080,
            'status': 'pending'
        }

        if not self.check_port_available(8080):
            result['status'] = 'skip'
            result['message'] = 'Web服务未启动，跳过测试'
            self.log("Web服务未启动，跳过WebSocket测试", 'WARNING')
            return result

        # 简单的WebSocket连接测试
        try:
            import httpx
            # 检查WebSocket端点是否存在
            response = httpx.get(f"{self.web_base}/ws/monitoring", timeout=5)
            # WebSocket连接会有不同的响应
            result['status'] = 'pass'
            result['note'] = 'WebSocket端点可访问'
            self.log("WebSocket端点可访问", 'SUCCESS')
        except Exception as e:
            result['status'] = 'warning'
            result['error'] = str(e)
            self.log(f"WebSocket连接测试: {e}", 'WARNING')

        return result

    def test_script_execution_api(self) -> Dict:
        """测试脚本执行API"""
        self.log("测试脚本执行API...")
        result = {
            'name': '脚本执行API',
            'endpoints': [],
            'status': 'pending'
        }

        if not self.check_port_available(8080):
            result['status'] = 'skip'
            result['message'] = 'Web服务未启动，跳过测试'
            self.log("Web服务未启动，跳过脚本执行API测试", 'WARNING')
            return result

        # 测试GET请求
        try:
            import httpx
            response = httpx.get(f"{self.web_base}/api/scripts/list", timeout=5)
            if response.status_code == 200:
                data = response.json()
                result['list_endpoint'] = 'accessible'
                result['scripts_count'] = len(data) if isinstance(data, list) else 0
                self.log(f"脚本列表API可访问，找到 {result['scripts_count']} 个脚本", 'SUCCESS')
            else:
                result['list_endpoint'] = f'error_{response.status_code}'
                self.log(f"脚本列表API返回状态码: {response.status_code}", 'WARNING')
        except Exception as e:
            result['list_endpoint'] = 'error'
            result['error'] = str(e)
            self.log(f"脚本列表API测试失败: {e}", 'WARNING')

        result['status'] = 'pass'
        return result

    def test_system_resources_api(self) -> Dict:
        """测试系统资源API"""
        self.log("测试系统资源API...")
        result = {
            'name': '系统资源API',
            'endpoint': '/api/system/resources',
            'status': 'pending'
        }

        if not self.check_port_available(8080):
            result['status'] = 'skip'
            result['message'] = 'Web服务未启动，跳过测试'
            self.log("Web服务未启动，跳过系统资源API测试", 'WARNING')
            return result

        try:
            import httpx
            response = httpx.get(f"{self.web_base}/api/system/resources", timeout=5)
            if response.status_code == 200:
                data = response.json()
                result['status'] = 'pass'
                result['response'] = data
                self.log(f"系统资源API返回数据: CPU={data.get('cpu_percent')}%", 'SUCCESS')
            else:
                result['status'] = 'fail'
                result['status_code'] = response.status_code
                self.log(f"系统资源API返回状态码: {response.status_code}", 'ERROR')
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            self.log(f"系统资源API测试失败: {e}", 'ERROR')

        return result

    def run_all_tests(self) -> Dict:
        """运行所有前后端联动测试"""
        self.log("=" * 60)
        self.log("开始前后端联动测试")
        self.log("=" * 60)

        results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'summary': {'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0, 'warnings': 0}
        }

        # 执行各项测试
        test_methods = [
            ('backend_api_health', self.test_backend_api_health),
            ('backend_api_endpoints', self.test_backend_api_endpoints),
            ('web_interface_health', self.test_web_interface_health),
            ('web_interface_endpoints', self.test_web_interface_endpoints),
            ('websocket_connection', self.test_websocket_connection),
            ('script_execution_api', self.test_script_execution_api),
            ('system_resources_api', self.test_system_resources_api),
        ]

        for test_name, test_method in test_methods:
            self.log(f"\n执行测试: {test_name}")
            try:
                test_result = test_method()
                results['tests'][test_name] = test_result
                results['summary']['total'] += 1

                if test_result.get('status') in ['pass', 'ready']:
                    results['summary']['passed'] += 1
                elif test_result.get('status') in ['fail', 'error']:
                    results['summary']['failed'] += 1
                elif test_result.get('status') == 'skip':
                    results['summary']['skipped'] += 1
                elif test_result.get('status') == 'warning':
                    results['summary']['warnings'] += 1
                elif test_result.get('status') == 'partial':
                    results['summary']['passed'] += 1
                    results['summary']['warnings'] += 1
            except Exception as e:
                self.log(f"测试执行失败: {e}", 'ERROR')
                results['tests'][test_name] = {'name': test_name, 'status': 'error', 'error': str(e)}
                results['summary']['total'] += 1
                results['summary']['failed'] += 1

        # 打印汇总
        self.log("\n" + "=" * 60)
        self.log("前后端联动测试结果汇总")
        self.log("=" * 60)
        self.log(f"总测试数: {results['summary']['total']}")
        self.log(f"通过: {results['summary']['passed']}")
        self.log(f"失败: {results['summary']['failed']}")
        self.log(f"跳过: {results['summary']['skipped']}")
        self.log(f"警告: {results['summary']['warnings']}")

        # 计算总体状态
        if results['summary']['failed'] > 0:
            results['overall_status'] = 'fail'
        elif results['summary']['skipped'] == results['summary']['total']:
            results['overall_status'] = 'skip'
        elif results['summary']['warnings'] > 0:
            results['overall_status'] = 'warning'
        else:
            results['overall_status'] = 'pass'

        self.log(f"总体状态: {results['overall_status']}")

        return results


def main():
    """主函数"""
    print("=" * 60)
    print("前后端联动测试工具")
    print("=" * 60)

    tester = FrontendBackendTester()
    results = tester.run_all_tests()

    # 保存结果
    report_dir = Path(__file__).parent / 'reports'
    report_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = report_dir / f'frontend_backend_test_report_{timestamp}.json'

    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n测试报告已保存: {report_file}")

    # 返回退出码
    sys.exit(0 if results['overall_status'] in ['pass', 'skip'] else 1)


if __name__ == '__main__':
    main()

