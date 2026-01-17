#!/usr/bin/env python3
"""
测试启动配置模块

功能:
    - 验证所有VSCode调试启动配置
    - 检查各服务启动状态
    - 验证端口可用性

使用方法:
    cd /workspaces/my_ai_popup_project
    python3 scripts/test/test_launch_config.py
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import socket
import subprocess
import time
from typing import Dict, List, Optional
from datetime import datetime


class LaunchConfigTester:
    """启动配置测试器"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.results = []

    def log(self, message: str, level: str = 'INFO'):
        """日志输出"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        prefix = {'INFO': '[INFO]', 'WARNING': '[WARNING]', 'ERROR': '[ERROR]', 'SUCCESS': '[SUCCESS]'}.get(level, '[INFO]')
        print(f"{timestamp} {prefix} {message}")
        self.results.append({'time': timestamp, 'level': level, 'message': message})

    def check_port_available(self, port: int, host: str = 'localhost') -> Dict:
        """检查端口是否可用"""
        result = {'port': port, 'host': host, 'status': 'unknown'}
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            connection = sock.connect_ex((host, port))
            result['status'] = 'occupied' if connection == 0 else 'available'
            sock.close()
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
        return result

    def test_python_version(self) -> Dict:
        """测试Python版本"""
        self.log("检查Python版本...")
        result = {
            'name': 'Python版本',
            'status': 'pass',
            'version': sys.version,
            'executable': sys.executable
        }

        if sys.version_info < (3, 8):
            result['status'] = 'fail'
            result['message'] = 'Python版本低于3.8'
            self.log(f"Python版本不符合要求: {sys.version}", 'ERROR')
        elif sys.version_info < (3, 10):
            result['status'] = 'warning'
            result['message'] = '建议使用Python 3.10+'
            self.log(f"Python版本较旧: {sys.version}", 'WARNING')
        else:
            self.log(f"Python版本符合要求: {sys.version}", 'SUCCESS')

        return result

    def test_backend_api_config(self) -> Dict:
        """测试后端API配置"""
        self.log("测试后端API启动配置...")
        result = {
            'name': '后端API服务',
            'config_path': 'src/backend/control_core/server.py',
            'default_port': 8000,
            'status': 'pending'
        }

        # 检查配置文件
        config_file = self.project_root / 'src' / 'backend' / 'control_core' / 'server.py'
        if config_file.exists():
            result['config_exists'] = True
            result['status'] = 'ready'
            self.log(f"后端API配置文件存在: {config_file}", 'SUCCESS')
        else:
            result['config_exists'] = False
            result['status'] = 'fail'
            self.log(f"后端API配置文件不存在: {config_file}", 'ERROR')

        # 检查端口
        port_check = self.check_port_available(8000)
        result['port_status'] = port_check['status']
        self.log(f"端口8000状态: {port_check['status']}", 'INFO')

        return result

    def test_web_interface_config(self) -> Dict:
        """测试Web界面配置"""
        self.log("测试Web界面启动配置...")
        result = {
            'name': 'Web界面服务',
            'config_path': 'web/app.py',
            'default_port': 8080,
            'status': 'pending'
        }

        # 检查配置文件
        config_file = self.project_root / 'web' / 'app.py'
        if config_file.exists():
            result['config_exists'] = True
            result['status'] = 'ready'
            self.log(f"Web界面配置文件存在: {config_file}", 'SUCCESS')
        else:
            result['config_exists'] = False
            result['status'] = 'fail'
            self.log(f"Web界面配置文件不存在: {config_file}", 'ERROR')

        # 检查端口
        port_check = self.check_port_available(8080)
        result['port_status'] = port_check['status']
        self.log(f"端口8080状态: {port_check['status']}", 'INFO')

        return result

    def test_gui_config(self) -> Dict:
        """测试GUI配置"""
        self.log("测试GUI启动配置...")
        result = {
            'name': 'GUI前端',
            'config_path': 'scripts/start_gui_py.py',
            'status': 'pending'
        }

        # 检查配置文件
        config_file = self.project_root / 'scripts' / 'start_gui_py.py'
        if config_file.exists():
            result['config_exists'] = True
            result['status'] = 'ready'
            self.log(f"GUI配置文件存在: {config_file}", 'SUCCESS')
        else:
            result['config_exists'] = False
            result['status'] = 'fail'
            self.log(f"GUI配置文件不存在: {config_file}", 'ERROR')

        # 检查PyQt
        try:
            import PyQt5
            result['pyqt5'] = 'installed'
            self.log("PyQt5已安装", 'SUCCESS')
        except ImportError:
            result['pyqt5'] = 'not_found'
            self.log("PyQt5未安装", 'WARNING')

        try:
            import PyQt6
            result['pyqt6'] = 'installed'
            self.log("PyQt6已安装", 'SUCCESS')
        except ImportError:
            result['pyqt6'] = 'not_found'
            self.log("PyQt6未安装", 'WARNING')

        return result

    def test_health_monitor_config(self) -> Dict:
        """测试健康监控配置"""
        self.log("测试健康监控启动配置...")
        result = {
            'name': '健康监控',
            'config_path': 'scripts/start_health_monitor.py',
            'status': 'pending'
        }

        # 检查配置文件
        config_file = self.project_root / 'scripts' / 'start_health_monitor.py'
        if config_file.exists():
            result['config_exists'] = True
            result['status'] = 'ready'
            self.log(f"健康监控配置文件存在: {config_file}", 'SUCCESS')
        else:
            result['config_exists'] = False
            result['status'] = 'fail'
            self.log(f"健康监控配置文件不存在: {config_file}", 'ERROR')

        return result

    def test_vscode_launch_config(self) -> Dict:
        """测试VSCode启动配置"""
        self.log("测试VSCode启动配置...")
        result = {
            'name': 'VSCode调试配置',
            'config_path': '.vscode/launch.json',
            'status': 'pending',
            'configurations': []
        }

        config_file = self.project_root / '.vscode' / 'launch.json'
        if config_file.exists():
            result['config_exists'] = True
            try:
                import json
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                result['configurations'] = []
                for cfg in config.get('configurations', []):
                    cfg_info = {
                        'name': cfg.get('name'),
                        'type': cfg.get('type'),
                        'request': cfg.get('request'),
                        'program': cfg.get('program'),
                        'group': cfg.get('presentation', {}).get('group')
                    }
                    result['configurations'].append(cfg_info)
                    self.log(f"发现启动配置: {cfg_info['name']} ({cfg_info['type']})", 'INFO')

                result['status'] = 'ready'
                self.log(f"VSCode启动配置有效，共{len(result['configurations'])}个配置", 'SUCCESS')
            except Exception as e:
                result['status'] = 'error'
                result['error'] = str(e)
                self.log(f"解析VSCode配置失败: {e}", 'ERROR')
        else:
            result['config_exists'] = False
            result['status'] = 'fail'
            self.log(f"VSCode启动配置文件不存在: {config_file}", 'ERROR')

        return result

    def run_all_tests(self) -> Dict:
        """运行所有启动配置测试"""
        self.log("=" * 60)
        self.log("开始启动配置测试")
        self.log("=" * 60)

        results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'summary': {'total': 0, 'passed': 0, 'failed': 0, 'warnings': 0}
        }

        # 执行各项测试
        test_methods = [
            ('python_version', self.test_python_version),
            ('vscode_launch', self.test_vscode_launch_config),
            ('backend_api', self.test_backend_api_config),
            ('web_interface', self.test_web_interface_config),
            ('gui', self.test_gui_config),
            ('health_monitor', self.test_health_monitor_config),
        ]

        for test_name, test_method in test_methods:
            self.log(f"\n执行测试: {test_name}")
            try:
                test_result = test_method()
                results['tests'][test_name] = test_result
                results['summary']['total'] += 1

                if test_result.get('status') in ['ready', 'pass']:
                    results['summary']['passed'] += 1
                elif test_result.get('status') == 'fail':
                    results['summary']['failed'] += 1
                elif test_result.get('status') == 'warning':
                    results['summary']['warnings'] += 1
            except Exception as e:
                self.log(f"测试执行失败: {e}", 'ERROR')
                results['tests'][test_name] = {'name': test_name, 'status': 'error', 'error': str(e)}
                results['summary']['total'] += 1
                results['summary']['failed'] += 1

        # 打印汇总
        self.log("\n" + "=" * 60)
        self.log("启动配置测试结果汇总")
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
    print("启动配置测试工具")
    print("=" * 60)

    tester = LaunchConfigTester()
    results = tester.run_all_tests()

    # 保存结果
    report_dir = Path(__file__).parent / 'reports'
    report_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = report_dir / f'launch_test_report_{timestamp}.json'

    import json
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n测试报告已保存: {report_file}")

    # 返回退出码
    sys.exit(0 if results['overall_status'] == 'pass' else 1)


if __name__ == '__main__':
    main()

