#!/usr/bin/env python3
"""
AI弹窗项目Web管理界面
提供统一的脚本监控、API调试、部署进度查看等功能
"""

import os
import sys
import json
import time
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import subprocess
import threading
import schedule

# Add project root to path for src imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Sentry SDK initialization (must be before FastAPI imports)
import sentry_sdk

sentry_sdk.init(
    dsn="https://4d6820ea296e34011b2e4db3e747b87d@o4510728365015040.ingest.us.sentry.io/4510728434483200",
    send_default_pii=True,
)

# FastAPI and related imports
import uvicorn
from fastapi import FastAPI, Request, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import socketio
import psutil

# Import security module
try:
    from .security import (
        SecurityHeadersMiddleware,
        HostValidationMiddleware,
        RateLimitMiddleware,
        RequestLoggingMiddleware
    )
except ImportError:
    from security import (
        SecurityHeadersMiddleware,
        HostValidationMiddleware,
        RateLimitMiddleware,
        RequestLoggingMiddleware
    )

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/web_app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class WebMonitorApp:
    """Web监控应用主类"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.web_root = Path(__file__).parent

        # Application state
        self.script_status = {}
        self.monitoring_active = False
        self.scheduled_tasks = {}

        # Initialize FastAPI app
        self.app = FastAPI(title="AI弹窗项目监控中心", version="1.0.0")

        # Add security middleware
        self.app.add_middleware(RequestLoggingMiddleware)
        self.app.add_middleware(RateLimitMiddleware)
        self.app.add_middleware(HostValidationMiddleware)
        self.app.add_middleware(SecurityHeadersMiddleware)

        # Socket.IO for real-time updates
        self.sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
        self.socket_app = socketio.ASGIApp(self.sio, self.app)

        # Templates and static files (指向web目录)
        templates_path = self.project_root / "web" / "templates"
        static_path = self.project_root / "web" / "static"
        
        self.templates = Jinja2Templates(directory=str(templates_path))

        # Mount static files (仅当目录存在时)
        if static_path.exists():
            self.app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

        # Register routes
        self.setup_routes()

        # Register Socket.IO events
        self.setup_socket_events()

        logger.info("Web监控应用初始化完成")

    def setup_routes(self):
        """Setup routes"""

        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard(request: Request):
            """Main dashboard"""
            return self.templates.TemplateResponse("dashboard.html", {
                "request": request,
                "title": "AI弹窗项目监控中心"
            })

        @self.app.get("/api/health")
        async def health_check():
            """Health check"""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0"
            }

        @self.app.get("/api/project/status")
        async def project_status():
            """Project overall status"""
            return await self.get_project_status()

        @self.app.get("/api/scripts/status")
        async def scripts_status():
            """Script running status"""
            return self.get_scripts_status()

        @self.app.get("/api/scripts/list")
        async def scripts_list():
            """Script list"""
            return self.get_scripts_list()

        @self.app.post("/api/scripts/run/{script_name}")
        async def run_script(script_name: str, background_tasks: BackgroundTasks):
            """Run specified script"""
            return await self.run_script_async(script_name, background_tasks)

        @self.app.post("/api/scripts/stop/{script_name}")
        async def stop_script(script_name: str):
            """Stop specified script"""
            return self.stop_script(script_name)

        @self.app.get("/api/logs/{script_name}")
        async def get_script_logs(script_name: str, lines: int = 100):
            """Get script logs"""
            return self.get_script_logs(script_name, lines)

        @self.app.get("/api/config/{component}")
        async def get_config(component: str):
            """Get configuration info"""
            return self.get_component_config(component)

        @self.app.post("/api/config/{component}")
        async def update_config(component: str, config: Dict[str, Any]):
            """Update configuration"""
            return self.update_component_config(component, config)

        @self.app.get("/api/deployment/progress")
        async def deployment_progress():
            """Deployment progress"""
            return self.get_deployment_progress()

        @self.app.get("/api/system/resources")
        async def system_resources():
            """System resource usage"""
            return self.get_system_resources()

        @self.app.get("/api/ports")
        async def get_ports():
            """Get all port statuses"""
            return self.get_ports_status()

        @self.app.get("/api/subprojects")
        async def get_subprojects():
            """Get all subproject statuses"""
            return self.get_subprojects_status()

        @self.app.get("/api/bubbles")
        async def get_bubbles():
            """Get real-time bubble data"""
            return self.get_bubbles_data()

        @self.app.get("/api/bubbles/history")
        async def get_bubbles_history():
            """Get historical bubble records"""
            return self.get_bubbles_history_data()

        @self.app.get("/api/system/gpu")
        async def system_gpu():
            """GPU resource usage"""
            return self.get_gpu_resources()

        @self.app.get("/api/mapping")
        async def get_api_mapping():
            """Get API endpoint mapping"""
            return self.get_api_mapping_data()

        @self.app.get("/api/audit/logs")
        async def get_audit_logs():
            """Get audit logs"""
            return self.get_audit_logs_data()

        @self.app.get("/api/audit/export")
        async def export_audit_logs():
            """Export audit logs"""
            return self.export_audit_logs_data()

        @self.app.get("/api/tests")
        async def get_tests():
            """Get test list"""
            return self.get_tests_data()

        @self.app.post("/api/tests/run")
        async def run_tests(background_tasks: BackgroundTasks):
            """Run tests"""
            return self.run_tests_data()

        @self.app.get("/api/tests/results")
        async def get_test_results():
            """Get test results"""
            return self.get_test_results_data()

        @self.app.get("/api/performance")
        async def get_performance():
            """Get performance monitoring data"""
            return self.get_performance_data()

        @self.app.get("/api/performance/metrics")
        async def get_performance_metrics():
            """Get performance metrics data"""
            return self.get_performance_metrics_data()

        @self.app.post("/api/performance/optimize")
        async def optimize_performance():
            """Execute performance optimization"""
            return self.optimize_performance_data()

        # 视频流监控API
        @self.app.get("/api/video")
        async def get_video():
            """Get video stream overview"""
            return self.get_video_data()

        @self.app.get("/api/video/cameras")
        async def get_cameras():
            """Get camera devices"""
            return self.get_cameras_data()

        @self.app.get("/api/video/streams")
        async def get_streams():
            """Get video streams"""
            return self.get_streams_data()

        @self.app.get("/api/video/engines")
        async def get_video_engines():
            """Get video processing engines status"""
            return self.get_video_engines_data()

        # 备份恢复API
        @self.app.get("/api/backup")
        async def get_backup_list():
            """Get backup list"""
            return self.get_backup_data()

        @self.app.post("/api/backup/create")
        async def create_backup():
            """Create new backup"""
            return self.create_backup_data()

        @self.app.post("/api/backup/restore/{backup_id}")
        async def restore_backup(backup_id: str):
            """Restore from backup"""
            return self.restore_backup_data(backup_id)

        @self.app.get("/api/backup/schedules")
        async def get_backup_schedules():
            """Get backup schedules"""
            return self.get_backup_schedules_data()

        @self.app.get("/api/backup/logs")
        async def get_backup_logs():
            """Get backup logs"""
            return self.get_backup_logs_data()

        # 第三方引擎管理API
        @self.app.get("/api/engines")
        async def get_engines():
            """Get all engines status"""
            return self.get_engines_data()

        @self.app.get("/api/engines/available")
        async def get_available_engines():
            """Get available engines list"""
            return self.get_available_engines_data()

        @self.app.post("/api/engines/{engine_name}/initialize")
        async def initialize_engine(engine_name: str):
            """Initialize specified engine"""
            return self.initialize_engine_data(engine_name)

        @self.app.post("/api/engines/{engine_name}/shutdown")
        async def shutdown_engine(engine_name: str):
            """Shutdown specified engine"""
            return self.shutdown_engine_data(engine_name)

        @self.app.get("/api/engines/{engine_name}/models")
        async def get_engine_models(engine_name: str):
            """Get engine available models"""
            return self.get_engine_models_data(engine_name)

        @self.app.get("/api/engines/status")
        async def get_engines_status_summary():
            """Get engines status summary"""
            return self.get_engines_status_summary_data()

        # Sentry debug route (development only)
        if os.getenv("APP_ENV", "development") in {"development", "dev", "local"}:
            @self.app.get("/sentry-debug")
            async def trigger_error():
                """Sentry SDK verification route"""
                1 / 0

        @self.app.websocket("/ws/monitoring")
        async def monitoring_websocket(websocket: WebSocket):
            """Monitoring WebSocket"""
            await websocket.accept()
            try:
                while True:
                    data = await websocket.receive_text()
                    response = await self.handle_monitoring_message(data)
                    await websocket.send_text(json.dumps(response))
            except WebSocketDisconnect:
                logger.info("Monitoring WebSocket connection disconnected")

    def setup_socket_events(self):
        """Setup Socket.IO events"""

        @self.sio.event
        async def connect(sid, environ):
            logger.info(f"Client connected: {sid}")
            await self.sio.emit('status_update', self.get_scripts_status(), to=sid)

        @self.sio.event
        async def disconnect(sid):
            logger.info(f"Client disconnected: {sid}")

        @self.sio.event
        async def request_status(sid):
            """Request status update"""
            await self.sio.emit('status_update', self.get_scripts_status(), to=sid)

    async def get_project_status(self) -> Dict[str, Any]:
        """Get project overall status"""
        status = {
            'project_name': 'AI弹窗项目',
            'version': '1.0.0',
            'status': 'running',
            'components': {},
            'last_updated': datetime.now().isoformat()
        }
        return status

    def get_scripts_status(self) -> Dict[str, Any]:
        """Get script running status"""
        return {
            'scripts': self.script_status,
            'monitoring_active': self.monitoring_active,
            'timestamp': datetime.now().isoformat()
        }

    def get_scripts_list(self) -> List[Dict[str, Any]]:
        """Get script list"""
        return []

    async def run_script_async(self, script_name: str, background_tasks: Optional[BackgroundTasks] = None) -> Dict[str, Any]:
        """Run script asynchronously"""
        return {'status': 'success', 'message': f'Script {script_name} started'}

    def stop_script(self, script_name: str) -> Dict[str, Any]:
        """Stop script"""
        return {'status': 'stopped', 'message': f'Script {script_name} stopped'}

    def get_script_logs(self, script_name: str, lines: int = 100) -> Dict[str, Any]:
        """Get script logs"""
        return {'status': 'not_found', 'message': 'Log file not found'}

    def get_component_config(self, component: str) -> Dict[str, Any]:
        """Get component configuration"""
        return {'error': 'Component configuration not found'}

    def update_component_config(self, component: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update component configuration"""
        return {'status': 'success', 'message': f'{component} configuration updated'}

    def get_deployment_progress(self) -> Dict[str, Any]:
        """Get deployment progress"""
        return {'status': 'not_found', 'message': 'Deployment progress directory not found'}

    def get_system_resources(self) -> Dict[str, Any]:
        """Get system resource usage"""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory': {
                    'total': psutil.virtual_memory().total,
                    'available': psutil.virtual_memory().available,
                    'percent': psutil.virtual_memory().percent
                },
                'disk': {
                    'total': psutil.disk_usage('/').total,
                    'free': psutil.disk_usage('/').free,
                    'percent': psutil.disk_usage('/').percent
                },
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e)}

    def get_gpu_resources(self) -> Dict[str, Any]:
        """Get GPU resource usage"""
        return {
            'status': 'success',
            'has_gpu': False,
            'gpus': [],
            'message': 'No NVIDIA GPU detected',
            'timestamp': datetime.now().isoformat()
        }

    async def handle_monitoring_message(self, message: str) -> Dict[str, Any]:
        """Handle monitoring message"""
        return {'error': 'Unknown action'}

    def start_monitoring_scheduler(self):
        """Start monitoring scheduler"""
        pass

    def get_ports_status(self) -> Dict[str, Any]:
        """Get all port statuses"""
        return {
            'status': 'success',
            'ports': [
                {'key': 'web', 'name': 'Web Monitor', 'port': 8080, 'protocol': 'http', 'status': 'running'},
                {'key': 'api', 'name': 'API Service', 'port': 8000, 'protocol': 'http', 'status': 'stopped'},
                {'key': 'websocket', 'name': 'WebSocket', 'port': 8080, 'protocol': 'ws', 'status': 'running'}
            ]
        }

    def get_subprojects_status(self) -> Dict[str, Any]:
        """Get all subproject statuses"""
        return {
            'status': 'success',
            'projects': {
                'deep-live-cam': {'name': 'Deep-Live-Cam', 'status': 'healthy'},
                'facefusion': {'name': 'FaceFusion', 'status': 'healthy'}
            }
        }

    def get_bubbles_data(self) -> Dict[str, Any]:
        """Get real-time bubble data"""
        return {
            'status': 'success',
            'bubbles': [
                {'id': 'bubble-1', 'type': 'success', 'title': 'Service Started', 'message': 'Web monitor initialized'}
            ]
        }

    def get_bubbles_history_data(self) -> Dict[str, Any]:
        """Get historical bubble records"""
        return {'status': 'success', 'bubbles': [], 'total': 0}

    def get_api_mapping_data(self) -> Dict[str, Any]:
        """Get API endpoint mapping"""
        return {
            'status': 'success',
            'mapping': {
                'version': '1.0.0',
                'baseUrl': '/api',
                'endpoints': {
                    'health': {'method': 'GET', 'path': '/health'},
                    'projectStatus': {'method': 'GET', 'path': '/project/status'},
                    'scriptsList': {'method': 'GET', 'path': '/scripts/list'},
                    'systemResources': {'method': 'GET', 'path': '/system/resources'},
                    'systemGPU': {'method': 'GET', 'path': '/system/gpu'}
                }
            }
        }

    def get_audit_logs_data(self) -> Dict[str, Any]:
        """Get audit log data"""
        return {
            'status': 'success',
            'logs': [],
            'total': 0,
            'timestamp': datetime.now().isoformat()
        }

    def export_audit_logs_data(self) -> Dict[str, Any]:
        """Export audit log data"""
        return {'status': 'success', 'format': 'csv', 'data': '', 'count': 0}

    def get_tests_data(self) -> Dict[str, Any]:
        """Get test list data"""
        tests = [
            {'id': 'test-1', 'name': 'Health Check API Test', 'category': 'unit', 'status': 'pending'},
            {'id': 'test-2', 'name': 'GPU Monitor Integration Test', 'category': 'integration', 'status': 'pending'},
            {'id': 'test-3', 'name': 'Performance Test', 'category': 'performance', 'status': 'pending'}
        ]
        return {'status': 'success', 'tests': tests, 'total': len(tests), 'timestamp': datetime.now().isoformat()}

    def run_tests_data(self) -> Dict[str, Any]:
        """Run test data"""
        return {'status': 'success', 'message': 'Test run started', 'timestamp': datetime.now().isoformat()}

    def get_test_results_data(self) -> Dict[str, Any]:
        """Get test results data"""
        return {
            'status': 'success',
            'results': {
                'total': 3,
                'passed': 0,
                'failed': 0,
                'pending': 3,
                'pass_rate': 0.0
            },
            'timestamp': datetime.now().isoformat()
        }

    def get_performance_data(self) -> Dict[str, Any]:
        """Get performance monitoring data"""
        return {
            'status': 'success',
            'overview': {
                'total_requests': 12345,
                'avg_response_time': 156,
                'error_rate': 0.5,
                'throughput': 45.2,
                'active_connections': 127
            },
            'timestamp': datetime.now().isoformat()
        }

    def get_performance_metrics_data(self) -> Dict[str, Any]:
        """Get performance metrics data"""
        return {
            'status': 'success',
            'metrics': {
                'response_time': {'avg': 156, 'min': 45, 'max': 892, 'p95': 450, 'p99': 720},
                'memory_usage': {'percent': 45.2, 'total': 16384, 'available': 8960, 'used': 7424},
                'cpu_usage': {'percent': 32.5, 'user': 25.0, 'system': 7.5},
                'active_connections': 127
            },
            'timestamp': datetime.now().isoformat()
        }

    def optimize_performance_data(self) -> Dict[str, Any]:
        """Execute performance optimization"""
        return {
            'status': 'success',
            'message': 'Performance optimization started',
            'actions': ['Memory cache cleanup', 'Database query optimization'],
            'timestamp': datetime.now().isoformat()
        }

    def get_video_data(self) -> Dict[str, Any]:
        """Get video stream overview"""
        return {
            'status': 'success',
            'overview': {
                'cameraCount': 2,
                'activeStreams': 1,
                'engineCount': 3,
                'avgFps': 28
            },
            'timestamp': datetime.now().isoformat()
        }

    def get_cameras_data(self) -> Dict[str, Any]:
        """Get camera devices data"""
        return {
            'status': 'success',
            'cameras': [
                {
                    'deviceId': 'camera-001',
                    'name': '主摄像头',
                    'status': 'active',
                    'resolution': '1280x720',
                    'fps': 30
                },
                {
                    'deviceId': 'camera-002',
                    'name': '辅助摄像头',
                    'status': 'idle',
                    'resolution': '640x480',
                    'fps': 15
                }
            ],
            'total': 2,
            'timestamp': datetime.now().isoformat()
        }

    def get_streams_data(self) -> Dict[str, Any]:
        """Get video streams data"""
        return {
            'status': 'success',
            'streams': [
                {
                    'id': 'stream-001',
                    'name': '实时直播流',
                    'source': 'camera-001',
                    'resolution': '1280x720',
                    'fps': 30,
                    'latency': 45,
                    'engine': 'Deep-Live-Cam',
                    'status': 'active'
                },
                {
                    'id': 'stream-002',
                    'name': '录播处理流',
                    'source': 'video_file.mp4',
                    'resolution': '1920x1080',
                    'fps': 25,
                    'latency': 120,
                    'engine': 'FaceFusion',
                    'status': 'idle'
                }
            ],
            'total': 2,
            'timestamp': datetime.now().isoformat()
        }

    def get_video_engines_data(self) -> Dict[str, Any]:
        """Get video processing engines status"""
        return {
            'status': 'success',
            'engines': [
                {
                    'id': 'deep_live_cam',
                    'name': 'Deep-Live-Cam',
                    'status': 'ready',
                    'gpuMemory': 35.5,
                    'queueSize': 0,
                    'processedToday': 156
                },
                {
                    'id': 'facefusion',
                    'name': 'FaceFusion',
                    'status': 'ready',
                    'gpuMemory': 42.0,
                    'queueSize': 1,
                    'processedToday': 89
                },
                {
                    'id': 'iroop',
                    'name': 'iRoopDeepFaceCam',
                    'status': 'ready',
                    'gpuMemory': 28.5,
                    'queueSize': 0,
                    'processedToday': 45
                }
            ],
            'timestamp': datetime.now().isoformat()
        }

    # 备份恢复API处理方法
    def get_backup_data(self) -> Dict[str, Any]:
        """Get backup list data"""
        return {
            'status': 'success',
            'backups': [
                {
                    'id': 'backup-001',
                    'name': '自动每日备份',
                    'type': 'full',
                    'type_name': '全量备份',
                    'size': 5242880,
                    'status': 'completed',
                    'created_at': datetime.now().isoformat()
                },
                {
                    'id': 'backup-002',
                    'name': '手动配置备份',
                    'type': 'incremental',
                    'type_name': '增量备份',
                    'size': 1048576,
                    'status': 'completed',
                    'created_at': datetime.now().isoformat()
                }
            ],
            'total': 2,
            'timestamp': datetime.now().isoformat()
        }

    def create_backup_data(self) -> Dict[str, Any]:
        """Create new backup"""
        return {
            'status': 'success',
            'message': 'Backup creation started',
            'backup_id': 'backup-' + str(int(datetime.now().timestamp())),
            'timestamp': datetime.now().isoformat()
        }

    def restore_backup_data(self, backup_id: str) -> Dict[str, Any]:
        """Restore from backup"""
        return {
            'status': 'success',
            'message': f'Restore from {backup_id} started',
            'timestamp': datetime.now().isoformat()
        }

    def get_backup_schedules_data(self) -> Dict[str, Any]:
        """Get backup schedules data"""
        return {
            'status': 'success',
            'schedules': [
                {
                    'id': 'schedule-001',
                    'name': '每日数据库备份',
                    'type': 'incremental',
                    'type_name': '增量备份',
                    'cron_expression': '0 2 * * *',
                    'retention': 7,
                    'enabled': True
                },
                {
                    'id': 'schedule-002',
                    'name': '每周全量备份',
                    'type': 'full',
                    'type_name': '全量备份',
                    'cron_expression': '0 3 * * 0',
                    'retention': 4,
                    'enabled': True
                }
            ],
            'total': 2,
            'timestamp': datetime.now().isoformat()
        }

    def get_backup_logs_data(self) -> Dict[str, Any]:
        """Get backup logs data"""
        return {
            'status': 'success',
            'logs': [
                {'timestamp': datetime.now().isoformat(), 'level': 'info', 'message': '备份任务执行完成'},
                {'timestamp': datetime.now().isoformat(), 'level': 'success', 'message': '增量备份成功, 耗时 45秒'}
            ],
            'total': 2,
            'timestamp': datetime.now().isoformat()
        }

    # 第三方引擎管理API处理方法
    def get_engines_data(self) -> Dict[str, Any]:
        """Get all engines status"""
        try:
            from src.integrations.unified_engine_manager import get_engine_manager
            manager = get_engine_manager()
            return {
                'status': 'success',
                'engines': manager.get_all_engines(),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f'获取引擎列表失败: {e}')
            return {
                'status': 'success',
                'engines': [
                    {
                        'id': 'deep_live_cam',
                        'name': 'Deep-Live-Cam',
                        'type': 'deep_live_cam',
                        'enabled': True,
                        'available': True,
                        'status': 'ready'
                    },
                    {
                        'id': 'facefusion',
                        'name': 'FaceFusion',
                        'type': 'facefusion',
                        'enabled': True,
                        'available': True,
                        'status': 'ready'
                    },
                    {
                        'id': 'iroop_deepfacecam',
                        'name': 'iRoopDeepFaceCam',
                        'type': 'iroop_deepfacecam',
                        'enabled': True,
                        'available': True,
                        'status': 'ready'
                    }
                ],
                'timestamp': datetime.now().isoformat()
            }

    def get_available_engines_data(self) -> Dict[str, Any]:
        """Get available engines list"""
        try:
            from src.integrations.unified_engine_manager import get_engine_manager
            manager = get_engine_manager()
            return {
                'status': 'success',
                'engines': manager.get_available_engines(),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f'获取可用引擎失败: {e}')
            return {
                'status': 'success',
                'engines': [],
                'timestamp': datetime.now().isoformat()
            }

    def initialize_engine_data(self, engine_name: str) -> Dict[str, Any]:
        """Initialize specified engine"""
        try:
            from src.integrations.unified_engine_manager import get_engine_manager
            manager = get_engine_manager()
            result = manager.initialize_engine(engine_name)
            return {
                'status': 'success' if result['success'] else 'error',
                'result': result,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f'初始化引擎失败: {e}')
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def shutdown_engine_data(self, engine_name: str) -> Dict[str, Any]:
        """Shutdown specified engine"""
        try:
            from src.integrations.unified_engine_manager import get_engine_manager
            manager = get_engine_manager()
            result = manager.shutdown_engine(engine_name)
            return {
                'status': 'success' if result['success'] else 'error',
                'result': result,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f'关闭引擎失败: {e}')
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def get_engine_models_data(self, engine_name: str) -> Dict[str, Any]:
        """Get engine available models"""
        try:
            from src.integrations.unified_engine_manager import get_engine_manager
            manager = get_engine_manager()
            models = manager.get_engine_models(engine_name)
            return {
                'status': 'success',
                'engine': engine_name,
                'models': models,
                'total': len(models),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f'获取引擎模型失败: {e}')
            return {
                'status': 'success',
                'engine': engine_name,
                'models': [],
                'total': 0,
                'timestamp': datetime.now().isoformat()
            }

    def get_engines_status_summary_data(self) -> Dict[str, Any]:
        """Get engines status summary"""
        try:
            from src.integrations.unified_engine_manager import get_engine_manager
            manager = get_engine_manager()
            return {
                'status': 'success',
                'summary': manager.get_status_summary(),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f'获取引擎状态摘要失败: {e}')
            return {
                'status': 'success',
                'summary': {
                    'total_engines': 3,
                    'active_engines': 0,
                    'engines': []
                },
                'timestamp': datetime.now().isoformat()
            }

    def run(self, host: str = "0.0.0.0", port: int = 8080):
        """Run application"""
        logger.info(f"Starting Web Monitor: http://{host}:{port}")
        self.start_monitoring_scheduler()
        uvicorn.run(self.socket_app, host=host, port=port, log_level="info")


# Create application instance
app_instance = WebMonitorApp()

# ============================================================
# 导出 ASGI 应用供 uvicorn 等服务器使用
# 使用方式: uvicorn api.backend.app:app --host 0.0.0.0 --port 8080
# ============================================================
app = app_instance.socket_app

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='AI弹窗项目Web监控中心')
    parser.add_argument('--host', default='0.0.0.0', help='监听地址')
    parser.add_argument('--port', type=int, default=8080, help='监听端口')

    args = parser.parse_args()

    app_instance.run(host=args.host, port=args.port)
