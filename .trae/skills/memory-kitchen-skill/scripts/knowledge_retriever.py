#!/usr/bin/env python3
"""
快速检索和提取知识库中的信息

此脚本用于根据用户需求，从知识库中检索相关信息，并以友好的方式呈现给用户。
"""

import os
import re
import json
from datetime import datetime

# 导入配置模块
from config import get_knowledge_base_dir, get_knowledge_base_dir_str


def retrieve_knowledge(query, knowledge_base_dir=None, max_results=5):
    """
    从知识库中检索相关信息

    Args:
        query (str): 查询关键词
        knowledge_base_dir (str): 知识库目录，默认为自动检测的配置目录
        max_results (int): 最大返回结果数

    Returns:
        list: 检索结果列表
    """
    # 如果没有指定知识库目录，使用默认路径
    if knowledge_base_dir is None:
        knowledge_base_dir = get_knowledge_base_dir_str()

    results = []

    # 遍历知识库目录
    categories_dir = os.path.join(knowledge_base_dir, 'categories')

    if os.path.exists(categories_dir):
        for root, dirs, files in os.walk(categories_dir):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)

                    # 读取文件内容
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 计算相关性得分
                    score = calculate_relevance(content, query)

                    if score > 0:
                        # 提取文件信息
                        file_info = extract_file_info(content, file_path, score)
                        results.append(file_info)

    # 按相关性得分排序
    results.sort(key=lambda x: x['score'], reverse=True)

    # 返回前 max_results 个结果
    return results[:max_results]


def calculate_relevance(content, query):
    """
    计算内容与查询的相关性得分

    Args:
        content (str): 文件内容
        query (str): 查询关键词

    Returns:
        float: 相关性得分
    """
    score = 0.0

    # 转换为小写进行匹配
    content_lower = content.lower()
    query_lower = query.lower()

    # 分割查询词
    query_terms = query_lower.split()

    # 计算完全匹配得分
    if query_lower in content_lower:
        score += 10.0

    # 计算部分匹配得分
    for term in query_terms:
        if term in content_lower:
            # 计算出现次数
            count = content_lower.count(term)
            score += count * 2.0

    # 计算标题匹配得分
    title_match = re.search(r'#\s+(.*)', content)
    if title_match:
        title = title_match.group(1).lower()
        if query_lower in title:
            score += 5.0
        for term in query_terms:
            if term in title:
                score += 3.0

    return score


def extract_file_info(content, file_path, score):
    """
    提取文件信息

    Args:
        content (str): 文件内容
        file_path (str): 文件路径
        score (float): 相关性得分

    Returns:
        dict: 文件信息
    """
    # 提取标题
    title_match = re.search(r'#\s+(.*)', content)
    title = title_match.group(1) if title_match else os.path.basename(file_path)

    # 提取答案部分
    answer_match = re.search(r'##\s+答案\s+(.*?)(?=##|$)', content, re.DOTALL)
    answer = answer_match.group(1).strip() if answer_match else ""

    # 提取标签
    tags_match = re.search(r'##\s+标签\s+(.*?)(?=##|$)', content, re.DOTALL)
    tags = []
    if tags_match:
        tags_text = tags_match.group(1)
        tag_matches = re.findall(r'-\s+(.*)', tags_text)
        tags = [tag.strip() for tag in tag_matches]

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

    # 提取更新时间
    updated_match = re.search(r'##\s+更新时间\s+(.*)', content)
    updated = updated_match.group(1).strip() if updated_match else ""

    return {
        'title': title,
        'answer': answer,
        'tags': tags,
        'categories': categories,
        'file_path': file_path,
        'score': score,
        'created': created,
        'updated': updated
    }


