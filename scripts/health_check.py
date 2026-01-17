#!/usr/bin/env python3
"""
my_ai_popup_project 自动化健康检测脚本
检查依赖层、系统层、进程层、业务层
支持优雅降级，缺少依赖时仍能运行基础功能
启动后自动弹窗浏览器（支持多种打开方式）
"""
import json
import socket
import threading
import subprocess
import os
import sys
import time
import webbrowser
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

# 依赖检查和优雅降级
PSUTIL_AVAILABLE = False
GPU_AVAILABLE = False
FLASK_AVAILABLE = False
REQUESTS_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    print("[警告] psutil未安装，系统监控功能将受限")

try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    print("[警告] GPUtil未安装，GPU监控功能将受限")

try:
    from flask import Flask, render_template_string, jsonify
    from werkzeug.serving import run_simple
    from werkzeug.wsgi import SharedDataMiddleware
    FLASK_AVAILABLE = True
except ImportError as e:
    print(f"[警告] Flask未安装，Web界面功能不可用: {e}")
    FLASK_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    print("[警告] requests未安装，API测试功能将受限")

from .path_config import get_project_root, get_web_dir, get_logs_dir
from .logging_utils import info, warning, error


class BrowserLauncher:
    """浏览器启动器 - 支持多种打开方式"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def detect_desktop_environment(self) -> str:
        """检测桌面环境类型"""
        desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
        session = os.environ.get("DESKTOP_SESSION", "").lower()

        if "gnome" in desktop or "gnome" in session:
            return "gnome"
        elif "kde" in desktop or "kde" in session or "plasma" in desktop:
            return "kde"
        elif "xfce" in desktop or "xfce" in session:
            return "xfce"
        elif "lxde" in desktop or "lxde" in session:
            return "lxde"
        elif "cinnamon" in desktop or "cinnamon" in session:
            return "cinnamon"
        elif "mate" in desktop or "mate" in session:
            return "mate"
        else:
            return "unknown"

    def is_display_available(self) -> bool:
        """检查DISPLAY环境变量是否设置"""
        display = os.environ.get("DISPLAY", "")
        return bool(display) and display != ""

    def is_headless(self) -> bool:
        """检查是否在无头环境中运行"""
        return not self.is_display_available()

    def get_available_methods(self) -> List[str]:
        """获取可用的浏览器打开方式"""
        methods = []

        # 检查webbrowser
        try:
            webbrowser.get()
            methods.append("webbrowser")
        except Exception:
            pass

        # 检查xdg-open
        try:
            subprocess.run(["which", "xdg-open"], capture_output=True, timeout=5)
            methods.append("xdg-open")
        except Exception:
            pass

        # 检查x-www-browser
        try:
            subprocess.run(["which", "x-www-browser"], capture_output=True, timeout=5)
            methods.append("x-www-browser")
        except Exception:
            pass

        # 检查gnome-open (GNOME)
        try:
            subprocess.run(["which", "gnome-open"], capture_output=True, timeout=5)
            methods.append("gnome-open")
        except Exception:
            pass

        # 检查kde-open (KDE)
        try:
            subprocess.run(["which", "kioclient"], capture_output=True, timeout=5)
            methods.append("kioclient")
        except Exception:
            pass

        return methods

    def open_browser(self, url: str, browser_name: Optional[str] = None) -> bool:
        """
        打开浏览器

        Args:
            url: 要打开的URL
            browser_name: 指定的浏览器名称（可选）

        Returns:
            bool: 是否成功打开
        """
        # 在无头环境中不尝试打开浏览器
        if self.is_headless():
            info(f"检测到无头环境，跳过浏览器打开")
            info(f"请手动访问: {url}")
            return False

        # 如果指定了浏览器名称
        if browser_name:
            try:
                browser = webbrowser.get(browser_name)
                browser.open(url, new=2, autoraise=True)
                info(f"已使用 {browser_name} 打开浏览器")
                return True
            except Exception as e:
                warning(f"无法使用指定浏览器 {browser_name}: {e}")

        # 尝试多种打开方式
        methods = self.get_available_methods()

        # 优先级顺序
        priority_methods = [
            "xdg-open",
            "x-www-browser",
            "gnome-open",
            "kioclient",
            "webbrowser",
        ]

        for method in priority_methods:
            if method not in methods:
                continue

            try:
                if method == "webbrowser":
                    # 使用webbrowser模块
                    success = self._open_with_webbrowser(url)
                    if success:
                        return True

                elif method == "xdg-open":
                    success = self._run_command(["xdg-open", url])
                    if success:
                        info("已使用 xdg-open 打开浏览器")
                        return True

                elif method == "x-www-browser":
                    success = self._run_command(["x-www-browser", url])
                    if success:
                        info("已使用 x-www-browser 打开浏览器")
                        return True

                elif method == "gnome-open":
                    success = self._run_command(["gnome-open", url])
                    if success:
                        info("已使用 gnome-open 打开浏览器")
                        return True

                elif method == "kioclient":
                    success = self._run_command(["kioclient", "exec", url])
                    if success:
                        info("已使用 kioclient 打开浏览器")
                        return True

            except Exception as e:
                warning(f"{method} 方式失败: {e}")
                continue

        # 最后尝试webbrowser
        return self._open_with_webbrowser(url)

    def _run_command(self, cmd: List[str]) -> bool:
        """运行命令并返回是否成功"""
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=self.timeout
            )
            return result.returncode == 0
        except Exception:
            return False

    def _open_with_webbrowser(self, url: str) -> bool:
        """使用webbrowser模块打开"""
        try:
            # 使用默认浏览器
            webbrowser.open(url, new=2, autoraise=True)
            info("已使用默认浏览器打开")
            return True
        except Exception as e:
            warning(f"webbrowser打开失败: {e}")
            return False


class ServiceChecker:
    """服务就绪检测器"""

    def __init__(self, host: str = "localhost", port: int = 8080, timeout: int = 30):
        self.host = host
        self.port = port
        self.timeout = timeout

    def wait_for_service(self, interval: float = 0.5) -> bool:
        """
        等待服务就绪

        Args:
            interval: 检查间隔（秒）

        Returns:
            bool: 服务是否就绪
        """
        start_time = time.time()

        info("等待服务启动...")

        while time.time() - start_time < self.timeout:
            if self._check_connection():
                elapsed = time.time() - start_time
                info(f"服务已就绪 (耗时: {elapsed:.1f}秒)")
                return True
            time.sleep(interval)

        warning(f"服务启动超时 ({self.timeout}秒)")
        return False

    def _check_connection(self) -> bool:
        """检查服务连接"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((self.host, self.port))
            sock.close()
            return result == 0
        except Exception:
            return False


