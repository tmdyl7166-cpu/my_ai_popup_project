#!/usr/bin/env python3
"""
部署系统功能模块
应用构建模块
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import subprocess
import sys
import os
import shutil

from deploy_core.base import BaseDeployModule, DeployContext


class BuildAppModule(BaseDeployModule):
    """应用构建模块"""
    
    def __init__(self, context: DeployContext):
        super().__init__("build_app", context)
        self.project_root = context.project_root
        self.build_output = self.project_root / "dist"
    
    def check_prerequisites(self) -> bool:
        """检查前置条件"""
        self.logger.info("检查应用构建前置条件")
        
        # 检查项目结构
        required_dirs = ["src", "web"]
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                self.logger.error(f"必要目录不存在: {dir_path}")
                return False
        
        self.logger.info("前置条件检查通过")
        return True
    
    def execute(self) -> bool:
        """执行应用构建"""
        self.logger.info("开始执行应用构建")
        
        try:
            # 1. 清理构建目录
            if not self._clean_build_dir():
                return False
            
            # 2. 复制Web静态文件
            if not self._copy_web_static():
                return False
            
            # 3. 验证Web界面
            if not self._verify_web_ui():
                return False
            
            # 4. 生成构建清单
            if not self._generate_build_manifest():
                return False
            
            self.logger.info("应用构建完成")
            return True
            
        except Exception as e:
            self.logger.exception(f"应用构建异常: {e}")
            return False
    
    def _clean_build_dir(self) -> bool:
        """清理构建目录"""
        self.logger.info("清理构建目录")
        
        try:
            if self.build_output.exists():
                shutil.rmtree(self.build_output)
            
            self.build_output.mkdir(parents=True, exist_ok=True)
            
            # 创建必要子目录
            (self.build_output / "static").mkdir(exist_ok=True)
            (self.build_output / "templates").mkdir(exist_ok=True)
            
            self.logger.info("构建目录已清理")
            return True
            
        except Exception as e:
            self.logger.error(f"清理构建目录失败: {e}")
            return False
    
    def _copy_web_static(self) -> bool:
        """复制Web静态文件"""
        self.logger.info("复制Web静态文件")
        
        try:
            web_static = self.project_root / "web" / "static"
            output_static = self.build_output / "static"
            
            if web_static.exists():
                shutil.copytree(web_static, output_static, dirs_exist_ok=True)
                self.logger.info("静态文件已复制")
            
            return True
            
        except Exception as e:
            self.logger.error(f"复制静态文件失败: {e}")
            return False
    
    def _verify_web_ui(self) -> bool:
        """验证Web界面"""
        self.logger.info("验证Web界面")
        
        try:
            required_files = [
                self.project_root / "web" / "templates" / "dashboard.html",
                self.project_root / "web" / "static" / "js" / "app.js"
            ]
            
            for file_path in required_files:
                if not file_path.exists():
                    self.logger.warning(f"Web文件不存在: {file_path}")
            
            self.logger.info("Web界面验证完成")
            return True
            
        except Exception as e:
            self.logger.error(f"验证Web界面失败: {e}")
            return False
    
    def _generate_build_manifest(self) -> bool:
        """生成构建清单"""
        self.logger.info("生成构建清单")
        
        try:
            manifest = {
                "build_time": datetime.now().isoformat(),
                "project_root": str(self.project_root),
                "output_dir": str(self.build_output),
                "files": []
            }
            
            # 列出构建的文件
            for file_path in self.build_output.rglob("*"):
                if file_path.is_file():
                    manifest["files"].append({
                        "path": str(file_path.relative_to(self.build_output)),
                        "size": file_path.stat().st_size
                    })
            
            # 保存清单
            manifest_path = self.build_output / "manifest.json"
            import json
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            
            self.context.artifacts["build_manifest"] = str(manifest_path)
            self.logger.info(f"构建清单已生成: {manifest_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"生成构建清单失败: {e}")
            return False
    
    def rollback(self) -> bool:
        """回滚应用构建"""
        self.logger.info("回滚应用构建")
        
        try:
            if self.build_output.exists():
                shutil.rmtree(self.build_output)
            self.logger.info("构建产物已清理")
            return True
        except Exception as e:
            self.logger.error(f"回滚失败: {e}")
            return False

