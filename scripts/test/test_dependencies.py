#!/usr/bin/env python3
"""
依赖检查模块

功能:
    - 检查项目依赖完整性
    - 验证关键包安装状态
    - 检查Python版本

使用方法:
    cd /workspaces/my_ai_popup_project
    python3 scripts/test/test_dependencies.py
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import subprocess
import json
from typing import Dict, List, Optional
from datetime import datetime


class DependencyChecker:
    """依赖检查器"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.results = []

    def log(self, message: str, level: str = 'INFO'):
        """日志输出"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        prefix = {'INFO': '[INFO]', 'WARNING': '[WARNING]', 'ERROR': '[ERROR]', 'SUCCESS': '[SUCCESS]'}.get(level, '[INFO]')
        print(f"{timestamp} {prefix} {message}")
        self.results.append({'time': timestamp, 'level': level, 'message': message})

    def get_installed_packages(self) -> Dict[str, str]:
        """获取已安装的包版本"""
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'list', '--format=json'],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                packages = json.loads(result.stdout)
                return {p['name'].lower(): p['version'] for p in packages}
        except Exception as e:
            self.log(f"获取已安装包列表失败: {e}", 'ERROR')
        return {}

    def check_python_version(self) -> Dict:
        """检查Python版本"""
        self.log("检查Python版本...")
        result = {
            'name': 'Python版本',
            'current': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'required': '>=3.10.0',
            'status': 'pass'
        }

        if sys.version_info < (3, 10):
            result['status'] = 'fail'
            result['message'] = 'Python版本低于3.10.0'
            self.log(f"Python版本不符合要求: {result['current']} < 3.10.0", 'ERROR')
        else:
            self.log(f"Python版本符合要求: {result['current']}", 'SUCCESS')

        return result

    def check_requirements_file(self) -> Dict:
        """检查requirements.txt文件"""
        self.log("检查requirements.txt文件...")
        result = {
            'name': 'requirements.txt',
            'path': str(self.project_root / 'requirements.txt'),
            'exists': False,
            'packages': [],
            'status': 'pending'
        }

        req_file = self.project_root / 'requirements.txt'
        if req_file.exists():
            result['exists'] = True
            try:
                with open(req_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 解析依赖
                packages = []
                for line in content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#') and not line.startswith('-'):
                        # 提取包名和版本
                        if '>=' in line:
                            pkg_name, version = line.split('>=')
                            packages.append({'name': pkg_name.strip(), 'version': line})
                        elif '==' in line:
                            pkg_name, version = line.split('==')
                            packages.append({'name': pkg_name.strip(), 'version': line})
                        elif '>' in line:
                            pkg_name, version = line.split('>')
                            packages.append({'name': pkg_name.strip(), 'version': line})
                        else:
                            packages.append({'name': line, 'version': line})

                result['packages'] = packages
                result['total_count'] = len(packages)
                result['status'] = 'ready'
                self.log(f"找到 {result['total_count']} 个依赖项", 'SUCCESS')
            except Exception as e:
                result['status'] = 'error'
                result['error'] = str(e)
                self.log(f"解析requirements.txt失败: {e}", 'ERROR')
        else:
            result['status'] = 'fail'
            self.log("requirements.txt文件不存在", 'ERROR')

        return result

    def check_core_dependencies(self) -> Dict:
        """检查核心依赖"""
        self.log("检查核心依赖...")
        result = {
            'name': '核心依赖',
            'packages': {},
            'status': 'pending'
        }

        # 核心依赖列表
        core_packages = {
            'fastapi': 'Web框架',
            'uvicorn': 'ASGI服务器',
            'pydantic': '数据验证',
            'PyQt5': 'GUI框架',
            'PyQt6': 'GUI框架',
            'numpy': '数值计算',
            'opencv-python': '图像处理',
            'httpx': 'HTTP客户端',
            'psutil': '系统监控',
            'requests': 'HTTP请求',
        }

        installed = self.get_installed_packages()
        result['packages'] = {}

        for pkg, description in core_packages.items():
            check_name = pkg.lower().replace('-', '_')
            status = 'not_found'
            version = None

            for installed_name, installed_version in installed.items():
                if check_name in installed_name or installed_name in check_name:
                    status = 'installed'
                    version = installed_version
                    break

            result['packages'][pkg] = {
                'name': pkg,
                'description': description,
                'status': status,
                'version': version
            }

            if status == 'installed':
                self.log(f"  ✓ {pkg} ({version}) - {description}", 'SUCCESS')
            else:
                self.log(f"  ✗ {pkg} - {description} (未安装)", 'WARNING')

        # 计算状态
        installed_count = sum(1 for p in result['packages'].values() if p['status'] == 'installed')
        total_count = len(core_packages)
        
        if installed_count == total_count:
            result['status'] = 'pass'
        elif installed_count > 0:
            result['status'] = 'partial'
        else:
            result['status'] = 'fail'

        result['installed_count'] = installed_count
        result['total_count'] = total_count

        return result

    def check_ai_dependencies(self) -> Dict:
        """检查AI相关依赖"""
        self.log("检查AI相关依赖...")
        result = {
            'name': 'AI依赖',
            'packages': {},
            'status': 'pending'
        }

        # AI相关依赖
        ai_packages = {
            'torch': 'PyTorch',
            'torchvision': 'Torch视觉',
            'torchaudio': 'Torch音频',
            'insightface': '人脸分析',
            'face-recognition': '人脸识别',
            'dlib': '人脸检测',
            'deepface': '深度人脸分析',
            'mediapipe': '面部网格',
            'onnxruntime': 'ONNX推理',
            'transformers': 'Transformer模型',
            'diffusers': '扩散模型',
            'ollama': '本地LLM',
        }

        installed = self.get_installed_packages()
        result['packages'] = {}

        for pkg, description in ai_packages.items():
            check_name = pkg.lower().replace('-', '_')
            status = 'not_found'
            version = None

            for installed_name, installed_version in installed.items():
                if check_name in installed_name or installed_name in check_name:
                    status = 'installed'
                    version = installed_version
                    break

            result['packages'][pkg] = {
                'name': pkg,
                'description': description,
                'status': status,
                'version': version
            }

            if status == 'installed':
                self.log(f"  ✓ {pkg} ({version}) - {description}", 'SUCCESS')
            else:
                self.log(f"  ✗ {pkg} - {description} (未安装)", 'INFO')

        # 计算状态
        installed_count = sum(1 for p in result['packages'].values() if p['status'] == 'installed')
        total_count = len(ai_packages)

        if installed_count == total_count:
            result['status'] = 'pass'
        elif installed_count > 0:
            result['status'] = 'partial'
        else:
            result['status'] = 'fail'

        result['installed_count'] = installed_count
        result['total_count'] = total_count

        return result

    def check_web_dependencies(self) -> Dict:
        """检查Web相关依赖"""
        self.log("检查Web相关依赖...")
        result = {
            'name': 'Web依赖',
            'packages': {},
            'status': 'pending'
        }

        # Web相关依赖
        web_packages = {
            'fastapi': 'FastAPI框架',
            'uvicorn': 'Uvicorn服务器',
            'jinja2': '模板引擎',
            'python-socketio': 'Socket.IO',
            'websockets': 'WebSocket支持',
            'python-multipart': '文件上传',
        }

        installed = self.get_installed_packages()
        result['packages'] = {}

        for pkg, description in web_packages.items():
            check_name = pkg.lower().replace('-', '_')
            status = 'not_found'
            version = None

            for installed_name, installed_version in installed.items():
                if check_name in installed_name or installed_name in check_name:
                    status = 'installed'
                    version = installed_version
                    break

            result['packages'][pkg] = {
                'name': pkg,
                'description': description,
                'status': status,
                'version': version
            }

            if status == 'installed':
                self.log(f"  ✓ {pkg} ({version}) - {description}", 'SUCCESS')
            else:
                self.log(f"  ✗ {pkg} - {description} (未安装)", 'WARNING')

        # 计算状态
        installed_count = sum(1 for p in result['packages'].values() if p['status'] == 'installed')
        total_count = len(web_packages)

        if installed_count == total_count:
            result['status'] = 'pass'
        elif installed_count > 0:
            result['status'] = 'partial'
        else:
            result['status'] = 'fail'

        result['installed_count'] = installed_count
        result['total_count'] = total_count

        return result

    def run_all_checks(self) -> Dict:
        """运行所有依赖检查"""
        self.log("=" * 60)
        self.log("开始依赖检查")
        self.log("=" * 60)

        results = {
            'timestamp': datetime.now().isoformat(),
            'summary': {'total': 0, 'passed': 0, 'failed': 0, 'warnings': 0}
        }

        # 执行各项检查
        check_methods = [
            ('python_version', self.check_python_version),
            ('requirements', self.check_requirements_file),
            ('core_dependencies', self.check_core_dependencies),
            ('ai_dependencies', self.check_ai_dependencies),
            ('web_dependencies', self.check_web_dependencies),
        ]

        for check_name, check_method in check_methods:
            self.log(f"\n执行检查: {check_name}")
            try:
                check_result = check_method()
                results[check_name] = check_result
                results['summary']['total'] += 1

                if check_result.get('status') in ['pass', 'ready']:
                    results['summary']['passed'] += 1
                elif check_result.get('status') in ['fail', 'error']:
                    results['summary']['failed'] += 1
                elif check_result.get('status') in ['partial']:
                    results['summary']['passed'] += 1
                    results['summary']['warnings'] += 1
            except Exception as e:
                self.log(f"检查执行失败: {e}", 'ERROR')
                results[check_name] = {'name': check_name, 'status': 'error', 'error': str(e)}
                results['summary']['total'] += 1
                results['summary']['failed'] += 1

        # 打印汇总
        self.log("\n" + "=" * 60)
        self.log("依赖检查结果汇总")
        self.log("=" * 60)
        self.log(f"总检查项: {results['summary']['total']}")
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
    print("依赖检查工具")
    print("=" * 60)

    checker = DependencyChecker()
    results = checker.run_all_checks()

    # 保存结果
    report_dir = Path(__file__).parent / 'reports'
    report_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = report_dir / f'dependency_check_report_{timestamp}.json'

    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n检查报告已保存: {report_file}")

    # 返回退出码
    sys.exit(0 if results['overall_status'] in ['pass', 'warning'] else 1)


if __name__ == '__main__':
    main()

