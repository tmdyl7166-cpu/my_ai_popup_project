# 📋 项目规则系统 (rules/)

## 🎯 规则系统概述

`rules/` 目录是项目的核心治理体系，采用独特的**五层逻辑规则架构**，确保项目的可持续发展和可演化性。

### 🏗️ 五层架构模型

```
L1 - 元目标层 (Meta Goal)
    ↓ 定义项目最高目标和约束条件
L2 - 全局理解层 (Understanding)
    ↓ 描述架构、模块关系和数据流
L3 - 约束层 (Constraints)
    ↓ 定义技术约束、规范和依赖关系
L4 - 决策层 (Decisions)
    ↓ 记录关键设计决策和权衡
L5 - 执行层 (Execution)
    ↓ 具体的执行规则、操作指南和任务分配
```

## 📁 目录结构详解

### 规则文件层级

```
rules/
├── L1-meta-goal.json         # 元目标层 - 项目愿景和核心价值
├── L2-understanding.json     # 全局理解层 - 架构理解和模块关系
├── L3-constraints.json       # 约束层 - 技术规范和依赖约束
├── L4-decisions.json         # 决策层 - 关键决策和技术选型
├── L5-execution.json         # 执行层 - 具体执行规则和流程
├── rules.config.js           # 规则系统配置 (可选)
├── rules_README.md           # 规则系统说明文档
└── data/                     # 规则相关数据
    └── data-schema.json      # 数据结构定义
```

### 📄 各层文件详细说明

#### 🎯 L1 - 元目标层 (`L1-meta-goal.json`)

**核心职责**: 定义项目的最高目标、核心价值和基本约束，是项目的宏观指导思想

**文件结构与内容逻辑**:

- **meta**: 元数据定义，包含层级标识、版本信息、创建时间等
- **project**: 项目基本信息，包括名称、代码标识、类型描述等
- **goals**: 目标体系
  - **primary**: 主要目标（智能人脸合成能力）
  - **secondary**: 次要目标（本地AI优先、多引擎集成、实时处理等）
- **values**: 核心价值观（隐私、性能、易用性、可扩展性、稳定性）
- **constraints**: 约束条件
  - **performance**: 性能约束（启动时间、处理延迟、内存限制等）
  - **compatibility**: 兼容性要求（Python版本、操作系统、硬件要求）
  - **resourceLimits**: 资源限制（并发任务、队列大小、缓存大小）
  - **security**: 安全约束（数据隐私、本地处理、无云端上传）
  - **quality**: 质量要求（人脸检测准确率、合成质量等）
- **nonGoals**: 非目标清单（明确不做的事情）
- **riskManagement**: 风险管理（已识别风险及缓解策略）
- **successMetrics**: 成功指标（功能、性能、稳定性、易用性指标）
- **roadmap**: 路线图规划（v1.0、v1.5、v2.0版本规划）

**逻辑关系**: 该层是所有其他层的基石，所有决策和技术选择都必须符合L1定义的目标和约束。

#### 🧠 L2 - 全局理解层 (`L2-understanding.json`)

**核心职责**: 描述项目的整体架构、模块关系和数据流转

**文件结构与内容逻辑**:

- **meta**: 元数据和依赖关系定义
- **architecture**: 架构描述
  - **style**: 架构风格（分层架构+**Web监控模式**）
  - **layers**: 各层定义（Web前端、API网关、应用层、AI处理等）
- **modules**: 模块详细定义
  - **web**: Web监控前端模块（路径: `web/`）
  - **api**: API网关与后端服务模块（路径: `api/`）
  - **scripts**: 自动化脚本模块（路径: `scripts/`）
  - **frontend**: 前端UI模块（路径: `src/frontend/`）
  - **backend**: 后端服务模块（路径: `src/backend/`）
  - **ai**: AI模块（路径: `src/ai/`）
  - **processing**: 媒体处理模块（路径: `src/processing/`）
  - **integrations**: 第三方引擎集成模块（路径: `src/integrations/`）
  - **utils**: 工具模块（路径: `src/utils/`）
  - **config**: 配置模块（路径: `src/config/`）
