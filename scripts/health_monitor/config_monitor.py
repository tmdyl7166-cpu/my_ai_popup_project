#!/usr/bin/env python3
"""
配置监控脚本
专门用于监控项目配置的一致性和完整性
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConfigMonitor:
    """配置监控类"""

    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or Path(__file__).parent.parent.parent)
        self.config_files = {
            'project': 'project_config.json',
            'docs': 'docs/docs_config.json',
            'rules_js': 'rules/rules.config.js',
            'src': 'src/src_config.json',
            'ai': 'src/ai/ai_config.json',
            'backend': 'src/backend/backend_config.json',
            'frontend': 'src/frontend/frontend_config.json',
            'processing': 'src/processing/processing_config.json',
            'integrations': 'src/integrations/integrations_config.json',
            'utils': 'src/utils/utils_config.json',
            'config': 'src/config/config_config.json'
        }

    def check_config_integrity(self) -> Dict[str, Any]:
        """检查配置完整性"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'configs': {},
            'issues': [],
            'summary': {}
        }

        for config_name, config_path in self.config_files.items():
            full_path = self.project_root / config_path
            if full_path.exists():
                try:
                    if config_path.endswith('.json'):
                        with open(full_path, 'r', encoding='utf-8') as f:
                            config_data = json.load(f)
                        results['configs'][config_name] = {
                            'status': 'loaded',
                            'path': str(full_path),
                            'data': config_data
                        }
                    elif config_path.endswith('.js'):
                        with open(full_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        results['configs'][config_name] = {
                            'status': 'loaded',
                            'path': str(full_path),
                            'content': content[:200] + '...' if len(content) > 200 else content
                        }
                except Exception as e:
                    results['configs'][config_name] = {
                        'status': 'error',
                        'error': str(e)
                    }
                    results['issues'].append(f"配置加载失败 {config_name}: {e}")
            else:
                results['configs'][config_name] = {
                    'status': 'missing',
                    'path': str(full_path)
                }
                results['issues'].append(f"缺少配置文件: {config_name} ({config_path})")

        # 检查配置一致性
        consistency_issues = self.check_config_consistency(results['configs'])
        results['issues'].extend(consistency_issues)

        results['summary'] = {
            'total_configs': len(self.config_files),
            'loaded_configs': len([c for c in results['configs'].values() if c['status'] == 'loaded']),
            'missing_configs': len([c for c in results['configs'].values() if c['status'] == 'missing']),
            'error_configs': len([c for c in results['configs'].values() if c['status'] == 'error']),
            'total_issues': len(results['issues'])
        }

        return results

    def check_config_consistency(self, configs: Dict[str, Any]) -> List[str]:
        """检查配置一致性"""
        issues = []

        # 检查项目配置与子配置的一致性
        if 'project' in configs and configs['project']['status'] == 'loaded':
            project_config = configs['project']['data']
            project_subprojects = project_config.get('subprojects', {})

            for sub_name, sub_info in project_subprojects.items():
                config_file = sub_info.get('configFile', '').replace('./', '')
                if config_file and config_file in [p.replace('./', '') for p in self.config_files.values()]:
                    if sub_name in configs:
                        sub_config = configs[sub_name]
                        if sub_config['status'] != 'loaded':
                            issues.append(f"子项目 {sub_name} 配置未正确加载")
                    else:
                        issues.append(f"项目配置中定义的子项目 {sub_name} 缺少对应配置检查")

        # 检查路径一致性
        if 'project' in configs and 'docs' in configs:
            project_data = configs['project'].get('data', {})
            docs_data = configs['docs'].get('data', {})

            project_paths = project_data.get('deployment', {}).get('paths', {})
            docs_structure = docs_data.get('structure', {})

            for path_key, project_path in project_paths.items():
                if path_key in docs_structure:
                    docs_path = docs_structure[path_key]
                    if project_path != docs_path:
                        issues.append(f"路径不一致 {path_key}: 项目={project_path}, 文档={docs_path}")

        return issues

    def validate_config_schema(self, config_name: str, config_data: Dict[str, Any]) -> List[str]:
        """验证配置架构"""
        issues = []

        # 基本结构检查
        if 'meta' not in config_data:
            issues.append(f"{config_name}: 缺少meta字段")
        else:
            meta = config_data['meta']
            required_meta_fields = ['name', 'version']
            for field in required_meta_fields:
                if field not in meta:
                    issues.append(f"{config_name}: meta缺少{field}字段")

        return issues

    def generate_config_report(self, results: Dict[str, Any]) -> str:
        """生成配置报告"""
        report = []
        report.append("# 配置完整性报告")
        report.append(f"生成时间: {results['timestamp']}")
        report.append("")

        report.append("## 配置状态汇总")
        summary = results['summary']
        report.append(f"- 总配置数: {summary['total_configs']}")
        report.append(f"- 已加载: {summary['loaded_configs']}")
        report.append(f"- 缺失: {summary['missing_configs']}")
        report.append(f"- 错误: {summary['error_configs']}")
        report.append(f"- 问题总数: {summary['total_issues']}")
        report.append("")

        if results['issues']:
            report.append("## 发现的问题")
            for issue in results['issues']:
                report.append(f"- {issue}")
            report.append("")

        report.append("## 详细配置状态")
        for config_name, config_info in results['configs'].items():
            report.append(f"### {config_name}")
            report.append(f"- 状态: {config_info['status']}")
            if 'path' in config_info:
                report.append(f"- 路径: {config_info['path']}")
            if 'error' in config_info:
                report.append(f"- 错误: {config_info['error']}")
            report.append("")

        return "\n".join(report)

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='配置监控脚本')
    parser.add_argument('--project-root', help='项目根目录')
    parser.add_argument('--output', help='输出报告文件')
    parser.add_argument('--format', choices=['json', 'md'], default='json', help='输出格式')

    args = parser.parse_args()

    monitor = ConfigMonitor(args.project_root)
    results = monitor.check_config_integrity()

    if args.format == 'json':
        output_content = json.dumps(results, indent=2, ensure_ascii=False)
        output_ext = 'json'
    else:
        output_content = monitor.generate_config_report(results)
        output_ext = 'md'

    if args.output:
        output_file = args.output
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"logs/config_report_{timestamp}.{output_ext}"

    output_path = monitor.project_root / output_file
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output_content)

    print(f"配置报告已保存到: {output_path}")

    # 输出摘要
    summary = results['summary']
    print("\n配置检查摘要:")
    print(f"总配置数: {summary['total_configs']}")
    print(f"已加载: {summary['loaded_configs']}")
    print(f"缺失: {summary['missing_configs']}")
    print(f"错误: {summary['error_configs']}")
    print(f"发现问题: {summary['total_issues']}")

    return 0 if summary['total_issues'] == 0 else 1

if __name__ == '__main__':
    exit(main())
