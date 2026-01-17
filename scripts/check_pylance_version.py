#!/usr/bin/env python3
"""
my_ai_popup_project Pylance版本检查器

功能:
    - 检查Pylance扩展版本
    - 检查Python语言服务器状态
    - 验证PyLance配置
    - 提供版本更新建议

使用方法:
    python3 scripts/check_pylance_version.py
"""

import subprocess
import sys
import json
import os
from pathlib import Path
from typing import Optional, Dict


class PylanceVersionChecker:
    """Pylance版本检查器"""

    def __init__(self):
        self.results = []

    def check_vscode_extension(self) -> Dict:
        """检查VSCode Pylance扩展"""
        result = {
            'name': 'Pylance扩展',
            'installed': False,
            'version': None,
            'latest': None,
            'status': 'unknown'
        }

        try:
            # 检查VSCode扩展
            code_extensions = Path.home() / '.vscode' / 'extensions'

            if code_extensions.exists():
                for ext_dir in code_extensions.iterdir():
                    if 'pylance' in ext_dir.name.lower():
                        result['installed'] = True
                        result['name'] = ext_dir.name
                        result['version'] = self._get_extension_version(ext_dir)
                        break

            if result['installed']:
                result['status'] = 'installed'
            else:
                result['status'] = 'not_found'

        except Exception as e:
            result['status'] = f'error: {str(e)}'

        return result

    def _get_extension_version(self, ext_dir: Path) -> str:
        """获取扩展版本"""
        try:
            manifest_file = ext_dir / 'package.json'
            if manifest_file.exists():
                with open(manifest_file, 'r') as f:
                    manifest = json.load(f)
                    return manifest.get('version', 'unknown')
        except:
            pass
        return 'unknown'

    def check_language_server(self) -> Dict:
        """检查Python语言服务器"""
        result = {
            'name': 'Python语言服务器',
            'type': None,
            'status': 'unknown',
            'pylance_available': False
        }

        try:
            # 检查Python路径
            python_path = sys.executable
            result['python_path'] = python_path

            # 检查已安装的包
            result['installed_packages'] = []

            try:
                result['pylance_available'] = True
                result['type'] = 'pylance'
                result['status'] = 'available'
            except ImportError:
                result['status'] = 'not_installed'

            # 检查其他语言服务器
            if not result['pylance_available']:
                try:
                    import pyright
                    result['type'] = 'pyright'
                    result['status'] = 'available'
                except ImportError:
                    pass

        except Exception as e:
            result['status'] = f'error: {str(e)}'

        return result

    def check_python_environment(self) -> Dict:
        """检查Python环境"""
        result = {
            'name': 'Python环境',
            'version': None,
            'path': None,
            'virtual_env': False,
            'packages': []
        }

        result['version'] = sys.version
        result['path'] = sys.executable
        result['virtual_env'] = (
            hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        )

        # 检查关键包
        key_packages = ['pylance', 'pyright', 'pyls', 'python-lsp-server']
        for pkg in key_packages:
            try:
                __import__(pkg.replace('-', '_'))
                result['packages'].append(pkg)
            except ImportError:
                pass

        return result

    def check_vscode_settings(self) -> Dict:
        """检查VSCode设置"""
        result = {
            'name': 'VSCode设置',
            'settings_file': None,
            'python_language_server': None,
            'pylance_mode': None
        }

        try:
            # 查找VSCode设置
            settings_paths = [
                Path.home() / '.vscode' / 'settings.json',
                Path.home() / '.vscode' / 'argv.json',
            ]

            for settings_path in settings_paths:
                if settings_path.exists():
                    result['settings_file'] = str(settings_path)
                    with open(settings_path, 'r') as f:
                        try:
                            settings = json.load(f)
                            result['python_language_server'] = settings.get(
                                'python.languageServer', 'Pylance'
                            )
                            result['pylance_mode'] = settings.get(
                                'python.analysis.typeCheckingMode', 'basic'
                            )
                        except json.JSONDecodeError:
                            pass
                    break

        except Exception as e:
            result['error'] = str(e)

        return result

    def run_checks(self) -> Dict:
        """运行所有检查"""
        print("检查Pylance版本和配置...")

        results = {
            'timestamp': str(__import__('datetime').datetime.now()),
            'checks': {}
        }

        # 执行各项检查
        results['checks']['extension'] = self.check_vscode_extension()
        results['checks']['language_server'] = self.check_language_server()
        results['checks']['environment'] = self.check_python_environment()
        results['checks']['vscode_settings'] = self.check_vscode_settings()

        # 生成状态总结
        all_passed = True
        for check_name, check_result in results['checks'].items():
            status = check_result.get('status', 'unknown')
            if status not in ['installed', 'available', 'configured']:
                all_passed = False

        results['overall_status'] = 'healthy' if all_passed else 'needs_attention'

        return results

    def print_results(self, results: Dict) -> None:
        """打印检查结果"""
        print("\n" + "=" * 60)
        print("Pylance版本检查结果")
        print("=" * 60)

        for check_name, check_result in results['checks'].items():
            print(f"\n{check_result.get('name', check_name)}:")
            for key, value in check_result.items():
                if key not in ['name']:
                    print(f"  {key}: {value}")

        print("\n" + "=" * 60)
        print(f"总体状态: {results['overall_status']}")
        print("=" * 60)

        return results

    def generate_recommendations(self, results: Dict) -> None:
        """生成优化建议"""
        print("\n优化建议:")
        print("-" * 40)

        checks = results['checks']

        # 检查扩展
        ext_check = checks.get('extension', {})
        if not ext_check.get('installed'):
            print("1. 安装Pylance扩展:")
            print("   VSCode扩展商店搜索'Pylance'并安装")
            print("   或运行: code --install-extension ms-python.vscode-pylance")

        # 检查语言服务器
        ls_check = checks.get('language_server', {})
        if not ls_check.get('pylance_available'):
            print("\n2. 安装Pylance Python包:")
            print("   pip install pylance")

        # 检查设置
        vscode_check = checks.get('vscode_settings', {})
        if vscode_check.get('python_language_server') != 'Pylance':
            print("\n3. 配置VSCode使用Pylance:")
            print("   在settings.json中添加:")
            print('   "python.languageServer": "Pylance"')

        if vscode_check.get('pylance_mode') == 'basic':
            print("\n4. 启用完整类型检查:")
            print('   在settings.json中添加:')
            print('   "python.analysis.typeCheckingMode": "basic"')
            print('   或 "strict" 启用严格模式')

        # 检查Python环境
        env_check = checks.get('environment', {})
        if not env_check.get('virtual_env'):
            print("\n5. 建议使用虚拟环境:")
            print("   python -m venv venv")
            print("   source venv/bin/activate")

        print()


def main():
    """主函数"""
    checker = PylanceVersionChecker()
    results = checker.run_checks()
    checker.print_results(results)
    checker.generate_recommendations(results)

    return results


if __name__ == '__main__':
    results = main()

    # 返回适当的退出码
    if results['overall_status'] == 'healthy':
        sys.exit(0)
    else:
        sys.exit(1)
