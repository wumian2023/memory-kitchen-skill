#!/usr/bin/env python3
"""
智能整理和分类知识

此脚本用于对收集到的知识进行分析、分类和结构化处理，为知识库提供组织良好的内容。
"""

import os
import json
import markdown
from datetime import datetime

# 导入配置模块
from config import get_knowledge_base_dir, get_knowledge_base_dir_str, ensure_knowledge_base_exists


def organize_knowledge(knowledge_items, output_dir=None):
    """
    整理和分类知识

    Args:
        knowledge_items (list): 知识条目列表
        output_dir (str): 输出目录，默认为知识库目录
    """
    # 如果没有指定输出目录，使用默认的知识库目录
    if output_dir is None:
        output_dir = get_knowledge_base_dir_str()

    # 确保知识库目录存在
    ensure_knowledge_base_exists()

    # 创建知识库目录结构
    create_knowledge_base_structure(output_dir)

    # 处理每个知识条目
    for item in knowledge_items:
        # 生成知识文件
        generate_knowledge_file(item, output_dir)

    # 更新知识库索引
    update_knowledge_base_index(knowledge_items, output_dir)

    # 更新最近更新记录
    update_recent_updates(knowledge_items, output_dir)


def create_knowledge_base_structure(output_dir):
    """
    创建知识库目录结构

    Args:
        output_dir (str): 输出目录
    """
    # 主知识库目录
    knowledge_dir = os.path.join(output_dir, 'knowledge')
    os.makedirs(knowledge_dir, exist_ok=True)

    # 分类目录
    categories_dir = os.path.join(knowledge_dir, 'categories')
    os.makedirs(categories_dir, exist_ok=True)

    # 技术知识目录
    tech_dir = os.path.join(categories_dir, 'technical')
    os.makedirs(tech_dir, exist_ok=True)
    os.makedirs(os.path.join(tech_dir, 'frontend'), exist_ok=True)
    os.makedirs(os.path.join(tech_dir, 'backend'), exist_ok=True)
    os.makedirs(os.path.join(tech_dir, 'cloud'), exist_ok=True)
    os.makedirs(os.path.join(tech_dir, 'database'), exist_ok=True)
    os.makedirs(os.path.join(tech_dir, 'version-control'), exist_ok=True)

    # 项目知识目录
    project_dir = os.path.join(categories_dir, 'project')
    os.makedirs(project_dir, exist_ok=True)

    # 问题解决方案目录
    problem_dir = os.path.join(categories_dir, 'problem-solving')
    os.makedirs(problem_dir, exist_ok=True)
    os.makedirs(os.path.join(problem_dir, 'tutorials'), exist_ok=True)
    os.makedirs(os.path.join(problem_dir, 'troubleshooting'), exist_ok=True)

    # 最佳实践目录
    best_practices_dir = os.path.join(categories_dir, 'best-practices')
    os.makedirs(best_practices_dir, exist_ok=True)

    # 标签目录
    tags_dir = os.path.join(knowledge_dir, 'tags')
    os.makedirs(tags_dir, exist_ok=True)


def generate_knowledge_file(knowledge_item, output_dir):
    """
    生成知识文件

    Args:
        knowledge_item (dict): 知识条目
        output_dir (str): 输出目录
    """
    # 确定文件路径
    file_path = determine_file_path(knowledge_item, output_dir)

    # 生成 Markdown 内容
    content = generate_markdown_content(knowledge_item)

    # 确保目录存在
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # 写入文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"已生成知识文件: {file_path}")


def determine_file_path(knowledge_item, output_dir):
    """
    确定知识文件的路径

    Args:
        knowledge_item (dict): 知识条目
        output_dir (str): 输出目录

    Returns:
        str: 文件路径
    """
    # 优先使用分类信息
    categories = knowledge_item.get('categories', ['其他'])

    # 选择第一个分类作为目录路径
    primary_category = categories[0]

    # 转换分类为目录路径
    category_path = primary_category.replace(' > ', os.sep)

    # 生成文件名
    # 使用问题的前几个词作为文件名
    question = knowledge_item['question']
    file_name = question[:50].replace(' ', '_').replace('?', '').replace('/', '_') + '.md'

    # 完整路径
    return os.path.join(output_dir, 'knowledge', 'categories', category_path, file_name)


def generate_markdown_content(knowledge_item):
    """
    生成 Markdown 内容

    Args:
        knowledge_item (dict): 知识条目

    Returns:
        str: Markdown 内容
    """
    # 生成 YAML frontmatter
    frontmatter = {
        'id': knowledge_item['id'],
        'title': knowledge_item['question'],
        'tags': knowledge_item['tags'],
        'categories': knowledge_item['categories'],
        'created': knowledge_item['timestamp'],
        'updated': datetime.now().isoformat()
    }

    # 构建 frontmatter 字符串
    frontmatter_str = '---\n'
    for key, value in frontmatter.items():
        if isinstance(value, list):
            frontmatter_str += f'{key}: {value}\n'
        else:
            frontmatter_str += f'{key}: {value}\n'
    frontmatter_str += '---\n\n'

    # 构建正文
    content = f"# {knowledge_item['question']}\n\n"
    content += f"## 答案\n\n{knowledge_item['answer']}\n\n"

    if knowledge_item['tags']:
        content += "## 标签\n\n"
        for tag in knowledge_item['tags']:
            content += f"- {tag}\n"
        content += "\n"

    if knowledge_item['categories']:
        content += "## 分类\n\n"
        for category in knowledge_item['categories']:
            content += f"- {category}\n"
        content += "\n"

    content += f"## 创建时间\n\n{knowledge_item['timestamp']}\n"
    content += f"## 更新时间\n\n{datetime.now().isoformat()}\n"

    return frontmatter_str + content


