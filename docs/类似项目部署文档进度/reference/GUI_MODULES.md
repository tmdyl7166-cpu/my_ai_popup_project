# GUI 模块功能说明

> AISP 图形界面层功能详解
> 
> 文档版本: 1.0.0
> 最后更新: 2025-01-21

---

## 模块结构

```
gui/
├── main_window.py             # 主窗口 ⭐
├── api_config.py              # API配置
├── dialogs/                   # 弹窗模块
│   ├── __init__.py
│   └── ar_config_dialog.py    # AR配置对话框
├── services/                  # GUI服务层 ⭐
│   ├── __init__.py
│   └── api_service.py         # API服务封装
└── widgets/                   # 自定义控件
    ├── __init__.py
    ├── ar_engine.py           # AR引擎控件
    └── live_streaming.py      # 直播控件
```

---

## 主窗口 (main_window.py)

**功能**: PyQt6主窗口，提供用户交互界面

**特性**:
- PyQt6 + PyQtGraph集成
- 实时视频显示
- 任务队列面板
- 日志面板

### 主要区域

| 区域 | 组件 | 说明 |
|------|------|------|
| 菜单栏 | QMenuBar | 文件、编辑、视图、帮助 |
| 工具栏 | QToolBar | 常用操作快捷按钮 |
| 视频显示 | VideoViewer | 实时视频/摄像头画面 |
| 任务面板 | TaskPanel | 任务队列UI |
| 状态栏 | QStatusBar | 系统状态显示 |

### 菜单结构

```
文件(F)
├── 新建项目
├── 打开项目
├── 保存配置
├── 退出

编辑(E)
├── 偏好设置
├── 快捷键配置

视图(V)
├── 工具栏
├── 状态栏
├── 日志面板
└── 任务面板

工具(T)
├── AI策略
├── 引擎选择
└── 性能监控

帮助(H)
├── 文档
├── 关于
└── 检查更新
```

---

## 弹窗模块 (dialogs/)

### ar_config_dialog.py - AR配置对话框

**功能**: 配置AR引擎参数

**配置项**:
- 引擎选择 (Deep-Live-Cam, FaceFusion, iRoop)
- 参数调节
- 预览设置

---

## 服务层 (services/)

### api_service.py - API服务封装 ⭐

**功能**: 封装后端API调用

**方法**:

| 方法 | 端点 | 说明 |
|------|------|------|
| `get_status()` | GET /api/status | 获取系统状态 |
| `get_camera_status()` | GET /api/camera/status | 摄像头状态 |
| `start_camera()` | POST /api/camera/start | 启动摄像头 |
| `stop_camera()` | POST /api/camera/stop | 停止摄像头 |
| `detect_faces()` | POST /api/recognition/detect | 人脸检测 |
| `compose_images()` | POST /api/recognition/compose | 图片合成 |
| `get_ar_engines()` | GET /api/ar/engines | 获取引擎列表 |
| `start_ar()` | POST /api/ar/start | 启动AR引擎 |
| `stop_ar()` | POST /api/ar/stop | 停止AR引擎 |

---

## 自定义控件 (widgets/)

### ar_engine.py - AR引擎控件

**功能**: 显示AR引擎状态和控制

### live_streaming.py - 直播控件

**功能**: 直播流显示和控制

---

## API配置 (api_config.py)

**功能**: 统一管理GUI的API端点配置

**配置结构**:
```python
API_CONFIG = {
    "base_url": "http://localhost:8000",
    "endpoints": {
        "status": "/api/status",
        "camera": "/api/camera/status",
        # ...
    }
}
```

---

## 相关文档

- [项目结构说明](../guide/项目结构说明.md) - 整体结构
- [用户功能模块内容](../guide/用户功能模块内容.md) - 功能详情
- [统一接口](../guide/统一接口.md) - API端点

---

*文档版本: 1.0.0*
*最后更新: 2025-01-21*

