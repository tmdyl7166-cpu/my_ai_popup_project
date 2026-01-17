#!/usr/bin/env python3
"""
Web编排器脚本
统一管理所有web相关脚本的执行和调度，作为主入口点
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.utils.logging_utils import get_script_logger
from scripts.utils.file_utils import read_json, write_json

class WebOrchestrator:
    """Web编排器"""

    def __init__(self):
        self.logger = get_script_logger("web_orchestrator")
        self.project_root = project_root
        self.orchestrator_config_path = self.project_root / "scripts" / "web" / "orchestrator_config.json"
        self.scripts_config_path = self.project_root / "scripts" / "scripts_config.json"
        
        # 注册可用的脚本模块
        self.available_scripts = {
            "api_manager": {
                "module": "api_manager",
                "description": "API管理和跨域处理",
                "dependencies": []
            },
            "menu_manager": {
                "module": "menu_manager",
                "description": "菜单互动性和结构管理",
                "dependencies": []
            },
            "security_validator": {
                "module": "security_validator",
                "description": "安全验证和漏洞检测",
                "dependencies": []
            }
        }

    def load_orchestrator_config(self) -> Dict[str, Any]:
        """加载编排器配置"""
        try:
            if self.orchestrator_config_path.exists():
                return read_json(self.orchestrator_config_path)
            else:
                # 创建默认编排器配置
                default_config = {
                    "orchestration": {
                        "execution_sequence": ["api_manager", "menu_manager", "security_validator"],
                        "parallel_execution": False,
                        "dependencies": {},
                        "timeout": 300,
                        "retry_attempts": 3
                    },
                    "monitoring": {
                        "enable_logging": True,
                        "log_level": "INFO",
                        "report_generation": True,
                        "performance_tracking": True
                    },
                    "web_interface": {
                        "dashboard_enabled": True,
                        "real_time_updates": True,
                        "interactive_controls": True,
                        "responsive_design": True
                    }
                }
                write_json(self.orchestrator_config_path, default_config)
                return default_config
        except Exception as e:
            self.logger.error(f"加载编排器配置失败: {e}")
            return {}

    def execute_script(self, script_name: str) -> Dict[str, Any]:
        """执行单个脚本"""
        if script_name not in self.available_scripts:
            return {"success": False, "error": f"脚本不存在: {script_name}"}

        script_info = self.available_scripts[script_name]
        script_path = Path(__file__).parent / f"{script_info['module']}.py"
        
        if not script_path.exists():
            return {"success": False, "error": f"脚本文件不存在: {script_path}"}

        try:
            self.logger.info(f"执行脚本: {script_name}")
            
            # 动态导入并执行脚本
            sys.path.insert(0, str(Path(__file__).parent))
            script_module = __import__(script_info['module'])
            
            # 执行脚本的run方法
            if hasattr(script_module, script_info['module'].title().replace("_", "")):
                script_class = getattr(script_module, script_info['module'].title().replace("_", ""))
                instance = script_class()
                if hasattr(instance, 'run'):
                    instance.run()
                    return {"success": True, "script": script_name, "output": "执行成功"}
            
            return {"success": True, "script": script_name, "output": "脚本执行完成"}
            
        except Exception as e:
            error_msg = f"执行脚本失败 {script_name}: {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}

    def orchestrate_execution(self, script_names: List[str] = None) -> Dict[str, Any]:
        """编排执行多个脚本"""
        config = self.load_orchestrator_config()
        
        if script_names is None:
            script_names = config.get("orchestration", {}).get("execution_sequence", [])
        
        orchestration_report = {
            "total_scripts": len(script_names),
            "successful_scripts": [],
            "failed_scripts": [],
            "execution_times": {},
            "start_time": datetime.now(),
            "end_time": None,
            "overall_status": "pending"
        }

        self.logger.info(f"开始编排执行 {len(script_names)} 个脚本")

        for script_name in script_names:
            if script_name not in self.available_scripts:
                orchestration_report["failed_scripts"].append({
                    "script": script_name,
                    "error": "脚本不可用",
                    "timestamp": datetime.now()
                })
                continue

            start_time = datetime.now()
            result = self.execute_script(script_name)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            orchestration_report["execution_times"][script_name] = execution_time
            
            if result["success"]:
                orchestration_report["successful_scripts"].append({
                    "script": script_name,
                    "execution_time": execution_time,
                    "timestamp": datetime.now()
                })
            else:
                orchestration_report["failed_scripts"].append({
                    "script": script_name,
                    "error": result.get("error", "未知错误"),
                    "execution_time": execution_time,
                    "timestamp": datetime.now()
                })

        orchestration_report["end_time"] = datetime.now()
        orchestration_report["total_execution_time"] = (
            orchestration_report["end_time"] - orchestration_report["start_time"]
        ).total_seconds()
        
        # 确定整体状态
        if len(orchestration_report["successful_scripts"]) == len(script_names):
            orchestration_report["overall_status"] = "success"
        elif len(orchestration_report["failed_scripts"]) == len(script_names):
            orchestration_report["overall_status"] = "failed"
        else:
            orchestration_report["overall_status"] = "partial_success"

        return orchestration_report

    def generate_unified_config(self) -> Dict[str, Any]:
        """生成统一的配置"""
        unified_config = {
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "components": {},
            "dependencies": {},
            "api_endpoints": {},
            "security_policies": {},
            "performance_settings": {}
        }

        # 收集各脚本的配置信息
        for script_name in self.available_scripts.keys():
            script_config_path = self.project_root / "scripts" / "web" / f"{script_name}_config.json"
            if script_config_path.exists():
                try:
                    script_config = read_json(script_config_path)
                    unified_config["components"][script_name] = script_config
                except Exception as e:
                    self.logger.warning(f"加载脚本配置失败 {script_name}: {e}")

        # 读取项目级配置
        project_config_path = self.project_root / "project_config.json"
        if project_config_path.exists():
            try:
                project_config = read_json(project_config_path)
                unified_config["project"] = project_config
            except Exception as e:
                self.logger.warning(f"加载项目配置失败: {e}")

        return unified_config

    def list_available_scripts(self) -> List[str]:
        """列出可用的脚本"""
        return list(self.available_scripts.keys())

    def get_script_info(self, script_name: str) -> Optional[Dict[str, Any]]:
        """获取脚本信息"""
        return self.available_scripts.get(script_name)

    def run(self, scripts_to_run: List[str] = None):
        """运行编排器"""
        self.logger.info("Web编排器启动")
        
        print("=" * 50)
        print("🚀 AI弹窗项目 Web编排器")
        print("=" * 50)
        
        if scripts_to_run:
            print(f"执行指定脚本: {', '.join(scripts_to_run)}")
        else:
            print("执行默认脚本序列")

        # 编排执行
        orchestration_result = self.orchestrate_execution(scripts_to_run)
        
        print("\n" + "=" * 50)
        print("📊 编排执行报告")
        print("=" * 50)
        
        print(f"总脚本数: {orchestration_result['total_scripts']}")
        print(f"成功执行: {len(orchestration_result['successful_scripts'])}")
        print(f"失败执行: {len(orchestration_result['failed_scripts'])}")
        print(f"总执行时间: {orchestration_result['total_execution_time']:.2f}秒")
        print(f"总体状态: {orchestration_result['overall_status']}")
        
        # 显示详细执行时间
        print("\n执行时间详情:")
        for script_name, exec_time in orchestration_result["execution_times"].items():
            print(f"- {script_name}: {exec_time:.2f}秒")
        
        # 显示失败详情
        if orchestration_result["failed_scripts"]:
            print("\n❌ 失败详情:")
            for failed_script in orchestration_result["failed_scripts"]:
                print(f"- {failed_script['script']}: {failed_script['error']}")

        # 生成统一配置
        unified_config = self.generate_unified_config()
        unified_config_path = self.project_root / "scripts" / "web" / "unified_config.json"
        write_json(unified_config_path, unified_config)
        
        print(f"\n✅ 统一配置文件已生成: {unified_config_path}")
        
        self.logger.info("Web编排器运行完成")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AI弹窗项目 Web编排器')
    parser.add_argument('--scripts', nargs='+', help='要执行的脚本名称')
    parser.add_argument('--list', action='store_true', help='列出可用的脚本')
    parser.add_argument('--info', help='显示指定脚本的详细信息')
    parser.add_argument('--generate-config', action='store_true', help='生成统一配置')

    args = parser.parse_args()

    orchestrator = WebOrchestrator()

    if args.list:
        scripts = orchestrator.list_available_scripts()
        print("可用的脚本:")
        for script in scripts:
            info = orchestrator.get_script_info(script)
            print(f"- {script}: {info['description']}")
        return

    if args.info:
        info = orchestrator.get_script_info(args.info)
        if info:
            print(f"脚本信息: {args.info}")
            for key, value in info.items():
                print(f"  {key}: {value}")
        else:
            print(f"脚本不存在: {args.info}")
        return

    if args.generate_config:
        unified_config = orchestrator.generate_unified_config()
        unified_config_path = orchestrator.project_root / "scripts" / "web" / "unified_config.json"
        write_json(unified_config_path, unified_config)
        print(f"统一配置文件已生成: {unified_config_path}")
        return

    # 执行编排
    orchestrator.run(args.scripts)

if __name__ == "__main__":
    main()