- **relationships**: 模块间关系
  - **dataFlow**: 数据流路径定义（**新增Web→API→脚本→后端**链路）
  - **dependencies**: 依赖关系图
  - **communication**: 通信模式（HTTP/HTTPS + WebSocket + Internal Call）
  - **dataContracts**: 数据契约定义（TaskRequest、TaskResponse等）
- **dataFlow**: 核心数据流说明（图片合成到摄像头、图片合成到视频、AI命令理解）
- **stateManagement**: 系统状态管理策略
- **entryPoints**: 系统入口点定义

**2026-01-21 更新内容**:

- ✅ 新增 `web/` 模块定义（Web监控前端）
- ✅ 新增 `api/` 模块定义（API网关层）
- ✅ 更新架构风格为 "分层架构+Web监控模式"
- ✅ 更新数据流路径（新增 Web→API→脚本 链路）
- ✅ 新增 path_reference 引用 project_config.json

**逻辑关系**: 建立项目架构的全局视图，为L3约束和L4决策提供基础架构理解。

#### ⚖️ L3 - 约束层 (`L3-constraints.json`)

**核心职责**: 定义技术实现的约束、规范和依赖关系

**文件结构与内容逻辑**:

- **meta**: 元数据定义
- **python**: Python环境约束（版本范围、编码要求、类型提示、代码规范）
- **dependencies**: 依赖包管理
  - **core**: 核心依赖（PyQt5、FastAPI、uvicorn）
  - **ai**: AI相关依赖（torch、ollama、insightface等）
  - **media**: 媒体处理依赖（opencv、moviepy、Pillow等）
  - **utilities**: 工具依赖（pydantic、loguru、psutil）
- **gpu**: GPU支持配置（CUDA、DirectML、CPU回退）
- **externalServices**: 外部服务配置（Ollama、虚拟摄像头）
- **fileFormats**: 支持的文件格式（输入/输出格式定义）
- **apiContracts**: API接口契约
  - **rest**: REST API定义（端点、方法、请求响应格式）
  - **websocket**: WebSocket通信协议
- **codingStandards**: 编码规范（风格、命名、文档、错误处理、测试要求）
- **performanceConstraints**: 性能约束（内存、CPU、GPU、延迟、吞吐量）
- **securityConstraints**: 安全约束（输入验证、文件系统、网络、隐私）
- **deploymentConstraints**: 部署约束（Docker配置、环境管理）
- **compatibilityMatrix**: 兼容性矩阵（操作系统支持）
- **thirdPartyEngines**: 第三方引擎配置

**逻辑关系**: 为L4决策提供技术约束边界，确保所有实现都符合技术规范。

#### 🤔 L4 - 决策层 (`L4-decisions.json`)

**核心职责**: 记录关键设计决策和权衡，以及为什么选择某种技术或架构

**文件结构与内容逻辑**:

- **meta**: 元数据定义
- **architectureDecisions**: 架构决策记录
  - 每个决策包含：标题、上下文、决策内容、备选方案、决策理由、后果分析、状态
  - 关键决策包括：分层架构+插件模式、PyQt5 GUI框架、本地AI优先、FastAPI后端、多引擎集成
- **technologyChoices**: 技术选型
  - **programmingLanguage**: Python 3.10+的选择理由
  - **aiFramework**: PyTorch + InsightFace的选型逻辑
  - **mediaProcessing**: OpenCV + MoviePy的选择
  - **configurationFormat**: JSON + Python配置类的选择
- **designPrinciples**: 设计原则
  - **modularity**: 高内聚低耦合原则及实现方式
  - **performance**: 性能优先原则及优化策略
  - **reliability**: 容错设计原则及降级策略
  - **usability**: 用户中心设计原则及实现方法
- **tradeOffs**: 权衡决策
  - **performanceVsUsability**: 性能与易用性的平衡
  - **featuresVsComplexity**: 功能与复杂度的权衡
  - **compatibilityVsInnovation**: 兼容性与创新的平衡
- **riskMitigation**: 风险缓解策略
- **futureConsiderations**: 未来考虑（可扩展性、维护性等）

