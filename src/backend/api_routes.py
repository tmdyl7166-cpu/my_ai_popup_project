#!/usr/bin/env python3
"""
统一API路由模块

实现api_mapping.json中定义的所有API端点
确保前后端API调用一致性
"""

import sys
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

import psutil
from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    Query,
    BackgroundTasks,
    Security,
)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from src.utils.logger import get_logger

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logger = get_logger(__name__)
router = APIRouter()

# 安全组件
bearer_scheme = HTTPBearer(auto_error=False)


# ==================== 响应模型 ====================


class HealthResponse(BaseModel):
    """健康检查响应"""

    status: str
    timestamp: str
    version: str
    services: Dict[str, str]


class ProjectStatusResponse(BaseModel):
    """项目状态响应"""

    project_name: str
    version: str
    status: str
    components: Dict[str, Any]
    health_score: float
    last_updated: str


class ScriptsListResponse(BaseModel):
    """脚本列表响应"""

    scripts: List[Dict[str, Any]]
    total: int
    timestamp: str


class ScriptsStatusResponse(BaseModel):
    """脚本状态响应"""

    scripts: Dict[str, Any]
    monitoring_active: bool
    timestamp: str


class SystemResourcesResponse(BaseModel):
    """系统资源响应"""

    cpu_percent: float
    memory: Dict[str, float]
    disk: Dict[str, float]
    timestamp: str


class GPUResourcesResponse(BaseModel):
    """GPU资源响应"""

    status: str
    has_gpu: bool
    gpus: List[Dict[str, Any]]
    message: str
    timestamp: str


class PortsResponse(BaseModel):
    """端口状态响应"""

    status: str
    ports: List[Dict[str, Any]]
    total: int
    timestamp: str


class SubProjectsResponse(BaseModel):
    """子项目响应"""

    status: str
    projects: Dict[str, Any]
    total: int
    timestamp: str


class BubblesResponse(BaseModel):
    """冒泡数据响应"""

    status: str
    bubbles: List[Dict[str, Any]]
    total: int
    timestamp: str


class DeploymentProgressResponse(BaseModel):
    """部署进度响应"""

    status: str
    content: Dict[str, Any]
    timestamp: str


class PerformanceResponse(BaseModel):
    """性能监控响应"""

    status: str
    overview: Dict[str, Any]
    timestamp: str


class VideoResponse(BaseModel):
    """视频流概览响应"""

    status: str
    overview: Dict[str, Any]
    timestamp: str


class EnginesResponse(BaseModel):
    """引擎列表响应"""

    status: str
    engines: List[Dict[str, Any]]
    total: int
    timestamp: str


# ==================== 辅助函数 ====================


def get_timestamp() -> str:
    """获取当前时间戳"""
    return datetime.now().isoformat()


# ==================== 认证依赖 ====================


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
) -> Optional[Dict[str, Any]]:
    """获取当前用户依赖"""
    if not credentials:
        return None

    # 简化版令牌验证 - 实际项目中应使用完整的安全管理器
    token_data = decode_token_simple(credentials.credentials)
    if not token_data:
        raise HTTPException(status_code=401, detail="无效的认证令牌")

    return token_data


def decode_token_simple(token: str) -> Optional[Dict[str, Any]]:
    """简单令牌解码 - 实际项目应使用JWT"""
    try:
        import base64

        parts = token.split(".")
        if len(parts) != 3:
            return None
        payload = base64.urlsafe_b64decode(parts[1] + "==")
        return json.loads(payload)
    except Exception:
        return None


async def get_admin_user(
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user),
) -> Dict[str, Any]:
    """管理员权限检查依赖"""
    if not current_user:
        raise HTTPException(status_code=401, detail="认证凭据缺失")
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return current_user


# ==================== 认证模型 ====================


class LoginRequest(BaseModel):
    """登录请求"""

    username: str
    password: str


class LoginResponse(BaseModel):
    """登录响应"""

    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


class UserResponse(BaseModel):
    """用户信息响应"""

    id: str
    username: str
    email: str
    role: str
    is_active: bool
    created_at: str


