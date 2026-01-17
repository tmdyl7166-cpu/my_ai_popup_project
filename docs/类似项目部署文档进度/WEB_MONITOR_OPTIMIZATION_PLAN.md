# Web端项目监控优化计划

## 一、现状分析

### 1.1 当前监控架构
```
┌─────────────────────────────────────────────────────────────────┐
│                      Web 前端层 (Vue.js + ECharts)               │
│  - index.html: 主页面模板                                       │
│  - api.js: API调用封装                                          │
│  - charts.js: 图表组件                                          │
│  - store.js: 状态管理                                           │
└─────────────────────────────────────────────────────────────────┘
                              ↑
                              │ HTTP轮询 (5秒间隔)
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Web API层 (web/web_api.py)                    │
│  - API代理到后端统一API                                          │
│  - 12个监控端点代理                                              │
└─────────────────────────────────────────────────────────────────┘
                              ↑
                              │ HTTP
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  后端统一API (backend/unified_api.py)            │
│  - /web/api/status        → 监控状态                            │
│  - /web/api/full-status   → 完整状态                            │
│  - /web/api/dependencies  → 依赖状态                            │
│  - /web/api/system        → 系统资源                            │
│  - /web/api/processes     → 进程状态                            │
│  - /web/api/business      → 业务模块                            │
│  - /web/api/output        → 输出模块                            │
│  - /web/api/engines       → 引擎详情                            │
│  - /web/api/summary       → 摘要信息                            │
│  - /web/api/layers        → 项目层级                            │
│  - /web/api/history       → 历史数据(模拟)                      │
└─────────────────────────────────────────────────────────────────┘
                              ↑
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                 性能监控 (backend/services/                      │
│                 performance_monitor.py)                         │
│  - FPS监控                                                        │
│  - CPU/GPU使用率                                                 │
│  - 内存使用率                                                     │
│  - 自动降级策略                                                   │
│  - 报警阈值管理                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 存在的问题

| 问题类别 | 具体问题 | 影响 |
|---------|---------|------|
| 实时性 | 无WebSocket推送，依赖轮询 | 延迟高、资源浪费 |
| 数据持久化 | 监控数据不持久化 | 无法查询历史趋势 |
| 报警系统 | 前端无实时报警通知 | 问题发现滞后 |
| 健康评分 | 无综合健康评分 | 状态不直观 |
| API设计 | 端点过多(12个) | 维护困难、请求频繁 |
| 图表刷新 | 固定5秒刷新 | 无法自适应变化 |
| 资源占用 | 重复采集相同数据 | 性能浪费 |

---

## 二、优化目标

### 2.1 功能增强
1. **WebSocket实时推送** - 报警和状态变更实时通知
2. **历史数据持久化** - SQLite存储，支持趋势分析
3. **健康评分系统** - 综合评分+详细指标
4. **智能报警** - 分级报警、报警历史
5. **自适应刷新** - 根据状态动态调整刷新频率

### 2.2 性能优化
1. **减少HTTP请求** - 合并API端点
2. **数据压缩** - 减少传输数据量
3. **懒加载** - 按需加载监控数据
4. **连接复用** - WebSocket长连接

---

## 三、优化方案

### 3.1 新增后端模块

#### 3.1.1 监控数据持久化
```python
# backend/services/monitor_storage.py
class MonitorStorage:
    """监控数据持久化存储"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or get_project_root() / "data/monitor.db"
        self._init_db()
    
    def save_metrics(self, metrics: Dict):
        """保存性能指标"""
        pass
    
    def get_history(self, metric_type: str, start: float, end: float, limit: int = 1000):
        """获取历史数据"""
        pass
    
    def get_health_score(self) -> float:
        """计算健康评分"""
        pass
```

#### 3.1.2 WebSocket处理器
```python
# backend/services/monitor_ws.py
class MonitorWebSocket:
    """监控WebSocket处理器"""
    
    def __init__(self):
        self.clients: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        """处理连接"""
        pass
    
    async def broadcast(self, message: Dict):
        """广播消息"""
        pass
    
    async def start_monitor_loop(self):
        """监控推送循环"""
        pass
```

#### 3.1.3 健康评分器
```python
# backend/services/health_scoring.py
class HealthScorer:
    """系统健康评分器"""
    
    def __init__(self):
        self.weights = {
            "cpu": 0.25,
            "memory": 0.25,
            "gpu": 0.2,
            "fps": 0.2,
            "disk": 0.1
        }
    
    def calculate_score(self, metrics: Dict) -> float:
        """计算健康评分(0-100)"""
        pass
    
    def get_health_level(self, score: float) -> str:
        """获取健康等级"""
        pass
```

### 3.2 API优化

#### 3.2.1 合并监控端点
```python
# 优化前: 12个独立端点
GET  /web/api/status
GET  /web/api/full-status
GET  /web/api/dependencies
GET  /web/api/system
GET  /web/api/processes
GET  /web/api/business
GET  /web/api/output
GET  /web/api/engines
GET  /web/api/summary
GET  /web/api/layers
GET  /web/api/history
POST /web/api/run_check

# 优化后: 5个端点 + WebSocket
GET  /web/api/dashboard     # 综合仪表盘数据(合并)
GET  /web/api/metrics/{type} # 性能指标(按类型)
GET  /web/api/history       # 历史数据
GET  /web/api/health        # 健康评分
POST /web/api/run_check     # 手动检查
WS   /ws/monitor            # WebSocket实时推送
```

#### 3.2.2 新增API响应格式
```json
{
  "success": true,
  "data": {
    "timestamp": "2025-01-21T12:00:00Z",
    "health_score": 85,
    "health_level": "good",
    "alerts": [],
    "metrics": {
      "cpu": {"value": 45, "unit": "%", "status": "ok"},
      "memory": {"value": 60, "unit": "%", "status": "ok"},
      "gpu": {"value": 35, "unit": "%", "status": "ok"},
      "fps": {"value": 28, "unit": "fps", "status": "ok"}
    },
    "modules": {...},
    "engines": {...}
  }
}
```

### 3.3 前端优化

#### 3.3.1 新增Vue组件
```javascript
// web/static/js/components.js 新增

// 健康评分环形图
Vue.component('health-score', {
    props: ['score', 'level'],
    template: `
        <div class="health-score">
            <canvas ref="chart"></canvas>
            <div class="score-overlay">{{ score }}</div>
        </div>
    `
});

// 实时报警面板
Vue.component('alert-panel', {
    props: ['alerts'],
    template: `
        <div class="alert-panel">
            <div v-for="alert in alerts" :class="['alert', 'alert-' + alert.level]">
                {{ alert.message }}
            </div>
        </div>
    `
});

// 自适应刷新控制
Vue.component('refresh-control', {
    data() {
        return {
            interval: 5000,
            mode: 'adaptive'  // 'adaptive' | 'fixed' | 'paused'
        }
    },
    methods: {
        calculateInterval() {
            // 根据健康状态动态调整
            if (this.healthScore < 60) return 2000;
            if (this.healthScore < 80) return 5000;
            return 10000;
        }
    }
});
```

#### 3.3.2 图表优化
```javascript
// web/static/js/charts.js 新增

// 实时性能趋势图
class RealtimeChart {
    constructor(container, options = {}) {
        this.data = [];
        this.maxPoints = options.maxPoints || 60;
        this.chart = echarts.init(container);
    }
    
    addPoint(timestamp, metrics) {
        this.data.push({ timestamp, ...metrics });
        if (this.data.length > this.maxPoints) {
            this.data.shift();
        }
        this.updateChart();
    }
    
    updateChart() {
        // 更新图表数据
    }
}

// 资源使用热力图
class ResourceHeatmap {
    // 资源使用趋势可视化
}
```

### 3.4 新增WebSocket客户端
```javascript
// web/static/js/websocket.js

class MonitorWebSocket {
    constructor(url) {
        this.url = url;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
    }
    
    connect() {
        this.ws = new WebSocket(this.url);
        
        this.ws.onopen = () => {
            console.log('[WS] Connected');
            this.reconnectAttempts = 0;
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };
        
        this.ws.onclose = () => {
            this.scheduleReconnect();
        };
    }
    
    handleMessage(data) {
        switch (data.type) {
            case 'metrics_update':
                EventBus.emit('metrics:update', data.payload);
                break;
            case 'alert':
                EventBus.emit('alert:new', data.payload);
                break;
            case 'health_change':
                EventBus.emit('health:change', data.payload);
                break;
        }
    }
    
    scheduleReconnect() {
        // 指数退避重连
    }
}
```

---

## 四、实施步骤

### 阶段1: 后端增强 (优先级: 高)
- [ ] 4.1.1 创建 `backend/services/monitor_storage.py`
  - SQLite数据库初始化
  - 性能指标存储
  - 历史数据查询接口
- [ ] 4.1.2 创建 `backend/services/health_scoring.py`
  - 健康评分算法
  - 等级判定逻辑
- [ ] 4.1.3 更新 `backend/unified_api.py`
  - 新增 `/web/api/dashboard` 端点
  - 新增 `/web/api/health` 端点
  - 优化 `/web/api/history` 端点

### 阶段2: WebSocket支持 (优先级: 高)
- [ ] 4.2.1 创建 `backend/services/monitor_ws.py`
  - WebSocket路由注册
  - 连接管理
  - 推送逻辑
- [ ] 4.2.2 更新 `backend/unified_api.py`
  - 集成WebSocket端点
  - 添加startup事件初始化

### 阶段3: 前端优化 (优先级: 中)
- [ ] 4.3.1 创建 `web/static/js/websocket.js`
  - WebSocket客户端封装
  - 自动重连机制
  - 消息处理器
- [ ] 4.3.2 更新 `web/static/js/api.js`
  - 新增dashboard API
  - 新增health API
- [ ] 4.3.3 更新 `web/static/js/app.js`
  - 集成WebSocket
  - 添加健康评分展示
  - 添加报警面板

### 阶段4: 图表增强 (优先级: 中)
- [ ] 4.4.1 更新 `web/static/js/charts.js`
  - 新增实时趋势图
  - 新增资源热力图
  - 优化现有图表性能
- [ ] 4.4.2 更新 `web/templates/index.html`
  - 添加健康评分组件
  - 添加报警面板
  - 优化布局

### 阶段5: 测试与文档 (优先级: 低)
- [ ] 4.5.1 功能测试
- [ ] 4.5.2 性能测试
- [ ] 4.5.3 更新文档

---

## 五、预期效果

### 5.1 性能提升
| 指标 | 优化前 | 优化后 | 提升 |
|-----|-------|-------|------|
| 页面加载时间 | 2s | 1.5s | 25% |
| 数据刷新延迟 | 5s | <1s | 80% |
| HTTP请求数/次 | 12 | 1 | 92% |
| 内存占用 | 100MB | 80MB | 20% |

### 5.2 功能增强
- ✅ 实时数据推送，延迟<1秒
- ✅ 7天历史数据查询
- ✅ 综合健康评分(0-100)
- ✅ 分级报警系统
- ✅ 自适应刷新频率
- ✅ 报警历史记录

---

## 六、风险与对策

| 风险 | 可能性 | 影响 | 对策 |
|-----|-------|-----|------|
| WebSocket连接不稳定 | 中 | 实时功能失效 | 自动重连、轮询降级 |
| 数据库写入性能问题 | 低 | 历史数据丢失 | 异步写入、定期清理 |
| 前端兼容性 | 低 | 图表不显示 | 优雅降级、使用canvas |

---

## 七、依赖变更

### 新增依赖
```txt
# requirements.txt 新增
websockets>=10.0  # WebSocket支持
```

### 已有依赖
```txt
# 保持不变
fastapi>=0.100.0
uvicorn>=0.22.0
psutil>=5.9.0
```

---

## 八、文件变更清单

### 新增文件
| 文件路径 | 描述 |
|---------|------|
| `backend/services/monitor_storage.py` | 监控数据持久化 |
| `backend/services/health_scoring.py` | 健康评分器 |
| `backend/services/monitor_ws.py` | WebSocket处理器 |
| `web/static/js/websocket.js` | WebSocket客户端 |

### 修改文件
| 文件路径 | 修改内容 |
|---------|---------|
| `backend/unified_api.py` | 新增API端点、集成WebSocket |
| `web/templates/index.html` | 添加组件、优化布局 |
| `web/static/js/api.js` | 新增dashboard API |
| `web/static/js/app.js` | 集成WebSocket、增强功能 |
| `web/static/js/charts.js` | 新增图表类型 |

### 删除文件
| 文件路径 | 删除原因 |
|---------|---------|
| 无 | - |

---

## 九、验证步骤

1. **启动服务**
   ```bash
   cd /workspaces/AISP
   python -m backend.unified_api
   ```

2. **验证API**
   ```bash
   # 测试综合仪表盘API
   curl http://localhost:8000/web/api/dashboard
   
   # 测试健康评分API
   curl http://localhost:8000/web/api/health
   
   # 测试历史数据API
   curl "http://localhost:8000/web/api/history?type=cpu&limit=100"
   ```

3. **验证WebSocket**
   ```bash
   # 使用wscat测试
   wscat -c ws://localhost:8000/ws/monitor
   ```

4. **验证前端**
   - 打开 http://localhost:8080
   - 检查健康评分显示
   - 检查实时数据更新
   - 检查报警通知

---

**创建时间**: 2025-01-21
**版本**: 1.0
**状态**: 待实施

