# 任务02 - 修复计划

## 任务编号
02

## 任务名称
环境修复计划

## 任务状态
已完成

## 创建时间
2026-01-16

---

## 阶段1: 依赖清理

### 1.1 清理主依赖文件 (requirements.txt)
- 移除重复的依赖定义
- 保留一份，去除重复

### 1.2 移除重复的 web/requirements.txt
- 在 web/requirements.txt 中只保留 web 特有依赖
- 注释掉与主文件重复的依赖

---

## 阶段2: 脚本重构

### 2.1 合并重复的监控脚本
- 合并为统一的配置检查脚本
- 建立统一的脚本入口

---

## 阶段3: 环境验证

### 检查Python环境
```bash
python3 --version  # Python 3.14.0
pip list
```

---

## 阶段4: 缺失依赖补齐

### 安装缺失依赖
```bash
pip install -r requirements.txt --no-deps
```

---

## 关联文档

- 分析报告: 01-environment-analysis.md
- 依赖清理: 03-dependency-cleanup.md