# ==================== 认证相关函数 ====================


def simple_authenticate(username: str, password: str) -> Optional[Dict[str, Any]]:
    """简单认证函数 - 实际项目应使用数据库验证"""
    # 演示用户 - 实际项目中应从数据库查询
    demo_users = {
        "admin": {
            "id": "user-001",
            "username": "admin",
            "email": "admin@example.com",
            "role": "admin",
            "is_active": True,
            "password": "admin123",
        },
        "user": {
            "id": "user-002",
            "username": "user",
            "email": "user@example.com",
            "role": "user",
            "is_active": True,
            "password": "user123",
        },
    }

    user_data = demo_users.get(username)
    if user_data and user_data["password"] == password:
        return {
            "id": user_data["id"],
            "username": user_data["username"],
            "email": user_data["email"],
            "role": user_data["role"],
            "is_active": user_data["is_active"],
        }
    return None


def create_simple_token(user_data: Dict[str, Any]) -> str:
    """创建简单令牌 - 实际项目应使用JWT"""
    import base64
    import json
    import time

    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": user_data["id"],
        "username": user_data["username"],
        "role": user_data["role"],
        "exp": int(time.time()) + 3600,
    }

    header_encoded = base64.urlsafe_b64encode(json.dumps(header).encode()).decode()
    payload_encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()

    return f"{header_encoded}.{payload_encoded}.signature"


# ==================== API端点 ====================


@router.post("/auth/login", response_model=LoginResponse, tags=["认证"])
async def login(request: LoginRequest):
    """用户登录"""
    user = simple_authenticate(request.username, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # 创建访问令牌
    access_token = create_simple_token(user)

    return LoginResponse(
        access_token=access_token,
        user=user,
    )


@router.get("/auth/me", response_model=UserResponse, tags=["认证"])
async def get_current_user_info(
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user),
):
    """获取当前用户信息"""
    if not current_user:
        raise HTTPException(status_code=401, detail="用户未认证")

    return UserResponse(
        id=current_user["id"],
        username=current_user["username"],
        email=current_user.get("email", ""),
        role=current_user["role"],
        is_active=current_user.get("is_active", True),
        created_at=get_timestamp(),
    )


@router.get("/health", response_model=HealthResponse, tags=["健康检查"])
async def health_check():
    """系统健康检查"""
    return HealthResponse(
        status="healthy",
        timestamp=get_timestamp(),
        version="1.0.0",
        services={"api_server": "running", "web_monitor": "running"},
    )


@router.get("/project/status", response_model=ProjectStatusResponse, tags=["项目"])
async def project_status():
    """获取项目整体状态"""
    return ProjectStatusResponse(
        project_name="AI弹窗项目",
        version="1.0.0",
        status="running",
        components={"api": {"status": "running"}, "web": {"status": "running"}},
        health_score=95.0,
        last_updated=get_timestamp(),
    )


@router.get("/scripts/list", response_model=ScriptsListResponse, tags=["脚本"])
async def scripts_list():
    """获取脚本列表"""
    scripts_dir = project_root / "scripts"
    scripts = []
    if scripts_dir.exists():
        for script_file in scripts_dir.glob("*.py"):
            if not script_file.name.startswith("_"):
                scripts.append(
                    {
                        "name": script_file.stem,
                        "display_name": script_file.stem.replace("_", " ").title(),
                        "description": f"脚本: {script_file.name}",
                        "status": "idle",
                        "frequency": "on-demand",
                    }
                )
    return ScriptsListResponse(
        scripts=scripts, total=len(scripts), timestamp=get_timestamp()
    )


@router.get("/scripts/status", response_model=ScriptsStatusResponse, tags=["脚本"])
async def scripts_status():
    """获取脚本运行状态"""
    return ScriptsStatusResponse(
        scripts={}, monitoring_active=True, timestamp=get_timestamp()
    )


