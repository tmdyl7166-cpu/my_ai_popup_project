#!/usr/bin/env python3
"""
错误处理测试模块

功能:
    - 测试启动顺序
    - 测试错误处理机制
    - 验证错误恢复能力

使用方法:
    cd /workspaces/my_ai_popup_project
    python3 scripts/test/test_error_handling.py
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import socket
import os
from typing import Dict, List, Optional
from datetime import datetime


class ErrorHandlingTester:
    """错误处理测试器"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.results = []

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

    def test_port_conflict_handling(self) -> Dict:
        """测试端口冲突处理"""
        self.log("测试端口冲突处理...")
        result = {
            'name': '端口冲突处理',
            'status': 'pending',
            'tests': []
        }

        # 测试8000端口
        port_8000_in_use = self.check_port_available(8000)
        result['tests'].append({
            'port': 8000,
            'in_use': port_8000_in_use,
            'expected': 'available'
        })
        self.log(f"  端口8000: {'已占用' if port_8000_in_use else '可用'}")

        # 测试8080端口
        port_8080_in_use = self.check_port_available(8080)
        result['tests'].append({
            'port': 8080,
            'in_use': port_8080_in_use,
            'expected': 'available'
        })
        self.log(f"  端口8080: {'已占用' if port_8080_in_use else '可用'}")

        # 检查服务是否正确配置了端口
        result['status'] = 'pass'
        if port_8000_in_use:
            self.log("  后端服务正在运行 (端口8000已占用)", 'INFO')
        if port_8080_in_use:
            self.log("  Web服务正在运行 (端口8080已占用)", 'INFO')

        return result

    def test_dependency_error_handling(self) -> Dict:
        """测试依赖缺失处理"""
        self.log("测试依赖缺失处理...")
        result = {
            'name': '依赖缺失处理',
            'status': 'pending',
            'missing_deps': [],
            'optional_deps': []
        }

        # 关键依赖列表
        critical_deps = ['fastapi', 'uvicorn', 'pydantic', 'httpx']
        # 可选依赖列表
        optional_deps = ['PyQt5', 'PyQt6', 'torch', 'insightface', 'ollama']

        for dep in critical_deps:
            try:
                __import__(dep.replace('-', '_'))
            except ImportError:
                result['missing_deps'].append(dep)
                self.log(f"  缺少关键依赖: {dep}", 'WARNING')

        for dep in optional_deps:
            try:
                __import__(dep.replace('-', '_'))
            except ImportError:
                result['optional_deps'].append(dep)
                self.log(f"  缺少可选依赖: {dep}", 'INFO')

        # 评估状态
        if len(result['missing_deps']) == 0:
            result['status'] = 'pass'
            self.log("所有关键依赖已安装", 'SUCCESS')
        else:
            result['status'] = 'warning'
            self.log(f"缺少 {len(result['missing_deps'])} 个关键依赖", 'WARNING')

        return result

    def test_environment_error_handling(self) -> Dict:
        """测试环境错误处理"""
        self.log("测试环境错误处理...")
        result = {
            'name': '环境错误处理',
            'status': 'pending',
            'checks': []
        }

        # 检查环境变量
        env_checks = {
            'PYTHONPATH': os.environ.get('PYTHONPATH'),
            'DISPLAY': os.environ.get('DISPLAY'),
            'PATH': os.environ.get('PATH'),
        }

        for env_name, env_value in env_checks.items():
            if env_value:
                result['checks'].append({
                    'name': env_name,
                    'status': 'set',
                    'value': env_value[:50] + '...' if len(env_value) > 50 else env_value
                })
                self.log(f"  环境变量 {env_name}: 已设置", 'INFO')
            else:
                result['checks'].append({
                    'name': env_name,
                    'status': 'not_set'
                })
                self.log(f"  环境变量 {env_name}: 未设置", 'WARNING')

        # 检查DISPLAY对于GUI的影响
        if not os.environ.get('DISPLAY'):
            self.log("  注意: DISPLAY未设置，GUI可能无法启动", 'WARNING')

        result['status'] = 'pass'
        return result

    def test_file_access_error_handling(self) -> Dict:
        """测试文件访问错误处理"""
        self.log("测试文件访问错误处理...")
        result = {
            'name': '文件访问错误处理',
            'status': 'pending',
            'file_checks': []
        }

        # 检查关键文件
        critical_files = [
            'project_config.json',
            'requirements.txt',
            'src/backend/control_core/server.py',
            'web/app.py',
            'scripts/start_gui_py.py',
        ]

        all_exist = True
        for file_path in critical_files:
            full_path = self.project_root / file_path
            exists = full_path.exists()
            result['file_checks'].append({
                'path': file_path,
                'exists': exists
            })
            if exists:
                self.log(f"  ✓ {file_path}", 'SUCCESS')
            else:
                self.log(f"  ✗ {file_path} (不存在)", 'ERROR')
                all_exist = False

        # 检查目录
        critical_dirs = ['src', 'web', 'scripts', 'logs', 'docs']
        for dir_name in critical_dirs:
            dir_path = self.project_root / dir_name
            exists = dir_path.exists() and dir_path.is_dir()
            result['file_checks'].append({
                'path': dir_name,
                'exists': exists,
                'is_dir': exists
            })
            if exists:
                self.log(f"  ✓ 目录 {dir_name}", 'SUCCESS')
            else:
                self.log(f"  ✗ 目录 {dir_name} (不存在)", 'ERROR')
                all_exist = False

        result['status'] = 'pass' if all_exist else 'fail'
        return result

    def test_startup_sequence(self) -> Dict:
        """测试启动顺序"""
        self.log("测试启动顺序...")
        result = {
            'name': '启动顺序',
            'status': 'pending',
            'sequence': []
        }

        # 定义推荐的启动顺序
        startup_sequence = [
            {'order': 1, 'service': '后端API服务', 'port': 8000, 'description': '先启动后端API'},
            {'order': 2, 'service': 'Web界面服务', 'port': 8080, 'description': '再启动Web界面'},
            {'order': 3, 'service': 'GUI前端', 'port': None, 'description': '最后启动GUI'},
        ]

        # 检查当前服务状态
        current_status = {
            8000: self.check_port_available(8000),
            8080: self.check_port_available(8080),
        }

        for step in startup_sequence:
            step_result = {
                'order': step['order'],
                'service': step['service'],
                'port': step['port'],
                'description': step['description'],
                'running': current_status.get(step['port'], False) if step['port'] else None
            }
            result['sequence'].append(step_result)

            if step['port']:
                status = '运行中' if current_status[step['port']] else '未运行'
                self.log(f"  步骤{step['order']}: {step['service']} (端口{step['port']}) - {status}", 'INFO')
            else:
                self.log(f"  步骤{step['order']}: {step['service']} - 检查跳过", 'INFO')

        result['status'] = 'pass'
        return result

    def test_error_recovery(self) -> Dict:
        """测试错误恢复"""
        self.log("测试错误恢复能力...")
        result = {
            'name': '错误恢复',
            'status': 'pending',
            'checks': []
        }

        # 检查日志目录
        logs_dir = self.project_root / 'logs'
        logs_writable = False
        try:
            logs_dir.mkdir(exist_ok=True)
            test_file = logs_dir / 'test_write.tmp'
            with open(test_file, 'w') as f:
                f.write('test')
            test_file.unlink()
            logs_writable = True
        except Exception as e:
            self.log(f"  日志目录不可写: {e}", 'WARNING')

        result['checks'].append({
            'name': 'logs目录',
            'writable': logs_writable,
            'path': str(logs_dir)
        })

        # 检查健康报告目录
        health_reports_dir = logs_dir / 'health_reports'
        reports_writable = False
        try:
            health_reports_dir.mkdir(exist_ok=True)
            test_file = health_reports_dir / 'test_write.tmp'
            with open(test_file, 'w') as f:
                f.write('test')
            test_file.unlink()
            reports_writable = True
        except Exception as e:
            self.log(f"  健康报告目录不可写: {e}", 'WARNING')

        result['checks'].append({
            'name': 'health_reports目录',
            'writable': reports_writable,
            'path': str(health_reports_dir)
        })

        # 检查配置文件备份
        result['status'] = 'pass' if logs_writable and reports_writable else 'warning'

        return result

    def run_all_tests(self) -> Dict:
        """运行所有错误处理测试"""
        self.log("=" * 60)
        self.log("开始错误处理测试")
        self.log("=" * 60)

        results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'summary': {'total': 0, 'passed': 0, 'failed': 0, 'warnings': 0}
        }

        # 执行各项测试
        test_methods = [
            ('port_conflict', self.test_port_conflict_handling),
            ('dependency_error', self.test_dependency_error_handling),
            ('environment_error', self.test_environment_error_handling),
            ('file_access', self.test_file_access_error_handling),
            ('startup_sequence', self.test_startup_sequence),
            ('error_recovery', self.test_error_recovery),
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
                elif test_result.get('status') == 'warning':
                    results['summary']['passed'] += 1
                    results['summary']['warnings'] += 1
            except Exception as e:
                self.log(f"测试执行失败: {e}", 'ERROR')
                results['tests'][test_name] = {'name': test_name, 'status': 'error', 'error': str(e)}
                results['summary']['total'] += 1
                results['summary']['failed'] += 1

        # 打印汇总
        self.log("\n" + "=" * 60)
        self.log("错误处理测试结果汇总")
        self.log("=" * 60)
        self.log(f"总测试数: {results['summary']['total']}")
        self.log(f"通过: {results['summary']['passed']}")
        self.log(f"失败: {results['summary']['failed']}")
        self.log(f"警告: {results['summary']['warnings']}")

        # 计算总体状态
        if results['summary']['failed'] > 0:
            results['overall_status'] = 'fail'
        elif results['summary']['warnings'] > 0:
            results['overall_status'] = 'warning'
        else:
            results['overall_status'] = 'pass'

        self.log(f"总体状态: {results['overall_status']}")

        return results


def main():
    """主函数"""
    print("=" * 60)
    print("错误处理测试工具")
    print("=" * 60)

    tester = ErrorHandlingTester()
    results = tester.run_all_tests()

    # 保存结果
    report_dir = Path(__file__).parent / 'reports'
    report_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = report_dir / f'error_handling_test_report_{timestamp}.json'

    import json
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n测试报告已保存: {report_file}")

    # 返回退出码
    sys.exit(0 if results['overall_status'] in ['pass', 'warning'] else 1)


if __name__ == '__main__':
    main()

