#!/usr/bin/env python3
"""
初始化技能目录结构的脚本

用法:
    python scripts/init_skill.py <skill-name> --path <output-directory>
"""

import os
import sys
import argparse
import yaml


def init_skill(skill_name, output_path):
    """初始化技能目录结构"""
    # 创建技能目录
    skill_dir = os.path.join(output_path, skill_name)
    os.makedirs(skill_dir, exist_ok=True)
    
    # 创建资源目录
    os.makedirs(os.path.join(skill_dir, 'scripts'), exist_ok=True)
    os.makedirs(os.path.join(skill_dir, 'references'), exist_ok=True)
    os.makedirs(os.path.join(skill_dir, 'assets'), exist_ok=True)
    
    # 创建 SKILL.md 文件
    skill_md_path = os.path.join(skill_dir, 'SKILL.md')
    
    # 生成 YAML frontmatter 和内容
    frontmatter = {
        'name': skill_name,
        'description': f'A skill for {skill_name} functionality'
    }
    
    content = f"""---
{yaml.dump(frontmatter, default_flow_style=False).strip()}
---

# {skill_name}

## Overview

[Brief description of what this skill does]

## When to Use

[Explain when this skill should be used]

## Workflow

[Describe the workflow for using this skill]

## Resources

### Scripts

[List and describe any scripts included in the skill]

### References

[List and describe any reference materials included in the skill]

### Assets

[List and describe any assets included in the skill]

## Examples

[Provide examples of how to use this skill]
"""
    
    with open(skill_md_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 创建示例文件
    create_example_files(skill_dir)
    
    print(f"Skill initialized successfully at: {skill_dir}")


def create_example_files(skill_dir):
    """创建示例文件"""
    # 示例脚本
    example_script = os.path.join(skill_dir, 'scripts', 'example.py')
    with open(example_script, 'w', encoding='utf-8') as f:
        f.write('''#!/usr/bin/env python3
"""
Example script for the skill
"""

print("Hello from example script!")
''')
    
    # 示例参考文件
    example_reference = os.path.join(skill_dir, 'references', 'example.md')
    with open(example_reference, 'w', encoding='utf-8') as f:
        f.write('''# Example Reference

This is an example reference file.
''')
    
    # 示例资产文件
    example_asset = os.path.join(skill_dir, 'assets', 'example.txt')
    with open(example_asset, 'w', encoding='utf-8') as f:
        f.write('This is an example asset file.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Initialize a new skill')
    parser.add_argument('skill_name', help='Name of the skill')
    parser.add_argument('--path', default='.', help='Output directory for the skill')
    
    args = parser.parse_args()
    
    init_skill(args.skill_name, args.path)