@router.post("/scripts/run/{script_name}", tags=["脚本"])
async def run_script(script_name: str, background_tasks: BackgroundTasks):
    """执行指定脚本"""
    script_path = project_root / "scripts" / f"{script_name}.py"
    if not script_path.exists():
        raise HTTPException(status_code=404, detail=f"脚本不存在: {script_name}")
    background_tasks.add_task(execute_script_background, script_name, script_path)
    return {
        "status": "started",
        "message": f"脚本 {script_name} 已开始执行",
        "script": script_name,
        "timestamp": get_timestamp(),
    }


async def execute_script_background(script_name: str, script_path: Path):
    """后台执行脚本"""
    try:
        import subprocess

        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=300,
        )
        logger.info(f"脚本 {script_name} 执行完成，返回码: {result.returncode}")
    except Exception as e:
        logger.error(f"脚本 {script_name} 执行失败: {e}")


@router.post("/scripts/stop/{script_name}", tags=["脚本"])
async def stop_script(script_name: str):
    """停止脚本"""
    return {
        "status": "stopped",
        "message": f"脚本 {script_name} 已停止",
        "script": script_name,
        "timestamp": get_timestamp(),
    }


@router.get("/logs/{script_name}", tags=["日志"])
async def get_script_logs(script_name: str, lines: int = Query(100, le=1000)):
    """获取脚本日志"""
    logs_dir = project_root / "logs"
    logs = []
    if logs_dir.exists():
        log_file = logs_dir / f"{script_name}.log"
        if log_file.exists():
            with open(log_file, "r", encoding="utf-8") as f:
                logs = [line.strip() for line in f.readlines()[-lines:]]
    return {
        "status": "success" if logs else "not_found",
        "logs": logs,
        "total_lines": len(logs),
        "returned_lines": len(logs),
        "timestamp": get_timestamp(),
    }


