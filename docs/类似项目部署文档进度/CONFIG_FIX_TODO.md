# 配置修复任务清单

## 任务概览
- **开始时间**: 2025-01-21
- **任务目标**: 修正项目配置和参数的所有问题

## 修复计划

### Phase 1: 清理配置目录
- [ ] 1.1 删除 `配置/AI_CLEANUP_POLICY.json` (与 data/rules 重复)
- [ ] 1.2 删除 `配置/AI_RULES.json` (与 data/rules/root_rules.json 重复)
- [ ] 1.3 删除 `配置/AI_PATH_CONTEXT.json` (与 directory_structure.json 冲突)
- [ ] 1.4 删除 `配置/` 目录下所有与项目根目录重复的配置文件

### Phase 2: 修复路径引用
- [ ] 2.1 修复 `ai_task_config.json` 中的路径引用
- [ ] 2.2 修复 `logic_layers_deployment.json` 中的路径映射
- [ ] 2.3 修复 `directory_structure.json` 中的配置引用

### Phase 3: 同步版本信息
- [ ] 3.1 统一 `ai_task_config.json` 版本为 2.0.0
- [ ] 3.2 统一 `directory_structure.json` 版本为 2.0.0
- [ ] 3.3 统一 `logic_layers_deployment.json` 版本为 2.0.0
- [ ] 3.4 更新 `data/rules/` 目录下所有配置文件的版本

### Phase 4: 修正引擎名称
- [ ] 4.1 更新 `AI_PATH_CONTEXT.json` 中的引擎名称为实际名称
- [ ] 4.2 同步更新相关配置中的引擎引用

### Phase 5: 验证修复
- [ ] 5.1 验证配置文件的JSON语法正确性
- [ ] 5.2 验证配置引用路径的一致性
- [ ] 5.3 生成配置修复报告

## 清理规则
- 以 `data/rules/` 目录为唯一权威配置源
- `配置/` 目录仅保留 VSCode 相关的编辑器配置
- 所有规则类配置必须集中在 `data/rules/` 目录

## 后续步骤
1. 执行配置清理
2. 同步更新相关文档
3. 验证配置一致性
4. 提交更改

