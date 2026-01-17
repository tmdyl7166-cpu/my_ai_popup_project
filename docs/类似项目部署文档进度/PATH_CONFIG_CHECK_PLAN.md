# AISP 路径与配置检查计划

## L1 元目标
- 保持项目结构一致性
- 保持项目逻辑一致性
- 确保所有路径引用正确

## L2 全局理解摘要

### 项目结构分析
- **根目录**: `/workspaces/AISP`
- **核心目录**: gui, backend, engines, scripts, data, docs
- **配置位置**: `data/rules/` (规则配置) vs `config/` (应用配置)
- **问题数量**: 6个主要路径配置问题

### 发现的问题

#### 问题 1: config 目录不存在
- **严重程度**: 高
- **影响范围**: path_config.py, verify_deployment.py
- **现象**: 脚本期望 `config/` 目录存在，但实际不存在
- **根因**: 项目架构设计中 `config/` 目录与应用配置分离

#### 问题 2: AI规则配置文件缺失
- **严重程度**: 中
- **影响范围**: emergency_recovery.sh, verify_deployment.py
- **现象**: 引用 `AI_RULES.json`, `AI_PATH_CONTEXT.json`, `AI_CLEANUP_POLICY.json`
- **根因**: 这些文件来自 .vscode 配置，但未同步到项目

#### 问题 3: path_config.py 路径指向错误
- **严重程度**: 高
- **影响文件**: scripts/path_config.py
- **具体问题**: 
  - `get_config_dir()` 返回 `PROJECT_ROOT / "config"` 不存在
  - `get_ai_config_path()` 返回 `config/ai` 不存在

#### 问题 4: backend/path_utils.py 引用不存在文件
- **严重程度**: 中
- **影响文件**: backend/path_utils.py
- **具体问题**: 检查 `PROJECT_ROOT / "AI_RULES.json"` 但文件不存在

#### 问题 5: 脚本配置引用不一致
- **严重程度**: 中
- **影响文件**: scripts/*.sh, scripts/*.py
- **具体问题**: 混合使用 `config/` 和 `data/rules/` 引用

#### 问题 6: directory_structure.json 与实际结构差异
- **严重程度**: 低
- **影响范围**: 文档一致性
- **具体问题**: 某些模块定义与实际文件不完全匹配

## L3 约束层检查

### 命名约束 (符合规范)
- ✅ Python模块: snake_case
- ✅ 配置文件: kebab-case
- ✅ 目录名: snake_case

### 结构约束 (部分违规)
- ⚠️ GUI层有直接导入backend模块
- ⚠️ 某些脚本绕过统一路径配置

### 安全约束 (基本符合)
- ✅ 未发现硬编码敏感信息
- ✅ 路径处理使用相对路径

## L4 决策

### 可修改内容
1. `scripts/path_config.py` - 路径配置模块
2. `scripts/verify_deployment.py` - 部署验证脚本
3. `backend/path_utils.py` - 路径工具模块

### 不可修改内容
1. `directory_structure.json` - 项目结构配置
2. `logic_layers_deployment.json` - 五层逻辑部署
3. `data/rules/` - 规则配置目录

## L5 执行计划

### 步骤 1: 创建 config 目录并迁移配置
```bash
mkdir -p /workspaces/AISP/config
```

### 步骤 2: 更新 path_config.py
- 修改 `get_config_dir()` 指向 `data/rules/`
- 或创建 `config/` 目录并同步必要配置

### 步骤 3: 更新 verify_deployment.py
- 修改配置检查路径指向正确位置
- 添加兼容性检查

### 步骤 4: 更新 backend/path_utils.py
- 修改 `AI_RULES.json` 检查路径
- 或创建占位符文件

### 步骤 5: 更新相关脚本
- emergency_recovery.sh
- api_opt_.sh
- 其他引用错误路径的脚本

## 验证清单
- [ ] 所有路径引用指向存在的文件/目录
- [ ] 脚本能正确识别项目根目录
- [ ] 配置文件加载无错误
- [ ] 路径工具函数返回正确结果
- [ ] 层级依赖关系符合约束

## 回滚策略
- 保留原始文件备份
- 记录所有修改
- 支持一键回滚