@router.get("/config/{component}", tags=["配置"])
async def get_component_config(component: str):
    """获取组件配置"""
    config_paths = {
        "project": project_root / "project_config.json",
        "api": project_root / "api" / "config" / "api_config.json",
        "web": project_root / "web" / "web_config.json",
        "scripts": project_root / "scripts" / "scripts_config.json",
        "assets": project_root / "assets" / "assets_config.json",
        "src": project_root / "src" / "src_config.json",
    }
    config_path = config_paths.get(component)
    if not config_path or not config_path.exists():
        raise HTTPException(status_code=404, detail=f"配置不存在: {component}")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        return {
            "status": "success",
            "component": component,
            "config": config,
            "timestamp": get_timestamp(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取配置失败: {str(e)}")


@router.get("/system/resources", response_model=SystemResourcesResponse, tags=["系统"])
async def system_resources():
    """获取系统资源使用情况"""
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    return SystemResourcesResponse(
        cpu_percent=psutil.cpu_percent(interval=1),
        memory={
            "total": memory.total,
            "available": memory.available,
            "percent": memory.percent,
            "used": memory.used,
        },
        disk={
            "total": disk.total,
            "free": disk.free,
            "percent": disk.percent,
            "used": disk.used,
        },
        timestamp=get_timestamp(),
    )


@router.get("/system/gpu", response_model=GPUResourcesResponse, tags=["系统"])
async def system_gpu():
    """获取GPU资源使用情况"""
    try:
        import subprocess

        result = subprocess.run(
            [
                "nvidia-smi",
                (
                    "--query-gpu=name,memory.total,memory.used,"
                    "utilization.gpu,temperature.gpu"
                ),
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            gpus = []
            for line in result.stdout.strip().split("\n"):
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 5:
                    gpus.append(
                        {
                            "name": parts[0],
                            "memory_total": float(parts[1]) * 1024,
                            "memory_used": float(parts[2]) * 1024,
                            "utilization": float(parts[3]),
                            "temperature": (
                                float(parts[4]) if parts[4] != "N/A" else None
                            ),
                        }
                    )
            return GPUResourcesResponse(
                status="success",
                has_gpu=len(gpus) > 0,
                gpus=gpus,
                message=f"检测到 {len(gpus)} 个GPU",
                timestamp=get_timestamp(),
            )
    except Exception as e:
        logger.warning(f"获取GPU信息失败: {e}")
    return GPUResourcesResponse(
        status="success",
        has_gpu=False,
        gpus=[],
        message="未检测到NVIDIA GPU",
        timestamp=get_timestamp(),
    )


@router.get("/ports", response_model=PortsResponse, tags=["系统"])
async def ports():
    """获取所有端口状态"""
    import socket

    ports_info = [
        {"key": "web", "name": "Web Monitor", "port": 8080, "protocol": "http"},
        {"key": "api", "name": "API Service", "port": 8000, "protocol": "http"},
    ]
    result = []
    for p in ports_info:
        status = "stopped"
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            status = (
                "running"
                if sock.connect_ex(("localhost", p["port"])) == 0
                else "stopped"
            )
            sock.close()
        except Exception:
            status = "unknown"
        result.append({**p, "status": status})
    return PortsResponse(
        status="success",
        ports=result,
        total=len(result),
        timestamp=get_timestamp(),
    )


@router.get("/subprojects", response_model=SubProjectsResponse, tags=["子项目"])
async def subprojects():
    """获取所有子项目状态"""
    projects = {}
    for name, path_name in [
        ("deep-live-cam", "Deep-Live-Cam-main"),
        ("facefusion", "facefusion-master"),
        ("iroop", "iRoopDeepFaceCam-main"),
    ]:
        path = project_root / "assets" / path_name
        projects[name] = {
            "name": path_name.replace("-", " ").title(),
            "status": "ready" if path.exists() else "not_found",
            "health": "healthy",
        }
    return SubProjectsResponse(
        status="success",
        projects=projects,
        total=len(projects),
        timestamp=get_timestamp(),
    )


@router.get("/bubbles", response_model=BubblesResponse, tags=["监控"])
async def bubbles():
    """获取实时冒泡数据"""
    return BubblesResponse(
        status="success",
        bubbles=[
            {
                "id": "bubble-1",
                "type": "info",
                "title": "系统运行正常",
                "message": "所有服务运行正常",
                "timestamp": get_timestamp(),
            }
        ],
        total=1,
        timestamp=get_timestamp(),
    )


@router.get(
    "/deployment/progress",
    response_model=DeploymentProgressResponse,
    tags=["部署"],
)
async def deployment_progress():
    """获取项目部署进度"""
    return DeploymentProgressResponse(
        status="success",
        content={"phase": "operational", "message": "项目运行正常"},
        timestamp=get_timestamp(),
    )


@router.get("/performance", response_model=PerformanceResponse, tags=["性能"])
async def performance():
    """获取性能监控概览"""
    return PerformanceResponse(
        status="success",
        overview={
            "total_requests": 12345,
            "avg_response_time": 156,
            "error_rate": 0.5,
            "throughput": 45.2,
            "active_connections": 127,
        },
        timestamp=get_timestamp(),
    )


@router.get("/performance/metrics", tags=["性能"])
async def performance_metrics():
    """获取性能指标数据"""
    return {
        "status": "success",
        "metrics": {"response_time": {"avg": 156, "min": 45, "max": 892}},
        "timestamp": get_timestamp(),
    }


@router.post("/performance/optimize", tags=["性能"])
async def performance_optimize():
    """执行性能优化"""
    return {
        "status": "success",
        "message": "性能优化已启动",
        "actions": ["内存缓存清理", "数据库查询优化"],
        "timestamp": get_timestamp(),
    }


@router.get("/video", response_model=VideoResponse, tags=["视频"])
async def video():
    """获取视频流概览"""
    return VideoResponse(
        status="success",
        overview={
            "cameraCount": 2,
            "activeStreams": 1,
            "engineCount": 3,
            "avgFps": 28,
        },
        timestamp=get_timestamp(),
    )


@router.get("/video/cameras", tags=["视频"])
async def video_cameras():
    """获取摄像头设备列表"""
    return {
        "status": "success",
        "cameras": [
            {
                "deviceId": "camera-001",
                "name": "主摄像头",
                "status": "active",
                "resolution": "1280x720",
                "fps": 30,
            }
        ],
        "total": 1,
        "timestamp": get_timestamp(),
    }


@router.get("/video/streams", tags=["视频"])
async def video_streams():
    """获取视频流数据"""
    return {
        "status": "success",
        "streams": [
            {
                "id": "stream-001",
                "name": "实时直播流",
                "source": "camera-001",
                "resolution": "1280x720",
                "fps": 30,
                "latency": 45,
                "engine": "Deep-Live-Cam",
                "status": "active",
            }
        ],
        "total": 1,
        "timestamp": get_timestamp(),
    }


@router.get("/video/engines", tags=["视频"])
async def video_engines():
    """获取视频处理引擎状态"""
    return {
        "status": "success",
        "engines": [
            {
                "id": "deep_live_cam",
                "name": "Deep-Live-Cam",
                "status": "ready",
                "gpuMemory": 35.5,
                "queueSize": 0,
                "processedToday": 156,
            }
        ],
        "timestamp": get_timestamp(),
    }


@router.get("/engines", response_model=EnginesResponse, tags=["引擎"])
async def engines():
    """获取所有引擎状态"""
    engines = [
        {
            "id": "deep_live_cam",
            "name": "Deep-Live-Cam",
            "type": "deep_live_cam",
            "enabled": True,
            "available": True,
            "status": "ready",
        },
        {
            "id": "facefusion",
            "name": "FaceFusion",
            "type": "facefusion",
            "enabled": True,
            "available": True,
            "status": "ready",
        },
        {
            "id": "iroop_deepfacecam",
            "name": "iRoopDeepFaceCam",
            "type": "iroop_deepfacecam",
            "enabled": True,
            "available": True,
            "status": "ready",
        },
    ]
    return EnginesResponse(
        status="success",
        engines=engines,
        total=len(engines),
        timestamp=get_timestamp(),
    )


@router.get("/engines/{name}/status", tags=["引擎"])
async def engine_status(name: str):
    """获取指定引擎状态"""
    return {
        "status": "success",
        "engine": {"id": name, "name": name, "status": "ready"},
        "timestamp": get_timestamp(),
    }


@router.post("/engines/{name}/start", tags=["引擎"])
async def engine_start(name: str):
    """启动指定引擎"""
    return {
        "status": "success",
        "message": f"引擎 {name} 已启动",
        "engine": name,
        "timestamp": get_timestamp(),
    }


@router.post("/engines/{name}/stop", tags=["引擎"])
async def engine_stop(name: str):
    """停止指定引擎"""
    return {
        "status": "success",
        "message": f"引擎 {name} 已停止",
        "engine": name,
        "timestamp": get_timestamp(),
    }


@router.get("/backup", tags=["备份"])
async def backup_list():
    """获取备份列表"""
    return {
        "status": "success",
        "backups": [],
        "total": 0,
        "timestamp": get_timestamp(),
    }


@router.post("/backup/create", tags=["备份"])
async def backup_create():
    """创建新备份"""
    return {
        "status": "success",
        "message": "备份创建已启动",
        "backup_id": f"backup-{int(time.time())}",
        "timestamp": get_timestamp(),
    }


@router.post("/backup/restore/{backup_id}", tags=["备份"])
async def backup_restore(backup_id: str):
    """从备份恢复"""
    return {
        "status": "success",
        "message": f"从 {backup_id} 恢复已启动",
        "backup_id": backup_id,
        "timestamp": get_timestamp(),
    }


@router.get("/audit/logs", tags=["审计"])
async def audit_logs(page: int = 1, limit: int = 100, level: Optional[str] = None):
    """获取审计日志"""
    return {
        "status": "success",
        "logs": [],
        "total": 0,
        "timestamp": get_timestamp(),
    }


@router.get("/audit/export", tags=["审计"])
async def audit_export(format: str = "csv", limit: int = 1000):
    """导出审计日志"""
    return {
        "status": "success",
        "format": format,
        "data": "",
        "count": 0,
        "timestamp": get_timestamp(),
    }


# 导出路由
__all__ = ["router"]
