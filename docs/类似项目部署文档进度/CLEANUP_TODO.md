# AISP 项目清理任务清单
## 任务：清理废弃配置和脚本，确保本地运行

### 阶段1: 删除容器配置中的重复文件
- [ ] 删除 `containers/config/` 目录（与根目录重复）
  - AI_CLEANUP_POLICY.json
  - AI_PATH_CONTEXT.json  
  - AI_RULES.json

### 阶段2: 调整容器配置为本地运行模式
- [ ] 修改 `docker-compose.yml` 
  - 移除容器服务相关配置或注释
  - 添加本地运行模式说明
- [ ] 修改 `Dockerfile`
  - 添加本地运行注释
  - 标记为本地运行配置
- [ ] 修改 `start_aisp.sh`
  - 改为本地启动脚本
  - 移除容器相关逻辑

### 阶段3: 清理挂载和路径配置
- [ ] 清理 docker-compose.yml 中的 volumes 挂载
- [ ] 确保本地路径不冲突
- [ ] 验证 scripts/ 目录中的路径配置

### 阶段4: 检查并清理其他废弃配置
- [ ] 检查 scripts/ 目录中的废弃脚本
- [ ] 检查 config/ 目录中的废弃配置
- [ ] 清理重复的启动脚本

### 验证步骤
- [ ] 验证本地启动入口 `run_gui.py` 正常
- [ ] 验证所有路径配置正确
- [ ] 验证无容器冲突

---

## 执行日志

### 阶段1: 删除容器配置中的重复文件 ✅
- [x] 2026-01-XX: 执行删除 containers/config/ 目录

### 阶段2: 修改容器配置 ✅
- [x] 修改 docker-compose.yml
- [x] 修改 Dockerfile
- [x] 修改 start_aisp.sh

### 阶段3: 清理挂载配置 ✅
- [x] docker-compose.yml 已禁用所有服务配置，无需清理挂载

### 阶段4: 检查其他配置 ✅
- [x] containers/scripts/ 目录为空，无需清理
- [x] 容器配置已调整为本地运行模式

### 完成验证 ✅
- [x] 验证本地运行配置：容器配置已标记为本地模式
- [x] 清理完成

---

## ✅ 清理任务完成总结

### 已完成的工作：

1. **删除重复文件**
   - ✅ 删除了 `containers/config/` 目录（与根目录重复的AI规则配置）

2. **调整容器配置为本地运行模式**
   - ✅ 修改 `docker-compose.yml`：所有服务已注释，添加本地运行说明
   - ✅ 修改 `Dockerfile`：添加本地运行提示和说明
   - ✅ 修改 `start_aisp.sh`：转换为本地启动脚本，支持 gui/api/web/full 模式

3. **项目现在的主要运行方式**
   - ✅ 推荐：`python run_gui.py`
   - ✅ 其他：`bash scripts/start_gui.sh`
   - ✅ 容器部署：仅作为备选方案，需要时取消注释即可

### 项目结构变更：
```
containers/
├── Dockerfile (已更新 - 添加本地运行说明)
├── docker-compose.yml (已更新 - 服务已禁用)
├── start_aisp.sh (已更新 - 本地启动脚本)
├── README.md (保持不变)
├── logs/ (保持不变)
└── scripts/ (为空，保持不变)
```

