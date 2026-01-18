#!/usr/bin/env python3
"""
AI弹窗项目 - 统一启动器 (优化版)
基于全局联通性设计原则

全局联通性设计原则:
1. 职责划分: 每个模块具有单一明确的功能
2. 接口标准化: REST API统一的响应格式
3. 数据共享: 统一数据格式和状态码
4. 顺序控制: 后端启动后才能启动Web
5. 异常处理: 全局异常处理和重试机制
6. 配置管理: 外部配置文件
7. 日志监控: 集中化管理
8. 安全性: 权限控制和数据保护

使用方式:
    python unified_launcher.py --mode all          # 启动所有模块
    python unified_launcher.py --mode sequential   # 按顺序启动
    python unified_launcher.py --mode web          # 启动Web监控
    python unified_launcher.py --mode check        # 健康检查
"""
import sys
import os
import argparse
import subprocess
import signal
import time
import json
import logging
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

# ========================================
# 统一配置管理
# ========================================
class ConfigManager:
    """配置管理器 - 集中管理所有配置"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """加载配置文件"""
        self.project_root = Path(__file__).parent.parent
        self.config = {}
        
        # 加载项目配置
        config_file = self.project_root / 'project_config.json'
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                self.config.update(json.load(f))
        
        # 加载环境变量
        self.config['env'] = os.environ.get('AI_POPUP_ENV', 'development')
        self.config['debug'] = os.environ.get('AI_POPUP_DEBUG', 'false').lower() == 'true'
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self.config.get(key, default)
    
    def get_module_config(self, module_name: str) -> Dict:
        """获取模块特定配置"""
        return self.config.get('modules', {}).get(module_name, {})


# ========================================
# 统一响应格式
# ========================================
class ResponseStatus(Enum):
    """响应状态枚举"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    PENDING = "pending"


@dataclass
class UnifiedResponse:
    """统一响应格式"""
    status: str
    message: str
    data: Dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    error_code: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "status": self.status,
            "message": self.message,
            "data": self.data,
            "timestamp": self.timestamp,
            "error_code": self.error_code
        }
    
    def to_json(self) -> str:
        """转换为JSON"""
        return json.dumps(self.to_dict(), ensure_ascii=False)
    
    @classmethod
    def success(cls, message: str, data: Dict = None) -> 'UnifiedResponse':
        """成功响应"""
        return cls(status=ResponseStatus.SUCCESS.value, message=message, data=data or {})
    
    @classmethod
    def error(cls, message: str, error_code: str = None, data: Dict = None) -> 'UnifiedResponse':
        """错误响应"""
        return cls(status=ResponseStatus.ERROR.value, message=message, 
                   data=data or {}, error_code=error_code)
    
    @classmethod
    def warning(cls, message: str, data: Dict = None) -> 'UnifiedResponse':
        """警告响应"""
        return cls(status=ResponseStatus.WARNING.value, message=message, data=data or {})


