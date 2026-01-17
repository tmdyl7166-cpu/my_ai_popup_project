#!/usr/bin/env python3
"""
部署系统功能模块
健康检查模块
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import subprocess
import sys
import os
import socket
import json

from deploy_core.base import BaseDeployModule, DeployContext
from deploy_utils.logger import get_logger


class HealthCheckModule(BaseDeployModule):
    """健康检查模块"""
    
    def __init__(self, context: DeployContext):
        super().__init__("health_check", context)
        self.project_root = context.project_root
        self.venv_name = "ai_popup_env"
        self.venv_path = self.project_root / self.venv_name
        self.health_results: Dict[str, Any] = {}
    
    def check_prerequisites(self) -> bool:
        """检查前置条件"""
        self.logger.info("检查健康检查前置条件")
        
        # 检查Python
        try:
            result = subprocess.run(
                [sys.executable, "--version"],
                capture_output=True,
                text=True
            )
            self.logger.info(f"Python版本: {result.stdout.strip()}")
        except Exception as e:
            self.logger.error(f"检查Python失败: {e}")
            return False
        
        self.logger.info("前置条件检查通过")
        return True
    
    def execute(self) -> bool:
        """执行健康检查"""
        self.logger.info("开始执行健康检查")
        
        try:
            # 1. 检查Python环境
            python_ok = self._check_python_environment()
            
            # 2. 检查关键依赖
            deps_ok = self._check_dependencies()
            
            # 3. 检查项目结构
            structure_ok = self._check_project_structure()
            
            # 4. 检查服务端口
            ports_ok = self._check_ports()
            
            # 5. 检查配置文件
            config_ok = self._check_configurations()
            
            # 生成健康报告
            self._generate_health_report()
            
            # 计算整体状态
            all_checks = [
                ("python", python_ok),
                ("dependencies", deps_ok),
                ("structure", structure_ok),
                ("ports", ports_ok),
                ("config", config_ok)
            ]
            
            passed = sum(1 for _, ok in all_checks if ok)
            total = len(all_checks)
            
            self.context.artifacts["health_check"] = {
                "passed": passed,
                "total": total,
                "success_rate": passed / total * 100 if total > 0 else 0,
                "details": self.health_results
            }
            
            self.logger.info(f"健康检查完成: {passed}/{total} 通过")
            return passed == total or passed >= total * 0.8  # 80%通过率
            
        except Exception as e:
            self.logger.exception(f"健康检查异常: {e}")
            self.context.artifacts["health_check"] = {"error": str(e)}
            return False
    
    def _check_python_environment(self) -> bool:
        """检查Python环境"""
        self.logger.info("检查Python环境")
        
        checks = {
            "version": False,
            "venv_exists": False,
            "pip_available": False
        }
        
        try:
            # 检查版本
            if sys.version_info >= (3, 10):
                checks["version"] = True
                self.logger.info("Python版本满足要求")
            else:
                self.logger.warning("Python版本过低")
            
            # 检查虚拟环境
            if self.venv_path.exists():
                checks["venv_exists"] = True
                self.logger.info("虚拟环境存在")
            
            # 检查pip
            result = subprocess.run(
                [sys.executable, "-m", "pip", "--version"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                checks["pip_available"] = True
                self.logger.info("pip可用")
            
        except Exception as e:
            self.logger.error(f"检查Python环境异常: {e}")
        
        self.health_results["python"] = checks
        return all(checks.values())
    
    def _check_dependencies(self) -> bool:
        """检查关键依赖"""
        self.logger.info("检查关键依赖")
        
        critical_deps = [
            'fastapi', 'uvicorn', 'jinja2', 'psutil', 
            'python_socketio', 'socketio', 'python-multipart'
        ]
        
        results = {}
        
        for dep in critical_deps:
            module_name = dep.replace('-', '_')
            try:
                __import__(module_name)
                results[dep] = True
            except ImportError:
                results[dep] = False
                self.logger.warning(f"依赖缺失: {dep}")
        
        # 检查可选依赖
        optional_deps = ['opencv-python', 'torch', 'tensorflow']
        for dep in optional_deps:
            module_name = dep.replace('-', '_').replace('_', '')
            try:
                __import__(module_name)
                results[dep] = True
            except ImportError:
                results[dep] = False
        
        self.health_results["dependencies"] = results
        
        # 关键依赖必须全部通过
        critical_passed = all(results.get(dep, False) for dep in critical_deps if dep in results)
        return critical_passed
    
    def _check_project_structure(self) -> bool:
        """检查项目结构"""
        self.logger.info("检查项目结构")
        
        required_dirs = ["src", "assets", "rules", "scripts", "web", "logs"]
        required_files = [
            "project_config.json", "requirements.txt", 
            "README.md", "web/app.py"
        ]
        
        results = {}
        
        for dir_name in required_dirs:
            path = self.project_root / dir_name
            results[f"dir_{dir_name}"] = path.exists()
        
        for file_name in required_files:
            path = self.project_root / file_name
            results[f"file_{file_name}"] = path.exists()
        
        self.health_results["structure"] = results
        
        # 检查是否有缺失的必要项
        missing = [k for k, v in results.items() if not v]
        
        if missing:
            self.logger.warning(f"项目结构缺失: {missing}")
        
        # 只要求关键项存在
        critical_files = ["project_config.json", "requirements.txt", "web/app.py"]
        critical_passed = all(results.get(f"file_{f}", False) for f in critical_files)
        
        return critical_passed
    
    def _check_ports(self) -> bool:
        """检查服务端口"""
        self.logger.info("检查服务端口")
        
        ports_to_check = [
            (8000, "Backend API"),
            (8080, "Web Monitor")
        ]
        
        results = {}
        
        for port, name in ports_to_check:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                
                is_used = result == 0
                results[f"port_{port}"] = {
                    "port": port,
                    "service": name,
                    "in_use": is_used
                }
                
                if is_used:
                    self.logger.info(f"端口 {port} ({name}) 已被占用")
                else:
                    self.logger.info(f"端口 {port} ({name}) 可用")
                    
            except Exception as e:
                results[f"port_{port}"] = {
                    "port": port,
                    "service": name,
                    "error": str(e)
                }
        
        self.health_results["ports"] = results
        return True  # 端口检查不影响整体状态
    
    def _check_configurations(self) -> bool:
        """检查配置文件"""
        self.logger.info("检查配置文件")
        
        config_files = [
            "project_config.json",
            "web/web_config.json",
            "scripts/scripts_config.json"
        ]
        
        results = {}
        
        for config_file in config_files:
            path = self.project_root / config_file
            
            if path.exists():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    
                    results[config_file] = {
                        "exists": True,
                        "valid_json": True,
                        "has_meta": "meta" in config
                    }
                    
                except json.JSONDecodeError as e:
                    results[config_file] = {
                        "exists": True,
                        "valid_json": False,
                        "error": str(e)
                    }
                    self.logger.error(f"配置文件JSON格式错误: {config_file}")
            else:
                results[config_file] = {
                    "exists": False
                }
        
        self.health_results["config"] = results
        
        # 检查关键配置文件
        critical_configs = ["project_config.json", "web/web_config.json"]
        critical_passed = all(
            results.get(cfg, {}).get("exists", False) 
            for cfg in critical_configs
        )
        
        return critical_passed
    
    def _generate_health_report(self) -> None:
        """生成健康报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "checks": self.health_results,
            "summary": {
                "status": "healthy" if self.context.artifacts.get("health_check", {}).get("success_rate", 0) >= 80 else "degraded"
            }
        }
        
        # 保存报告
        report_path = self.project_root / "logs" / "health_report.json"
        try:
            report_path.parent.mkdir(parents=True, exist_ok=True)
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"健康报告已保存: {report_path}")
        except Exception as e:
            self.logger.error(f"保存健康报告失败: {e}")
    
    def rollback(self) -> bool:
        """回滚健康检查"""
        self.logger.info("健康检查无需回滚")
        return True

