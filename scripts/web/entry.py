#!/usr/bin/env python3
"""
Web脚本系统统一入口
提供统一的命令行接口和配置管理
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.utils.logging_utils import get_script_logger, setup_global_logging
from scripts.utils.file_utils import read_json, write_json

class WebEntryPoint:
    """Web脚本系统统一入口"""

    def __init__(self):
        self.logger = get_script_logger("web_entry")
        self.project_root = project_root
        self.web_config_path = self.project_root / "scripts" / "web" / "web_config.json"

        # 注册可用的命令
        self.commands = {
            "orchestrate": {
                "description": "编排执行所有web相关脚本",
                "handler": self.handle_orchestrate,
                "args": []
            },
            "api": {
                "description": "API管理和跨域处理",
                "handler": self.handle_api,
                "args": []
            },
            "menu": {
                "description": "菜单互动性和结构管理",
                "handler": self.handle_menu,
                "args": []
            },
            "security": {
                "description": "安全验证和漏洞检测",
                "handler": self.handle_security,
                "args": []
            },
            "config": {
                "description": "配置管理",
                "handler": self.handle_config,
                "args": ["action", "key", "value"]
            },
            "status": {
                "description": "显示系统状态",
                "handler": self.handle_status,
                "args": []
            }
        }

    def load_web_config(self) -> Dict[str, Any]:
        """加载web配置"""
        try:
            if self.web_config_path.exists():
                return read_json(self.web_config_path)
            else:
                # 创建默认web配置
                default_config = {
                    "version": "1.0.0",
                    "last_updated": datetime.now().isoformat(),
                    "settings": {
                        "auto_save": True,
                        "debug_mode": False,
                        "log_level": "INFO"
                    },
                    "modules": {
                        "api_manager": {"enabled": True, "priority": 1},
                        "menu_manager": {"enabled": True, "priority": 2},
                        "security_validator": {"enabled": True, "priority": 3}
                    },
                    "orchestration": {
                        "execution_order": ["api_manager", "menu_manager", "security_validator"],
                        "parallel_execution": False,
                        "timeout": 300
                    }
                }
                write_json(self.web_config_path, default_config)
                return default_config
        except Exception as e:
            self.logger.error(f"加载web配置失败: {e}")
            return {}

    def handle_orchestrate(self, args: argparse.Namespace) -> int:
        """处理编排命令"""
        try:
            from scripts.web.web_orchestrator import WebOrchestrator
            orchestrator = WebOrchestrator()
            orchestrator.run()
            return 0
        except Exception as e:
            self.logger.error(f"编排执行失败: {e}")
            return 1

    def handle_api(self, args: argparse.Namespace) -> int:
        """处理API命令"""
        try:
            from scripts.web.api_manager import APIManager
            manager = APIManager()
            manager.run()
            return 0
        except Exception as e:
            self.logger.error(f"API管理执行失败: {e}")
            return 1

    def handle_menu(self, args: argparse.Namespace) -> int:
        """处理菜单命令"""
        try:
            from scripts.web.menu_manager import MenuManager
            manager = MenuManager()
            manager.run()
            return 0
        except Exception as e:
            self.logger.error(f"菜单管理执行失败: {e}")
            return 1

    def handle_security(self, args: argparse.Namespace) -> int:
        """处理安全命令"""
        try:
            from scripts.web.security_validator import SecurityValidator
            validator = SecurityValidator()
            validator.run()
            return 0
        except Exception as e:
            self.logger.error(f"安全验证执行失败: {e}")
            return 1

    def handle_config(self, args: argparse.Namespace) -> int:
        """处理配置命令"""
        config = self.load_web_config()

        if args.action == "get":
            if args.key:
                # 获取特定配置项
                keys = args.key.split('.')
                value = config
                try:
                    for key in keys:
                        value = value[key]
                    print(f"{args.key}: {value}")
                except KeyError:
                    print(f"配置项不存在: {args.key}")
                    return 1
            else:
                # 显示所有配置
                print("当前配置:")
                print(json.dumps(config, indent=2, ensure_ascii=False))

        elif args.action == "set":
            if not args.key or args.value is None:
                print("设置配置需要指定key和value")
                return 1

            # 设置配置项
            keys = args.key.split('.')
            current = config
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]

            # 尝试转换值类型
            value = args.value
            if value.lower() in ('true', 'false'):
                value = value.lower() == 'true'
            elif value.isdigit():
                value = int(value)
            elif value.replace('.', '').isdigit():
                value = float(value)

            current[keys[-1]] = value
            config["last_updated"] = datetime.now().isoformat()

            # 保存配置
            write_json(self.web_config_path, config)
            print(f"配置已更新: {args.key} = {value}")

        elif args.action == "reset":
            # 重置配置
            if os.path.exists(self.web_config_path):
                os.remove(self.web_config_path)
            print("配置已重置")

        else:
            print(f"未知的配置操作: {args.action}")
            return 1

        return 0

    def handle_status(self, args: argparse.Namespace) -> int:
        """处理状态命令"""
        config = self.load_web_config()

        print("Web脚本系统状态:")
        print(f"- 版本: {config.get('version', 'unknown')}")
        print(f"- 最后更新: {config.get('last_updated', 'unknown')}")

        settings = config.get('settings', {})
        print(f"- 自动保存: {'启用' if settings.get('auto_save') else '禁用'}")
        print(f"- 调试模式: {'启用' if settings.get('debug_mode') else '禁用'}")
        print(f"- 日志级别: {settings.get('log_level', 'INFO')}")

        modules = config.get('modules', {})
        print("\n模块状态:")
        for module_name, module_config in modules.items():
            status = "启用" if module_config.get('enabled') else "禁用"
            priority = module_config.get('priority', 'N/A')
            print(f"- {module_name}: {status} (优先级: {priority})")

        return 0

    def run(self):
        """运行入口点"""
        parser = argparse.ArgumentParser(
            description='AI弹窗项目 Web脚本系统',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
使用示例:
  python entry.py orchestrate              # 编排执行所有脚本
  python entry.py api                      # 执行API管理
  python entry.py menu                     # 执行菜单管理
  python entry.py security                 # 执行安全验证
  python entry.py config get settings      # 获取配置
  python entry.py config set settings.debug_mode true  # 设置配置
  python entry.py status                   # 显示系统状态
            """
        )

        parser.add_argument('command', choices=list(self.commands.keys()),
                          help='要执行的命令')
        parser.add_argument('args', nargs='*',
                          help='命令参数')

        # 配置管理子命令
        if len(sys.argv) > 1 and sys.argv[1] == 'config':
            parser.add_argument('--action', choices=['get', 'set', 'reset'],
                              required=True, help='配置操作')
            parser.add_argument('--key', help='配置键')
            parser.add_argument('--value', help='配置值')

        args = parser.parse_args()

        # 设置全局日志
        setup_global_logging()

        # 执行命令
        if args.command in self.commands:
            command_info = self.commands[args.command]

            # 特殊处理config命令的参数
            if args.command == 'config':
                if not hasattr(args, 'action'):
                    parser.error("config命令需要--action参数")
                args.action = getattr(args, 'action', None)
                args.key = getattr(args, 'key', None)
                args.value = getattr(args, 'value', None)

            try:
                exit_code = command_info['handler'](args)
                sys.exit(exit_code)
            except Exception as e:
                self.logger.error(f"命令执行失败: {e}")
                sys.exit(1)
        else:
            parser.error(f"未知命令: {args.command}")

def main():
    """主函数"""
    entry = WebEntryPoint()
    entry.run()

if __name__ == "__main__":
    main()
