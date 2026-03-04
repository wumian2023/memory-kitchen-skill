#!/usr/bin/env python3
"""
更新和维护知识库内容

此脚本用于更新和维护知识库内容，包括检查过时信息、合并重复知识、标记需要验证的知识等。
"""

import os
import re
import json
from datetime import datetime, timedelta


def get_knowledge_base_dir():
    """
    获取知识库目录路径

    Returns:
        str: 知识库目录路径
    """
    # 获取用户主目录
    home_dir = os.path.expanduser('~')

    # 构建知识库路径
    knowledge_base_dir = os.path.join(home_dir, '.trae-cn', 'knowledge')

    return knowledge_base_dir


def update_knowledge_base(knowledge_base_dir=None):
    """
    更新和维护知识库

    Args:
        knowledge_base_dir (str): 知识库目录，默认为用户目录下的 .trae-cn/knowledge
    """
    # 如果没有指定知识库目录，使用默认路径
    if knowledge_base_dir is None:
        knowledge_base_dir = get_knowledge_base_dir()

    # 收集所有知识文件
    knowledge_files = collect_knowledge_files(knowledge_base_dir)

    # 检查过时信息
    check_outdated_information(knowledge_files)

    # 合并重复知识
    merge_duplicate_knowledge(knowledge_files)

    # 标记需要验证的知识
    mark_needs_verification(knowledge_files)

    # 更新知识库索引
    update_knowledge_base_index(knowledge_base_dir)

    # 更新最近更新记录
    update_recent_updates(knowledge_base_dir)


def collect_knowledge_files(knowledge_base_dir):
    """
    收集所有知识文件

    Args:
        knowledge_base_dir (str): 知识库目录

    Returns:
        list: 知识文件路径列表
    """
    knowledge_files = []

    categories_dir = os.path.join(knowledge_base_dir, 'categories')

    if os.path.exists(categories_dir):
        for root, dirs, files in os.walk(categories_dir):
            for file in files:
                if file.endswith('.md'):
                    knowledge_files.append(os.path.join(root, file))

    return knowledge_files


def check_outdated_information(knowledge_files):
    """
    检查过时信息

    Args:
        knowledge_files (list): 知识文件路径列表
    """
    outdated_threshold = datetime.now() - timedelta(days=365)  # 1年

    for file_path in knowledge_files:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取更新时间
        updated_match = re.search(r'##\s+更新时间\s+(.*)', content)
        if updated_match:
            updated_str = updated_match.group(1).strip()
            try:
                updated_date = datetime.fromisoformat(updated_str)

                # 检查是否过时
                if updated_date < outdated_threshold:
                    # 标记为过时
                    mark_as_outdated(file_path, content)
            except ValueError:
                pass


def mark_as_outdated(file_path, content):
    """
    标记文件为过时

    Args:
        file_path (str): 文件路径
        content (str): 文件内容
    """
    # 检查是否已经标记为过时
    if "## 状态\n\n过时" not in content:
        # 添加过时标记
        updated_content = content.replace("## 更新时间", "## 状态\n\n过时\n\n## 更新时间")

        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)

        print(f"已标记为过时: {file_path}")


def merge_duplicate_knowledge(knowledge_files):
    """
    合并重复知识

    Args:
        knowledge_files (list): 知识文件路径列表
    """
    # 存储知识内容的哈希值
    content_hashes = {}
    duplicates = []

    for file_path in knowledge_files:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 计算内容哈希值（忽略时间戳）
        content_no_timestamps = re.sub(r'##\s+(创建时间|更新时间)\s+.*', '', content)
        content_hash = hash(content_no_timestamps)

        # 检查是否重复
        if content_hash in content_hashes:
            duplicates.append((file_path, content_hashes[content_hash]))
        else:
            content_hashes[content_hash] = file_path

    # 处理重复文件
    for duplicate_file, original_file in duplicates:
        print(f"发现重复文件: {duplicate_file} 与 {original_file}")
        # 可以选择删除重复文件或合并内容
        # 这里简单地删除重复文件
        os.remove(duplicate_file)
        print(f"已删除重复文件: {duplicate_file}")


def mark_needs_verification(knowledge_files):
    """
    标记需要验证的知识

    Args:
        knowledge_files (list): 知识文件路径列表
    """
    # 关键词列表，包含这些关键词的知识可能需要验证
    verification_keywords = [
        '可能', '大概', '也许', '估计', '不确定',
        '临时', '暂时', '有待确认', '需要验证'
    ]

    for file_path in knowledge_files:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查是否包含需要验证的关键词
        needs_verification = False
        for keyword in verification_keywords:
            if keyword in content:
                needs_verification = True
                break

        # 标记为需要验证
        if needs_verification and "## 状态\n\n需要验证" not in content:
            updated_content = content.replace("## 更新时间", "## 状态\n\n需要验证\n\n## 更新时间")

            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)

            print(f"已标记为需要验证: {file_path}")


