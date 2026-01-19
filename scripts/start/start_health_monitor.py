#!/usr/bin/env python3
"""
my_ai_popup_project 健康监控启动脚本

功能:
    - 启动系统健康监控服务
    - 实时监控项目运行状态
    - 定期检查各个组件健康状况

使用方法:
    python3 scripts/start/start_health_monitor.py
    python3 scripts/start/start_health_monitor.py --interval 30
    python3 scripts/start/start_health_monitor.py --verbose
"""

import sys
import time
import signal
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import json


class HealthMonitor:
    """健康监控器"""

    def __init__(self, verbose: bool = False, interval: int = 60):
        self.verbose = verbose
        self.interval = interval
        self.running = True
        self.start_time = None

        # 项目根目录
        self.project_root = Path(__file__).parent.parent.parent

        # 注册信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """信号处理"""
        print("\n\n接收到停止信号，正在退出...")
        self.running = False

    def log(self, message: str, level: str = 'INFO'):
        """日志输出"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        prefix = {
            'INFO': '[INFO]',
            'WARNING': '[WARNING]',
            'ERROR': '[ERROR]',
            'SUCCESS': '[SUCCESS]'
        }.get(level, '[INFO]')

        print(f"{timestamp} {prefix} {message}")

    def check_python(self) -> Dict:
        """检查Python环境"""
        result = {
            'name': 'Python环境',
            'status': 'healthy',
            'version': sys.version,
            'path': sys.executable
        }

        try:
            # 检查版本
            if sys.version_info < (3, 8):
                result['status'] = 'warning'
                result['message'] = 'Python版本低于3.8'

            # 检查虚拟环境
            is_venv = (
                hasattr(sys, 'real_prefix') or
                (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
            )
            result['virtual_env'] = is_venv

        except Exception as e:
            result['status'] = 'error'
            result['message'] = str(e)

        return result

    def check_project_structure(self) -> Dict:
        """检查项目结构"""
        result = {
            'name': '项目结构',
            'status': 'healthy',
            'directories': {},
            'files': {}
        }

        try:
            required_dirs = ['src', 'rules', 'assets', 'docs', 'logs', 'web', 'scripts']
            required_files = ['project_config.json', 'requirements.txt', 'README.md']

            for dir_name in required_dirs:
                dir_path = self.project_root / dir_name
                exists = dir_path.exists()
                result['directories'][dir_name] = {
                    'exists': exists,
                    'path': str(dir_path)
                }
                if not exists:
                    result['status'] = 'warning'

            for file_name in required_files:
                file_path = self.project_root / file_name
                exists = file_path.exists()
                result['files'][file_name] = {
                    'exists': exists,
                    'path': str(file_path)
                }
                if not exists:
                    result['status'] = 'warning'

        except Exception as e:
            result['status'] = 'error'
            result['message'] = str(e)

        return result

    def check_dependencies(self) -> Dict:
        """检查依赖"""
        result = {
            'name': '依赖',
            'status': 'healthy',
            'packages': {}
        }

        try:
            # 检查关键依赖 (包名: 导入名)
            key_packages = {
                'fastapi': 'fastapi',
                'uvicorn': 'uvicorn',
                'pydantic': 'pydantic',
                'PyQt5': 'PyQt5',
                'PyQt6': 'PyQt6',
                'numpy': 'numpy',
                'opencv-python': 'cv2',
                'requests': 'requests',
                'websocket-client': 'websocket',
                'psutil': 'psutil',
                'httpx': 'httpx'
            }

            for package, import_name in key_packages.items():
                try:
                    __import__(import_name)
                    result['packages'][package] = 'installed'
                except (ImportError, ModuleNotFoundError):
                    result['packages'][package] = 'missing'
                    result['status'] = 'warning'

        except Exception as e:
            result['status'] = 'error'
            result['message'] = str(e)

        return result

    def check_services(self) -> Dict:
        """检查服务状态"""
        result = {
            'name': '服务',
            'status': 'healthy',
            'services': {}
        }

        try:
            # 检查API服务
            result['services']['api'] = self._check_port(8000)

            # 检查Web服务
            result['services']['web'] = self._check_port(8080)

            # 检查Ollama
            result['services']['ollama'] = self._check_ollama()

        except Exception as e:
            result['status'] = 'error'
            result['message'] = str(e)

        return result

    def _check_port(self, port: int) -> Dict:
        """检查端口"""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()

            return {
                'port': port,
                'status': 'running' if result == 0 else 'stopped'
            }
        except Exception as e:
            return {
                'port': port,
                'status': 'unknown',
                'error': str(e)
            }

    def _check_ollama(self) -> Dict:
        """检查Ollama服务"""
        try:
            import requests
            response = requests.get('http://localhost:11434/api/version', timeout=2)
            if response.status_code == 200:
                return {
                    'status': 'running',
                    'version': response.json().get('version', 'unknown')
                }
            else:
                return {'status': 'stopped'}
        except:
            return {'status': 'stopped'}

    def check_resources(self) -> Dict:
        """检查资源使用"""
        result = {
            'name': '资源',
            'status': 'healthy',
            'cpu': 0,
            'memory': 0,
            'disk': 0
        }

        try:
            import psutil

            # CPU使用率
            result['cpu'] = psutil.cpu_percent(interval=1)

            # 内存使用率
            memory = psutil.virtual_memory()
            result['memory'] = memory.percent

            # 磁盘使用率
            disk = psutil.disk_usage(str(self.project_root))
            result['disk'] = disk.percent

            # 设置状态
            if result['cpu'] > 90 or result['memory'] > 90 or result['disk'] > 90:
                result['status'] = 'critical'
            elif result['cpu'] > 70 or result['memory'] > 80 or result['disk'] > 80:
                result['status'] = 'warning'

        except ImportError:
            result['message'] = 'psutil未安装，跳过资源检查'
        except Exception as e:
            result['status'] = 'error'
            result['message'] = str(e)

        return result

    def run_check(self) -> Dict:
        """运行健康检查"""
        check_results = {
            'timestamp': datetime.now().isoformat(),
            'checks': {}
        }

        # 执行各项检查
        check_results['checks']['python'] = self.check_python()
        check_results['checks']['structure'] = self.check_project_structure()
        check_results['checks']['dependencies'] = self.check_dependencies()
        check_results['checks']['services'] = self.check_services()
        check_results['checks']['resources'] = self.check_resources()

        # 计算总体状态
        statuses = [c.get('status', 'unknown') for c in check_results['checks'].values()]
        if 'error' in statuses:
            check_results['overall_status'] = 'error'
        elif 'critical' in statuses:
            check_results['overall_status'] = 'critical'
        elif 'warning' in statuses:
            check_results['overall_status'] = 'warning'
        else:
            check_results['overall_status'] = 'healthy'

        return check_results

    def print_results(self, results: Dict):
        """打印检查结果"""
        print("\n" + "=" * 60)
        print(f"健康检查报告 - {results['timestamp']}")
        print("=" * 60)

        status_symbols = {
            'healthy': '✓',
            'warning': '⚠',
            'error': '✗',
            'critical': '🚨'
        }

        for check_name, check_result in results['checks'].items():
            symbol = status_symbols.get(check_result.get('status', 'unknown'), '?')
            name = check_result.get('name', check_name)
            print(f"\n{symbol} {name}")

            if self.verbose:
                for key, value in check_result.items():
                    if key not in ['name']:
                        print(f"    {key}: {value}")

        print("\n" + "=" * 60)
        print(f"总体状态: {results['overall_status']}")
        print("=" * 60)

    def save_results(self, results: Dict):
        """保存检查结果"""
        report_dir = self.project_root / 'logs' / 'health_reports'
        report_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = report_dir / f'health_report_{timestamp}.json'

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        self.log(f"报告已保存: {report_file}")

    def run(self):
        """运行监控"""
        self.start_time = datetime.now()
        self.log(f"健康监控启动")
        self.log(f"检查间隔: {self.interval}秒")
        self.log(f"详细输出: {'是' if self.verbose else '否'}")

        while self.running:
            results = self.run_check()
            self.print_results(results)
            self.save_results(results)

            # 等待下次检查
            for i in range(self.interval):
                if not self.running:
                    break
                time.sleep(1)

        uptime = datetime.now() - self.start_time
        self.log(f"监控已停止，运行时间: {uptime}")


def main():
    """主函数"""
    print("=" * 50)
    print("my_ai_popup_project 健康监控")
    print("=" * 50)

    # 解析命令行参数
    verbose = False
    interval = 60

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == '--verbose' or args[i] == '-v':
            verbose = True
            i += 1
        elif args[i] == '--interval' and i + 1 < len(args):
            interval = int(args[i + 1])
            i += 2
        elif args[i] in ['--help', '-h']:
            print("使用方法:")
            print("  python3 scripts/start/start_health_monitor.py")
            print("  python3 scripts/start/start_health_monitor.py --verbose")
            print("  python3 scripts/start/start_health_monitor.py --interval 30")
            sys.exit(0)
        else:
            i += 1

    # 启动监控
    monitor = HealthMonitor(verbose=verbose, interval=interval)
    monitor.run()


if __name__ == '__main__':
    main()

