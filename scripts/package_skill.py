#!/usr/bin/env python3
"""
打包技能为 .skill 文件

用法:
    python scripts/package_skill.py <path/to/skill-folder> <output-directory>
"""

import os
import sys
import argparse
import zipfile
import yaml


def package_skill(skill_path, output_dir):
    """
    打包技能为 .skill 文件

    Args:
        skill_path (str): 技能目录路径
        output_dir (str): 输出目录
    """
    # 验证技能目录
    if not os.path.exists(skill_path):
        print(f"技能目录不存在: {skill_path}")
        return False

    # 验证 SKILL.md 文件
    skill_md_path = os.path.join(skill_path, 'SKILL.md')
    if not os.path.exists(skill_md_path):
        print(f"SKILL.md 文件不存在: {skill_md_path}")
        return False

    # 读取并验证 SKILL.md
    if not validate_skill_md(skill_md_path):
        return False

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 生成 .skill 文件名
    skill_name = os.path.basename(skill_path)
    output_file = os.path.join(output_dir, f'{skill_name}.skill')

    # 打包技能
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 遍历技能目录
        for root, dirs, files in os.walk(skill_path):
            for file in files:
                file_path = os.path.join(root, file)
                # 计算相对路径
                arcname = os.path.relpath(file_path, skill_path)
                # 添加文件到 zip
                zipf.write(file_path, arcname)

    print(f"技能打包成功: {output_file}")
    return True


def validate_skill_md(skill_md_path):
    """
    验证 SKILL.md 文件

    Args:
        skill_md_path (str): SKILL.md 文件路径

    Returns:
        bool: 验证是否通过
    """
    try:
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取 YAML frontmatter
        if content.startswith('---'):
            frontmatter_end = content.find('---', 3)
            if frontmatter_end != -1:
                frontmatter_content = content[3:frontmatter_end]
                frontmatter = yaml.safe_load(frontmatter_content)

                # 验证必需字段
                if 'name' not in frontmatter:
                    print("SKILL.md 缺少 name 字段")
                    return False

                if 'description' not in frontmatter:
                    print("SKILL.md 缺少 description 字段")
                    return False

                print(f"验证通过: {frontmatter['name']}")
                return True

        print("SKILL.md 格式不正确，缺少 YAML frontmatter")
        return False

    except Exception as e:
        print(f"验证 SKILL.md 时出错: {e}")
        return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='打包技能为 .skill 文件')
    parser.add_argument('skill_path', help='技能目录路径')
    parser.add_argument('output_dir', nargs='?', default='./dist', help='输出目录')

    args = parser.parse_args()

    package_skill(args.skill_path, args.output_dir)
