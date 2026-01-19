#!/usr/bin/env python3
"""
my_ai_popup_project 配置验证器
功能: 验证所有配置文件的有效性和层级关系

使用方式:
    python3 scripts/validate_configs.py --all      # 验证所有配置
    python3 scripts/validate_configs.py --level 1  # 验证L1配置
    python3 scripts/validate_configs.py --json     # 输出JSON格式

版本: 1.0.0
最后更新: 2025-01-21
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class ConfigLevel(Enum):
    """配置层级枚举"""
    LEVEL_1 = "L1 - 元目标层 (最高优先级)"
    LEVEL_2 = "L2 - 全局理解层"
    LEVEL_3 = "L3 - 约束层"
    LEVEL_4 = "L4 - 决策层"
    LEVEL_5 = "L5 - 执行层"
    PROJECT = "项目配置"
    UNKNOWN = "未知层级"


class ValidationStatus(Enum):
    """验证状态枚举"""
    PASS = "通过"
    FAIL = "失败"
    WARNING = "警告"
    SKIP = "跳过"


@dataclass
class ConfigFile:
    """配置文件信息"""
    path: str
    level: ConfigLevel
    required: bool
    exists: bool = False
    valid_json: bool = False
    content: Dict = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class ValidationResult:
    """验证结果"""
    config_file: ConfigFile
    status: ValidationStatus
    message: str
    details: Dict = field(default_factory=dict)


class ConfigValidator:
    """
    my_ai_popup_project配置验证器
    验证项目中的所有配置文件
    """

    def __init__(self):
        self.project_root = self._get_project_root()
        self.results: List[ValidationResult] = []
        self.config_files = self._define_config_files()

    def _get_project_root(self) -> Path:
        """获取项目根目录"""
        current_file = Path(__file__).resolve()
        return current_file.parent.parent

    def _define_config_files(self) -> List[ConfigFile]:
        """定义需要验证的配置文件"""
        files = []

        # L1 层级 - 元目标层 (最高优先级)
        files.append(ConfigFile(
            path="rules/L1-meta-goal.json",
            level=ConfigLevel.LEVEL_1,
            required=True
        ))

        # L2 层级 - 全局理解层
        files.append(ConfigFile(
            path="rules/L2-understanding.json",
            level=ConfigLevel.LEVEL_2,
            required=True
        ))

        # L3 层级 - 约束层
        files.append(ConfigFile(
            path="rules/L3-constraints.json",
            level=ConfigLevel.LEVEL_3,
            required=True
        ))

        # L4 层级 - 决策层
        files.append(ConfigFile(
            path="rules/L4-decisions.json",
            level=ConfigLevel.LEVEL_4,
            required=True
        ))

        # L5 层级 - 执行层
        files.append(ConfigFile(
            path="rules/L5-execution.json",
            level=ConfigLevel.LEVEL_5,
            required=True
        ))

        # 项目配置文件 (JSON格式)
        files.append(ConfigFile(
            path="project_config.json",
            level=ConfigLevel.PROJECT,
            required=True
        ))

        # src配置
        files.append(ConfigFile(
            path="src/src_config.json",
            level=ConfigLevel.PROJECT,
            required=False
        ))
        files.append(ConfigFile(
            path="src/src_config_refactor.json",
            level=ConfigLevel.PROJECT,
            required=False
        ))

        # scripts配置
        files.append(ConfigFile(
            path="scripts/scripts_config.json",
            level=ConfigLevel.PROJECT,
            required=False
        ))
        files.append(ConfigFile(
            path="scripts/scripts_config_refactor.json",
            level=ConfigLevel.PROJECT,
            required=False
        ))

        # web配置
        files.append(ConfigFile(
            path="web/web_config.json",
            level=ConfigLevel.PROJECT,
            required=False
        ))
        files.append(ConfigFile(
            path="web/web_config_refactor.json",
            level=ConfigLevel.PROJECT,
            required=False
        ))

        # docs配置
        files.append(ConfigFile(
            path="docs/docs_config.json",
            level=ConfigLevel.PROJECT,
            required=False
        ))

        # assets配置
        files.append(ConfigFile(
            path="assets/assets_config.json",
            level=ConfigLevel.PROJECT,
            required=False
        ))

        return files

    def _load_json(self, file_path: Path) -> tuple:
        """
        加载JSON文件

        Returns:
            tuple: (是否成功, 内容或错误信息)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
            return True, content
        except json.JSONDecodeError as e:
            return False, f"JSON解析错误: {e}"
        except FileNotFoundError:
            return False, "文件不存在"
        except Exception as e:
            return False, f"未知错误: {e}"

    def _validate_required_fields(self, content: Dict, level: ConfigLevel) -> List[str]:
        """验证必需字段"""
        errors = []

        # L1配置应该有meta和goals
        if level == ConfigLevel.LEVEL_1:
            if 'meta' not in content:
                errors.append("缺少 meta 字段")
            if 'goals' not in content and 'project_goals' not in content:
                errors.append("缺少 goals/project_goals 字段")

        # L2配置应该有核心架构字段
        if level == ConfigLevel.LEVEL_2:
            required_fields = ['architecture', 'modules', 'relationships']
            for field in required_fields:
                if field not in content:
                    errors.append(f"缺少 {field} 字段")

        # L3配置应该有约束相关字段
        if level == ConfigLevel.LEVEL_3:
            required_fields = ['dependencies', 'python', 'performanceConstraints']
            for field in required_fields:
                if field not in content:
                    errors.append(f"缺少 {field} 字段")

        # L4配置应该有决策相关字段
        if level == ConfigLevel.LEVEL_4:
            required_fields = ['architectureDecisions', 'technologyChoices']
            for field in required_fields:
                if field not in content:
                    errors.append(f"缺少 {field} 字段")

        # L5配置应该有执行相关字段
        if level == ConfigLevel.LEVEL_5:
            required_fields = ['executionPlan', 'implementationDetails']
            for field in required_fields:
                if field not in content:
                    errors.append(f"缺少 {field} 字段")

        return errors

    def _validate_inheritance(self, content: Dict, level: ConfigLevel) -> List[str]:
        """验证层级继承关系"""
        warnings = []

        # L2-L5配置应该引用上层配置
        if level.value != ConfigLevel.LEVEL_1.value:
            # 检查是否有对上层规则的引用
            content_str = json.dumps(content)
            if 'L1' not in content_str and 'meta' not in content_str:
                warnings.append("配置未显式引用L1元目标层")

        return warnings

    def validate_file(self, config_file: ConfigFile) -> ValidationResult:
        """验证单个配置文件"""
        file_path = self.project_root / config_file.path

        # 检查文件是否存在
        if not file_path.exists():
            config_file.exists = False
            if config_file.required:
                return ValidationResult(
                    config_file=config_file,
                    status=ValidationStatus.FAIL,
                    message=f"必需配置文件不存在: {config_file.path}",
                    details={"path": str(file_path)}
                )
            else:
                return ValidationResult(
                    config_file=config_file,
                    status=ValidationStatus.SKIP,
                    message=f"可选配置文件不存在: {config_file.path}",
                    details={"path": str(file_path)}
                )

        config_file.exists = True

        # 加载并解析JSON
        success, result = self._load_json(file_path)
        if not success:
            config_file.valid_json = False
            config_file.errors.append(result)
            return ValidationResult(
                config_file=config_file,
                status=ValidationStatus.FAIL,
                message=f"配置文件解析失败: {config_file.path}",
                details={"error": result}
            )

        config_file.valid_json = True
        config_file.content = result

        # 验证必需字段
        errors = self._validate_required_fields(result, config_file.level)
        config_file.errors.extend(errors)

        # 验证继承关系
        warnings = self._validate_inheritance(result, config_file.level)
        config_file.warnings.extend(warnings)

        # 生成消息
        if errors:
            message = f"配置文件验证失败: {config_file.path}"
            status = ValidationStatus.FAIL
        elif warnings:
            message = f"配置文件有警告: {config_file.path}"
            status = ValidationStatus.WARNING
        else:
            message = f"配置文件验证通过: {config_file.path}"
            status = ValidationStatus.PASS

        return ValidationResult(
            config_file=config_file,
            status=status,
            message=message,
            details={
                "errors": config_file.errors,
                "warnings": config_file.warnings,
                "meta": config_file.content.get("meta", {})
            }
        )

    def validate_all(self, level: Optional[ConfigLevel] = None) -> Dict[str, Any]:
        """验证所有配置文件"""
        self.results.clear()

        for config_file in self.config_files:
            if level is None or config_file.level == level:
                result = self.validate_file(config_file)
                self.results.append(result)

        return self._summarize_results()

    def _summarize_results(self) -> Dict[str, Any]:
        """汇总验证结果"""
        passed = sum(1 for r in self.results if r.status == ValidationStatus.PASS)
        failed = sum(1 for r in self.results if r.status == ValidationStatus.FAIL)
        warnings = sum(1 for r in self.results if r.status == ValidationStatus.WARNING)
        skipped = sum(1 for r in self.results if r.status == ValidationStatus.SKIP)

        by_level: Dict[str, Dict[str, int]] = {}
        for result in self.results:
            level_name = result.config_file.level.name
            if level_name not in by_level:
                by_level[level_name] = {"pass": 0, "fail": 0, "warning": 0, "skip": 0}
            by_level[level_name][result.status.name.lower()] += 1

        return {
            "timestamp": datetime.now().isoformat(),
            "total": len(self.results),
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "skipped": skipped,
            "all_passed": failed == 0,
            "by_level": by_level,
            "results": [
                {
                    "path": r.config_file.path,
                    "level": r.config_file.level.name,
                    "status": r.status.value,
                    "message": r.message,
                    "errors": r.config_file.errors,
                    "warnings": r.config_file.warnings
                }
                for r in self.results
            ]
        }

    def print_summary(self, json_output: bool = False):
        """打印验证摘要"""
        summary = self.validate_all()

        if json_output:
            print(json.dumps(summary, ensure_ascii=False, indent=2))
            return

        print("\n" + "=" * 70)
        print("my_ai_popup_project 配置验证报告")
        print("=" * 70)
        print(f"验证时间: {summary['timestamp']}")
        print()

        # 总体统计
        print("总体结果:")
        print(f"  ✓ 通过: {summary['passed']}")
        if summary['warnings'] > 0:
            print(f"  ⚠ 警告: {summary['warnings']}")
        if summary['failed'] > 0:
            print(f"  ✗ 失败: {summary['failed']}")
        if summary['skipped'] > 0:
            print(f"  ○ 跳过: {summary['skipped']}")
        print()

        # 按层级显示
        print("按层级统计:")
        for level, stats in summary['by_level'].items():
            level_icon = "✓" if stats['fail'] == 0 else ("⚠" if stats['warning'] > 0 else "✗")
            print(f"  {level_icon} {level}:", end=" ")
            parts = []
            if stats['pass'] > 0:
                parts.append(f"{stats['pass']}通过")
            if stats['warning'] > 0:
                parts.append(f"{stats['warning']}警告")
            if stats['fail'] > 0:
                parts.append(f"{stats['fail']}失败")
            if stats['skip'] > 0:
                parts.append(f"{stats['skip']}跳过")
            print(", ".join(parts))
        print()

        # 详细结果
        print("详细结果:")
        for result in summary['results']:
            if result['status'] == '通过':
                icon = "✓"
            elif result['status'] == '失败':
                icon = "✗"
            elif result['status'] == '警告':
                icon = "⚠"
            else:
                icon = "○"

            print(f"  {icon} [{result['level']}] {result['path']}")
            print(f"      {result['message']}")

            if result['errors']:
                for error in result['errors']:
                    print(f"      ✗ {error}")
            if result['warnings']:
                for warning in result['warnings']:
                    print(f"      ⚠ {warning}")
        print()

        # 总体结论
        print("=" * 70)
        if summary['all_passed']:
            print("  ✓ 所有配置验证通过!")
        else:
            print("  ✗ 存在配置问题，请检查上述错误")
        print("=" * 70)

        return summary


def main():
    import argparse

    parser = argparse.ArgumentParser(description="my_ai_popup_project 配置验证器")
    parser.add_argument("--all", action="store_true", help="验证所有配置")
    parser.add_argument("--level", type=int, choices=[1, 2, 3, 4, 5],
                        help="验证指定层级配置 (1-5)")
    parser.add_argument("--json", action="store_true", help="输出JSON格式")

    args = parser.parse_args()

    validator = ConfigValidator()

    if args.level:
        level_map = {
            1: ConfigLevel.LEVEL_1,
            2: ConfigLevel.LEVEL_2,
            3: ConfigLevel.LEVEL_3,
            4: ConfigLevel.LEVEL_4,
            5: ConfigLevel.LEVEL_5
        }
        summary = validator.validate_all(level=level_map[args.level])
        if args.json:
            print(json.dumps(summary, ensure_ascii=False, indent=2))
        else:
            validator.print_summary(json_output=True)
    else:
        validator.print_summary(json_output=args.json)


if __name__ == "__main__":
    main()