def update_knowledge_base_index(knowledge_items, output_dir):
    """
    更新知识库索引

    Args:
        knowledge_items (list): 知识条目列表
        output_dir (str): 输出目录
    """
    index_path = os.path.join(output_dir, 'knowledge', 'index.md')

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
            relative_path = determine_file_path(item, output_dir)
            relative_path = relative_path.replace(output_dir + os.sep, '')
            content += f"- [{item['question']}]({relative_path})\n"
        content += "\n"

    # 写入索引文件
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"已更新知识库索引: {index_path}")


def update_recent_updates(knowledge_items, output_dir):
    """
    更新最近更新记录

    Args:
        knowledge_items (list): 知识条目列表
        output_dir (str): 输出目录
    """
    recent_updates_path = os.path.join(output_dir, 'knowledge', 'recent-updates.md')

    # 按时间排序知识条目
    sorted_items = sorted(knowledge_items, key=lambda x: x['timestamp'], reverse=True)

    # 生成最近更新内容
    content = "# 最近更新\n\n"
    content += f"最后更新: {datetime.now().isoformat()}\n\n"
    content += "## 最近添加的知识\n\n"

    for item in sorted_items[:10]:  # 只显示最近10条
        # 生成相对路径
        relative_path = determine_file_path(item, output_dir)
        relative_path = relative_path.replace(output_dir + os.sep, '')
        content += f"- [{item['question']}]({relative_path}) - {item['timestamp']}\n"

    # 写入最近更新文件
    with open(recent_updates_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"已更新最近更新记录: {recent_updates_path}")


def load_collected_knowledge(input_file=None):
    """
    加载收集到的知识

    Args:
        input_file (str): 输入文件路径，默认为知识库目录下的最新收集文件

    Returns:
        list: 知识条目列表
    """
    # 如果没有指定输入文件，尝试在知识库目录中查找最新的收集文件
    if input_file is None:
        knowledge_base_dir = get_knowledge_base_dir_str()
        collected_files = []

        if os.path.exists(knowledge_base_dir):
            for file in os.listdir(knowledge_base_dir):
                if file.startswith('collected_knowledge_') and file.endswith('.json'):
                    file_path = os.path.join(knowledge_base_dir, file)
                    collected_files.append((file_path, os.path.getmtime(file_path)))

        if collected_files:
            # 按修改时间排序，获取最新的文件
            collected_files.sort(key=lambda x: x[1], reverse=True)
            input_file = collected_files[0][0]
        else:
            print("未找到收集的知识文件")
            return []

    with open(input_file, 'r', encoding='utf-8') as f:
        return json.load(f)


if __name__ == '__main__':
    # 示例使用
    input_file = './collected/collected_knowledge_20260304_113456.json'  # 替换为实际文件路径
    output_dir = '.'

    if os.path.exists(input_file):
        # 加载收集到的知识
        knowledge_items = load_collected_knowledge(input_file)

        # 整理知识
        organize_knowledge(knowledge_items, output_dir)

        print(f"已成功整理 {len(knowledge_items)} 条知识")
    else:
        print(f"输入文件不存在: {input_file}")
        # 使用示例数据
        sample_data = [
            {
                "id": "1",
                "question": "如何解决 Python 中的内存泄漏问题？",
                "answer": "Python 中的内存泄漏问题通常可以通过以下方法解决：1. 使用 gc 模块手动触发垃圾回收 2. 避免循环引用，特别是在类的 __del__ 方法中 3. 使用 weakref 模块来创建弱引用 4. 使用内存分析工具如 memory_profiler 来检测内存泄漏 5. 注意关闭文件句柄和网络连接",
                "timestamp": "2026-03-04T11:34:56",
                "tags": ["Python", "解决方案"],
                "categories": ["技术知识 > 后端", "问题解决方案 > 故障排除"]
            },
            {
                "id": "2",
                "question": "什么是 Docker 容器编排？",
                "answer": "Docker 容器编排是指管理多个 Docker 容器的生命周期，包括：1. 容器的部署和扩展 2. 负载均衡 3. 服务发现 4. 健康检查 5. 滚动更新。最流行的容器编排工具包括 Kubernetes、Docker Swarm 和 Mesos。",
                "timestamp": "2026-03-04T11:35:00",
                "tags": ["Docker", "概念"],
                "categories": ["技术知识 > 云原生", "基础知识 > 概念"]
            }
        ]
        organize_knowledge(sample_data, output_dir)
        print("已使用示例数据成功整理知识")
