#!/usr/bin/env python3
"""
配置一致性验证脚本
独立运行，验证项目配置的一致性和完整性
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/config_validator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ConfigValidator:
    """配置验证器"""

    def __init__(self, project_root: Optional[str] = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.issues = []
        self.warnings = []

        # 关键配置文件路径
        self.config_paths = {
            'project_config': self.project_root / 'project_config.json',
            'docs_config': self.project_root / 'docs' / 'docs_config.json',
            'scripts_config': self.project_root / 'scripts' / 'scripts_config.json',
            'rules_config': self.project_root / 'rules' / 'rules.config.js'
        }

        logger.info(f"初始化配置验证器，项目根目录: {self.project_root}")

    def validate_all_configs(self) -> Dict[str, Any]:
        """验证所有配置文件"""
        logger.info("开始验证所有配置文件...")
        start_time = time.time()

        results = {
            'timestamp': datetime.now().isoformat(),
            'validations': {},
            'issues': [],
            'warnings': [],
            'summary': {}
        }

        # 1. 验证项目主配置
        results['validations']['project_config'] = self.validate_project_config()

        # 2. 验证文档配置
        results['validations']['docs_config'] = self.validate_docs_config()

        # 3. 验证脚本配置
        results['validations']['scripts_config'] = self.validate_scripts_config()

        # 4. 验证规则配置
        results['validations']['rules_config'] = self.validate_rules_config()

        # 5. 验证配置间一致性
        results['validations']['cross_config'] = self.validate_cross_config_consistency()

        # 汇总结果
        results['issues'] = self.issues
        results['warnings'] = self.warnings
        results['summary'] = self.generate_summary(results)
        results['duration'] = time.time() - start_time

        logger.info(f"配置验证完成，耗时: {results['duration']:.2f}秒")
        return results

    def validate_project_config(self) -> Dict[str, Any]:
        """验证项目主配置"""
        result = {'status': 'pass', 'details': {}, 'issues': [], 'warnings': []}

        config_path = self.config_paths['project_config']
        if not config_path.exists():
            result['issues'].append("项目主配置文件不存在")
            result['status'] = 'fail'
            return result

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # 验证必需字段
            required_fields = ['meta', 'project', 'subprojects']
            for field in required_fields:
                if field not in config:
                    result['issues'].append(f"缺少必需字段: {field}")
                    result['status'] = 'fail'

            # 验证子项目配置
            if 'subprojects' in config:
                subprojects = config['subprojects']
                required_subprojects = ['src', 'assets', 'rules', 'scripts', 'docs']

                for sub in required_subprojects:
                    if sub not in subprojects:
                        result['issues'].append(f"缺少子项目配置: {sub}")
                        result['status'] = 'fail'
                    else:
                        sub_config = subprojects[sub]
                        if 'path' not in sub_config:
                            result['warnings'].append(f"子项目 {sub} 缺少路径配置")

                        # 验证rulesLink
                        if 'rulesLink' not in sub_config:
                            result['warnings'].append(f"子项目 {sub} 缺少规则链接")

            result['details']['config_version'] = config.get('meta', {}).get('version', 'unknown')

        except Exception as e:
            result['issues'].append(f"项目配置解析失败: {e}")
            result['status'] = 'fail'

        self.issues.extend(result['issues'])
        self.warnings.extend(result['warnings'])
        return result

    def validate_docs_config(self) -> Dict[str, Any]:
        """验证文档配置"""
        result = {'status': 'pass', 'details': {}, 'issues': [], 'warnings': []}

        config_path = self.config_paths['docs_config']
        if not config_path.exists():
            result['issues'].append("文档配置文件不存在")
            result['status'] = 'fail'
            return result

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # 验证文档结构
            if 'structure' not in config:
                result['issues'].append("文档配置缺少结构定义")
                result['status'] = 'fail'

            # 验证文档路径
            docs_dir = self.project_root / 'docs'
            if docs_dir.exists():
                required_docs = [
                    'docs_README.md',
                    'docs_config.json',
                    'project_docs/01-project-architecture.md',
                    'deployment_progress/01-overall-progress.md'
                ]

                for doc in required_docs:
                    doc_path = docs_dir / doc
                    if not doc_path.exists():
                        result['issues'].append(f"缺少文档文件: {doc}")
                        result['status'] = 'fail'

        except Exception as e:
            result['issues'].append(f"文档配置解析失败: {e}")
            result['status'] = 'fail'

        self.issues.extend(result['issues'])
        self.warnings.extend(result['warnings'])
        return result

    def validate_scripts_config(self) -> Dict[str, Any]:
        """验证脚本配置"""
        result = {'status': 'pass', 'details': {}, 'issues': [], 'warnings': []}

        config_path = self.config_paths['scripts_config']
        if not config_path.exists():
            result['issues'].append("脚本配置文件不存在")
            result['status'] = 'fail'
            return result

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # 验证脚本结构
            if 'structure' not in config:
                result['issues'].append("脚本配置缺少结构定义")
                result['status'] = 'fail'

            # 验证健康监控脚本
            structure = config.get('structure', {})
            health_monitor = structure.get('scripts/health_monitor/', {})

            if 'subScripts' not in health_monitor:
                result['issues'].append("缺少健康监控脚本定义")
                result['status'] = 'fail'
            else:
                required_scripts = [
                    'health_monitor.py',
                    'config_validator.py',
                    'ui_interaction_monitor.py'
                ]

                for script in required_scripts:
                    if script not in health_monitor['subScripts']:
                        result['issues'].append(f"缺少健康监控脚本: {script}")
                        result['status'] = 'fail'

            # 验证执行规则
            if 'executionRules' not in config:
                result['warnings'].append("建议添加脚本执行规则配置")

        except Exception as e:
            result['issues'].append(f"脚本配置解析失败: {e}")
            result['status'] = 'fail'

        self.issues.extend(result['issues'])
        self.warnings.extend(result['warnings'])
        return result

    def validate_rules_config(self) -> Dict[str, Any]:
        """验证规则配置"""
        result = {'status': 'pass', 'details': {}, 'issues': [], 'warnings': []}

        config_path = self.config_paths['rules_config']
        if not config_path.exists():
            result['warnings'].append("规则JS配置文件不存在，使用JSON配置")
            return result

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 验证基本JS结构
            if 'module.exports' not in content and 'export' not in content:
                result['warnings'].append("规则配置文件缺少导出语句")

        except Exception as e:
            result['issues'].append(f"规则配置读取失败: {e}")
            result['status'] = 'fail'

        # 验证五层规则文件
        rules_dir = self.project_root / 'rules'
        required_rules = [
            'L1-meta-goal.json',
            'L2-understanding.json',
            'L3-constraints.json',
            'L4-decisions.json',
            'L5-execution.json'
        ]

        for rule_file in required_rules:
            rule_path = rules_dir / rule_file
            if not rule_path.exists():
                result['issues'].append(f"缺少规则文件: {rule_file}")
                result['status'] = 'fail'
            else:
                try:
                    with open(rule_path, 'r', encoding='utf-8') as f:
                        rule_data = json.load(f)

                    # 验证规则层级
                    expected_layer = rule_file.split('-')[0]
                    if rule_data.get('meta', {}).get('layer') != expected_layer:
                        result['warnings'].append(f"规则文件层级不匹配: {rule_file}")

                except Exception as e:
                    result['issues'].append(f"规则文件解析失败 {rule_file}: {e}")
                    result['status'] = 'fail'

        self.issues.extend(result['issues'])
        self.warnings.extend(result['warnings'])
        return result

    def validate_cross_config_consistency(self) -> Dict[str, Any]:
        """验证配置间一致性"""
        result = {'status': 'pass', 'details': {}, 'issues': [], 'warnings': []}

        try:
            # 读取所有配置文件
            configs = {}
            for name, path in self.config_paths.items():
                if path.exists():
                    try:
                        if path.suffix == '.json':
                            with open(path, 'r', encoding='utf-8') as f:
                                configs[name] = json.load(f)
                        elif path.suffix == '.js':
                            with open(path, 'r', encoding='utf-8') as f:
                                configs[name] = {'content': f.read()}
                    except Exception as e:
                        result['issues'].append(f"配置文件读取失败 {name}: {e}")
                        continue

            # 验证路径一致性
            if 'project_config' in configs and 'docs_config' in configs:
                project_paths = configs['project_config'].get('deployment', {}).get('paths', {})
                docs_paths = configs['docs_config'].get('structure', {})

                for key, path in project_paths.items():
                    if key in docs_paths:
                        if path != docs_paths[key]:
                            result['issues'].append(f"路径不一致 {key}: 项目配置({path}) vs 文档配置({docs_paths[key]})")
                            result['status'] = 'fail'

            # 验证版本一致性
            versions = {}
            for name, config in configs.items():
                if isinstance(config, dict) and 'meta' in config:
                    version = config['meta'].get('version')
                    if version:
                        versions[name] = version

            if len(versions) > 1:
                version_values = list(versions.values())
                if not all(v == version_values[0] for v in version_values):
                    result['warnings'].append(f"配置版本不一致: {versions}")

        except Exception as e:
            result['issues'].append(f"跨配置一致性检查失败: {e}")
            result['status'] = 'fail'

        self.issues.extend(result['issues'])
        self.warnings.extend(result['warnings'])
        return result

    def generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """生成验证摘要"""
        summary = {
            'total_validations': len(results['validations']),
            'passed_validations': 0,
            'failed_validations': 0,
            'warning_validations': 0,
            'total_issues': len(results['issues']),
            'total_warnings': len(results['warnings']),
            'consistency_score': 0.0
        }

        for validation_name, validation_result in results['validations'].items():
            status = validation_result.get('status', 'unknown')
            if status == 'pass':
                summary['passed_validations'] += 1
            elif status == 'fail':
                summary['failed_validations'] += 1
            elif status == 'warning':
                summary['warning_validations'] += 1

        summary['consistency_score'] = (summary['passed_validations'] / summary['total_validations']) * 100 if summary['total_validations'] > 0 else 0.0

        return summary

    def save_report(self, results: Dict[str, Any], output_file: Optional[str] = None) -> str:
        """保存验证报告"""
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"logs/config_validation_report_{timestamp}.json"

        output_path = self.project_root / output_file
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info(f"配置验证报告已保存到: {output_path}")
        return str(output_path)

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='配置一致性验证器')
    parser.add_argument('--project-root', help='项目根目录路径')
    parser.add_argument('--output', help='输出报告文件路径')
    parser.add_argument('--quiet', action='store_true', help='静默模式')

    args = parser.parse_args()

    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)

    validator = ConfigValidator(args.project_root)
    results = validator.validate_all_configs()

    # 保存报告
    report_path = validator.save_report(results, args.output)

    # 输出摘要
    summary = results['summary']
    print(f"\n配置验证摘要:")
    print(f"总验证数: {summary['total_validations']}")
    print(f"通过: {summary['passed_validations']}")
    print(f"失败: {summary['failed_validations']}")
    print(f"警告: {summary['warning_validations']}")
    print(f"一致性评分: {summary['consistency_score']:.1f}%")
    print(f"发现问题: {summary['total_issues']}")
    print(f"警告信息: {summary['total_warnings']}")
    print(f"报告路径: {report_path}")

    # 返回退出码
    return 0 if summary['failed_validations'] == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
