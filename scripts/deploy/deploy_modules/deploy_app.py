#!/usr/bin/env python3
"""
部署系统功能模块
应用部署模块
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import subprocess
import sys
import os
import signal

from deploy_core.base import BaseDeployModule, DeployContext
from deploy_utils.logger import get_logger


class DeployAppModule(BaseDeployModule):
    """应用部署模块"""
    
    def __init__(self, context: DeployContext):
        super().__init__("deploy_app", context)
        self.project_root = context.project_root
        self.venv_path = self.project_root / "ai_popup_env"
        self.pid_file = self.project_root / "logs" / "service_pids.txt"
        self.services: List[Dict[str, Any]] = []
    
    def check_prerequisites(self) -> bool:
        """检查前置条件"""
        self.logger.info("检查应用部署前置条件")
        
        # 检查虚拟环境
        if not self.venv_path.exists():
            self.logger.warning("虚拟环境不存在，将尝试使用系统Python")
        
        # 检查Web应用
        web_app = self.project_root / "web" / "app.py"
        if not web_app.exists():
            self.logger.error("Web应用不存在")
            return False
        
        self.logger.info("前置条件检查通过")
        return True
    
    def execute(self) -> bool:
        """执行应用部署"""
        self.logger.info("开始执行应用部署")
        
        try:
            # 1. 停止现有服务
            if not self._stop_existing_services():
                self.logger.warning("停止现有服务时出现问题")
            
            # 2. 启动Web服务
            if not self._start_web_service():
                return False
            
            # 3. 保存服务PID
            if not self._save_service_pids():
                return False
            
            # 4. 验证服务状态
            if not self._verify_services():
                return False
            
            self.logger.info("应用部署完成")
            return True
            
        except Exception as e:
            self.logger.exception(f"应用部署异常: {e}")
            return False
    
    def _stop_existing_services(self) -> bool:
        """停止现有服务"""
        self.logger.info("停止现有服务")
        
        try:
            if self.pid_file.exists():
                with open(self.pid_file, 'r') as f:
                    pids = f.read().strip().split()
                
                for pid in pids:
                    try:
                        pid = int(pid)
                        os.kill(pid, signal.SIGTERM)
                        self.logger.info(f"已停止服务 PID: {pid}")
                    except (ProcessLookupError, ValueError):
                        pass
                
                # 清理PID文件
                self.pid_file.unlink()
            
            # 额外检查常见端口
            ports = [8000, 8080]
            for port in ports:
                result = subprocess.run(
                    f'lsof -ti:{port} | xargs kill -9 2>/dev/null',
                    shell=True,
                    capture_output=True
                )
            
            return True
            
        except Exception as e:
            self.logger.error(f"停止服务失败: {e}")
            return False
    
    def _start_web_service(self) -> bool:
        """启动Web服务"""
        self.logger.info("启动Web服务")
        
        try:
            log_dir = self.project_root / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # 使用nohup启动
            python_path = self.venv_path / "bin" / "python" if not os.name == 'nt' else self.venv_path / "Scripts" / "python.exe"
            
            # 如果虚拟环境不存在，使用系统Python
            if not python_path.exists():
                python_path = sys.executable
            
            # 构建命令
            cmd = [
                str(python_path),
                str(self.project_root / "web" / "start_monitor.py"),
                "--host", "0.0.0.0",
                "--port", "8080"
            ]
            
            # 使用subprocess启动
            self.process = subprocess.Popen(
                cmd,
                stdout=open(log_dir / "web_service.log", 'w'),
                stderr=open(log_dir / "web_service_error.log", 'w'),
                cwd=str(self.project_root)
            )
            
            self.services.append({
                "name": "web_monitor",
                "process": self.process,
                "port": 8080
            })
            
            self.logger.info(f"Web服务已启动 (PID: {self.process.pid})")
            
            # 等待服务启动
            import time
            time.sleep(3)
            
            return True
            
        except Exception as e:
            self.logger.error(f"启动Web服务失败: {e}")
            return False
    
    def _save_service_pids(self) -> bool:
        """保存服务PID"""
        self.logger.info("保存服务PID")
        
        try:
            pids = []
            for service in self.services:
                if service.get("process"):
                    pids.append(str(service["process"].pid))
            
            if pids:
                self.pid_file.parent.mkdir(parents=True, exist_ok=True)
                with open(self.pid_file, 'w') as f:
                    f.write(" ".join(pids))
                
                self.context.artifacts["service_pids"] = pids
            
            return True
            
        except Exception as e:
            self.logger.error(f"保存PID失败: {e}")
            return False
    
    def _verify_services(self) -> bool:
        """验证服务状态"""
        self.logger.info("验证服务状态")
        
        try:
            import socket
            
            all_ok = True
            for service in self.services:
                port = service.get("port")
                name = service.get("name")
                
                # 检查端口是否监听
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                
                if result == 0:
                    self.logger.info(f"服务 {name} 端口 {port} 已就绪")
                else:
                    self.logger.warning(f"服务 {name} 端口 {port} 未响应")
                    all_ok = False
            
            # 检查健康端点
            import urllib.request
            try:
                response = urllib.request.urlopen('http://localhost:8080/api/health', timeout=5)
                if response.status == 200:
                    self.logger.info("健康检查端点正常")
            except Exception as e:
                self.logger.warning(f"健康检查失败: {e}")
            
            return all_ok
            
        except Exception as e:
            self.logger.error(f"验证服务失败: {e}")
            return False
    
    def rollback(self) -> bool:
        """回滚应用部署"""
        self.logger.info("回滚应用部署")
        
        try:
            # 停止所有服务
            self._stop_existing_services()
            
            # 清理PID文件
            if self.pid_file.exists():
                self.pid_file.unlink()
            
            self.logger.info("应用部署已回滚")
            return True
        except Exception as e:
            self.logger.error(f"回滚失败: {e}")
            return False

