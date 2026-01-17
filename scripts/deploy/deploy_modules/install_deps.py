#!/usr/bin/env python3
"""
部署系统功能模块
依赖安装模块
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import subprocess
import sys
import os

from deploy_core.base import BaseDeployModule, DeployContext
from deploy_utils.logger import get_logger


class InstallDepsModule(BaseDeployModule):
    """依赖安装模块"""
    
    def __init__(self, context: DeployContext):
        super().__init__("install_deps", context)
        self.project_root = context.project_root
        self.venv_name = "ai_popup_env"
        self.venv_path = self.project_root / self.venv_name
        self.installed_packages: List[str] = []
    
    def check_prerequisites(self) -> bool:
        """检查前置条件"""
        self.logger.info("检查依赖安装前置条件")
        
        # 检查虚拟环境
        if not self.venv_path.exists():
            self.logger.error("虚拟环境不存在，请先运行setup_env模块")
            return False
        
        # 检查Python可执行文件
        python_path = self.venv_path / "bin" / "python"
        if os.name == 'nt':
            python_path = self.venv_path / "Scripts" / "python.exe"
        
        if not python_path.exists():
            self.logger.error(f"Python可执行文件不存在: {python_path}")
            return False
        
        # 检查requirements.txt
        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            self.logger.error("requirements.txt不存在")
            return False
        
        self.logger.info("前置条件检查通过")
        return True
    
    def execute(self) -> bool:
        """执行依赖安装"""
        self.logger.info("开始执行依赖安装")
        
        try:
            # 1. 获取Python路径
            python_path = self._get_python_path()
            if not python_path:
                return False
            
            # 2. 读取依赖列表
            dependencies = self._load_dependencies()
            if not dependencies:
                self.logger.warning("没有需要安装的依赖")
                return True
            
            # 3. 安装主项目依赖
            if not self._install_main_dependencies(python_path, dependencies):
                return False
            
            # 4. 安装Web依赖
            if not self._install_web_dependencies(python_path):
                return False
            
            # 5. 验证安装结果
            if not self._verify_installation(python_path):
                return False
            
            self.logger.info("依赖安装完成")
            return True
            
        except Exception as e:
            self.logger.exception(f"依赖安装异常: {e}")
            return False
    
    def _get_python_path(self) -> Optional[Path]:
        """获取Python路径"""
        python_path = self.venv_path / "bin" / "python"
        if os.name == 'nt':
            python_path = self.venv_path / "Scripts" / "python.exe"
        
        if python_path.exists():
            return python_path
        
        self.logger.error(f"Python路径不存在: {python_path}")
        return None
    
    def _load_dependencies(self) -> List[str]:
        """加载依赖列表"""
        requirements_file = self.project_root / "requirements.txt"
        
        try:
            with open(requirements_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            dependencies = []
            for line in lines:
                line = line.strip()
                # 跳过注释和空行
                if line and not line.startswith('#'):
                    # 去除版本号
                    package = line.split('>=')[0].split('==')[0].split('[')[0].strip()
                    if package:
                        dependencies.append(package)
            
            return dependencies
            
        except Exception as e:
            self.logger.error(f"读取依赖文件失败: {e}")
            return []
    
    def _install_main_dependencies(self, python_path: Path, dependencies: List[str]) -> bool:
        """安装主项目依赖"""
        self.logger.info(f"安装 {len(dependencies)} 个主项目依赖")
        
        try:
            # 升级pip
            upgrade_result = subprocess.run(
                [str(python_path), "-m", "pip", "install", "--upgrade", "pip"],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if upgrade_result.returncode != 0:
                self.logger.warning(f"pip升级失败: {upgrade_result.stderr}")
            
            # 安装依赖
            result = subprocess.run(
                [str(python_path), "-m", "pip", "install", "-r", str(self.project_root / "requirements.txt")],
                capture_output=True,
                text=True,
                timeout=1800  # 30分钟超时
            )
            
            if result.returncode == 0:
                self.logger.info("主项目依赖安装成功")
                self.context.artifacts["main_deps_installed"] = True
                return True
            else:
                self.logger.error(f"依赖安装失败: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("依赖安装超时")
            return False
        except Exception as e:
            self.logger.error(f"安装依赖异常: {e}")
            return False
    
    def _install_web_dependencies(self, python_path: Path) -> bool:
        """安装Web依赖"""
        web_requirements = self.project_root / "web" / "requirements.txt"
        
        if not web_requirements.exists():
            self.logger.info("Web依赖文件不存在，跳过")
            return True
        
        self.logger.info("安装Web依赖")
        
        try:
            result = subprocess.run(
                [str(python_path), "-m", "pip", "install", "-r", str(web_requirements)],
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode == 0:
                self.logger.info("Web依赖安装成功")
                self.context.artifacts["web_deps_installed"] = True
                return True
            else:
                # 检查是否只是警告
                if "WARNING" in result.stderr:
                    self.logger.warning(f"Web依赖安装有警告: {result.stderr}")
                    return True
                self.logger.error(f"Web依赖安装失败: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"安装Web依赖异常: {e}")
            return False
    
    def _verify_installation(self, python_path: Path) -> bool:
        """验证安装结果"""
        self.logger.info("验证依赖安装结果")
        
        try:
            # 检查关键包
            critical_packages = [
                'fastapi', 'uvicorn', 'jinja2', 'psutil', 'python-socketio'
            ]
            
            missing = []
            for package in critical_packages:
                result = subprocess.run(
                    [str(python_path), "-c", f"import {package.replace('-', '_')}"],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    missing.append(package)
                    self.logger.warning(f"关键包未安装: {package}")
            
            if missing:
                self.logger.warning(f"缺少 {len(missing)} 个关键包")
                self.context.artifacts["missing_packages"] = missing
            
            # 检查已安装的包数量
            result = subprocess.run(
                [str(python_path), "-m", "pip", "list", "--format=freeze"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                installed_count = len(result.stdout.strip().split('\n'))
                self.logger.info(f"已安装 {installed_count} 个包")
                self.context.artifacts["installed_count"] = installed_count
            
            return True
            
        except Exception as e:
            self.logger.error(f"验证安装结果异常: {e}")
            return False
    
    def rollback(self) -> bool:
        """回滚依赖安装"""
        self.logger.info("回滚依赖安装")
        
        try:
            # 依赖安装通常不需要回滚，因为卸载可能导致问题
            self.logger.info("依赖安装已保留（不建议回滚依赖）")
            return True
        except Exception as e:
            self.logger.error(f"回滚失败: {e}")
            return False