def format_retrieval_results(results):
    """
    格式化检索结果

    Args:
        results (list): 检索结果列表

    Returns:
        str: 格式化的结果
    """
    if not results:
        return "未找到相关知识"

    formatted_results = f"找到 {len(results)} 条相关知识：\n\n"

    for i, result in enumerate(results, 1):
        formatted_results += f"## 结果 {i}\n"
        formatted_results += f"**标题**: {result['title']}\n"
        formatted_results += f"**相关性**: {result['score']:.2f}\n"
        formatted_results += f"**答案**: {result['answer'][:200]}...\n"  # 只显示前200个字符

        if result['tags']:
            formatted_results += f"**标签**: {', '.join(result['tags'])}\n"

        if result['categories']:
            formatted_results += f"**分类**: {', '.join(result['categories'])}\n"

        formatted_results += f"**创建时间**: {result['created']}\n"
        formatted_results += f"**更新时间**: {result['updated']}\n"
        formatted_results += f"**文件路径**: {result['file_path']}\n\n"

    return formatted_results


def search_by_tags(tags, knowledge_base_dir=None, max_results=10):
    """
    根据标签搜索知识
    
    Args:
        tags (list): 标签列表
        knowledge_base_dir (str): 知识库目录，默认为自动检测的配置目录
        max_results (int): 最大返回结果数
    
    Returns:
        list: 检索结果列表
    """
    # 如果没有指定知识库目录，使用默认路径
    if knowledge_base_dir is None:
        knowledge_base_dir = get_knowledge_base_dir_str()
    
    results = []
    
    # 遍历知识库目录
    categories_dir = os.path.join(knowledge_base_dir, 'categories')

    if os.path.exists(categories_dir):
        for root, dirs, files in os.walk(categories_dir):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)

                    # 读取文件内容
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 提取标签
                    tags_match = re.search(r'##\s+标签\s+(.*?)(?=##|$)', content, re.DOTALL)
                    file_tags = []
                    if tags_match:
                        tags_text = tags_match.group(1)
                        tag_matches = re.findall(r'-\s+(.*)', tags_text)
                        file_tags = [tag.strip() for tag in tag_matches]

                    # 计算标签匹配数
                    match_count = sum(1 for tag in tags if tag in file_tags)

                    if match_count > 0:
                        # 提取文件信息
                        file_info = extract_file_info(content, file_path, match_count)
                        results.append(file_info)

    # 按匹配标签数排序
    results.sort(key=lambda x: x['score'], reverse=True)

    # 返回前 max_results 个结果
    return results[:max_results]


def search_by_category(category, knowledge_base_dir=None, max_results=10):
    """
    根据分类搜索知识
    
    Args:
        category (str): 分类
        knowledge_base_dir (str): 知识库目录，默认为自动检测的配置目录
        max_results (int): 最大返回结果数
    
    Returns:
        list: 检索结果列表
    """
    # 如果没有指定知识库目录，使用默认路径
    if knowledge_base_dir is None:
        knowledge_base_dir = get_knowledge_base_dir_str()
    
    results = []
    
    # 遍历知识库目录
    categories_dir = os.path.join(knowledge_base_dir, 'categories')

    if os.path.exists(categories_dir):
        for root, dirs, files in os.walk(categories_dir):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)

                    # 读取文件内容
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 提取分类
                    categories_match = re.search(r'##\s+分类\s+(.*?)(?=##|$)', content, re.DOTALL)
                    file_categories = []
                    if categories_match:
                        categories_text = categories_match.group(1)
                        category_matches = re.findall(r'-\s+(.*)', categories_text)
                        file_categories = [category.strip() for category in category_matches]

                    # 检查分类是否匹配
                    if category in file_categories:
                        # 提取文件信息
                        file_info = extract_file_info(content, file_path, 1.0)
                        results.append(file_info)

    # 返回前 max_results 个结果
    return results[:max_results]


if __name__ == '__main__':
    # 示例使用
    knowledge_base_dir = './knowledge/categories'

    # 示例1: 关键词搜索
    print("示例1: 关键词搜索 'Python 内存泄漏'")
    results = retrieve_knowledge('Python 内存泄漏', knowledge_base_dir)
    print(format_retrieval_results(results))

    # 示例2: 标签搜索
    print("\n示例2: 标签搜索 ['Docker']")
    tag_results = search_by_tags(['Docker'], knowledge_base_dir)
    print(format_retrieval_results(tag_results))

    # 示例3: 分类搜索
    print("\n示例3: 分类搜索 '技术知识 > 云原生'")
    category_results = search_by_category('技术知识 > 云原生', knowledge_base_dir)
    print(format_retrieval_results(category_results))