# ========================================
# 日志管理器
# ========================================
class LogManager:
    """日志管理器 - 集中化管理日志"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_logger()
        return cls._instance
    
    def _init_logger(self):
        """初始化日志器"""
        self.project_root = Path(__file__).parent.parent
        self.log_dir = self.project_root / 'logs'
        self.log_dir.mkdir(exist_ok=True)
        
        # 创建日志文件
        log_file = self.log_dir / f"launcher_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        self.logger = logging.getLogger('UnifiedLauncher')
        self.logger.setLevel(logging.DEBUG)
        
        # 文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 格式化
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def get_logger(self) -> logging.Logger:
        """获取日志器"""
        return self.logger
    
    def log_operation(self, operation: str, status: str, details: Dict = None):
        """记录操作日志"""
        self.logger.info(f"[{status}] {operation} | Details: {details or {}}")


# ========================================
# 健康检查器
# ========================================
class HealthChecker:
    """健康检查器 - 验证服务状态"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.logger = LogManager().get_logger()
    
    def check_port(self, port: int, timeout: int = 5) -> bool:
        """检查端口是否开放"""
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        try:
            result = sock.connect_ex(('127.0.0.1', port))
            return result == 0
        except Exception as e:
            self.logger.error(f"端口检查失败: {e}")
            return False
        finally:
            sock.close()
    
    def check_api_health(self, port: int, endpoint: str = '/api/health') -> bool:
        """检查API健康状态"""
        import urllib.request
        import json
        
        url = f"http://127.0.0.1:{port}{endpoint}"
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data.get('status') == 'healthy'
        except Exception as e:
            self.logger.error(f"API健康检查失败: {e}")
            return False
    
    def check_process(self, process_name: str) -> bool:
        """检查进程是否运行"""
        try:
            result = subprocess.run(
                ['pgrep', '-f', process_name],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"进程检查失败: {e}")
            return False
    
    def wait_for_service(self, port: int, max_retries: int = 10, 
                         delay: float = 1.0) -> tuple:
        """等待服务启动"""
        for attempt in range(max_retries):
            if self.check_port(port):
                return True, f"服务已在端口 {port} 启动"
            
            if attempt < max_retries - 1:
                time.sleep(delay)
        
        return False, f"服务在端口 {port} 启动超时"


# ========================================
# 进程管理器
# ========================================
class ProcessInfo:
    """进程信息"""
    def __init__(self, name: str, pid: int, script: str, 
                 start_time: datetime, status: str = 'running'):
        self.name = name
        self.pid = pid
        self.script = script
        self.start_time = start_time
        self.status = status
        self.restart_count = 0


