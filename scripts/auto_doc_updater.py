#!/usr/bin/env python3
"""
自动文档更新器
自动同步项目变更到文档系统，更新版本、时间戳、进度等信息
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import subprocess
import hashlib
import re

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent


class AutoDocUpdater:
    """自动文档更新器"""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.logger = self._setup_logging()
        self.docs_config_path = self.project_root / "docs" / "docs_config.json"
        self.readme_path = self.project_root / "README.md"
        self.project_config_path = self.project_root / "project_config.json"

        # 加载配置
        self.docs_config = self._load_docs_config()
        self.project_config = self._load_project_config()

    def _setup_logging(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger("auto_doc_updater")
        logger.setLevel(logging.INFO)

        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # 文件处理器
        log_file = self.project_root / "logs" / "auto_doc_updater.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger

    def _load_docs_config(self) -> Dict[str, Any]:
        """加载文档配置"""
        if self.docs_config_path.exists():
            try:
                with open(self.docs_config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"加载文档配置失败: {e}")
        return {}

    def _load_project_config(self) -> Dict[str, Any]:
        """加载项目配置"""
        if self.project_config_path.exists():
            try:
                with open(self.project_config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"加载项目配置失败: {e}")
        return {}

    def _save_docs_config(self):
        """保存文档配置"""
        try:
            with open(self.docs_config_path, "w", encoding="utf-8") as f:
                json.dump(self.docs_config, f, indent=2, ensure_ascii=False)
            self.logger.info("文档配置已保存")
        except Exception as e:
            self.logger.error(f"保存文档配置失败: {e}")

    def _get_git_changes(self) -> List[str]:
        """获取最近的git变更"""
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "-10"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return result.stdout.strip().split("\n")
        except Exception as e:
            self.logger.error(f"获取git变更失败: {e}")
        return []

    def _get_file_hash(self, file_path: Path) -> str:
        """获取文件哈希"""
        try:
            with open(file_path, "rb") as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""

    def _scan_project_changes(self) -> Dict[str, Any]:
        """扫描项目变更"""
        changes = {
            "modified_files": [],
            "new_files": [],
            "deleted_files": [],
            "config_changes": {},
            "script_changes": {},
            "doc_changes": {},
        }

        # 扫描主要目录
        key_dirs = ["src", "scripts", "web", "api", "assets", "rules", "docs"]

        for dir_name in key_dirs:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                continue

            for file_path in dir_path.rglob("*"):
                if file_path.is_file() and not file_path.name.startswith("."):
                    # 这里可以添加文件变更检测逻辑
                    # 暂时简化处理
                    pass

        return changes

    def update_version_info(self):
        """更新版本信息"""
        self.logger.info("更新版本信息...")

        current_time = datetime.now().isoformat()

        # 更新文档配置中的时间戳
        if "meta" in self.docs_config:
            self.docs_config["meta"]["lastModified"] = current_time
            self.docs_config["meta"]["version"] = self._increment_version(
                self.docs_config["meta"].get("version", "1.0.0")
            )

        # 更新项目配置中的时间戳
        if self.project_config and "meta" in self.project_config:
            self.project_config["meta"]["lastModified"] = current_time

    def _increment_version(self, version: str) -> str:
        """递增版本号"""
        try:
            parts = version.split(".")
            if len(parts) >= 3:
                parts[-1] = str(int(parts[-1]) + 1)
                return ".".join(parts)
        except Exception:
            pass
        return version

    def update_deployment_progress(self):
        """更新部署进度"""
        self.logger.info("更新部署进度...")

        # 扫描任务完成情况
        completed_tasks = 0
        total_tasks = 0

        if (
            "structure" in self.docs_config
            and "docs/deployment_progress/" in self.docs_config["structure"]
        ):
            progress_docs = self.docs_config["structure"]["docs/deployment_progress/"]
            if "subDocs" in progress_docs:
                for doc_name, doc_info in progress_docs["subDocs"].items():
                    total_tasks += 1
                    if doc_info.get("status") == "completed":
                        completed_tasks += 1

        # 更新统计信息
        if "stats" in self.docs_config["structure"]["docs/"]:
            stats = self.docs_config["structure"]["docs/"]["stats"]
            stats["completedTasks"] = completed_tasks
            stats["totalTasks"] = total_tasks
            stats["pendingTasks"] = total_tasks - completed_tasks

            # 计算完成百分比
            if total_tasks > 0:
                completion_percentage = (completed_tasks / total_tasks) * 100
                stats["completionPercentage"] = round(completion_percentage, 1)

    def update_readme_status(self):
        """更新README状态信息"""
        self.logger.info("更新README状态信息...")

        if not self.readme_path.exists():
            return

        try:
            with open(self.readme_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 更新部署进度
            if "stats" in self.docs_config.get("structure", {}).get("docs/", {}):
                stats = self.docs_config["structure"]["docs/"]["stats"]
                completion_percentage = stats.get("completionPercentage", 0)

                # 替换进度信息
                progress_pattern = r"\*\*部署进度\*\*: \d+\%"
                new_progress = f"**部署进度**: {completion_percentage}%"
                content = re.sub(progress_pattern, new_progress, content)

                # 更新版本号
                version = self.docs_config.get("meta", {}).get("version", "1.0.0")
                version_pattern = r"\*\*版本\*\*: [\d\.]+"
                new_version = f"**版本**: {version}"
                content = re.sub(version_pattern, new_version, content)

                # 更新最后更新时间
                current_time = datetime.now().strftime("%Y-%m-%d")
                time_pattern = r"\*\*最后更新\*\*: [\d\-]+"
                new_time = f"**最后更新**: {current_time}"
                content = re.sub(time_pattern, new_time, content)

            # 写回文件
            with open(self.readme_path, "w", encoding="utf-8") as f:
                f.write(content)

            self.logger.info("README已更新")

        except Exception as e:
            self.logger.error(f"更新README失败: {e}")

    def sync_documentation(self):
        """同步文档系统"""
        self.logger.info("同步文档系统...")

        # 检查文档完整性
        self._check_docs_integrity()

        # 更新文档索引
        self._update_docs_index()

        # 清理过期文档
        self._cleanup_old_docs()

    def _check_docs_integrity(self):
        """检查文档完整性"""
        self.logger.info("检查文档完整性...")

        docs_dir = self.project_root / "docs"
        if not docs_dir.exists():
            return

        # 检查必需文档是否存在
        required_docs = ["docs_README.md", "文档索引说明.md", "docs_config.json"]

        for doc in required_docs:
            doc_path = docs_dir / doc
            if not doc_path.exists():
                self.logger.warning(f"缺少必需文档: {doc}")
                # 可以在这里创建默认文档

    def _update_docs_index(self):
        """更新文档索引"""
        self.logger.info("更新文档索引...")

        # 这里可以实现文档索引的自动更新逻辑
        # 暂时简化处理
        pass

    def _cleanup_old_docs(self):
        """清理过期文档"""
        self.logger.info("清理过期文档...")

        # 删除超过1年的历史文档
        cutoff_date = datetime.now() - timedelta(days=365)

        # 这里可以实现清理逻辑
        # 暂时简化处理
        pass

    def generate_progress_report(self) -> Dict[str, Any]:
        """生成进度报告"""
        self.logger.info("生成进度报告...")

        report = {
            "timestamp": datetime.now().isoformat(),
            "version": self.docs_config.get("meta", {}).get("version", "1.0.0"),
            "stats": self.docs_config.get("structure", {})
            .get("docs/", {})
            .get("stats", {}),
            "changes": self._scan_project_changes(),
            "recommendations": [],
        }

        # 生成建议
        stats = report["stats"]
        completion_percentage = stats.get("completionPercentage", 0)

        if completion_percentage < 50:
            report["recommendations"].append("项目部署进度较低，建议优先完成核心功能")
        elif completion_percentage < 80:
            report["recommendations"].append("项目部署进度良好，继续完善剩余功能")
        else:
            report["recommendations"].append("项目部署进度优秀，建议进行全面测试和优化")

        return report

    def run_full_update(self) -> Dict[str, Any]:
        """运行完整更新"""
        self.logger.info("=== 开始自动文档更新 ===")

        start_time = time.time()

        # 1. 更新版本信息
        self.update_version_info()

        # 2. 更新部署进度
        self.update_deployment_progress()

        # 3. 更新README
        self.update_readme_status()

        # 4. 同步文档系统
        self.sync_documentation()

        # 5. 保存配置
        self._save_docs_config()

        # 6. 生成报告
        report = self.generate_progress_report()

        elapsed_time = time.time() - start_time
        report["execution_time"] = round(elapsed_time, 2)

        self.logger.info(f"=== 自动文档更新完成，耗时: {elapsed_time:.2f}秒 ===")

        return report


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="自动文档更新器")
    parser.add_argument("--dry-run", action="store_true", help="仅检查，不执行更新")
    parser.add_argument("--force", action="store_true", help="强制更新所有内容")
    parser.add_argument("--report-only", action="store_true", help="仅生成报告")
    parser.add_argument("--quiet", action="store_true", help="静默模式")

    args = parser.parse_args()

    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)

    updater = AutoDocUpdater()

    if args.dry_run:
        # 仅检查模式
        print("=== 文档更新检查模式 ===")
        changes = updater._scan_project_changes()
        print(json.dumps(changes, indent=2, ensure_ascii=False))
        return 0

    if args.report_only:
        # 仅报告模式
        report = updater.generate_progress_report()
        print("=== 进度报告 ===")
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0

    # 执行完整更新
    report = updater.run_full_update()

    print("\n=== 更新摘要 ===")
    print(f"版本: {report['version']}")
    print(f"完成进度: {report['stats'].get('completionPercentage', 0)}%")
    print(f"执行时间: {report['execution_time']}秒")

    if report["recommendations"]:
        print("\n建议:")
        for rec in report["recommendations"]:
            print(f"  - {rec}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
