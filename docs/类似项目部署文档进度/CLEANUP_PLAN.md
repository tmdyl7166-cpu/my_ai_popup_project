# AISP 项目清理计划
## 任务：清理废弃配置和脚本，确保本地运行

---

## 一、项目现状分析

### 1.1 containers 文件夹状态 ✅ 已清理
| 项目 | 状态 | 说明 |
|------|------|------|
| `docker-compose.yml` | ✅ 已配置本地模式 | 所有服务已注释，标记为本地运行 |
| `Dockerfile` | ✅ 已标记本地模式 | 添加了本地运行说明 |
| `start_aisp.sh` | ✅ 已转换为本地启动脚本 | 支持 gui/api/web/full 模式 |
| `README.md` | ✅ 保持不变 | 文档说明 |
| `logs/startup.log` | ✅ 保留 | 启动日志 |
| `scripts/` | ✅ 为空目录 | 无需清理 |
| `config/` | ✅ 为空目录 | 已清理重复文件 |

### 1.2 根目录配置文件分析
| 文件 | 状态 | 说明 |
|------|------|------|
| AI_RULES.json | ✅ 保留 | AI行为约束主规则 |
| AI_PATH_CONTEXT.json | ✅ 保留 | 路径与职责约束 |
| AI_CLEANUP_POLICY.json | ✅ 保留 | 清理策略配置 |
| run_config.json | ✅ 保留 | 运行配置 |
| project_config.json | ⚠️ 需检查 | 需确认是否需要 |
| ai_config.json | ⚠️ 需检查 | 需确认是否需要 |
| engines_config.json | ⚠️ 需检查 | 需确认是否需要 |
| output_config.json | ⚠️ 需检查 | 需确认是否需要 |

### 1.3 scripts 文件夹中的容器相关脚本
| 脚本 | 状态 | 说明 |
|------|------|------|
| `cleanup_env.sh` | ✅ 保留 | Docker清理是必要功能 |
| `deploy_config.sh` | ✅ 保留 | 配置管理脚本 |
| `deploy.sh` | ✅ 保留 | 部署脚本含Docker选项 |
| 其他脚本 | ✅ 检查通过 | 无容器相关配置 |

---

## 二、清理任务清单

### 阶段1: 根目录配置文件精简
- [ ] 检查 `project_config.json` 是否与 `run_config.json` 重复
- [ ] 检查 `ai_config.json` 是否必要
- [ ] 检查 `engines_config.json` 是否必要
- [ ] 检查 `output_config.json` 是否必要
- [ ] 合并重复配置，删除冗余文件

### 阶段2: 容器配置最终确认
- [ ] 确认 `docker-compose.yml` 所有服务已注释
- [ ] 确认 `Dockerfile` 明确标记本地运行
- [ ] 确认 `start_aisp.sh` 是纯本地启动脚本
- [ ] 验证无 volumes 挂载配置冲突

### 阶段3: 脚本容器引用检查
- [ ] 验证 `cleanup_env.sh` Docker清理逻辑正确
- [ ] 验证 `deploy_config.sh` Docker配置变量清晰
- [ ] 验证 `deploy.sh` Docker模式选择逻辑完整
- [ ] 移除脚本中过时的容器启动命令

### 阶段4: 本地运行验证
- [ ] 验证 `run_gui.py` 启动入口正常
- [ ] 验证 `scripts/start_gui.sh` 正常
- [ ] 验证 `scripts/start_all.sh` 正常
- [ ] 验证路径配置无冲突

---

## 三、配置文件依赖关系

```
层级1 (AI行为约束):
  AI_RULES.json ← AI_PATH_CONTEXT.json ← AI_CLEANUP_POLICY.json
  
层级2 (项目主配置):
  project_config.json (需检查)
  ai_config.json (需检查)
  engines_config.json (需检查)
  output_config.json (需检查)
  
层级3 (运行配置):
  run_config.json ← health_check_config.json
  
层级4 (功能子配置):
  ai/model_config.json
  ai/capability_map.json
```

---

## 四、执行步骤

### Step 1: 检查根目录重复配置文件
```bash
# 检查配置文件内容重复
ls -la *.json
```

### Step 2: 验证容器配置状态
```bash
# 确认docker-compose.yml服务已注释
grep -c "^  #" containers/docker-compose.yml

# 确认Dockerfile有本地运行标记
grep "本地运行" containers/Dockerfile
```

### Step 3: 验证本地启动脚本
```bash
# 测试启动脚本是否存在
ls -la scripts/start_*.sh
```

### Step 4: 执行清理操作
```bash
# 如有需要，删除重复配置文件
rm -f project_config.json ai_config.json engines_config.json output_config.json
```

### Step 5: 验证本地运行
```bash
# 验证run_gui.py存在
python3 run_gui.py --help 2>/dev/null || echo "GUI启动验证"
```

---

## 五、风险评估

| 操作 | 风险级别 | 应对措施 |
|------|---------|---------|
| 删除重复配置文件 | 中 | 先备份，确认无依赖后删除 |
| 修改容器配置 | 低 | 仅注释，不删除配置 |
| 清理scripts目录 | 低 | 目录已为空 |

---

## 六、预期结果

1. **containers 文件夹**: 仅包含本地运行模式的容器配置，无实际容器运行配置
2. **根目录**: 配置文件精简，无重复配置
3. **scripts 文件夹**: 保留必要的Docker相关脚本，但明确为本地运行服务
4. **本地运行**: 项目可通过 `python run_gui.py` 正常启动

---

## 七、后续验证

- [ ] 运行 `python run_gui.py` 验证GUI可启动
- [ ] 运行 `bash scripts/start_gui.sh` 验证启动脚本
- [ ] 检查 `containers/start_aisp.sh help` 输出
- [ ] 确认无Docker服务意外启动

---

*创建时间: 2024*
*版本: 1.0.0*