class HealthChecker:
    """my_ai_popup_project健康检测器"""

    def __init__(self, config_path: str = None):
        # 动态获取项目根目录
        self.project_root = get_project_root()

        # 使用相对路径定义配置文件
        if config_path is None:
            config_path = self.project_root / "rules" / "health_check_config.json"

        self.config_path = Path(config_path)
        self.config = self._load_config()

        self.results = {
            "timestamp": datetime.now().isoformat(),
            "dependency_check": {},
            "system_check": {},
            "process_check": {},
            "business_check": {},
            "output_check": {},
            "overall_status": "unknown",
        }

    def _load_config(self) -> Dict:
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _get_package_version(self, package: str) -> str:
        """获取包版本"""
        try:
            result = subprocess.run(
                [
                    "python3",
                    "-c",
                    f"import {package.replace('-', '_')}; print({package.replace('-', '_')}.__version__)",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.stdout.strip() or "unknown"
        except Exception:
            return "unknown"

    def check_dependencies(self) -> Dict[str, Any]:
        """检查Python依赖包"""
        result = {
            "status": "pending",
            "progress": 0,
            "checked_packages": [],
            "missing_packages": [],
            "optional_missing": [],
            "warnings": [],
        }

        required = self.config.get("dependency_check", {}).get("required_packages", [])
        optional = self.config.get("dependency_check", {}).get("optional_packages", [])

        if not PSUTIL_AVAILABLE:
            result["warnings"].append("psutil未安装，部分系统监控功能不可用")

        total = len(required) + len(optional)
        checked = 0

        for pkg in required:
            try:
                __import__(pkg.replace("-", "_"))
                result["checked_packages"].append(
                    {
                        "name": pkg,
                        "status": "ok",
                        "version": self._get_package_version(pkg),
                    }
                )
            except ImportError:
                result["missing_packages"].append(pkg)
            checked += 1
            result["progress"] = int(checked / total * 100)

        for pkg in optional:
            try:
                __import__(pkg.replace("-", "_"))
                result["checked_packages"].append(
                    {
                        "name": pkg,
                        "status": "ok",
                        "optional": True,
                        "version": self._get_package_version(pkg),
                    }
                )
            except ImportError:
                result["optional_missing"].append(pkg)
            checked += 1
            result["progress"] = int(checked / total * 100)

        if not result["missing_packages"]:
            result["status"] = "ok" if not result["optional_missing"] else "warning"
        else:
            result["status"] = "critical"

        return result

    def check_system(self) -> Dict[str, Any]:
        """检查系统资源"""
        result = {"status": "pending", "progress": 0, "checks": {}, "warnings": []}

        if not PSUTIL_AVAILABLE:
            result["warnings"].append("psutil未安装，跳过系统检查")
            result["status"] = "warning"
            result["progress"] = 100
            result["checks"]["system"] = {
                "value": "unavailable",
                "status": "warning",
                "message": "psutil未安装",
            }
            return result

        thresholds = self.config.get("system_check", {}).get("thresholds", {})
        check_items = self.config.get("system_check", {}).get("check_items", [])

        total = len(check_items)
        checked = 0

        if "cpu_usage" in check_items:
            try:
                cpu = psutil.cpu_percent(interval=1)
                status = "ok"
                if cpu > thresholds.get("cpu_percent_critical", 90):
                    status = "critical"
                elif cpu > thresholds.get("cpu_percent_warning", 70):
                    status = "warning"
                result["checks"]["cpu_usage"] = {
                    "value": cpu,
                    "unit": "%",
                    "status": status,
                    "threshold": thresholds.get("cpu_percent_warning", 70),
                }
            except Exception as e:
                result["checks"]["cpu_usage"] = {
                    "value": 0,
                    "unit": "%",
                    "status": "error",
                    "message": str(e),
                }
            checked += 1
            result["progress"] = int(checked / total * 100)

        if "memory_usage" in check_items:
            try:
                memory = psutil.virtual_memory()
                status = "ok"
                if memory.percent > thresholds.get("memory_percent_critical", 90):
                    status = "critical"
                elif memory.percent > thresholds.get("memory_percent_warning", 75):
                    status = "warning"
                result["checks"]["memory_usage"] = {
                    "value": memory.percent,
                    "unit": "%",
                    "status": status,
                    "total_gb": round(memory.total / (1024**3), 2),
                    "used_gb": round(memory.used / (1024**3), 2),
                }
            except Exception as e:
                result["checks"]["memory_usage"] = {
                    "value": 0,
                    "unit": "%",
                    "status": "error",
                    "message": str(e),
                }
            checked += 1
            result["progress"] = int(checked / total * 100)

        if "disk_usage" in check_items:
            try:
                disk = psutil.disk_usage("/")
                percent = disk.percent
                status = "ok"
                if percent > thresholds.get("disk_percent_critical", 95):
                    status = "critical"
                elif percent > thresholds.get("disk_percent_warning", 80):
                    status = "warning"
                result["checks"]["disk_usage"] = {
                    "value": percent,
                    "unit": "%",
                    "status": status,
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                }
            except Exception as e:
                result["checks"]["disk_usage"] = {
                    "value": 0,
                    "unit": "%",
                    "status": "error",
                    "message": str(e),
                }
            checked += 1
            result["progress"] = int(checked / total * 100)

        if "gpu_usage" in check_items:
            if GPU_AVAILABLE:
                try:
                    gpus = GPUtil.getGPUs()
                    if gpus:
                        gpu = gpus[0]
                        load = gpu.load * 100
                        status = "ok"
                        if load > thresholds.get("gpu_percent_critical", 95):
                            status = "critical"
                        elif load > thresholds.get("gpu_percent_warning", 80):
                            status = "warning"
                        result["checks"]["gpu_usage"] = {
                            "value": round(load, 1),
                            "unit": "%",
                            "status": status,
                            "name": gpu.name,
                        }
                    else:
                        result["checks"]["gpu_usage"] = {
                            "value": 0,
                            "unit": "%",
                            "status": "ok",
                            "message": "无GPU",
                        }
                except Exception as e:
                    result["checks"]["gpu_usage"] = {
                        "value": 0,
                        "unit": "%",
                        "status": "warning",
                        "message": str(e),
                    }
            else:
                result["checks"]["gpu_usage"] = {
                    "value": 0,
                    "unit": "%",
                    "status": "warning",
                    "message": "GPUtil未安装",
                }
            checked += 1
            result["progress"] = int(checked / total * 100)

        statuses = [c.get("status", "ok") for c in result["checks"].values()]
        if "critical" in statuses:
            result["status"] = "critical"
        elif "warning" in statuses:
            result["status"] = "warning"
        else:
            result["status"] = "ok"

        return result

    def check_processes(self) -> Dict[str, Any]:
        """检查必要进程"""
        result = {"status": "pending", "progress": 0, "processes": {}}

        required = self.config.get("process_check", {}).get("required_processes", [])
        optional = self.config.get("process_check", {}).get("optional_processes", [])

        all_processes = required + optional
        total = len(all_processes)
        checked = 0

        for proc in all_processes:
            port = proc.get("port")
            name = proc.get("name")
            required_flag = proc in required

            port_status = self._check_port(port)
            process_status = self._check_process(name) if PSUTIL_AVAILABLE else None

            status = (
                "ok" if port_status else ("critical" if required_flag else "warning")
            )

            result["processes"][name] = {
                "name": name,
                "port": port,
                "port_open": port_status,
                "process_running": process_status,
                "status": status,
                "required": required_flag,
            }

            checked += 1
            result["progress"] = int(checked / total * 100)

        statuses = [p.get("status") for p in result["processes"].values()]
        if "critical" in statuses:
            result["status"] = "critical"
        elif "warning" in statuses:
            result["status"] = "warning"
        else:
            result["status"] = "ok"

        return result

    def _check_port(self, port: int) -> bool:
        """检查端口是否开放"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        try:
            result = sock.connect_ex(("localhost", port))
            return result == 0
        except Exception:
            return False
        finally:
            sock.close()

    def _check_process(self, name: str) -> bool:
        """检查进程是否运行"""
        for proc in psutil.process_iter(["name"]):
            try:
                if name.lower() in proc.info.get("name", "").lower():
                    return True
            except Exception:
                pass
        return False

    def check_business(self) -> Dict[str, Any]:
        """检查业务模块"""
        result = {
            "status": "pending",
            "progress": 0,
            "api_endpoints": {},
            "modules": {},
            "engines": {},
            "engine_details": {},
        }

        endpoints = self.config.get("business_check", {}).get("api_endpoints", [])
        for ep in endpoints:
            url = ep.get("url", "")
            name = ep.get("name", "")
            status = self._check_endpoint(url, ep.get("timeout", 5))
            result["api_endpoints"][name] = {"url": url, "status": status}

        modules = self.config.get("business_check", {}).get("modules_to_check", [])
        for module in modules:
            name = module.get("name", "")
            path = self.project_root / module.get("path", "")
            files = module.get("files", [])
            file_status = [{"file": f, "exists": (path / f).exists()} for f in files]
            result["modules"][name] = {"path": str(path), "files": file_status}

        # 增强引擎检查
        result["engine_details"] = self._check_engines_detail()
        engines = self.config.get("business_check", {}).get("engines_to_check", [])
        for engine in engines:
            name = engine.get("name", "")
            path = self.project_root / engine.get("path", "")
            exists = path.exists()
            detail = result["engine_details"].get(name.lower().replace("-", ""), {})
            result["engines"][name] = {
                "path": str(path),
                "exists": exists,
                "available": detail.get("available", exists),
                "status": detail.get("status", "unknown"),
            }

        api_ok = all(e.get("status") == "ok" for e in result["api_endpoints"].values())
        engine_ok = all(e.get("available") for e in result["engines"].values())

        result["progress"] = 100
        result["status"] = "ok" if api_ok and engine_ok else "warning"

        return result

    def _check_engines_detail(self) -> Dict[str, Any]:
        """详细检查所有引擎适配器"""
        results = {}

        # 检查 Deep-Live-Cam
        results["deeplivecam"] = self._check_deep_live_cam()

        # 检查 FaceFusion
        results["facefusion"] = self._check_face_fusion()

        # 检查 iRoop
        results["iroop"] = self._check_iroop()

        return results

    def _check_deep_live_cam(self) -> Dict[str, Any]:
        """检查 Deep-Live-Cam 引擎"""
        result = {
            "name": "Deep-Live-Cam",
            "available": False,
            "status": "unavailable",
            "details": {},
        }

        try:
            # 适配my_ai_popup_project的路径
            from src.integrations.deep_live_cam import DeepLiveCamAdapter

            adapter = DeepLiveCamAdapter()

            # 检查文件存在
            vendor_path = self.project_root / "assets" / "Deep-Live-Cam-main"
            run_py = vendor_path / "run.py"
            models_dir = vendor_path / "models"

            result["details"]["run_py_exists"] = run_py.exists()
            result["details"]["models_dir_exists"] = models_dir.exists()

            # 检查适配器可用性
            if adapter.is_available():
                result["available"] = True
                result["status"] = "ready"
                result["details"]["adapter_loaded"] = True
            else:
                result["status"] = "missing_files"

        except ImportError as e:
            result["status"] = "import_error"
            result["details"]["error"] = str(e)
        except Exception as e:
            result["status"] = "error"
            result["details"]["error"] = str(e)

        return result

    def _check_face_fusion(self) -> Dict[str, Any]:
        """检查 FaceFusion 引擎"""
        result = {
            "name": "FaceFusion",
            "available": False,
            "status": "unavailable",
            "details": {},
        }

        try:
            # 适配my_ai_popup_project的路径
            from src.integrations.facefusion import FaceFusionAdapter

            adapter = FaceFusionAdapter()

            # 检查文件存在
            vendor_path = self.project_root / "assets" / "facefusion-master"
            facefusion_py = vendor_path / "facefusion.py"
            configs_dir = vendor_path / "facefusion"

            result["details"]["facefusion_py_exists"] = facefusion_py.exists()
            result["details"]["configs_dir_exists"] = configs_dir.exists()

            # 检查适配器可用性
            if adapter.is_available():
                result["available"] = True
                result["status"] = "ready"
                result["details"]["adapter_loaded"] = True
            else:
                result["status"] = "missing_files"

        except ImportError as e:
            result["status"] = "import_error"
            result["details"]["error"] = str(e)
        except Exception as e:
            result["status"] = "error"
            result["details"]["error"] = str(e)

        return result

    def _check_iroop(self) -> Dict[str, Any]:
        """检查 iRoop 引擎"""
        result = {
            "name": "iRoop",
            "available": False,
            "status": "unavailable",
            "details": {},
        }

        try:
            # 适配my_ai_popup_project的路径
            from src.integrations.iroop import IRoopAdapter

            adapter = IRoopAdapter()

            # 检查文件存在
            vendor_path = self.project_root / "assets" / "iRoopDeepFaceCam-main"
            run_py = vendor_path / "run.py"
            models_dir = vendor_path / "models"

            result["details"]["run_py_exists"] = run_py.exists()
            result["details"]["models_dir_exists"] = models_dir.exists()

            # 检查适配器可用性
            if adapter.is_available():
                result["available"] = True
                result["status"] = "ready"
                result["details"]["adapter_loaded"] = True
            else:
                result["status"] = "missing_files"

        except ImportError as e:
            result["status"] = "import_error"
            result["details"]["error"] = str(e)
        except Exception as e:
            result["status"] = "error"
            result["details"]["error"] = str(e)

        return result

    def _check_endpoint(self, url: str, timeout: int) -> str:
        """检查API端点"""
        if not REQUESTS_AVAILABLE:
            return "unavailable"
        try:
            r = requests.get(url, timeout=timeout)
            return "ok" if r.status_code == 200 else "error"
        except Exception:
            return "unreachable"

    def check_output(self) -> Dict[str, Any]:
        """检查输出模块（虚拟摄像头等）"""
        result = {"status": "pending", "progress": 0, "modules": {}, "warnings": []}

        # 检查虚拟摄像头
        try:
            # 适配my_ai_popup_project的路径
            from src.processing.virtual_camera import VirtualCamera

            vc = VirtualCamera()
            is_available = vc.is_available()
            result["modules"]["virtual_camera"] = {
                "name": "虚拟摄像头",
                "available": is_available,
                "status": "ok" if is_available else "warning",
                "message": "可用" if is_available else "pyvirtualcam未安装",
            }
        except Exception as e:
            result["modules"]["virtual_camera"] = {
                "name": "虚拟摄像头",
                "available": False,
                "status": "error",
                "message": str(e),
            }

        # 检查虚拟摄像头模块文件
        vc_path = self.project_root / "src" / "processing" / "virtual_camera.py"
        result["modules"]["virtual_cam_file"] = {
            "name": "virtual_camera.py",
            "exists": vc_path.exists(),
            "status": "ok" if vc_path.exists() else "error",
        }

        result["progress"] = 100

        statuses = [m.get("status") for m in result["modules"].values()]
        if "error" in statuses:
            result["status"] = "critical"
        elif "warning" in statuses:
            result["status"] = "warning"
        else:
            result["status"] = "ok"

        return result

    def run_full_check(self) -> Dict[str, Any]:
        """执行完整健康检查"""
        print("开始my_ai_popup_project健康检测...")

        print("[1/5] 检查依赖层...")
        self.results["dependency_check"] = self.check_dependencies()
        print(f"  状态: {self.results['dependency_check']['status']}")

        print("[2/5] 检查系统层...")
        self.results["system_check"] = self.check_system()
        print(f"  状态: {self.results['system_check']['status']}")

        print("[3/5] 检查进程层...")
        self.results["process_check"] = self.check_processes()
        print(f"  状态: {self.results['process_check']['status']}")

        print("[4/5] 检查业务层...")
        self.results["business_check"] = self.check_business()
        print(f"  状态: {self.results['business_check']['status']}")

        print("[5/5] 检查输出层...")
        self.results["output_check"] = self.check_output()
        print(f"  状态: {self.results['output_check']['status']}")

        statuses = [
            self.results["dependency_check"].get("status"),
            self.results["system_check"].get("status"),
            self.results["process_check"].get("status"),
            self.results["business_check"].get("status"),
            self.results["output_check"].get("status"),
        ]

        if "critical" in statuses:
            self.results["overall_status"] = "critical"
        elif "warning" in statuses:
            self.results["overall_status"] = "warning"
        else:
            self.results["overall_status"] = "ok"

        print(f"\n整体状态: {self.results['overall_status']}")
        return self.results

    def save_results(self, path: str = "logs/health_check_latest.json"):
        """保存检查结果"""
        output_path = self.project_root / path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        info(f"结果已保存到: {output_path}")

    def get_summary(self) -> Dict[str, Any]:
        return {
            "timestamp": self.results.get("timestamp") or "",
            "overall_status": self.results.get("overall_status") or "unknown",
            "dependency_status": self.results.get("dependency_check", {}).get("status")
            or "pending",
            "system_status": self.results.get("system_check", {}).get("status")
            or "pending",
            "process_status": self.results.get("process_check", {}).get("status")
            or "pending",
            "business_status": self.results.get("business_check", {}).get("status")
            or "pending",
        }

    def run_web_interface(self, port: int = 8080, auto_open_browser: bool = True):
        """
        启动Web界面

        Args:
            port: Web服务端口
            auto_open_browser: 是否自动打开浏览器
        """
        url = f"http://localhost:{port}"
        print(f"\n{'='*50}")
        print(f"🌐 my_ai_popup_project 健康检测 Web 界面")
        print(f"{'='*50}")
        print(f"📍 访问地址: {url}")
        print(f"📋 API状态: {url}/api/status")
        print(f"{'='*50}\n")

        if auto_open_browser:
            launcher = BrowserLauncher()
            # 延迟1秒打开浏览器，确保服务已启动
            threading.Timer(1, lambda: launcher.open_browser(url)).start()
            print("✅ 浏览器弹窗已启动...")

        # 启动Flask应用
        app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


if FLASK_AVAILABLE:
    app = Flask(__name__)

    # 获取项目根目录
    PROJECT_ROOT = get_project_root()
    WEB_DIR = get_web_dir()
    TEMPLATES_DIR = WEB_DIR / "templates"
    STATIC_DIR = WEB_DIR / "static"

    # health_checker 将在首次请求时初始化为 HealthChecker 实例
    health_checker: Optional["HealthChecker"] = None

    # 挂载静态文件 - 使用werkzeug
    if STATIC_DIR.exists():
        app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
            '/static': str(STATIC_DIR)
        })

    @app.route("/")
    def index():
        """提供Web监控主页"""
        index_path = TEMPLATES_DIR / "index.html"
        if index_path.exists():
            with open(index_path, 'r', encoding='utf-8') as f:
                return f.read()
        return """<!DOCTYPE html><html><head><meta charset="UTF-8"><title>my_ai_popup_project 健康监控</title></head><body><h1>my_ai_popup_project 健康监控</h1><p>正在加载...</p></body></html>"""

    @app.route("/api/status")
    def api_status():
        global health_checker
        if health_checker is not None:
            # type: ignore[union-attr] - Pylance 无法追踪全局变量的类型变化
            return jsonify(health_checker.get_summary())  # type: ignore[union-attr]
        return jsonify({"running": False})

    @app.route("/api/run_check", methods=["POST"])
    def api_run_check():
        global health_checker
        # 确保 health_checker 已初始化
        if health_checker is None:
            health_checker = HealthChecker()
        # type: ignore[union-attr] - Pylance 无法理解条件检查后的类型变化
        threading.Thread(
            target=lambda: (
                health_checker.run_full_check(),  # type: ignore[union-attr]
                health_checker.save_results(),  # type: ignore[union-attr]
            )
        ).start()
        return jsonify({"status": "started"})


def main():
    import argparse
    import signal
    import sys

    parser = argparse.ArgumentParser(description="my_ai_popup_project健康检测")
    parser.add_argument("--web", action="store_true", help="启动Web界面")
    parser.add_argument(
        "--monitor", action="store_true", help="启动实时监控模式（循环检测）"
    )
    parser.add_argument(
        "--interval", type=int, default=30, help="监控刷新间隔（秒），默认30秒"
    )
    parser.add_argument("--port", type=int, default=8080, help="Web端口")
    args = parser.parse_args()

    checker = HealthChecker()

    def signal_handler(sig, frame):
        """优雅退出处理"""
        print("\n\n👋 收到退出信号，正在停止监控...")
        sys.exit(0)

    if args.monitor:
        # 实时监控模式
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        print(f"启动实时监控模式，刷新间隔: {args.interval}秒")
        print("按 Ctrl+C 退出监控\n")
        print("=" * 60)

        while True:
            try:
                checker.run_full_check()
                checker.save_results()
                summary = checker.get_summary()

                # 简洁输出
                status_symbol = (
                    "✓"
                    if summary["overall_status"] == "ok"
                    else ("⚠" if summary["overall_status"] == "warning" else "✗")
                )
                ts = summary.get("timestamp", "")
                timestamp = ts.split("T")[1].split(".")[0] if ts else "N/A"

                print(
                    f"[{timestamp}] {status_symbol} 整体: {summary['overall_status']} | "
                    f"依赖: {summary['dependency_status']} | "
                    f"系统: {summary['system_status']} | "
                    f"进程: {summary['process_status']} | "
                    f"业务: {summary['business_status']}"
                )

                import time

                time.sleep(args.interval)
            except KeyboardInterrupt:
                break
            except Exception as e:
                error(f"监控异常: {e}")
                import time

                time.sleep(args.interval)

        print("\n👋 监控已停止")
        return

    if args.web:
        if not FLASK_AVAILABLE:
            error("Flask未安装，无法启动Web界面")
            print("请安装Flask: pip3 install flask")
            return
        info(f"启动Web界面: http://localhost:{args.port}")
        checker.run_full_check()
        checker.save_results()
        checker.run_web_interface(args.port)
    else:
        results = checker.run_full_check()
        checker.save_results()
        summary = checker.get_summary()
        print("\n" + "=" * 50)
        print("my_ai_popup_project 健康检测报告")
        print("=" * 50)
        print(f"整体状态: {summary['overall_status']}")
        print(f"依赖检查: {summary['dependency_status']}")
        print(f"系统检查: {summary['system_status']}")
        print(f"进程检查: {summary['process_status']}")
        print(f"业务检查: {summary['business_status']}")


if __name__ == "__main__":
    main()