**逻辑关系**: 记录所有重要决策的理由和权衡，为L5执行提供决策依据。

#### ⚡ L5 - 执行层 (`L5-execution.json`)

**核心职责**: 具体的执行规则、操作指南和任务分配

**文件结构与内容逻辑**:

- **meta**: 元数据定义
- **executionRules**: 执行规则
  - **taskLifecycle**: 任务生命周期管理
  - **errorHandling**: 错误处理策略
  - **resourceManagement**: 资源管理规则
  - **performanceOptimization**: 性能优化规则
- **operationalProcedures**: 操作流程
  - **startupSequence**: 启动序列
  - **shutdownSequence**: 关闭序列
  - **maintenanceProcedures**: 维护流程
- **apiSpecifications**: API规范
  - **endpoints**: 端点定义
  - **requestResponse**: 请求响应格式
  - **authentication**: 认证机制
  - **rateLimiting**: 速率限制
- **cliCommands**: 命令行工具
  - **availableCommands**: 可用命令列表
  - **commandSyntax**: 命令语法
  - **examples**: 使用示例
- **checklists**: 检查清单
  - **preStartup**: 启动前检查
  - **preTask**: 任务前检查
  - **postTask**: 任务后清理
  - **healthChecks**: 健康检查
- **monitoring**: 监控配置
  - **metrics**: 监控指标
  - **alerts**: 告警规则
  - **logging**: 日志配置
- **troubleshooting**: 故障排除指南
- **frontendRendering**: **前端动态渲染规则**（2026-01-21新增）
  - **corePrinciples**: 前端不写死，数据驱动UI
  - **dataDrivenUI**: 动态渲染机制定义
  - **componentLifecycle**: 组件生命周期管理
- **functionCardSpecification**: **功能卡片规范**（2026-01-21新增）
  - **requiredFields**: 必需字段（冒泡检测、前端名称、功能说明、参数区域、后端节点、优化建议、标签、状态）
  - **cardTemplate**: 卡片模板结构
  - **status**: 🟢可用 / 🟡部分完成 / 🔴未部署
- **realtimeCommunication**: **实时通信约束**（2026-01-21新增）
  - **websocket**: WebSocket配置（路径、重连、心跳）
  - **channels**: progress/log/data/heartbeat
  - **fallback**: Polling降级策略
- **apiMappingMechanism**: **API映射机制**（2026-01-21新增）
  - **mappingSource**: api/mapping/api_mapping.json
  - **frontendIntegration**: ws.js、charting.js、progress.js等组件
  - **formSubmission**: #runForm → POST /api/run
- **bubbleDetection**: **冒泡检测规则**（2026-01-21新增）
  - **events**: click/submit/change事件
  - **tracking**: [data-bubble]、[data-module]、[data-action]元素
  - **reporting**: /api/bubbles 批量上报
- **scriptToApiMapping**: **脚本到API映射**（2026-01-21新增）
  - **rules**: 脚本不直接暴露，统一通过API映射
  - **endpoints**: POST /api/scripts/{name}/run | GET /api/scripts/{name}/status
- **rulesIntegration**: **规则联动配置**（2026-01-21新增）
  - **linkedFiles**: project_config.json、api_mapping.json、web_config.json
  - **syncRules**: 规则文件修改时自动验证

**2026-01-21 更新内容**:

- ✅ 新增 frontendRendering 规则（数据驱动UI）
- ✅ 新增 functionCardSpecification 规范（功能卡片标准）
- ✅ 新增 realtimeCommunication 配置（WebSocket/SSE）
- ✅ 新增 apiMappingMechanism 机制（前后端调用规范）
- ✅ 新增 bubbleDetection 规则（事件冒泡监控）
- ✅ 新增 scriptToApiMapping 规则（脚本调用映射）
- ✅ 新增 rulesIntegration 配置（规则联动）

**逻辑关系**: 将前四层的抽象规则转换为具体的可执行操作指南。

## 🔄 规则系统工作原理

### 📊 决策流程

```
用户需求/问题
    ↓
L1: 是否符合项目目标？
    ↓
L2: 如何在架构中实现？
    ↓
L3: 技术上是否可行？
    ↓
L4: 选择最佳解决方案
    ↓
L5: 具体执行步骤
```

