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


def collect_knowledge(input_data):
    """
    从对话历史和上下文中收集有价值的信息

    Args:
        input_data (str or dict): 输入数据，可以是对话历史文本或包含上下文的字典

    Returns:
        list: 收集到的知识条目列表
    """
    knowledge_items = []

    # 处理不同类型的输入
    if isinstance(input_data, dict):
        # 从字典中提取对话历史和上下文
        dialogue_history = ""

        # 提取消息历史
        if 'messages' in input_data:
            for message in input_data['messages']:
                role = message.get('role', 'unknown')
                content = message.get('content', '')
                dialogue_history += f"[{role}]: {content}\n\n"

        # 提取系统提示和其他上下文
        if 'system' in input_data:
            dialogue_history += f"[系统]: {input_data['system']}\n\n"

        if 'context' in input_data:
            dialogue_history += f"[上下文]: {input_data['context']}\n\n"
    else:
        # 直接使用字符串作为对话历史
        dialogue_history = str(input_data)

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
    从对话历史和上下文中提取问题和答案对

    Args:
        dialogue_history (str): 对话历史文本

    Returns:
        list: 问题和答案对的列表
    """
    # 支持多种对话格式
    # 格式1: [用户]: ... [助手]: ...
    # 格式2: 用户: ... 助手: ...
    # 格式3: [User]: ... [Assistant]: ...
    # 格式4: User: ... Assistant: ...
    # 格式5: [系统]: ... 或 [上下文]: ...

    lines = dialogue_history.strip().split('\n')
    pairs = []

    question = None
    answer = []

    # 定义用户和助手的识别模式
    user_patterns = [
        r'^\[用户\]:',
        r'^\[User\]:',
        r'^用户:',
        r'^User:',
        r'^\[user\]:',
        r'^user:'
    ]

    assistant_patterns = [
        r'^\[助手\]:',
        r'^\[Assistant\]:',
        r'^助手:',
        r'^Assistant:',
        r'^\[assistant\]:',
        r'^assistant:'
    ]

    # 定义系统和上下文的识别模式
    context_patterns = [
        r'^\[系统\]:',
        r'^\[上下文\]:',
        r'^系统:',
        r'^上下文:'
    ]

    def is_user_line(line):
        for pattern in user_patterns:
            if re.match(pattern, line):
                return True
        return False

    def is_assistant_line(line):
        for pattern in assistant_patterns:
            if re.match(pattern, line):
                return True
        return False

    def is_context_line(line):
        for pattern in context_patterns:
            if re.match(pattern, line):
                return True
        return False

    def extract_content(line):
        # 提取冒号后面的内容
        if ':' in line:
            return line.split(':', 1)[1].strip()
        return line.strip()

    # 处理对话和上下文
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 检查是否是用户问题
        if is_user_line(line):
            # 保存之前的问题和答案对
            if question and answer:
                pairs.append((question, ' '.join(answer)))
                answer = []
            # 提取新问题
            question = extract_content(line)

        # 检查是否是助手回答
        elif is_assistant_line(line):
            if question:
                answer.append(extract_content(line))

        # 检查是否是上下文信息
        elif is_context_line(line):
            # 从上下文中提取知识
            context_content = extract_content(line)
            if context_content:
                # 尝试从上下文中识别问题-答案对
                context_pairs = extract_knowledge_from_context(context_content)
                pairs.extend(context_pairs)

        # 处理多行回答
        elif question and not is_user_line(line):
            # 如果是回答的延续行
            if answer or (question and not any(is_user_line(l) for l in lines[lines.index(line)+1:lines.index(line)+5] if l.strip())):
                answer.append(line)

    # 处理最后一对
    if question and answer:
        pairs.append((question, ' '.join(answer)))

    return pairs


def extract_knowledge_from_context(context_content):
    """
    从上下文中提取知识

    Args:
        context_content (str): 上下文内容

    Returns:
        list: 问题和答案对的列表
    """
    pairs = []

    # 简单的上下文知识提取逻辑
    # 1. 识别包含 "如何"、"什么是"、"为什么" 等关键词的句子作为问题
    # 2. 识别后续的解释作为答案

    sentences = re.split(r'[。！？]', context_content)
    i = 0
    while i < len(sentences):
        sentence = sentences[i].strip()
        if not sentence:
            i += 1
            continue

        # 识别问题句子
        if re.search(r'(如何|什么是|为什么|如何解决|如何使用|怎么|怎样)', sentence):
            question = sentence
            answer = []

            # 收集后续句子作为答案
            j = i + 1
            while j < len(sentences) and not re.search(r'(如何|什么是|为什么|如何解决|如何使用|怎么|怎样)', sentences[j]):
                answer_sentence = sentences[j].strip()
                if answer_sentence:
                    answer.append(answer_sentence)
                j += 1

            if answer:
                pairs.append((question, ' '.join(answer)))
                i = j
            else:
                i += 1
        else:
            i += 1

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
        'Git', 'GitHub', 'GitLab', 'CI/CD', 'DevOps',
        'HTML', 'CSS', 'JavaScript', '知识库', '日期', '时间'
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
        r'调试': '调试',
        r'需要': '需求',
        r'修改': '修改',
        r'优化': '优化'
    }

    # 提取技术标签
    for keyword in tech_keywords:
        if keyword.lower() in (question + ' ' + answer).lower():
            tags.append(keyword)

    # 提取问题类型标签
    for pattern, tag in question_types.items():
        if re.search(pattern, question):
            tags.append(tag)

    # 如果没有提取到标签，添加默认标签
    if not tags:
        tags.append('其他')

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

    # 自动调用知识组织脚本，生成HTML文件
    try:
        # 导入知识组织模块
        from knowledge_organizer import organize_knowledge
        print(f"正在自动组织知识库...")
        organize_knowledge(knowledge_items, output_dir)
        print(f"知识库组织完成！")
    except Exception as e:
        print(f"警告: 自动组织知识库时出错: {e}")
        import traceback
        traceback.print_exc()


def collect_knowledge_advanced(input_data, output_dir=None):
    """
    使用高级知识收集器收集知识（推荐）

    此函数使用新的KnowledgeCollector类，支持：
    - 隐含知识挖掘（技术栈、问题-解决方案、决策记录）
    - 代码块识别
    - 实体识别增强
    - 更智能的价值判断

    Args:
        input_data (str or dict): 输入数据，可以是对话历史文本或包含上下文的字典
        output_dir (str): 输出目录，默认为知识库目录

    Returns:
        list: 收集到的知识条目列表
    """
    try:
        # 尝试导入新的收集器
        from knowledge_collector_v2 import KnowledgeCollector

        collector = KnowledgeCollector()
        knowledge_items = collector.collect(input_data)

        if output_dir is None:
            output_dir = get_knowledge_base_dir()

        collector.save(output_dir)

        return knowledge_items
    except ImportError as e:
        print(f"⚠️ 高级收集器不可用，回退到基础收集器: {e}")
        # 回退到基础收集器
        knowledge_items = collect_knowledge(input_data)
        save_collected_knowledge(knowledge_items, output_dir)
        return knowledge_items
    except Exception as e:
        print(f"⚠️ 高级收集器出错: {e}")
        import traceback
        traceback.print_exc()
        # 回退到基础收集器
        knowledge_items = collect_knowledge(input_data)
        save_collected_knowledge(knowledge_items, output_dir)
        return knowledge_items


if __name__ == '__main__':
    # 示例对话历史（包含隐含信息）
    sample_data = {
        "messages": [
            {"role": "user", "content": "你好，我最近在使用 Python 开发一个微服务。"},
            {"role": "assistant", "content": "太好了，Python 非常适合微服务。你打算使用什么框架？"},
            {"role": "user", "content": "我决定采用 FastAPI，因为性能更好。但是遇到了一个 CORS 报错的问题。"},
            {"role": "assistant", "content": "CORS 问题很常见。你需要在 FastAPI 中添加 CORSMiddleware。"},
            {"role": "user", "content": "解决了！我是这样配置的：\n```python\nfrom fastapi.middleware.cors import CORSMiddleware\napp.add_middleware(CORSMiddleware)\n```"},
            {"role": "user", "content": "另外，我们计划把数据库从 MySQL 迁移到 PostgreSQL，并使用 Docker 部署。"},
            {"role": "assistant", "content": "这是一个很好的架构决策。PostgreSQL 对 JSON 支持更好。"}
        ],
        "context": "项目背景：电商后台管理系统。技术栈要求：高并发，低延迟。"
    }

    # 使用高级收集器收集知识（推荐）
    print("=" * 50)
    print("使用高级知识收集器")
    print("=" * 50)
    knowledge = collect_knowledge_advanced(sample_data)

    # 打印结果
    print(f"\n收集到 {len(knowledge)} 条知识：")
    for item in knowledge:
        print(f"\n[{item.get('source_type', 'QA')}] {item['question'][:50]}...")
        print(f"  标签：{', '.join(item.get('tags', [])[:5])}")
        print(f"  分类：{', '.join(item.get('categories', []))}")
        print(f"  置信度：{item.get('confidence', 'N/A')}")
