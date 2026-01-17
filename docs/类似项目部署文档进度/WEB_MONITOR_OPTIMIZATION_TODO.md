# Web端项目监控优化任务清单

## 项目概述
**目标**: 针对在web呈现整个项目监控，对整个项目的内容进行优化建议
**创建时间**: 2025-01-21
**计划文档**: /workspaces/AISP/docs/WEB_MONITOR_OPTIMIZATION_PLAN.md

---

## 任务状态说明
- [ ] 未开始
- [x] 进行中
- [ ] 已完成
- [ ] 已跳过
- [ ] 被阻塞

---

## 阶段1: 后端增强 (优先级: 高)

### 1.1 监控数据持久化
- [ ] 1.1.1 创建 `backend/services/monitor_storage.py`
  - [ ] SQLite数据库初始化
  - [ ] 性能指标存储结构设计
  - [ ] 性能指标保存方法 `save_metrics()`
  - [ ] 历史数据查询方法 `get_history()`
  - [ ] 报警历史存储方法

### 1.2 健康评分系统
- [ ] 1.2.1 创建 `backend/services/health_scoring.py`
  - [ ] 健康评分算法设计
  - [ ] 权重配置 (CPU/Memory/GPU/FPS/Disk)
  - [ ] 计算健康评分方法 `calculate_score()`
  - [ ] 健康等级判定方法 `get_health_level()`
  - [ ] 详细健康报告生成

### 1.3 API端点优化
- [ ] 1.3.1 更新 `backend/unified_api.py`
  - [ ] 新增 `/web/api/dashboard` 端点 (合并12个端点)
  - [ ] 新增 `/web/api/health` 端点
  - [ ] 优化 `/web/api/history` 端点 (使用真实数据)
  - [ ] 集成监控存储服务
  - [ ] 集成健康评分服务

---

## 阶段2: WebSocket支持 (优先级: 高)

### 2.1 WebSocket处理器
- [ ] 2.1.1 创建 `backend/services/monitor_ws.py`
  - [ ] WebSocket路由定义
  - [ ] 连接管理 (连接/断开/心跳)
  - [ ] 消息广播方法
  - [ ] 监控推送循环
  - [ ] 自动重连机制

### 2.2 后端集成
- [ ] 2.2.1 更新 `backend/unified_api.py`
  - [ ] 注册WebSocket端点 `/ws/monitor`
  - [ ] 添加startup事件初始化WebSocket服务
  - [ ] 添加shutdown事件清理连接
  - [ ] 集成性能监控推送

---

## 阶段3: 前端优化 (优先级: 中)

### 3.1 WebSocket客户端
- [ ] 3.1.1 创建 `web/static/js/websocket.js`
  - [ ] WebSocket客户端类封装
  - [ ] 自动重连机制 (指数退避)
  - [ ] 消息处理器 (metrics/alert/health)
  - [ ] 连接状态管理
  - [ ] 与EventBus集成

### 3.2 API模块更新
- [ ] 3.2.1 更新 `web/static/js/api.js`
  - [ ] 新增 `dashboardAPI` 模块
  - [ ] 新增 `healthAPI` 模块
  - [ ] 优化现有监控API

### 3.3 应用集成
- [ ] 3.3.1 更新 `web/static/js/app.js`
  - [ ] 集成WebSocket客户端
  - [ ] 添加健康评分展示
  - [ ] 添加实时报警面板
  - [ ] 实现自适应刷新频率
  - [ ] 优化数据加载逻辑

---

## 阶段4: 图表增强 (优先级: 中)

### 4.1 图表组件新增
- [ ] 4.1.1 更新 `web/static/js/charts.js`
  - [ ] 新增实时性能趋势图 `RealtimeChart`
  - [ ] 新增资源使用热力图 `ResourceHeatmap`
  - [ ] 新增健康评分环形图
  - [ ] 优化现有图表渲染性能
  - [ ] 添加图表动画效果

### 4.2 前端模板更新
- [ ] 4.2.1 更新 `web/templates/index.html`
  - [ ] 添加健康评分组件
  - [ ] 添加报警通知面板
  - [ ] 优化整体布局
  - [ ] 添加实时数据指示器
  - [ ] 优化移动端响应式布局

---

## 阶段5: 测试与文档 (优先级: 低)

### 5.1 功能测试
- [ ] 5.1.1 API测试
  - [ ] 测试 `/web/api/dashboard` 端点
  - [ ] 测试 `/web/api/health` 端点
  - [ ] 测试 `/web/api/history` 端点
  - [ ] 测试历史数据查询准确性
- [ ] 5.1.2 WebSocket测试
  - [ ] 测试连接建立
  - [ ] 测试实时消息推送
  - [ ] 测试自动重连
- [ ] 5.1.3 前端功能测试
  - [ ] 测试健康评分显示
  - [ ] 测试实时数据更新
  - [ ] 测试报警通知
  - [ ] 测试自适应刷新

### 5.2 性能测试
- [ ] 5.2.1 性能指标测试
  - [ ] 页面加载时间 < 2s
  - [ ] 数据刷新延迟 < 1s
  - [ ] 内存占用 < 100MB
  - [ ] WebSocket连接稳定性

### 5.3 文档更新
- [ ] 5.3.1 更新相关文档
  - [ ] 更新 `docs/README.md` 添加监控优化说明
  - [ ] 更新 `docs/健康监控启动配置.md`
  - [ ] 添加API文档注释

---

## 依赖更新

### requirements.txt
- [ ] 确认 `websockets>=10.0` 已添加 (如需要)

---

## 验证检查清单

### 启动验证
- [ ] 后端服务启动正常
- [ ] WebSocket服务正常运行
- [ ] 前端页面加载正常

### 功能验证
- [ ] 综合仪表盘数据正确显示
- [ ] 健康评分准确计算
- [ ] 实时数据推送正常
- [ ] 报警通知正常工作
- [ ] 历史数据查询正常

### 性能验证
- [ ] HTTP请求数减少
- [ ] 数据刷新延迟降低
- [ ] 内存占用在合理范围
- [ ] WebSocket连接稳定

---

## 任务追踪

### 已完成任务
- [x] 2025-01-21: 创建优化计划文档
- [x] 2025-01-21: 开始实施优化计划
- [x] 阶段1: 后端增强
  - [x] 创建 `backend/services/monitor_storage.py` - 监控数据持久化
  - [x] 创建 `backend/services/health_scoring.py` - 健康评分器
  - [x] 创建 `backend/services/monitor_ws.py` - WebSocket处理器
- [x] 阶段2: 前端增强
  - [x] 创建 `web/static/js/websocket.js` - WebSocket客户端
  - [x] 更新 `web/static/js/store.js` - 状态管理增强

### 当前状态
- 正在进行: 更新 `backend/unified_api.py` 集成新API端点

### 待完成任务
- [ ] 更新 `backend/unified_api.py` - 集成新API端点 (dashboard, health)
- [ ] 更新 `web/templates/index.html` - 添加健康评分UI组件
- [ ] 更新 `web/static/js/app.js` - 集成WebSocket客户端
- [ ] 更新 `web/static/js/charts.js` - 添加实时图表
- [ ] 功能测试与验证

---

## 备注

### 阻塞项
- 无

### 已知问题
- 无

### 后续优化方向
- 添加告警规则自定义功能
- 支持多用户并发监控
- 添加监控数据导出功能
- 集成Grafana可视化

