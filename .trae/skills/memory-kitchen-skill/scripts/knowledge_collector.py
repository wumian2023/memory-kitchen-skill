#!/usr/bin/env python3
"""
自动收集对话中的重要信息

此脚本用于分析对话内容，识别和提取有价值的信息，为知识库提供原始数据。
"""

import re
import json
import os
from datetime import datetime

# 导入配置模块
from config import get_knowledge_base_dir, get_knowledge_base_dir_str


def collect_knowledge(dialogue_history):
    """
    从对话历史中收集有价值的信息

    Args:
        dialogue_history (str): 对话历史文本

    Returns:
        list: 收集到的知识条目列表
    """
    knowledge_items = []

    # 提取问题和答案对
    question_answer_pairs = extract_question_answer_pairs(dialogue_history)

    for q, a in question_answer_pairs:
        # 分析内容，判断是否有价值
        if is_valuable_information(q, a):
            knowledge_item = {
                "id": generate_id(),
                "question": q,
                "answer": a,
                "timestamp": datetime.now().isoformat(),
                "tags": extract_tags(q, a),
                "categories": determine_categories(q, a)
            }
            knowledge_items.append(knowledge_item)

    return knowledge_items


def extract_question_answer_pairs(dialogue_history):
    """
    从对话历史中提取问题和答案对

    Args:
        dialogue_history (str): 对话历史文本

    Returns:
        list: 问题和答案对的列表
    """
    # 简单的对话模式匹配
    # 实际应用中可能需要更复杂的NLP处理
    lines = dialogue_history.strip().split('\n')
    pairs = []

    question = None
    answer = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 假设以 "用户:" 开头的是问题
        if line.startswith('用户:'):
            if question and answer:
                pairs.append((question, ' '.join(answer)))
                answer = []
            question = line[3:].strip()
        # 假设以 "助手:" 开头的是答案
        elif line.startswith('助手:'):
            if question:
                answer.append(line[3:].strip())

    # 处理最后一对
    if question and answer:
        pairs.append((question, ' '.join(answer)))

    return pairs


def is_valuable_information(question, answer):
    """
    判断信息是否有价值

    Args:
        question (str): 问题
        answer (str): 答案

    Returns:
        bool: 是否有价值
    """
    # 简单的价值判断逻辑
    # 实际应用中可能需要更复杂的分析
    if not question or not answer:
        return False

    # 过滤掉简单的寒暄
    trivial_patterns = [
        r'你好', r'您好', r'早上好', r'下午好', r'晚上好',
        r'再见', r'拜拜', r'谢谢', r'不客气'
    ]

    for pattern in trivial_patterns:
        if re.search(pattern, question) or re.search(pattern, answer):
            return False

    # 过滤掉太短的内容
    if len(question) < 5 or len(answer) < 10:
        return False

    return True


def extract_tags(question, answer):
    """
    从问题和答案中提取标签

    Args:
        question (str): 问题
        answer (str): 答案

    Returns:
        list: 标签列表
    """
    tags = []

    # 技术相关标签
    tech_keywords = [
        'Python', 'Java', 'JavaScript', 'React', 'Vue', 'Angular',
        'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP',
        'SQL', 'NoSQL', 'MongoDB', 'PostgreSQL', 'MySQL',
        'Git', 'GitHub', 'GitLab', 'CI/CD', 'DevOps'
    ]

    # 问题类型标签
    question_types = {
        r'如何': '教程',
        r'什么是': '概念',
        r'为什么': '原理',
        r'最佳实践': '最佳实践',
        r'解决方案': '解决方案',
        r'问题': '问题',
        r'错误': '错误',
        r'调试': '调试'
    }

    # 提取技术标签
    for keyword in tech_keywords:
        if keyword.lower() in (question + ' ' + answer).lower():
            tags.append(keyword)

    # 提取问题类型标签
    for pattern, tag in question_types.items():
        if re.search(pattern, question):
            tags.append(tag)

    return list(set(tags))  # 去重


def determine_categories(question, answer):
    """
    确定知识条目的分类

    Args:
        question (str): 问题
        answer (str): 答案

    Returns:
        list: 分类列表
    """
    categories = []

    # 技术分类
    tech_categories = {
        r'Python|Java|JavaScript|React|Vue|Angular': '技术知识 > 前端开发',
        r'Docker|Kubernetes|AWS|Azure|GCP|CI/CD|DevOps': '技术知识 > 云原生',
        r'SQL|NoSQL|MongoDB|PostgreSQL|MySQL': '技术知识 > 数据库',
        r'Git|GitHub|GitLab': '技术知识 > 版本控制'
    }

    # 问题类型分类
    type_categories = {
        r'如何': '问题解决方案 > 教程',
        r'什么是': '基础知识 > 概念',
        r'为什么': '基础知识 > 原理',
        r'最佳实践': '最佳实践',
        r'问题|错误|调试': '问题解决方案 > 故障排除'
    }

    # 确定技术分类
    for pattern, category in tech_categories.items():
        if re.search(pattern, question + ' ' + answer):
            categories.append(category)

    # 确定问题类型分类
    for pattern, category in type_categories.items():
        if re.search(pattern, question):
            categories.append(category)

    # 默认分类
    if not categories:
        categories.append('其他')

    return categories


def generate_id():
    """
    生成唯一ID

    Returns:
        str: 唯一ID
    """
    import uuid
    return str(uuid.uuid4())


def save_collected_knowledge(knowledge_items, output_dir=None):
    """
    保存收集到的知识

    Args:
        knowledge_items (list): 知识条目列表
        output_dir (str): 输出目录，默认为知识库目录
    """
    # 如果没有指定输出目录，使用默认的知识库目录
    if output_dir is None:
        output_dir = get_knowledge_base_dir()

    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(output_dir, f'collected_knowledge_{timestamp}.json')

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(knowledge_items, f, ensure_ascii=False, indent=2)

    print(f"已保存 {len(knowledge_items)} 条知识到 {output_file}")


if __name__ == '__main__':
    # 示例对话历史
    sample_dialogue = """
    用户: 如何解决 Python 中的内存泄漏问题？
    助手: Python 中的内存泄漏问题通常可以通过以下方法解决：
    1. 使用 gc 模块手动触发垃圾回收
    2. 避免循环引用，特别是在类的 __del__ 方法中
    3. 使用 weakref 模块来创建弱引用
    4. 使用内存分析工具如 memory_profiler 来检测内存泄漏
    5. 注意关闭文件句柄和网络连接

    用户: 什么是 Docker 容器编排？
    助手: Docker 容器编排是指管理多个 Docker 容器的生命周期，包括：
    1. 容器的部署和扩展
    2. 负载均衡
    3. 服务发现
    4. 健康检查
    5. 滚动更新

    最流行的容器编排工具包括 Kubernetes、Docker Swarm 和 Mesos。
    """

    # 收集知识
    knowledge = collect_knowledge(sample_dialogue)

    # 保存知识
    save_collected_knowledge(knowledge, './collected')

    # 打印结果
    print(f"收集到 {len(knowledge)} 条知识：")
    for item in knowledge:
        print(f"\nID: {item['id']}")
        print(f"问题: {item['question']}")
        print(f"答案: {item['answer']}")
        print(f"标签: {item['tags']}")
        print(f"分类: {item['categories']}")
