#!/usr/bin/env python3
"""
统一监控启动器
一键启动前后端实时健康检测监控系统，并自动弹出浏览器页面
"""

import os
import sys
import time
import json
import subprocess
import threading
import webbrowser
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import socket
import psutil
from datetime import datetime

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent


class UnifiedMonitorLauncher:
    """统一监控启动器"""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.logger = self._setup_logging()
        self.processes = {}
        self.monitoring_active = False

        # 配置路径
        self.config = {
            "web_port": 8080,
            "api_port": 5000,
            "health_check_interval": 30,
            "auto_open_browser": True,
            "browser_url": "http://localhost:8080",
        }

    def _setup_logging(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger("unified_launcher")
        logger.setLevel(logging.INFO)

        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # 文件处理器
        log_file = self.project_root / "logs" / "unified_launcher.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger

    def check_system_requirements(self) -> Dict[str, Any]:
        """检查系统要求"""
        self.logger.info("检查系统要求...")

        results = {
            "python_version": sys.version,
            "project_root_exists": self.project_root.exists(),
            "required_dirs": {},
            "ports_available": {},
            "dependencies": {},
        }

        # 检查必需目录
        required_dirs = ["web", "api", "scripts", "src", "assets", "rules", "docs"]
        for dir_name in required_dirs:
            path = self.project_root / dir_name
            results["required_dirs"][dir_name] = path.exists()

        # 检查端口可用性
        ports_to_check = [self.config["web_port"], self.config["api_port"]]
        for port in ports_to_check:
            results["ports_available"][port] = self._is_port_available(port)

        # 检查关键依赖
        key_deps = ["fastapi", "uvicorn", "psutil", "socketio"]
        for dep in key_deps:
            try:
                __import__(dep)
                results["dependencies"][dep] = "available"
            except ImportError:
                results["dependencies"][dep] = "missing"

        return results

    def _is_port_available(self, port: int) -> bool:
        """检查端口是否可用"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(("localhost", port))
            sock.close()
            return result != 0
        except:
            return False

    def start_health_monitoring(self) -> bool:
        """启动健康监控"""
        self.logger.info("启动健康监控系统...")

        try:
            # 启动健康监控脚本
            health_script = (
                self.project_root / "scripts" / "health_monitor" / "health_monitor.py"
            )
            if health_script.exists():
                self.logger.info("启动后台健康监控...")
                # 这里可以启动后台监控进程
                pass
            else:
                self.logger.warning("健康监控脚本不存在，跳过启动")

            self.monitoring_active = True
            return True

        except Exception as e:
            self.logger.error(f"启动健康监控失败: {e}")
            return False

    def start_web_monitor(self) -> bool:
        """启动Web监控界面"""
        self.logger.info("启动Web监控界面...")

        try:
            web_app = self.project_root / "web" / "start_monitor.py"
            if web_app.exists():
                self.logger.info(f"启动Web应用在端口 {self.config['web_port']}...")

                # 启动Web应用进程
                process = subprocess.Popen(
                    [sys.executable, str(web_app)],
                    cwd=str(self.project_root / "web"),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

                self.processes["web_monitor"] = process
                self.logger.info(f"Web监控进程已启动，PID: {process.pid}")

                # 等待服务启动
                time.sleep(3)

                # 检查服务是否启动成功
                if self._is_port_available(self.config["web_port"]):
                    self.logger.warning("Web服务可能未成功启动")
                    return False

                return True
            else:
                self.logger.error("Web启动脚本不存在")
                return False

        except Exception as e:
            self.logger.error(f"启动Web监控失败: {e}")
            return False

    def start_api_server(self) -> bool:
        """启动API服务器"""
        self.logger.info("启动API服务器...")

        try:
            api_app = self.project_root / "api" / "backend" / "entry.py"
            if api_app.exists():
                self.logger.info(f"启动API服务在端口 {self.config['api_port']}...")

                process = subprocess.Popen(
                    [sys.executable, str(api_app)],
                    cwd=str(self.project_root / "api"),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

                self.processes["api_server"] = process
                self.logger.info(f"API服务器进程已启动，PID: {process.pid}")

                # 等待服务启动
                time.sleep(2)
                return True
            else:
                self.logger.warning("API启动脚本不存在，跳过启动")
                return True  # 不影响整体启动

        except Exception as e:
            self.logger.error(f"启动API服务器失败: {e}")
            return False

    def open_browser(self) -> bool:
        """打开浏览器"""
        if not self.config["auto_open_browser"]:
            return True

        try:
            self.logger.info(f"自动打开浏览器访问: {self.config['browser_url']}")
            webbrowser.open(self.config["browser_url"])
            return True
        except Exception as e:
            self.logger.error(f"打开浏览器失败: {e}")
            return False

    def start_background_monitoring(self):
        """启动后台监控"""

        def monitor_loop():
            while self.monitoring_active:
                try:
                    # 执行健康检查
                    self._perform_health_check()

                    # 等待下次检查
                    time.sleep(self.config["health_check_interval"])

                except Exception as e:
                    self.logger.error(f"后台监控错误: {e}")
                    time.sleep(10)

        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        self.logger.info("后台监控线程已启动")

    def _perform_health_check(self):
        """执行健康检查"""
        try:
            # 检查进程状态
            for name, process in self.processes.items():
                if process.poll() is not None:
                    self.logger.warning(
                        f"进程 {name} 已退出，退出码: {process.returncode}"
                    )

            # 检查系统资源
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent

            if cpu_percent > 90:
                self.logger.warning(f"CPU使用率过高: {cpu_percent:.1f}%")
            if memory_percent > 90:
                self.logger.warning(f"内存使用率过高: {memory_percent:.1f}%")

            # 检查端口状态
            for port in [self.config["web_port"], self.config["api_port"]]:
                if self._is_port_available(port):
                    self.logger.warning(f"端口 {port} 无响应")

        except Exception as e:
            self.logger.error(f"健康检查执行失败: {e}")

    def wait_for_services(self, timeout: int = 30) -> bool:
        """等待服务启动"""
        self.logger.info("等待服务启动...")

        start_time = time.time()
        while time.time() - start_time < timeout:
            web_ready = not self._is_port_available(self.config["web_port"])
            api_ready = not self._is_port_available(self.config["api_port"])

            if web_ready:
                self.logger.info("Web服务已就绪")
                if api_ready:
                    self.logger.info("API服务已就绪")
                return True

            time.sleep(1)

        self.logger.error("服务启动超时")
        return False

    def launch_all(self) -> Dict[str, Any]:
        """一键启动所有服务"""
        self.logger.info("=== 开始统一监控系统启动 ===")

        results = {
            "timestamp": datetime.now().isoformat(),
            "system_check": {},
            "services_started": {},
            "overall_success": False,
        }

        # 1. 系统要求检查
        results["system_check"] = self.check_system_requirements()

        # 检查是否有严重问题
        critical_issues = []
        if not results["system_check"]["project_root_exists"]:
            critical_issues.append("项目根目录不存在")

        missing_deps = [
            dep
            for dep, status in results["system_check"]["dependencies"].items()
            if status == "missing"
        ]
        if missing_deps:
            critical_issues.append(f"缺少关键依赖: {', '.join(missing_deps)}")

        occupied_ports = [
            port
            for port, available in results["system_check"]["ports_available"].items()
            if not available
        ]
        if occupied_ports:
            critical_issues.append(f"端口被占用: {', '.join(map(str, occupied_ports))}")

        if critical_issues:
            results["critical_issues"] = critical_issues
            self.logger.error("发现关键问题，无法启动:")
            for issue in critical_issues:
                self.logger.error(f"  - {issue}")
            return results

        # 2. 启动健康监控
        results["services_started"]["health_monitor"] = self.start_health_monitoring()

        # 3. 启动API服务器
        results["services_started"]["api_server"] = self.start_api_server()

        # 4. 启动Web监控
        results["services_started"]["web_monitor"] = self.start_web_monitor()

        # 5. 等待服务就绪
        if not self.wait_for_services():
            results["services_started"]["web_monitor"] = False

        # 6. 启动后台监控
        if results["services_started"]["web_monitor"]:
            self.start_background_monitoring()

        # 7. 打开浏览器
        if results["services_started"]["web_monitor"]:
            self.open_browser()

        # 8. 总结结果
        all_started = all(results["services_started"].values())
        results["overall_success"] = all_started

        if all_started:
            self.logger.info("=== 统一监控系统启动成功 ===")
            self.logger.info(f"访问地址: {self.config['browser_url']}")
        else:
            self.logger.error("=== 统一监控系统启动失败 ===")
            failed_services = [
                name
                for name, started in results["services_started"].items()
                if not started
            ]
            self.logger.error(f"失败的服务: {', '.join(failed_services)}")

        return results

    def shutdown(self):
        """关闭所有服务"""
        self.logger.info("正在关闭所有服务...")
        self.monitoring_active = False

        for name, process in self.processes.items():
            try:
                process.terminate()
                process.wait(timeout=5)
                self.logger.info(f"服务 {name} 已关闭")
            except Exception as e:
                self.logger.error(f"关闭服务 {name} 失败: {e}")
                try:
                    process.kill()
                except:
                    pass

        self.logger.info("所有服务已关闭")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="统一监控系统启动器")
    parser.add_argument("--no-browser", action="store_true", help="不自动打开浏览器")
    parser.add_argument("--web-port", type=int, default=8080, help="Web服务端口")
    parser.add_argument("--api-port", type=int, default=5000, help="API服务端口")
    parser.add_argument(
        "--check-only", action="store_true", help="仅检查系统要求，不启动服务"
    )

    args = parser.parse_args()

    launcher = UnifiedMonitorLauncher()
    launcher.config["auto_open_browser"] = not args.no_browser
    launcher.config["web_port"] = args.web_port
    launcher.config["api_port"] = args.api_port
    launcher.config["browser_url"] = f"http://localhost:{args.web_port}"

    if args.check_only:
        # 仅检查系统要求
        results = launcher.check_system_requirements()
        print("\n=== 系统要求检查结果 ===")
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return 0

    # 启动所有服务
    results = launcher.launch_all()

    # 输出结果
    print(f"\n=== 启动结果摘要 ===")
    print(f"整体成功: {results['overall_success']}")
    print(f"服务状态: {results['services_started']}")

    if results["overall_success"]:
        print(f"\n🎉 监控系统已启动！请访问: {launcher.config['browser_url']}")
        print("按 Ctrl+C 退出...")

        try:
            # 保持运行
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            launcher.shutdown()
    else:
        print("\n❌ 启动失败，请检查上述错误信息")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
