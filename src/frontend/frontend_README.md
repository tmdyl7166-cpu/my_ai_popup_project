# Frontend 前端模块说明文档

## 概述

Frontend 模块是 AI 弹窗项目的用户界面层，基于 PyQt5 框架构建，提供直观的图形化操作界面。该模块负责用户交互、界面展示、状态监控和与后端服务的通信，实现人脸合成与视频处理平台的完整用户体验。

## 目录结构

```
src/frontend/
├── __init__.py                    # 模块初始化文件
├── frontend_config.json          # 前端界面配置定义文件
├── frontend_README.md            # 前端模块说明文档（本文件）
├── components/                   # UI组件目录
│   └── progress_bar.py           # 进度条组件
├── styles/                       # 样式定义目录
│   └── __init__.py               # 样式模块初始化
├── main_window.py                # 主窗口类（计划中）
└── popup_window.py               # 弹窗窗口类（计划中）
```

## 核心功能

### 1. 主窗口 (MainWindow)

**功能描述：**
- 应用程序的主界面窗口
- 包含多标签页布局（首页、处理、监控、设置）
- 集成侧边栏、工具栏和状态栏
- 支持文件拖拽上传
- 实时显示处理进度和系统状态

**主要特性：**
- 响应式布局设计
- 深色/浅色主题切换
- 键盘快捷键支持
- 多线程处理避免界面冻结

### 2. 弹窗窗口 (PopupWindow)

**功能描述：**
- 提供临时性的用户交互界面
- 显示处理结果预览
- 错误信息提示
- 进度详情展示

**应用场景：**
- 处理完成通知
- 错误告警显示
- 用户确认对话框
- 详细进度查看

### 3. 进度条组件 (ProgressBar)

**功能描述：**
- 可视化显示任务执行进度
- 支持取消操作
- 显示详细处理信息
- 自动适应不同界面尺寸

**特性：**
- 实时进度更新
- 详细信息展示
- 用户可取消操作
- 样式可定制

## 技术架构

### UI框架
- **框架：** PyQt5 5.15+
- **主题：** 支持深色/浅色/自动主题
- **布局：** 响应式网格布局
- **组件：** 自定义组件库

### 界面配置

#### 窗口配置
```json
{
  "window": {
    "title": "AI弹窗项目 - 智能人脸合成与视频处理平台",
    "defaultSize": {"width": 1280, "height": 720},
    "minSize": {"width": 800, "height": 600},
    "position": "center"
  }
}
```

#### 主题配置
- **主色调：** #007bff (蓝色)
- **背景色：** #1a1a1a (深色主题)
- **文字色：** #ffffff (白色)
- **支持高对比度模式**

### 标签页结构

1. **首页标签页**
   - 欢迎信息展示
   - 快速操作入口
   - 最近项目列表

2. **处理标签页**
   - 文件选择和上传
   - 处理参数配置
   - 任务队列管理
   - 实时预览

3. **监控标签页**
   - 系统资源监控
   - 处理任务状态
   - 性能指标图表
   - 日志实时查看

4. **设置标签页**
   - 界面主题设置
   - 处理参数配置
   - 系统偏好设置
   - 高级选项

## 通信机制

### 后端通信

**HTTP API通信：**
- **协议：** HTTP
- **主机：** localhost:8000
- **基础路径：** /api/v1
- **超时时间：** 30秒
- **重试机制：** 3次重试，1秒间隔

**WebSocket通信：**
- **启用状态：** 是
- **地址：** ws://localhost:8000/ws
- **自动重连：** 是
- **心跳间隔：** 30秒

### 数据格式
- **请求格式：** JSON
- **响应格式：** JSON
- **字符编码：** UTF-8

## 交互特性

### 快捷键支持

**全局快捷键：**
- `Ctrl+O`：打开文件
- `Ctrl+N`：新建项目
- `Ctrl+S`：保存
- `Ctrl+Q`：退出
- `F11`：全屏
- `F5`：刷新

**处理快捷键：**
- `F9`：开始处理
- `F10`：暂停处理
- `F12`：停止处理
- `Space`：预览