class ProcessManager:
    """进程管理器 - 负责任务调度和进程管理"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.processes: Dict[str, ProcessInfo] = {}
        self.running_processes: Dict[str, subprocess.Popen] = {}
        self.logger = LogManager().get_logger()
        self.health_checker = HealthChecker()
        self._get_python_path()
    
    def _get_python_path(self):
        """获取Python解释器路径 - 增强检测逻辑"""
        project_root = self.project_root
        
        # 虚拟环境路径
        venv_python = project_root / '.venv' / 'bin' / 'python3'
        venv_python_fallback = project_root / '.venv' / 'bin' / 'python'
        
        # 1. 检查虚拟环境是否存在且有效
        if venv_python.exists():
            self.python_path = str(venv_python)
            self.logger.info(f"使用虚拟环境: {self.python_path}")
            return
        
        if venv_python_fallback.exists():
            self.python_path = str(venv_python_fallback)
            self.logger.info(f"使用虚拟环境: {self.python_path}")
            return
        
        # 2. 检查虚拟环境目录结构是否有效
        venv_lib = project_root / '.venv' / 'lib'
        if (project_root / '.venv').exists() and venv_lib.exists():
            # 虚拟环境目录存在但损坏，尝试查找版本目录
            python_dirs = list(venv_lib.glob("python*"))
            if python_dirs:
                for py_dir in python_dirs:
                    bin_path = py_dir / 'bin' / 'python3'
                    if bin_path.exists():
                        self.python_path = str(bin_path)
                        self.logger.info(f"使用虚拟环境 (版本目录): {self.python_path}")
                        return
        
        # 3. 回退到系统 Python
        self.python_path = sys.executable
        self.logger.warning(f"虚拟环境无效，使用系统 Python: {self.python_path}")
    
    def _get_environment(self, extra_env: Dict = None) -> Dict:
        """获取环境变量"""
        env = os.environ.copy()
        env['PYTHONPATH'] = f"{self.project_root}:{self.project_root}/src"
        env['AI_POPUP_ENV'] = 'development'
        env['AI_POPUP_LAUNCHER'] = 'true'
        env['PYTHONUNBUFFERED'] = '1'
        
        if extra_env:
            env.update(extra_env)
        
        return env
    
    def start_process(self, name: str, script: str, 
                      args: List[str] = None, 
                      env: Dict = None,
                      cwd: Path = None,
                      wait_for_health: bool = False,
                      health_port: int = None) -> UnifiedResponse:
        """启动进程 (统一响应格式)"""
        try:
            # 检查是否已运行
            if name in self.running_processes and self._is_process_running(name):
                return UnifiedResponse.warning(f"进程 {name} 已在运行")
            
            # 构建命令
            cmd = [self.python_path, str(script)] + (args or [])
            
            # 设置环境变量
            process_env = self._get_environment(env)
            
            # 设置工作目录
            work_dir = cwd or self.project_root
            
            self.logger.info(f"启动进程: {name}")
            self.logger.info(f"命令: {' '.join(cmd)}")
            
            # 启动进程
            process = subprocess.Popen(
                cmd,
                env=process_env,
                cwd=str(work_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                preexec_fn=os.setsid if os.name != 'nt' else None
            )
            
            # 记录进程信息
            self.running_processes[name] = process
            self.processes[name] = ProcessInfo(
                name=name,
                pid=process.pid,
                script=str(script),
                start_time=datetime.now()
            )
            
            self.logger.info(f"进程已启动: {name} (PID: {process.pid})")
            
            # 如果需要等待健康检查
            if wait_for_health and health_port:
                success, message = self.health_checker.wait_for_service(health_port)
                if not success:
                    return UnifiedResponse.error(
                        f"进程 {name} 启动失败: {message}",
                        error_code="HEALTH_CHECK_FAILED"
                    )
            
            return UnifiedResponse.success(
                f"进程 {name} 启动成功",
                data={"pid": process.pid, "name": name}
            )
            
        except Exception as e:
            error_msg = f"启动进程失败 {name}: {e}"
            self.logger.error(error_msg)
            return UnifiedResponse.error(error_msg, error_code="PROCESS_START_FAILED")
    
    def _is_process_running(self, name: str) -> bool:
        """检查进程是否在运行"""
        if name in self.running_processes:
            return self.running_processes[name].poll() is None
        return False
    
    def stop_process(self, name: str) -> UnifiedResponse:
        """停止进程"""
        if name not in self.running_processes:
            return UnifiedResponse.warning(f"进程 {name} 未运行")
        
        try:
            process = self.running_processes[name]
            
            # 发送SIGTERM信号
            process.terminate()
            
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # 强制终止
                if os.name != 'nt':
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                else:
                    process.kill()
            
            del self.running_processes[name]
            
            if name in self.processes:
                self.processes[name].status = 'stopped'
            
            self.logger.info(f"进程已停止: {name}")
            return UnifiedResponse.success(f"进程 {name} 已停止")
            
        except Exception as e:
            error_msg = f"停止进程失败 {name}: {e}"
            self.logger.error(error_msg)
            return UnifiedResponse.error(error_msg, error_code="PROCESS_STOP_FAILED")
    
    def stop_all(self) -> UnifiedResponse:
        """停止所有进程"""
        stopped = []
        failed = []
        
        for name in list(self.running_processes.keys()):
            result = self.stop_process(name)
            if result.status == ResponseStatus.SUCCESS.value:
                stopped.append(name)
            else:
                failed.append(name)
        
        return UnifiedResponse.success(
            "所有进程已停止",
            data={"stopped": stopped, "failed": failed}
        )
    
    def get_status(self) -> UnifiedResponse:
        """获取所有进程状态"""
        status_list = []
        
        for name, info in self.processes.items():
            is_running = self._is_process_running(name)
            status_list.append({
                "name": name,
                "status": "running" if is_running else info.status,
                "pid": info.pid,
                "script": info.script,
                "start_time": info.start_time.isoformat(),
                "restart_count": info.restart_count
            })
        
        return UnifiedResponse.success(
            "进程状态查询成功",
            data={"processes": status_list, "total": len(status_list)}
        )


# ========================================
# 模块定义
# ========================================
class ModuleType(Enum):
    """模块类型"""
    BACKEND = "backend"
    WEB = "web"
    HEALTH = "health"
    GUI = "gui"
    VALIDATE = "validate"
    VERIFY_PATHS = "verify-paths"


@dataclass
class ModuleDefinition:
    """模块定义"""
    name: str
    module_type: ModuleType
    script: str
    host: str = "0.0.0.0"
    port: int = None
    group: str = ""
    description: str = ""
    dependencies: List[str] = field(default_factory=list)
    health_check: bool = False
    health_port: int = None
    auto_restart: bool = False
    startup_delay: float = 0


# ========================================
# 模块注册表
# ========================================
class ModuleRegistry:
    """模块注册表 - 管理所有可用模块"""
    
    _instance = None
    _modules: Dict[str, ModuleDefinition] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._register_modules()
        return cls._instance
    
    def _register_modules(self):
        """注册所有模块"""
        project_root = Path(__file__).parent.parent
        
        self._modules = {
            'backend': ModuleDefinition(
                name='后端API服务',
                module_type=ModuleType.BACKEND,
                script=str(project_root / 'src' / 'backend' / 'api_server.py'),
                host='0.0.0.0',
                port=8000,
                group='后端服务',
                description='提供RESTful API和WebSocket服务',
                health_check=True,
                health_port=8000,
                startup_delay=0
            ),
            'web': ModuleDefinition(
                name='Web监控中心',
                module_type=ModuleType.WEB,
                script=str(project_root / 'web' / 'app.py'),
                host='0.0.0.0',
                port=8080,
                group='Web界面',
                description='基于FastAPI的Web管理界面',
                dependencies=['backend'],
                health_check=True,
                health_port=8080,
                startup_delay=2
            ),
            'health': ModuleDefinition(
                name='健康监控',
                module_type=ModuleType.HEALTH,
                script=str(project_root / 'scripts' / 'health_monitor' / 'health_monitor.py'),
                group='监控工具',
                description='项目健康检查和监控',
                startup_delay=1
            ),
            'gui': ModuleDefinition(
                name='GUI图形界面',
                module_type=ModuleType.GUI,
                script=str(project_root / 'src' / 'frontend' / 'main_window.py'),
                group='前端界面',
                description='PyQt5图形用户界面',
                dependencies=['backend']
            ),
            'validate': ModuleDefinition(
                name='配置验证',
                module_type=ModuleType.VALIDATE,
                script=str(project_root / 'scripts' / 'validate_configs.py'),
                group='工具',
                description='验证项目配置正确性'
            ),
            'verify-paths': ModuleDefinition(
                name='路径验证',
                module_type=ModuleType.VERIFY_PATHS,
                script=str(project_root / 'scripts' / 'verify_paths.py'),
                group='工具',
                description='验证项目路径配置'
            )
        }
    
    def get_module(self, name: str) -> Optional[ModuleDefinition]:
        """获取模块定义"""
        return self._modules.get(name)
    
    def get_all_modules(self) -> Dict[str, ModuleDefinition]:
        """获取所有模块"""
        return self._modules.copy()
    
    def get_modules_by_group(self, group: str) -> List[ModuleDefinition]:
        """按组获取模块"""
        return [m for m in self._modules.values() if m.group == group]
    
    def list_modules(self) -> List[Dict]:
        """列出所有模块"""
        return [
            {
                "key": name,
                "name": m.name,
                "group": m.group,
                "description": m.description,
                "dependencies": m.dependencies
            }
            for name, m in self._modules.items()
        ]


# ========================================
# 统一启动器 (优化版)
# ========================================
class UnifiedLauncher:
    """统一启动器主类 - 基于全局联通性设计"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.process_manager = ProcessManager()
        self.module_registry = ModuleRegistry()
        self.logger = LogManager().get_logger()
        
        # 信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """信号处理"""
        self.logger.info(f"收到信号 {signum}，正在停止所有进程...")
        self.process_manager.stop_all()
        sys.exit(0)
    
    def _build_args(self, module: ModuleDefinition, args: Dict = None) -> List[str]:
        """构建模块启动参数"""
        cmd_args = []
        
        # 主机和端口
        if module.host:
            cmd_args.extend(['--host', module.host])
        if module.port:
            cmd_args.extend(['--port', str(module.port)])
        
        # 自定义参数
        if args:
            for key, value in args.items():
                if isinstance(value, bool) and value:
                    cmd_args.append(f'--{key}')
                elif not isinstance(value, bool):
                    cmd_args.extend([f'--{key}', str(value)])
        
        return cmd_args
    
    def _check_dependencies(self, dependencies: List[str]) -> tuple:
        """检查依赖模块是否已启动"""
        not_ready = []
        for dep in dependencies:
            if not self.process_manager._is_process_running(dep):
                not_ready.append(dep)
        return not_ready
    
    def run_sequential(self, modules: List[str], exclude: List[str] = None) -> UnifiedResponse:
        """按顺序启动模块 (依赖顺序)"""
        exclude = exclude or []
        results = []
        
        for module_name in modules:
            if module_name in exclude:
                self.logger.info(f"跳过模块: {module_name}")
                continue
            
            module = self.module_registry.get_module(module_name)
            if not module:
                self.logger.warning(f"未知模块: {module_name}")
                continue
            
            # 检查依赖
            if module.dependencies:
                not_ready = self._check_dependencies(module.dependencies)
                if not_ready:
                    return UnifiedResponse.error(
                        f"模块 {module_name} 的依赖未就绪: {not_ready}",
                        error_code="DEPENDENCIES_NOT_READY"
                    )
            
            # 启动延迟
            if module.startup_delay > 0:
                self.logger.info(f"等待 {module.startup_delay} 秒...")
                time.sleep(module.startup_delay)
            
            # 启动模块
            args = self._build_args(module)
            result = self.process_manager.start_process(
                module_name,
                module.script,
                args,
                wait_for_health=module.health_check,
                health_port=module.health_port
            )
            
            results.append({
                "module": module_name,
                "result": result.to_dict()
            })
        
        return UnifiedResponse.success(
            "模块按顺序启动完成",
            data={"results": results}
        )
    
    def run_parallel(self, modules: List[str], exclude: List[str] = None) -> UnifiedResponse:
        """并行启动模块"""
        exclude = exclude or []
        threads = []
        results = []
        
        for module_name in modules:
            if module_name in exclude:
                continue
            
            module = self.module_registry.get_module(module_name)
            if not module:
                continue
            
            def start_module(m_name, m_module):
                args = self._build_args(m_module)
                result = self.process_manager.start_process(
                    m_name,
                    m_module.script,
                    args,
                    wait_for_health=m_module.health_check,
                    health_port=m_module.health_port
                )
                results.append({"module": m_name, "result": result.to_dict()})
            
            thread = threading.Thread(target=start_module, args=(module_name, module))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        return UnifiedResponse.success(
            "模块并行启动完成",
            data={"results": results}
        )
    
    def check_health(self) -> UnifiedResponse:
        """健康检查"""
        health_status = []
        all_healthy = True
        
        for name, module in self.module_registry.get_all_modules().items():
            if module.health_check and module.health_port:
                is_healthy = self.process_manager._is_process_running(name)
                health_status.append({
                    "module": name,
                    "port": module.health_port,
                    "status": "healthy" if is_healthy else "unhealthy"
                })
                if not is_healthy:
                    all_healthy = False
        
        status = ResponseStatus.SUCCESS if all_healthy else ResponseStatus.WARNING
        
        return UnifiedResponse(
            status=status.value,
            message="健康检查完成",
            data={"checks": health_status, "all_healthy": all_healthy}
        )
    
    def list_modules(self):
        """列出所有模块"""
        print("\n" + "=" * 70)
        print("可用模块列表")
        print("=" * 70)
        
        modules = self.module_registry.list_modules()
        
        # 按组分类显示
        groups = {}
        for m in modules:
            group = m['group'] or '未分类'
            if group not in groups:
                groups[group] = []
            groups[group].append(m)
        
        for group, group_modules in groups.items():
            print(f"\n【{group}】")
            for m in group_modules:
                deps = f" (依赖: {', '.join(m['dependencies'])})" if m['dependencies'] else ""
                print(f"  • {m['key']:15} | {m['name']:20}{deps}")
                print(f"    {m['description']}")
        
        print("\n" + "-" * 70)
        print("组合命令:")
        print("  --mode all         | 启动所有模块 (按依赖顺序)")
        print("  --mode parallel    | 并行启动所有模块")
        print("  --mode check       | 健康检查")
        print("  --mode status      | 查看进程状态")
        print("-" * 70)
    
    def main(self):
        """主函数"""
        parser = argparse.ArgumentParser(
            description='AI弹窗项目 - 统一启动器 (优化版)',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
示例:
  %(prog)s --mode all              # 按依赖顺序启动所有模块
  %(prog)s --mode parallel         # 并行启动所有模块
  %(prog)s --mode web              # 启动Web监控中心
  %(prog)s --mode backend          # 启动后端API服务
  %(prog)s --mode check            # 健康检查
  %(prog)s --mode status           # 查看进程状态
  %(prog)s --list                  # 列出所有模块
  %(prog)s --mode all --exclude gui  # 启动除GUI外的所有模块
            """
        )
        
        parser.add_argument(
            '--mode', '-m',
            default='web',
            choices=['all', 'parallel', 'web', 'backend', 'health', 'check', 'status'],
            help='运行模式 (默认: web)'
        )
        parser.add_argument(
            '--list', '-l',
            action='store_true',
            help='列出所有可用模块'
        )
        parser.add_argument(
            '--exclude', '-e',
            action='append',
            default=[],
            help='排除的模块'
        )
        parser.add_argument(
            '--host',
            default='0.0.0.0',
            help='监听地址'
        )
        parser.add_argument(
            '--port', '-p',
            type=int,
            default=8080,
            help='监听端口'
        )
        parser.add_argument(
            '--output', '-o',
            help='输出文件路径'
        )
        
        args = parser.parse_args()
        
        # 列出模块
        if args.list:
            self.list_modules()
            return 0
        
        # 获取所有模块列表
        all_modules = list(self.module_registry.get_all_modules().keys())
        
        # 根据模式执行
        if args.mode == 'all':
            self.logger.info("按依赖顺序启动所有模块...")
            result = self.run_sequential(all_modules, args.exclude)
            print(result.to_json())
        
        elif args.mode == 'parallel':
            self.logger.info("并行启动所有模块...")
            result = self.run_parallel(all_modules, args.exclude)
            print(result.to_json())
        
        elif args.mode == 'check':
            result = self.check_health()
            print(result.to_json())
        
        elif args.mode == 'status':
            result = self.process_manager.get_status()
            print(result.to_json())
        
        elif args.mode in all_modules:
            module = self.module_registry.get_module(args.mode)
            
            # 构建参数
            module_args = {}
            if args.host and args.host != '0.0.0.0':
                module_args['host'] = args.host
            if args.port and args.port != 8080:
                module_args['port'] = args.port
            if args.output:
                module_args['output'] = args.output
            
            result = self.process_manager.start_process(
                args.mode,
                module.script,
                self._build_args(module, module_args),
                wait_for_health=module.health_check,
                health_port=module.health_port
            )
            print(result.to_json())
            
            # 等待进程
            try:
                self.process_manager.running_processes[args.mode].wait()
            except KeyboardInterrupt:
                self.process_manager.stop_process(args.mode)
        
        else:
            self.logger.error(f"未知模式: {args.mode}")
            self.list_modules()
            return 1
        
        return 0


if __name__ == '__main__':
    launcher = UnifiedLauncher()
    sys.exit(launcher.main())

