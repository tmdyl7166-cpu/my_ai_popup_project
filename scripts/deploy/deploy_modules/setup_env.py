#!/usr/bin/env python3
"""
部署系统功能模块
环境准备模块
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import subprocess
import sys
import os

from deploy_core.base import BaseDeployModule, DeployContext
from deploy_utils.logger import get_logger


class SetupEnvModule(BaseDeployModule):
    """环境准备模块"""
    
    def __init__(self, context: DeployContext):
        super().__init__("setup_env", context)
        self.project_root = context.project_root
        self.venv_name = "ai_popup_env"
        self.venv_path = self.project_root / self.venv_name
    
    def check_prerequisites(self) -> bool:
        """检查前置条件"""
        self.logger.info("检查环境准备前置条件")
        
        # 检查Python版本
        try:
            result = subprocess.run(
                [sys.executable, "--version"],
                capture_output=True,
                text=True
            )
            version = result.stdout.strip()
            self.logger.info(f"Python版本: {version}")
            
            # 解析版本号
            version_parts = version.split()[1].split(".")
            major, minor = int(version_parts[0]), int(version_parts[1])
            
            if major < 3 or (major == 3 and minor < 10):
                self.logger.error("Python版本需要3.10+")
                return False
                
        except Exception as e:
            self.logger.error(f"检查Python版本失败: {e}")
            return False
        
        # 检查必要的目录和文件
        required_paths = [
            self.project_root / "project_config.json",
            self.project_root / "requirements.txt"
        ]
        
        for path in required_paths:
            if not path.exists():
                self.logger.error(f"必要文件不存在: {path}")
                return False
        
        self.logger.info("前置条件检查通过")
        return True
    
    def execute(self) -> bool:
        """执行环境准备"""
        self.logger.info("开始执行环境准备")
        
        try:
            # 1. 创建虚拟环境
            if not self._create_virtualenv():
                return False
            
            # 2. 升级pip
            if not self._upgrade_pip():
                return False
            
            # 3. 创建必要的目录
            if not self._create_directories():
                return False
            
            # 4. 检查项目结构
            if not self._verify_project_structure():
                return False
            
            self.logger.info("环境准备完成")
            return True
            
        except Exception as e:
            self.logger.exception(f"环境准备异常: {e}")
            return False
    
    def _create_virtualenv(self) -> bool:
        """创建虚拟环境"""
        self.logger.info(f"创建虚拟环境: {self.venv_path}")
        
        try:
            if self.venv_path.exists():
                self.logger.info("虚拟环境已存在")
                return True
            
            result = subprocess.run(
                [sys.executable, "-m", "venv", str(self.venv_path)],
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode == 0:
                self.logger.info("虚拟环境创建成功")
                return True
            else:
                self.logger.error(f"虚拟环境创建失败: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("虚拟环境创建超时")
            return False
        except Exception as e:
            self.logger.error(f"创建虚拟环境异常: {e}")
            return False
    
    def _upgrade_pip(self) -> bool:
        """升级pip"""
        self.logger.info("升级pip")
        
        try:
            python_path = self.venv_path / "bin" / "python"
            if os.name == 'nt':
                python_path = self.venv_path / "Scripts" / "python.exe"
            
            result = subprocess.run(
                [str(python_path), "-m", "pip", "install", "--upgrade", "pip", "wheel", "setuptools"],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                self.logger.info("pip升级成功")
                return True
            else:
                self.logger.warning(f"pip升级失败: {result.stderr}")
                return True  # 不阻塞部署
            
        except Exception as e:
            self.logger.warning(f"pip升级异常: {e}")
            return True
    
    def _create_directories(self) -> bool:
        """创建必要的目录"""
        self.logger.info("创建必要的目录")
        
        directories = [
            self.project_root / "logs",
            self.project_root / "data",
            self.project_root / "assets" / "images" / "output",
            self.project_root / "assets" / "videos" / "output",
            self.project_root / "backup" / "deploy"
        ]
        
        try:
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
                self.logger.debug(f"创建目录: {directory}")
            
            self.logger.info("目录创建完成")
            return True
            
        except Exception as e:
            self.logger.error(f"创建目录失败: {e}")
            return False
    
    def _verify_project_structure(self) -> bool:
        """验证项目结构"""
        self.logger.info("验证项目结构")
        
        required_dirs = ["src", "assets", "rules", "scripts", "web"]
        required_files = ["project_config.json", "requirements.txt", "README.md"]
        
        # 检查目录
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                self.logger.error(f"必要目录不存在: {dir_path}")
                return False
        
        # 检查文件
        for file_name in required_files:
            file_path = self.project_root / file_name
            if not file_path.exists():
                self.logger.error(f"必要文件不存在: {file_path}")
                return False
        
        self.logger.info("项目结构验证通过")
        return True
    
    def rollback(self) -> bool:
        """回滚环境准备"""
        self.logger.info("回滚环境准备")
        
        try:
            # 注意：不删除虚拟环境，只清理创建的文件
            self.logger.info("环境准备回滚完成（虚拟环境保留）")
            return True
        except Exception as e:
            self.logger.error(f"回滚失败: {e}")
            return False