def update_knowledge_base_index(knowledge_base_dir):
    """
    更新知识库索引

    Args:
        knowledge_base_dir (str): 知识库目录
    """
    index_path = os.path.join(knowledge_base_dir, 'index.md')
    categories_dir = os.path.join(knowledge_base_dir, 'categories')

    # 收集所有知识文件
    knowledge_items = []

    if os.path.exists(categories_dir):
        for root, dirs, files in os.walk(categories_dir):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)

                    # 读取文件内容
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 提取标题
                    title_match = re.search(r'#\s+(.*)', content)
                    title = title_match.group(1) if title_match else os.path.basename(file_path)

                    # 提取分类
                    categories_match = re.search(r'##\s+分类\s+(.*?)(?=##|$)', content, re.DOTALL)
                    categories = []
                    if categories_match:
                        categories_text = categories_match.group(1)
                        category_matches = re.findall(r'-\s+(.*)', categories_text)
                        categories = [category.strip() for category in category_matches]

                    # 提取创建时间
                    created_match = re.search(r'##\s+创建时间\s+(.*)', content)
                    created = created_match.group(1).strip() if created_match else ""

                    knowledge_items.append({
                        'title': title,
                        'file_path': file_path,
                        'categories': categories,
                        'created': created
                    })

    # 生成索引内容
    content = "# 知识库索引\n\n"
    content += f"最后更新: {datetime.now().isoformat()}\n\n"
    content += "## 知识条目\n\n"

    # 按分类组织知识条目
    categories = {}
    for item in knowledge_items:
        for category in item['categories']:
            if category not in categories:
                categories[category] = []
            categories[category].append(item)

    # 生成分类索引
    for category, items in sorted(categories.items()):
        content += f"### {category}\n\n"
        for item in items:
            # 生成相对路径
            relative_path = item['file_path'].replace(knowledge_base_dir + os.sep, '')
            content += f"- [{item['title']}]({relative_path}) - {item['created']}\n"
        content += "\n"

    # 写入索引文件
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"已更新知识库索引: {index_path}")


def update_recent_updates(knowledge_base_dir):
    """
    更新最近更新记录

    Args:
        knowledge_base_dir (str): 知识库目录
    """
    recent_updates_path = os.path.join(knowledge_base_dir, 'recent-updates.md')
    categories_dir = os.path.join(knowledge_base_dir, 'categories')

    # 收集所有知识文件
    knowledge_items = []

    if os.path.exists(categories_dir):
        for root, dirs, files in os.walk(categories_dir):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)

                    # 读取文件内容
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 提取标题
                    title_match = re.search(r'#\s+(.*)', content)
                    title = title_match.group(1) if title_match else os.path.basename(file_path)

                    # 提取更新时间
                    updated_match = re.search(r'##\s+更新时间\s+(.*)', content)
                    updated = updated_match.group(1).strip() if updated_match else ""

                    knowledge_items.append({
                        'title': title,
                        'file_path': file_path,
                        'updated': updated
                    })

    # 按更新时间排序
    def get_updated_date(item):
        try:
            return datetime.fromisoformat(item['updated'])
        except:
            return datetime.min

    sorted_items = sorted(knowledge_items, key=get_updated_date, reverse=True)

    # 生成最近更新内容
    content = "# 最近更新\n\n"
    content += f"最后更新: {datetime.now().isoformat()}\n\n"
    content += "## 最近更新的知识\n\n"

    for item in sorted_items[:10]:  # 只显示最近10条
        if item['updated']:
            # 生成相对路径
            relative_path = item['file_path'].replace(knowledge_base_dir + os.sep, '')
            content += f"- [{item['title']}]({relative_path}) - {item['updated']}\n"

    # 写入最近更新文件
    with open(recent_updates_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"已更新最近更新记录: {recent_updates_path}")


def update_knowledge_item(file_path, new_content):
    """
    更新单个知识条目

    Args:
        file_path (str): 文件路径
        new_content (str): 新内容
    """
    # 读取现有内容
    with open(file_path, 'r', encoding='utf-8') as f:
        existing_content = f.read()

    # 更新内容
    updated_content = new_content

    # 更新更新时间
    updated_content = re.sub(r'##\s+更新时间\s+.*', f'## 更新时间\n\n{datetime.now().isoformat()}', updated_content)

    # 写入文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)

    print(f"已更新知识条目: {file_path}")


if __name__ == '__main__':
    # 示例使用
    knowledge_base_dir = './knowledge'

    if os.path.exists(knowledge_base_dir):
        update_knowledge_base(knowledge_base_dir)
        print("知识库更新完成")
    else:
        print(f"知识库目录不存在: {knowledge_base_dir}")
        print("请先运行 knowledge_organizer.py 创建知识库")
