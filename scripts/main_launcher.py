#!/usr/bin/env python3
"""
AI弹窗项目 - 统一启动器
提供一键启动所有功能模块的入口点

功能模块:
- backend: 后端API服务
- web: Web监控中心  
- health: 健康监控
- gui: GUI图形界面
- all: 启动所有模块

使用方式:
    python main_launcher.py --module all
    python main_launcher.py --module web --port 8080
    python main_launcher.py --module health --auto-fix
"""
import sys
import os
import argparse
import subprocess
import signal
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# 确保项目根目录在Python路径中
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 配置日志
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/launcher.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class ProcessManager:
    """进程管理器 - 负责启动和管理子进程"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.processes: Dict[str, subprocess.Popen] = {}
        self.python_path = self._get_python_path()
    
    def _get_python_path(self) -> str:
        """获取正确的Python解释器路径"""
        venv_python = self.project_root / '.venv' / 'bin' / 'python3'
        if venv_python.exists():
            return str(venv_python)
        return sys.executable
    
    def start_process(self, name: str, script: str, args: List[str] = None, 
                      env: Dict[str, str] = None, cwd: Path = None) -> bool:
        """启动一个进程"""
        try:
            # 构建命令
            cmd = [self.python_path, str(script)] + (args or [])
            
            # 设置环境变量
            process_env = os.environ.copy()
            process_env['PYTHONPATH'] = f"{self.project_root}:{self.project_root}/src"
            process_env['AI_POPUP_ENV'] = 'development'
            if env:
                process_env.update(env)
            
            # 设置工作目录
            work_dir = cwd or self.project_root
            
            logger.info(f"启动进程: {name}")
            logger.info(f"命令: {' '.join(cmd)}")
            
            # 启动进程
            process = subprocess.Popen(
                cmd,
                env=process_env,
                cwd=str(work_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            self.processes[name] = process
            logger.info(f"进程已启动: {name} (PID: {process.pid})")
            
            return True
            
        except Exception as e:
            logger.error(f"启动进程失败 {name}: {e}")
            return False
    
    def stop_process(self, name: str) -> bool:
        """停止一个进程"""
        if name in self.processes:
            try:
                process = self.processes[name]
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                del self.processes[name]
                logger.info(f"进程已停止: {name}")
                return True
            except Exception as e:
                logger.error(f"停止进程失败 {name}: {e}")
                return False
        return False
    
    def stop_all(self):
        """停止所有进程"""
        for name in list(self.processes.keys()):
            self.stop_process(name)
    
    def wait_all(self):
        """等待所有进程完成"""
        for process in self.processes.values():
            process.wait()
    
    def is_running(self, name: str) -> bool:
        """检查进程是否在运行"""
        if name in self.processes:
            return self.processes[name].poll() is None
        return False


class ModuleRunner:
    """模块运行器 - 负责执行具体功能模块"""
    
    MODULES = {
        'backend': {
            'name': '后端API服务',
            'script': 'src/backend/api_server.py',
            'host': '0.0.0.0',
            'port': 8000,
            'group': '后端服务',
            'description': '提供RESTful API和WebSocket服务'
        },
        'web': {
            'name': 'Web监控中心',
            'script': 'web/app.py',
            'host': '0.0.0.0',
            'port': 8080,
            'group': 'Web界面',
            'description': '基于FastAPI的Web管理界面'
        },
        'health': {
            'name': '健康监控',
            'script': 'scripts/health_monitor/health_monitor.py',
            'auto_fix': False,
            'group': '监控工具',
            'description': '项目健康检查和监控'
        },
        'gui': {
            'name': 'GUI图形界面',
            'script': 'src/frontend/main_window.py',
            'group': '前端界面',
            'description': 'PyQt5图形用户界面'
        },
        'validate': {
            'name': '配置验证',
            'script': 'scripts/validate_configs.py',
            'group': '工具',
            'description': '验证项目配置正确性'
        },
        'verify-paths': {
            'name': '路径验证',
            'script': 'scripts/verify_paths.py',
            'group': '工具',
            'description': '验证项目路径配置'
        }
    }
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.process_manager = ProcessManager(project_root)
    
    def run_module(self, module_name: str, args: Dict = None) -> bool:
        """运行单个模块"""
        if module_name not in self.MODULES:
            logger.error(f"未知模块: {module_name}")
            logger.info(f"可用模块: {', '.join(self.MODULES.keys())}")
            return False
        
        module = self.MODULES[module_name]
        script_path = self.project_root / module['script']
        
        if not script_path.exists():
            logger.error(f"脚本不存在: {script_path}")
            return False
        
        # 构建参数
        cmd_args = []
        if 'host' in module and module.get('host'):
            cmd_args.extend(['--host', module['host']])
        if 'port' in module and module.get('port'):
            cmd_args.extend(['--port', str(module['port'])])
        if args:
            for key, value in args.items():
                if isinstance(value, bool) and value:
                    cmd_args.append(f'--{key}')
                elif not isinstance(value, bool):
                    cmd_args.extend([f'--{key}', str(value)])
        
        return self.process_manager.start_process(
            module_name,
            script_path,
            cmd_args
        )
    
    def run_all(self, exclude: List[str] = None) -> bool:
        """运行所有模块"""
        exclude = exclude or []
        success = True
        
        # 按顺序启动后端服务
        if 'backend' not in exclude:
            self.run_module('backend')
            time.sleep(2)  # 等待后端启动
        
        # 启动Web监控
        if 'web' not in exclude:
            self.run_module('web')
            time.sleep(1)
        
        # 启动健康监控
        if 'health' not in exclude:
            self.run_module('health')
        
        return success
    
    def list_modules(self):
        """列出所有可用模块"""
        print("\n可用模块:")
        print("-" * 60)
        for key, module in self.MODULES.items():
            print(f"  {key:15} | {module['name']:20} | {module['description']}")
        print("-" * 60)
        print("  all            | 所有模块             | 启动所有功能模块")
        print("-" * 60)


class UnifiedLauncher:
    """统一启动器主类"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.module_runner = ModuleRunner(self.project_root)
    
    def main(self):
        """主函数"""
        parser = argparse.ArgumentParser(
            description='AI弹窗项目 - 统一启动器',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
示例:
  %(prog)s --module web              # 启动Web监控中心
  %(prog)s --module backend          # 启动后端API服务
  %(prog)s --module health           # 运行健康检查
  %(prog)s --module all              # 启动所有模块
  %(prog)s --module all --exclude gui    # 启动除GUI外的所有模块
  %(prog)s --list                    # 列出所有可用模块
            """
        )
        
        parser.add_argument(
            '--module', '-m',
            default='web',
            help='要运行的模块 (默认: web)'
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
            help='排除的模块 (用于 --module all)'
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
            '--auto-fix',
            action='store_true',
            help='自动修复发现的问题'
        )
        parser.add_argument(
            '--quiet',
            action='store_true',
            help='静默模式'
        )
        parser.add_argument(
            '--output', '-o',
            help='输出文件路径'
        )
        
        args = parser.parse_args()
        
        if args.quiet:
            logging.getLogger().setLevel(logging.WARNING)
        
        # 列出模块
        if args.list:
            self.module_runner.list_modules()
            return 0
        
        # 运行模块
        module = args.module
        
        if module == 'all':
            logger.info("启动所有功能模块...")
            self.module_runner.run_all(args.exclude)
            
            # 等待用户中断
            try:
                logger.info("所有模块已启动，按 Ctrl+C 停止...")
                self.module_runner.process_manager.wait_all()
            except KeyboardInterrupt:
                logger.info("收到中断信号，正在停止所有模块...")
                self.module_runner.process_manager.stop_all()
        
        elif module in self.module_runner.MODULES:
            # 构建模块参数，只包含非空值
            module_args = {}
            if args.host and args.host != '0.0.0.0':
                module_args['host'] = args.host
            if args.port and args.port != 8080:
                module_args['port'] = args.port
            if args.auto_fix:
                module_args['auto_fix'] = args.auto_fix
            if args.output:
                module_args['output'] = args.output
            self.module_runner.run_module(module, module_args)
            
            # 等待进程
            try:
                self.module_runner.process_manager.wait_all()
            except KeyboardInterrupt:
                logger.info("收到中断信号，正在停止...")
                self.module_runner.process_manager.stop_all()
        
        else:
            logger.error(f"未知模块: {module}")
            self.module_runner.list_modules()
            return 1
        
        return 0


def signal_handler(signum, frame):
    """信号处理"""
    logger.info(f"收到信号 {signum}，正在停止所有进程...")
    sys.exit(0)


if __name__ == '__main__':
    # 注册信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 运行启动器
    launcher = UnifiedLauncher()
    sys.exit(launcher.main())

