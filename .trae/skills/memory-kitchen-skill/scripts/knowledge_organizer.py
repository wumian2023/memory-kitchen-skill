#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库组织器模块

该模块负责将收集到的知识进行组织、分类和格式化，
生成主题聚合文件和索引文件。
"""

import os
import json
import re
import glob
from datetime import datetime


def calculate_css_relative_path(file_depth):
    """
    根据文件深度计算 CSS 相对路径

    Args:
        file_depth (int): 文件相对于 knowledge 目录的层级数

    Returns:
        str: CSS 相对路径
    """
    if file_depth <= 0:
        return "static/styles.css"
    return "../" * file_depth + "static/styles.css"


def calculate_js_relative_path(file_depth):
    """
    根据文件深度计算 JS 相对路径

    Args:
        file_depth (int): 文件相对于 knowledge 目录的层级数

    Returns:
        str: JS 相对路径
    """
    if file_depth <= 0:
        return "static/scripts.js"
    return "../" * file_depth + "static/scripts.js"


def get_file_depth(file_path, output_dir):
    """
    计算文件相对于 knowledge 目录的深度

    Args:
        file_path (str): 文件路径
        output_dir (str): 输出目录

    Returns:
        int: 文件深度
    """
    output_dir_str = str(output_dir)
    knowledge_dir = os.path.join(output_dir_str, 'knowledge')
    relative_path = file_path.replace(knowledge_dir, '')
    depth = relative_path.count(os.sep) - 1
    return max(0, depth)


def format_datetime(dt=None):
    """
    格式化日期时间显示

    Args:
        dt (datetime, optional): 日期时间对象，默认当前时间

    Returns:
        str: 格式化后的日期时间字符串
    """
    if dt is None:
        dt = datetime.now()
    elif isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except ValueError:
            return dt
    return dt.strftime("%Y年%m月%d日 %H:%M")


def group_items_by_topic(knowledge_items):
    """
    按主题分组知识条目

    Args:
        knowledge_items (list): 知识条目列表

    Returns:
        dict: 按主题分组的知识条目
    """
    grouped = {}

    for item in knowledge_items:
        # 提取主题
        tags = item.get('tags', [])
        if tags:
            # 优先使用技术相关的标签作为主题
            tech_tags = [tag for tag in tags if tag in ['Git', 'Python', 'React', 'Docker', 'JavaScript', 'Linux', 'Windows', 'MySQL', 'PostgreSQL', 'MongoDB', 'AWS', 'Azure', 'Docker', 'Kubernetes']]
            topic = tech_tags[0] if tech_tags else tags[0]
        else:
            topic = '其他'

        if topic not in grouped:
            grouped[topic] = []
        grouped[topic].append(item)

    return grouped


def group_items_by_category(knowledge_items):
    """
    按分类分组知识条目（统一分组逻辑）

    Args:
        knowledge_items (list): 知识条目列表

    Returns:
        dict: 按分类分组的知识条目
    """
    grouped = {}

    for item in knowledge_items:
        categories = item.get('categories', [])
        if categories:
            primary_category = categories[0]
        else:
            primary_category = '其他'

        if primary_category not in grouped:
            grouped[primary_category] = []
        grouped[primary_category].append(item)

    return grouped


def sanitize_filename(filename):
    """
    清理文件名，移除不合法的字符和空格

    Args:
        filename (str): 原始文件名

    Returns:
        str: 清理后的文件名
    """
    invalid_chars = '<>:"/\\|?* '
    for char in invalid_chars:
        filename = filename.replace(char, '')
    return filename


def determine_topic_file_path(topic, items, output_dir):
    """
    确定主题文件的路径 - 统一按分类组织

    Args:
        topic (str): 主题名称
        items (list): 知识条目列表
        output_dir (str): 输出目录

    Returns:
        str: 主题文件的路径
    """
    output_dir_str = str(output_dir)

    category_path = []
    original_category = ''
    if items:
        categories = items[0].get('categories', [])
        if categories:
            original_category = categories[0]
            # 对于多级分类，创建嵌套目录结构
            # 确保正确分割分类路径，处理空格不一致的情况
            if ' > ' in original_category:
                # 多级分类：技术知识 > 版本控制 -> 技术知识/版本控制
                category_parts = original_category.split(' > ')
                category_path = category_parts
            else:
                # 单级分类：其他 -> 其他
                category_path = [original_category]

    if not category_path:
        category_path = ['其他']

    # 清理分类路径中的非法字符
    category_path = [sanitize_filename(part) for part in category_path]
    topic = sanitize_filename(topic)

    # 生成一致的文件名格式，与Git相关.html保持一致
    if ' > ' in original_category:
        # 对于多级分类，使用最后一级作为文件名
        last_category = original_category.split(' > ')[-1]
        last_category = sanitize_filename(last_category)
        file_name = f"{last_category}相关.html"
    else:
        file_name = f"{topic}相关.html"

    # 移除文件名中可能的重复空格
    file_name = file_name.replace('  ', ' ').strip()

    # 确保目录存在
    full_dir = os.path.join(output_dir_str, 'knowledge', 'categories', *category_path)
    os.makedirs(full_dir, exist_ok=True)

    return os.path.join(full_dir, file_name)


def generate_topic_html_content(topic, knowledge_items, file_depth=0):
    """
    生成主题 HTML 内容

    Args:
        topic (str): 主题名称
        knowledge_items (list): 知识条目列表
        file_depth (int): 文件相对于 knowledge 目录的层级数

    Returns:
        str: HTML 内容
    """
    css_path = calculate_css_relative_path(file_depth)
    js_path = calculate_js_relative_path(file_depth)

    index_path = "../" * file_depth + "index.html" if file_depth > 0 else "index.html"
    recent_path = "../" * file_depth + "recent-updates.html" if file_depth > 0 else "recent-updates.html"

    html = f'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{topic}相关知识</title>
    <link rel="stylesheet" href="{css_path}?v=2">
</head>
<body>
    <div class="container">
        <!-- 左侧边栏 -->
        <div class="sidebar">
            <!-- 导航链接 -->
            <nav class="toc-nav">
                <ul>
                    <li><a href="{index_path}">返回索引</a></li>
                    <li><a href="{recent_path}">最近更新</a></li>
                </ul>
            </nav>

            <!-- 目录 -->
            <div class="toc">
                <h2>目录</h2>
                <ul>

'''

    # 生成目录项
    for idx, item in enumerate(knowledge_items, 1):
        # 生成锚点链接
        anchor = f"item-{idx}"
        html += f"                    <li><a href=\"#{anchor}\">{idx}. {item['question']}</a></li>\n"
    html += f"                </ul>\n"
    html += f"            </div>\n"
    html += f"        </div>\n\n"

    # 主要内容
    html += f"        <!-- 主要内容 -->\n"
    html += f"        <div class=\"main-content\">\n"

    html += f"            <div class=\"header\">\n"
    html += f"            <h1>{topic}相关知识</h1>\n"
    html += f"            <p>最后更新: {format_datetime()}</p>\n"
    html += f"            <p>本文件包含与 {topic} 相关的知识条目</p>\n"
    html += f"        </div>\n\n"

    # 为每个知识条目生成内容
    for idx, item in enumerate(knowledge_items, 1):
        # 生成锚点
        anchor = f"item-{idx}"
        item_id = item.get('id', '')
        html += f"        <div class=\"knowledge-item\" id=\"{anchor}\" data-id=\"{item_id}\">\n"
        html += f"            <div class=\"item-header\">\n"
        html += f"                <h2>{idx}. {item['question']}</h2>\n"
        # 添加删除按钮
        html += f"                <button class=\"delete-btn\" onclick=\"deleteKnowledge('{item_id}', this)\" title=\"删除此知识\">\n"
        html += f"                    <svg width=\"16\" height=\"16\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\">\n"
        html += f"                        <polyline points=\"3 6 5 6 21 6\"></polyline>\n"
        html += f"                        <path d=\"M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2\"></path>\n"
        html += f"                    </svg>\n"
        html += f"                </button>\n"
        html += f"            </div>\n"

        # 添加创建时间
        if item.get('timestamp'):
            formatted_time = format_datetime(item['timestamp'])
            html += f"            <p class=\"item-time\">创建时间: {formatted_time}</p>\n"

        # 处理答案内容，将 Markdown 转换为 HTML
        answer = item['answer']
        # 转换代码块
        answer = re.sub(r'```(\w*)\n(.*?)```', r'<pre><code class="language-\1">\2</code></pre>', answer, flags=re.DOTALL)
        # 转换标题
        answer = re.sub(r'## (.*?)\n', r'<h3>\1</h3>\n', answer)
        # 转换加粗文本
        answer = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', answer)
        # 转换列表
        answer = re.sub(r'^- (.*?)$', r'<li>\1</li>', answer, flags=re.MULTILINE)
        answer = re.sub(r'(<li>.*?</li>\s*)+', r'<ul>\g<0></ul>', answer, flags=re.DOTALL)
        # 转换空行
        answer = answer.replace('\n\n', '</p>\n<p>')
        if not answer.startswith('<'):
            answer = f'<p>{answer}</p>'

        html += f"            <div class=\"item-content\">{answer}</div>\n"

        if item.get('tags'):
            html += f"            <div class=\"tags\">\n"
            for tag in item['tags']:
                html += f"                <span class=\"tag\">{tag}</span>\n"
            html += f"            </div>\n"

        html += f"        </div>\n\n"

    # 构建页脚
    html += f"            <div class=\"footer\">\n"
    html += f"                <p>© {datetime.now().year} 知识库</p>\n"
    html += f"            </div>\n"
    html += f"        </div>\n"

    # 构建 HTML 尾部
    html += f'''
    </div>
    <script src="{js_path}?v=2"></script>
</body>
</html>
'''

    return html


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

    # 静态文件目录
    static_dir = os.path.join(knowledge_dir, 'static')
    os.makedirs(static_dir, exist_ok=True)


def check_and_rebuild_knowledge_files(output_dir):
    """
    检查知识库文件是否完整，如果不完整则重新生成

    Args:
        output_dir (str): 输出目录

    Returns:
        bool: 是否需要重新生成文件
    """
    knowledge_dir = os.path.join(output_dir, 'knowledge')
    categories_dir = os.path.join(knowledge_dir, 'categories')
    index_file = os.path.join(knowledge_dir, 'index.html')
    recent_updates_file = os.path.join(knowledge_dir, 'recent-updates.html')
    static_dir = os.path.join(knowledge_dir, 'static')
    styles_file = os.path.join(static_dir, 'styles.css')
    scripts_file = os.path.join(static_dir, 'scripts.js')

    # 检查关键文件是否存在
    files_to_check = [
        index_file,
        recent_updates_file,
        styles_file,
        scripts_file
    ]

    missing_files = []
    for file_path in files_to_check:
        if not os.path.exists(file_path):
            missing_files.append(file_path)

    # 检查分类目录下是否有文件
    categories_empty = True
    if os.path.exists(categories_dir):
        for root, dirs, files in os.walk(categories_dir):
            if files:
                categories_empty = False
                break

    if missing_files or categories_empty:
        print(f"检测到知识库文件不完整:")
        if missing_files:
            for f in missing_files:
                print(f"  - 缺失文件: {f}")
        if categories_empty:
            print(f"  - 分类目录为空或不存在")
        return True

    return False


def generate_topic_knowledge_file(topic, items, output_dir):
    """
    生成主题知识文件

    Args:
        topic (str): 主题名称
        items (list): 知识条目列表
        output_dir (str): 输出目录
    """
    file_path = determine_topic_file_path(topic, items, output_dir)

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    file_depth = get_file_depth(file_path, output_dir)
    content = generate_topic_html_content(topic, items, file_depth)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"已生成主题知识文件: {file_path}")


def update_knowledge_base_index(knowledge_items, output_dir):
    """
    更新知识库索引

    Args:
        knowledge_items (list): 知识条目列表
        output_dir (str): 输出目录
    """
    # 将 output_dir 转换为字符串
    output_dir_str = str(output_dir)

    # 生成 HTML 索引文件
    index_path = os.path.join(output_dir_str, 'knowledge', 'index.html')

    # 按分类分组知识条目
    grouped_items = group_items_by_category(knowledge_items)

    # 生成 HTML 内容
    html = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>知识库索引</title>
    <link rel="stylesheet" href="static/styles.css">
</head>
<body>
    <div class="container">
        <!-- 左侧边栏 -->
        <div class="sidebar">
            <!-- 导航链接 -->
            <nav class="toc-nav">
                <ul>
                    <li><a href="recent-updates.html">最近更新</a></li>
                </ul>
            </nav>
        </div>

        <!-- 主要内容 -->
        <div class="main-content">
            <div class="header">
                <h1>知识库索引</h1>
                <p>最后更新: '''
    html += f"{format_datetime()}"
    html += '''</p>
        </div>

        <div class="content">
            <h2>知识条目</h2>
'''

    # 按主题生成索引
    for topic, items in sorted(grouped_items.items()):
        # 对于多级分类，使用最后一级作为主题名称
        if ' > ' in topic:
            actual_topic = topic.split(' > ')[-1]
        else:
            actual_topic = topic
        # 生成主题文件路径
        topic_file_path = determine_topic_file_path(actual_topic, items, output_dir_str)
        relative_path = topic_file_path.replace(output_dir_str + os.sep + 'knowledge' + os.sep, '')
        # 将反斜杠替换为正斜杠，确保链接可以直接点击
        relative_path = relative_path.replace('\\', '/')
        html += f"            <div class=\"topic\">\n"
        # 主题标题支持点击跳转到主题页面
        html += f"                <h3><a href=\"{relative_path}\">{topic}相关</a></h3>\n"
        # 列出该主题下的具体问题，支持点击跳转
        html += f"                <ul class=\"sub-list\">\n"
        for idx, item in enumerate(items, 1):
            anchor = f"item-{idx}"
            item_id = item.get('id', '')
            html += f"                    <li data-id=\"{item_id}\"><a href=\"{relative_path}#{anchor}\">{item['question']}</a></li>\n"
        html += f"                </ul>\n"
        html += f"            </div>\n"

    html += '''
        </div>

            <div class="footer">
                <p>© '''
    html += f"{datetime.now().year}"
    html += ''' 知识库</p>
            </div>
        </div>
    </div>
    <script src="static/scripts.js"></script>
    <script>
        // 索引页面：隐藏已删除的知识条目
        (function() {
            const deletedItems = JSON.parse(localStorage.getItem('deletedKnowledgeItems') || '[]');
            const deletedIds = deletedItems.map(item => typeof item === 'object' ? item.id : item);

            // 获取所有知识条目并隐藏已删除的
            document.querySelectorAll('.sub-list li[data-id]').forEach(link => {
                const itemId = link.getAttribute('data-id');
                if (deletedIds.includes(itemId)) {
                    link.style.display = 'none';
                }
            });

            // 为每个主题统计可见条目数，如果全部删除则隐藏整个主题
            document.querySelectorAll('.topic').forEach(topic => {
                const subList = topic.querySelector('.sub-list');
                if (subList) {
                    const allItems = subList.querySelectorAll('li[data-id]');
                    const visibleItems = subList.querySelectorAll('li[data-id]:not([style*="display: none"])');
                    // 如果主题下有知识条目且全部都被删除，则隐藏整个主题
                    if (allItems.length > 0 && visibleItems.length === 0) {
                        topic.style.display = 'none';
                    }
                }
            });
        })();
    </script>
</body>
</html>
'''

    # 写入索引文件
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"已更新知识库索引: {index_path}")


def update_recent_updates(knowledge_items, output_dir):
    """
    更新最近更新记录

    Args:
        knowledge_items (list): 知识条目列表
        output_dir (str): 输出目录
    """
    # 将 output_dir 转换为字符串
    output_dir_str = str(output_dir)

    # 生成 HTML 最近更新文件
    recent_updates_path = os.path.join(output_dir_str, 'knowledge', 'recent-updates.html')

    # 按时间排序知识条目
    sorted_items = sorted(knowledge_items, key=lambda x: x['timestamp'], reverse=True)

    # 按分类分组最近更新的知识
    recent_grouped = {}
    for item in sorted_items[:10]:  # 只处理最近10条
        # 提取分类
        categories = item.get('categories', [])
        if categories:
            topic = categories[0]
        else:
            topic = '其他'

        if topic not in recent_grouped:
            recent_grouped[topic] = []
        recent_grouped[topic].append(item)

    # 生成 HTML 内容
    html = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>最近更新</title>
    <link rel="stylesheet" href="static/styles.css">
</head>
<body>
    <div class="container">
        <!-- 左侧边栏 -->
        <div class="sidebar">
            <!-- 导航链接 -->
            <nav class="toc-nav">
                <ul>
                    <li><a href="index.html">返回索引</a></li>
                </ul>
            </nav>
        </div>

        <!-- 主要内容 -->
        <div class="main-content">
            <div class="header">
                <h1>最近更新</h1>
                <p>最后更新: '''
    html += f"{format_datetime()}"
    html += '''</p>
        </div>

        <div class="content">
            <h2>最近添加的知识</h2>
'''

    for topic, items in recent_grouped.items():
        # 对于多级分类，使用最后一级作为主题名称
        if ' > ' in topic:
            actual_topic = topic.split(' > ')[-1]
        else:
            actual_topic = topic
        # 生成主题文件路径
        topic_file_path = determine_topic_file_path(actual_topic, items, output_dir_str)
        # 计算相对于索引文件的路径（索引文件在 knowledge 目录下）
        relative_path = topic_file_path.replace(output_dir_str + os.sep + 'knowledge' + os.sep, '')
        # 将反斜杠替换为正斜杠，确保链接可以直接点击
        relative_path = relative_path.replace(os.sep, '/')
        html += f"            <div class=\"topic\">\n"
        # 主题标题支持点击跳转到主题页面
        html += f"                <h3><a href=\"{relative_path}\">{topic}相关</a></h3>\n"
        # 列出该主题下的具体问题，支持点击跳转
        html += f"                <ul class=\"sub-list\">\n"
        for idx, item in enumerate(items, 1):
            anchor = f"item-{idx}"
            item_id = item.get('id', '')
            formatted_time = format_datetime(item['timestamp'])
            html += f"                    <li data-id=\"{item_id}\"><a href=\"{relative_path}#{anchor}\">{item['question']} <span class=\"timestamp\">{formatted_time}</span></a></li>\n"
        html += f"                </ul>\n"
        html += f"            </div>\n"

    html += '''
        </div>

            <div class="footer">
                <p>© '''
    html += f"{datetime.now().year}"
    html += ''' 知识库</p>
            </div>
        </div>
    </div>
    <script src="static/scripts.js"></script>
    <script>
        // 最近更新页面：隐藏已删除的知识条目
        (function() {
            const deletedItems = JSON.parse(localStorage.getItem('deletedKnowledgeItems') || '[]');
            const deletedIds = deletedItems.map(item => typeof item === 'object' ? item.id : item);

            // 获取所有知识条目并隐藏已删除的
            document.querySelectorAll('.sub-list li[data-id]').forEach(link => {
                const itemId = link.getAttribute('data-id');
                if (deletedIds.includes(itemId)) {
                    link.style.display = 'none';
                }
            });

            // 为每个主题统计可见条目数，如果全部删除则隐藏整个主题
            document.querySelectorAll('.topic').forEach(topic => {
                const subList = topic.querySelector('.sub-list');
                if (subList) {
                    const allItems = subList.querySelectorAll('li[data-id]');
                    const visibleItems = subList.querySelectorAll('li[data-id]:not([style*="display: none"])');
                    // 如果主题下有知识条目且全部都被删除，则隐藏整个主题
                    if (allItems.length > 0 && visibleItems.length === 0) {
                        topic.style.display = 'none';
                    }
                }
            });
        })();
    </script>
</body>
</html>
'''

    # 写入最近更新文件
    with open(recent_updates_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"已更新最近更新记录: {recent_updates_path}")


def load_collected_knowledge(input_file=None, knowledge_dir=None, include_deleted=False):
    """
    加载收集的知识

    Args:
        input_file (str, optional): 输入文件路径
        knowledge_dir (str, optional): 知识库目录，用于加载所有历史知识
        include_deleted (bool): 是否包含已删除的知识

    Returns:
        list: 知识条目列表
    """
    import glob

    # 加载已删除的知识列表
    deleted_ids = set()
    if knowledge_dir and not include_deleted:
        deleted_file = os.path.join(knowledge_dir, 'deleted_items.json')
        if os.path.exists(deleted_file):
            try:
                with open(deleted_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    deleted_ids = set(data.get('deleted_ids', []))
            except:
                deleted_ids = set()

    if input_file:
        with open(input_file, 'r', encoding='utf-8') as f:
            items = json.load(f)
            if not include_deleted:
                items = [item for item in items if item.get('id') not in deleted_ids]
            return items

    # 如果指定了知识库目录，加载所有历史知识文件
    if knowledge_dir:
        all_knowledge = []
        seen_questions = set()  # 用于去重
        json_files = glob.glob(os.path.join(knowledge_dir, 'collected_knowledge_*.json'))
        json_files.extend(glob.glob(os.path.join(knowledge_dir, 'knowledge_dump_*.json')))

        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    knowledge_items = json.load(f)
                    for item in knowledge_items:
                        # 跳过已删除的知识
                        if not include_deleted and item.get('id') in deleted_ids:
                            continue

                        question = item.get('question', '')
                        if question and question not in seen_questions:
                            all_knowledge.append(item)
                            seen_questions.add(question)
            except Exception as e:
                print(f"警告: 无法加载文件 {json_file}: {e}")
        return all_knowledge

    return []


def organize_knowledge(knowledge_items, output_dir):
    """
    组织知识 - 统一按分类组织

    Args:
        knowledge_items (list): 知识条目列表
        output_dir (str): 输出目录
    """
    create_knowledge_base_structure(output_dir)

    # 检查知识库文件是否完整，如果不完整则重新生成
    needs_rebuild = check_and_rebuild_knowledge_files(output_dir)

    # 加载所有历史知识
    all_knowledge = load_collected_knowledge(knowledge_dir=output_dir)
    existing_questions = {item.get('question', '').strip() for item in all_knowledge if item.get('question')}

    # 合并新的知识条目（使用问题内容去重，而不是ID）
    for item in knowledge_items:
        question = item.get('question', '').strip()
        if question and question not in existing_questions:
            all_knowledge.append(item)
            existing_questions.add(question)

    # 如果文件不完整或没有知识条目，需要重新生成所有文件
    if needs_rebuild or not all_knowledge:
        print("正在重新生成知识库文件...")

    # 对所有知识条目进行分组
    grouped_items = group_items_by_category(all_knowledge)

    # 为所有分组生成主题文件
    for topic, items in grouped_items.items():
        # 对于多级分类，使用最后一级作为主题名称
        if ' > ' in topic:
            actual_topic = topic.split(' > ')[-1]
        else:
            actual_topic = topic
        generate_topic_knowledge_file(actual_topic, items, output_dir)

    # 更新索引和最近更新页面
    update_knowledge_base_index(all_knowledge, output_dir)
    update_recent_updates(all_knowledge, output_dir)

    import shutil
    script_dir = os.path.dirname(os.path.abspath(__file__))
    static_src_dir = os.path.join(script_dir, 'static')
    static_dst_dir = os.path.join(output_dir, 'knowledge', 'static')

    if os.path.exists(static_src_dir):
        for file_name in os.listdir(static_src_dir):
            src_path = os.path.join(static_src_dir, file_name)
            dst_path = os.path.join(static_dst_dir, file_name)
            if os.path.isfile(src_path):
                shutil.copy2(src_path, dst_path)
                print(f"已复制静态文件: {file_name}")


if __name__ == "__main__":
    # 示例用法
    sample_items = [
        {
            "id": "1",
            "question": "如何解决 Git 提交时的代理配置问题？",
            "answer": "Git 提交时的代理配置问题通常是由于 Git 配置了错误的代理设置导致的。解决方法如下：\n\n## 步骤 1：检查当前代理设置\n```bash\ngit config --global --get http.proxy\ngit config --global --get https.proxy\n```\n\n## 步骤 2：移除错误的代理设置\n```bash\ngit config --global --unset http.proxy\ngit config --global --unset https.proxy\n```\n\n## 步骤 3：验证设置是否生效\n```bash\ngit config --global --list\n```",
            "timestamp": "2026-03-04T13:00:00",
            "tags": ["Git", "问题", "教程"],
            "categories": ["技术知识 > 版本控制"]
        }
    ]
    output_dir = os.path.expanduser("~/.trae-cn/knowledge")
    organize_knowledge(sample_items, output_dir)