### 拖拽上传
- **支持格式：** 图片(*.jpg, *.jpeg, *.png, *.bmp)，视频(*.mp4, *.avi, *.mov)
- **最大文件数：** 10个
- **最大总大小：** 1GB
- **预览功能：** 支持拖拽预览

### 上下文菜单

**文件列表菜单：**
- 打开文件
- 预览文件
- 删除文件
- 查看属性

**任务队列菜单：**
- 开始任务
- 暂停任务
- 取消任务
- 设置优先级

## 性能优化

### 渲染优化
- **双缓冲：** 启用
- **硬件加速：** 启用
- **垂直同步：** 启用
- **最大帧率：** 60 FPS

### 内存管理
- **图片缓存：** 100MB
- **预览缓存：** 50MB
- **自动清理：** 启用
- **清理间隔：** 5分钟

### 多线程处理
- **UI线程：** 主线程
- **工作线程：** 2个
- **最大并发：** 4个操作

## 无障碍访问

### 辅助功能
- **键盘导航：** 启用
- **屏幕阅读器：** 支持
- **高对比度：** 可选
- **字体大小：** 可调节（小/中/大）
- **语言：** 中文简体

## 日志和错误处理

### 日志配置
- **启用状态：** 是
- **日志级别：** INFO
- **日志文件：** logs/frontend.log
- **最大大小：** 10MB
- **备份数量：** 5个

### 错误处理
- **错误对话框：** 显示
- **自动上报：** 关闭（隐私保护）
- **用户友好消息：** 启用
- **恢复选项：** 提供
- **错误记录：** 启用

## 开发指南

### 环境要求
- **Python：** 3.7+
- **PyQt5：** 5.15+
- **操作系统：** Windows 10+, macOS 10.15+, Ubuntu 18.04+

### 安装依赖
```bash
pip install PyQt5
pip install qss-themes  # 主题支持
```

### 运行界面
```python
from src.frontend import MainWindow
import sys
from PyQt5.QtWidgets import QApplication

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
```

### 组件开发

**创建新组件的步骤：**
1. 在 `components/` 目录创建组件文件
2. 继承相应的 PyQt5 基类
3. 实现必要的信号和槽
4. 在配置文件中注册组件
5. 更新样式定义

**示例组件结构：**
```python
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import pyqtSignal

class CustomWidget(QWidget):
    # 定义信号
    valueChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        # 添加组件...
        self.setLayout(layout)
```

### 样式定制

**QSS样式文件：**
```css
/* styles/custom.qss */
QWidget {
    background-color: #2d2d2d;
    color: #ffffff;
}

QPushButton {
    background-color: #007bff;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
}

QPushButton:hover {
    background-color: #0056b3;
}
```

**动态样式应用：**
```python
from PyQt5.QtWidgets import QApplication

# 加载样式
with open('src/frontend/styles/custom.qss', 'r') as f:
    style = f.read()
    QApplication.instance().setStyleSheet(style)
```

## 测试和调试

### 单元测试
```bash
# 运行前端组件测试
python -m pytest tests/test_frontend/ -v
```

### 界面调试
- 使用 Qt Designer 设计界面
- 启用调试模式查看组件层次
- 检查信号-槽连接
- 验证样式应用

### 性能分析
- 使用 QTimer 测量响应时间
- 监控内存使用情况
- 检查 UI 线程阻塞

## 部署和分发

### 打包应用
```bash
# 使用 PyInstaller 打包
pyinstaller --onefile --windowed main.py
```

### 跨平台支持
- **Windows：** .exe 文件
- **macOS：** .app 包
- **Linux：** AppImage

### 配置管理
- 配置文件随应用分发
- 用户设置本地存储
- 自动更新机制

## 维护和更新

### 版本管理
- 遵循语义化版本控制
- 维护向后兼容性
- 定期更新依赖

### 用户反馈
- 收集使用统计
- 处理错误报告
- 实现功能请求

### 文档更新
- 保持 API 文档同步
- 更新用户指南
- 维护变更日志

---

*最后更新时间：2024-01-16*
*版本：1.0.0*
*框架：PyQt5 5.15+*
