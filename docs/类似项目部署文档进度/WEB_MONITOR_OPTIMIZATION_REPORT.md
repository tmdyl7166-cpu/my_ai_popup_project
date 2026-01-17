# Web端项目监控优化实施报告

## 一、实施概述

**任务目标**: 针对在web呈现整个项目监控，对整个项目的内容进行优化建议
**实施时间**: 2025-01-21
**项目路径**: /workspaces/AISP

---

## 二、实施内容

### 2.1 新增后端模块

#### 2.1.1 监控数据持久化 (`backend/services/monitor_storage.py`)
```
功能:
├── SQLite数据库存储
│   ├── metrics 表 - 性能指标历史
│   ├── health_records 表 - 健康评分记录
│   ├── alerts 表 - 报警历史
│   └── system_info 表 - 系统静态信息
├── 数据查询
│   ├── get_metrics() - 性能指标查询
│   ├── get_history() - 健康评分历史
│   ├── get_alerts() - 报警记录查询
│   └── get_health_trend() - 健康趋势分析
└── 数据维护
    ├── 自动清理过期数据
    ├── 数据库压缩
    └── 存储统计
```

#### 2.1.2 健康评分器 (`backend/services/health_scoring.py`)
```
功能:
├── 综合健康评分 (0-100)
│   ├── CPU评分 (权重25%)
│   ├── 内存评分 (权重25%)
│   ├── GPU评分 (权重20%)
│   ├── FPS评分 (权重20%)
│   └── 磁盘评分 (权重10%)
├── 健康等级
│   ├── excellent (90-100) 🟢 优秀
│   ├── good (75-90) 🔵 良好
│   ├── fair (60-75) 🟡 一般
│   ├── poor (40-60) 🟠 较差
│   └── critical (0-40) 🔴 严重
├── 趋势分析
│   ├── analyze_trend() - 趋势计算
│   └── generate_report() - 详细报告
└── 阈值配置
    ├── 可自定义各指标阈值
    └── 可调整权重比例
```

#### 2.1.3 WebSocket处理器 (`backend/services/monitor_ws.py`)
```
功能:
├── 连接管理
│   ├── ConnectionManager - 连接池管理
│   ├── 自动心跳检测
│   └── 连接状态追踪
├── 消息处理
│   ├── broadcast() - 广播消息
│   ├── send_personal() - 发送个人消息
│   └── 消息类型路由
└── 事件推送
    ├── metrics_update - 性能指标更新
    ├── alert - 报警事件
    └── health_change - 健康状态变更
```

### 2.2 新增前端模块

#### 2.2.1 WebSocket客户端 (`web/static/js/websocket.js`)
```
功能:
├── 连接管理
│   ├── 自动重连 (指数退避)
│   ├── 心跳机制
│   └── 状态追踪
├── 消息处理
│   ├── 消息类型分发
│   ├── 错误处理
│   └── 数据解析
└── EventBus集成
    ├── ws:connected - 连接成功
    ├── ws:metrics - 收到指标
    ├── ws:health - 收到健康状态
    └── ws:alert - 收到报警
```

#### 2.2.2 状态管理增强 (`web/static/js/store.js`)
```
新增功能:
├── 性能指标管理
│   ├── updateMetrics() - 更新指标
│   ├── getChartData() - 获取图表数据
│   └── 历史数据追踪
├── 健康状态管理
│   ├── updateHealth() - 更新健康状态
│   ├── getHealthTrend() - 获取健康趋势
│   └── 历史记录存储
├── 报警管理
│   ├── addAlert() - 添加报警
│   ├── acknowledgeAlert() - 确认报警
│   ├── clearAlerts() - 清除报警
│   └── getUnacknowledgedCount() - 未确认数量
└── 图表数据缓存
    ├── 自动缓存60个数据点
    ├── 实时数据更新
    └── 性能优化
```

---

## 三、文件变更清单

### 新增文件
| 文件路径 | 描述 | 行数 |
|---------|------|------|
| `backend/services/monitor_storage.py` | 监控数据持久化模块 | ~850 |
| `backend/services/health_scoring.py` | 健康评分计算模块 | ~630 |
| `backend/services/monitor_ws.py` | WebSocket处理器 | ~410 |
| `web/static/js/websocket.js` | WebSocket客户端 | ~350 |

### 修改文件
| 文件路径 | 修改内容 |
|---------|---------|
| `web/static/js/store.js` | 添加监控专用方法、报警管理 |

### 文档文件
| 文件路径 | 描述 |
|---------|------|
| `docs/WEB_MONITOR_OPTIMIZATION_PLAN.md` | 详细优化计划 |
| `docs/WEB_MONITOR_OPTIMIZATION_TODO.md` | 任务清单追踪 |

---

## 四、待完成任务

### 4.1 后端API集成
- [ ] 更新 `backend/unified_api.py`
  - 新增 `/web/api/dashboard` 端点 (合并监控数据)
  - 新增 `/web/api/health` 端点 (健康评分)
  - 集成 `monitor_storage.py`
  - 集成 `health_scoring.py`
  - 集成 `monitor_ws.py`

### 4.2 前端UI增强
- [ ] 更新 `web/templates/index.html`
  - 添加健康评分环形图组件
  - 添加实时报警面板
  - 优化布局
- [ ] 更新 `web/static/js/app.js`
  - 集成WebSocket客户端
  - 添加自适应刷新逻辑
- [ ] 更新 `web/static/js/charts.js`
  - 添加实时趋势图
  - 添加资源使用热力图

### 4.3 测试验证
- [ ] API端点测试
- [ ] WebSocket连接测试
- [ ] 健康评分计算验证
- [ ] 报警功能测试
- [ ] 性能测试

---

## 五、预期效果

### 5.1 功能增强
| 功能 | 优化前 | 优化后 |
|-----|-------|-------|
| 数据刷新 | 5秒轮询 | 实时推送 (<1秒) |
| 历史数据 | 无 | 7天存储 |
| 健康评分 | 无 | 0-100综合评分 |
| 报警通知 | 无 | 实时推送+浏览器通知 |
| 趋势分析 | 无 | 历史趋势图表 |

### 5.2 性能优化
| 指标 | 优化前 | 优化后 |
|-----|-------|-------|
| HTTP请求数 | 12个/次 | 1个/次 |
| 数据传输 | 重复采集 | 增量推送 |
| 连接方式 | 短连接轮询 | WebSocket长连接 |
| 前端响应 | 延迟5秒 | 实时更新 |

---

## 六、使用说明

### 6.1 启动监控服务
```bash
# 启动后端服务 (包含监控API)
python -m backend.unified_api

# 启动Web服务
python -m web.web_api
```

### 6.2 访问监控页面
```
http://localhost:8080
```

### 6.3 WebSocket连接
```javascript
// 前端自动连接
const ws = new WebSocket('ws://localhost:8000/ws/monitor');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(data.type, data.data);
};
```

---

## 七、后续优化方向

1. **监控数据导出** - 支持CSV/JSON导出
2. **告警规则自定义** - 用户配置告警阈值
3. **多用户并发** - WebSocket多客户端支持
4. **Grafana集成** - 对接专业可视化工具
5. **性能基线** - 建立性能基准线对比

---

**报告生成时间**: 2025-01-21
**版本**: 1.0
**状态**: 实施中