### 🔗 配置联动机制

规则系统与项目配置通过以下方式联动：

#### 1. 直接引用 (Direct Reference)

```json
{
  "rulesLink": {
    "L1": "rules/L1-meta-goal.json",
    "L2": "rules/L2-understanding.json",
    "L3": "rules/L3-constraints.json",
    "L4": "rules/L4-decisions.json",
    "L5": "rules/L5-execution.json"
  }
}
```

#### 2. 约束驱动 (Constraint Driven)

- L3约束层定义技术规范
- 项目配置必须符合L3定义的约束
- 配置验证脚本自动检查合规性

#### 3. 决策指引 (Decision Guided)

- L4决策层记录技术选型理由
- 新功能开发参考L4决策原则
- 架构演化遵循L4决策框架

### 📈 规则演化机制

#### 版本管理

- 每个规则文件独立版本控制
- 版本号格式: `主版本.次版本.修订版本`
- 向后兼容性保证

#### 更新流程

```
需求提出 → 规则评估 → 影响分析 → 更新规则 → 验证合规 → 实施变更
```

#### 一致性检查

- 自动化脚本每日检查规则一致性
- 跨文件引用自动验证
- 配置合规性实时监控

## 🛠️ 规则系统工具

### 📋 验证工具

```bash
# 检查规则系统完整性
python scripts/health_monitor/config_validator.py --rules

# 验证配置合规性
python scripts/health_monitor/config_validator.py --compliance

# 生成规则依赖图
python scripts/health_monitor/config_validator.py --dependencies
```

### 📊 监控工具

```bash
# 规则系统健康监控
python scripts/health_monitor/rules_monitor.py

# 配置变更跟踪
python scripts/health_monitor/config_monitor.py --rules

# 合规性报告生成
python scripts/health_monitor/compliance_report.py
```

### 🔧 维护工具

```bash
# 规则文件格式化
python scripts/maintenance/rules_formatter.py

# 规则一致性修复
python scripts/maintenance/rules_consistency.py

# 规则文档同步
python scripts/maintenance/docs_sync.py --rules
```

## 📖 使用指南

### 👥 开发者指南

1. **新功能开发前**: 先检查L1-L4规则确定方向
2. **技术选型时**: 参考L4决策层已有决策
3. **实现过程中**: 遵循L5执行层具体规范
4. **提交代码前**: 运行规则合规性检查

### 👨‍💼 项目管理者指南

1. **需求评估时**: 用L1目标层验证需求合理性
2. **架构决策时**: 在L4决策层记录决策理由
3. **进度监控时**: 参考L5执行层检查执行规范
4. **风险识别时**: 关注L3约束层的技术风险

### 🔧 运维人员指南

1. **部署前**: 检查L3约束层的环境要求
2. **配置时**: 遵循L5执行层的配置规范
3. **故障排查时**: 参考L2理解层的架构关系
4. **性能优化时**: 遵循L4决策层的优化策略

## 🚨 注意事项

### ⚠️ 规则修改原则

- **慎重修改**: L1-L3层规则修改需要集体讨论
- **向后兼容**: 规则变更不能破坏现有功能
- **充分验证**: 规则修改后必须通过完整测试
- **文档同步**: 规则修改后及时更新相关文档

### 🚫 禁止行为

- ❌ 直接修改规则文件而不通过审核流程
- ❌ 违反L3约束层定义的技术规范
- ❌ 忽略L4决策层已有决策原则
- ❌ 不遵循L5执行层具体操作规范

### 🔍 监控要点

- 📊 规则合规性: > 95%
- 📈 配置一致性: 100%
- ⏱️ 规则更新频率: 按需更新
- 📋 文档同步率: 100%

## 📞 相关链接

- [项目架构文档](../docs/project_docs/01-project-architecture.md)
- [配置管理系统](../src/config/)
- [健康监控脚本](../scripts/health_monitor/)
- [项目主文档](../README.md)

---

_规则系统是项目的基石，请严格遵循规则执行项目开发和管理_
_最后更新: 2026-01-21_
