# AI弹窗项目Web监控中心

统一的Web管理员界面，用于监控和管理AI弹窗项目的各个组件、脚本执行状态、部署进度和系统资源。

## 功能特性

### 📊 实时监控
- **脚本状态监控**: 实时显示所有自动化脚本的运行状态
- **系统资源监控**: CPU、内存、磁盘使用情况实时更新
- **部署进度跟踪**: 各组件部署状态和配置进度

### 🔧 管理功能
- **脚本控制**: 启动、停止、重启自动化脚本
- **配置管理**: 在线查看和编辑项目配置
- **日志查看**: 实时查看脚本执行日志和系统日志

### 🌐 Web界面
- **响应式设计**: 支持桌面和移动设备
- **实时更新**: WebSocket实时推送状态变化
- **直观界面**: 现代化的Bootstrap UI设计

## 快速开始

### 1. 安装依赖

```bash
# 方式1: 自动安装并启动
python web/start_monitor.py --auto-install

# 方式2: 手动安装
pip install -r web/requirements.txt
python web/start_monitor.py
```

### 2. 访问界面

启动成功后，在浏览器中访问：
```
http://localhost:8080
```

## 界面说明

### 主仪表板
- **系统状态**: 显示项目整体运行状态
- **资源监控**: 实时显示CPU、内存、磁盘使用率
- **快速操作**: 常用功能的快捷按钮

### 脚本监控标签页
- **脚本列表**: 显示所有自动化脚本及其状态
- **操作按钮**:
  - ▶️ 运行脚本
  - ℹ️ 查看详情
  - 📄 查看日志
- **状态指示器**:
  - 🔵 运行中
  - 🟢 已完成
  - 🔴 失败
  - ⚪ 空闲

### 部署进度标签页
- 显示项目各组件的部署状态
- 配置验证结果
- 依赖检查状态

### 配置管理标签页
- **项目配置**: 整体项目设置
- **前端配置**: UI相关配置
- **后端配置**: API服务配置
- **脚本配置**: 自动化脚本配置

### 日志查看标签页
- 选择脚本查看对应日志
- 实时日志更新
- 日志搜索和过滤

## API接口

### REST API

#### 健康检查
```http
GET /api/health
```

#### 项目状态
```http
GET /api/project/status
```

#### 脚本管理
```http
GET  /api/scripts/list          # 获取脚本列表
GET  /api/scripts/status        # 获取脚本状态
POST /api/scripts/run/{name}    # 运行脚本
POST /api/scripts/stop/{name}   # 停止脚本
```

#### 配置管理
```http
GET    /api/config/{component}     # 获取配置
POST   /api/config/{component}     # 更新配置
```

#### 日志查看
```http
GET /api/logs/{script_name}?lines=100
```

#### 系统资源
```http
GET /api/system/resources
```

#### 部署进度
```http
GET /api/deployment/progress
```

### WebSocket

#### 监控连接
```javascript
const socket = io();
socket.on('status_update', (data) => {
    console.log('状态更新:', data);
});
```

## 脚本架构

### 独立脚本设计
每个监控功能都是独立的Python脚本，可以单独运行：

```
scripts/health_monitor/
├── health_monitor.py        # 主健康检查
├── config_validator.py      # 配置验证
├── docs_sync_monitor.py     # 文档同步
└── ui_interaction_monitor.py # UI交互检测
```

### 脚本配置
所有脚本的配置集中管理在 `scripts/scripts_config.json`：

```json
{
  "executionRules": {
    "scheduling": {
      "daily": {
        "time": "02:00",
        "scripts": ["health_monitor.py", "config_validator.py"]
      }
    }
  }
}
```

## 部署选项

### 开发环境
```bash
python web/start_monitor.py --host 127.0.0.1 --port 3000
```

### 生产环境
```bash
# 使用反向代理（如Nginx）
# 配置SSL证书
# 设置系统服务
```

### Docker部署
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . .

RUN pip install -r web/requirements.txt

EXPOSE 8080
CMD ["python", "web/start_monitor.py", "--host", "0.0.0.0"]
```

## 安全考虑

### 访问控制
- 默认绑定到 `0.0.0.0`，生产环境建议配置防火墙
- 考虑添加身份验证机制
- API接口需要适当的权限控制

### 数据安全
- 日志文件不包含敏感信息
- 配置数据在传输过程中需要加密
- 定期清理临时文件和缓存

## 故障排除

### 常见问题

#### 端口占用
```bash
# 检查端口使用情况
netstat -tulpn | grep :8080

# 更换端口
python web/start_monitor.py --port 8081
```

#### 依赖安装失败
```bash
# 升级pip
pip install --upgrade pip

# 使用国内源
pip install -r web/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

#### WebSocket连接失败
- 检查防火墙设置
- 确认浏览器支持WebSocket
- 查看浏览器控制台错误信息

### 日志位置
- 应用日志: `logs/web_app.log`
- 脚本日志: `logs/{script_name}.log`
- 系统日志: 根据操作系统配置

## 扩展开发

### 添加新的监控脚本
1. 在 `scripts/health_monitor/` 创建新的脚本
2. 在 `scripts/scripts_config.json` 中注册
3. 在 `web/app.py` 中添加对应的API路由
4. 更新前端界面

### 自定义界面主题
修改 `web/static/css/custom.css` 中的样式变量。

### 添加新的API接口
在 `web/app.py` 中添加新的路由处理函数。

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 发起Pull Request

## 许可证

本项目采用MIT许可证。
