#!/usr/bin/env python3
"""
分析对话并更新知识库
"""

import os
import json
from datetime import datetime

from knowledge_collector import collect_knowledge, save_collected_knowledge
from knowledge_organizer import organize_knowledge
from config import ensure_knowledge_base_exists

dialogue_content = """
用户: 新建的这些文件布局格式还是老样子没有与Git相关.html格式完全一致
助手: 我发现了问题根源！这段代码存在几个关键问题：

1. 核心问题：CSS样式路径硬编码
问题描述：在generate_topic_html_content函数中，CSS路径被硬编码为../../../static/styles.css。然而，文件生成的深度是由determine_topic_file_path动态决定的（取决于分类层级）。

2. 逻辑冲突：按"标签"分组，按"分类"存路径
问题描述：group_items_by_topic是根据Tags进行分组的，determine_topic_file_path是根据Categories决定文件存储路径的。这导致文件结构混乱。

3. 格式不统一：Markdown vs HTML
问题描述：retrieve_knowledge设计用来检索.md文件，organize_knowledge生成的是.html文件。两个脚本操作的是完全不同的文件体系。

4. 路径分隔符问题
问题描述：代码中混用了os.sep和URL需要的/，虽然有replace('\\\\', '/')的补救措施，但可能导致链接失效。

修复方案：

1. 动态计算CSS相对路径
添加了calculate_css_relative_path、calculate_js_relative_path和get_file_depth函数，根据文件深度动态计算CSS和JS的相对路径。

2. 统一分组逻辑
添加了group_items_by_category函数，统一按分类分组知识条目，确保分组逻辑与文件路径一致。

3. 修复路径分隔符
在生成HTML内部链接时，始终使用/作为分隔符，确保Web兼容性。
"""

knowledge_base_dir = ensure_knowledge_base_exists()
print(f"知识库目录: {knowledge_base_dir}")

print("\n正在分析对话内容...")
knowledge_items = collect_knowledge(dialogue_content)

if not knowledge_items:
    print("未从对话中提取到任何知识")
else:
    print(f"从对话中提取到 {len(knowledge_items)} 条知识")

    print("\n正在保存知识...")
    save_collected_knowledge(knowledge_items)

    print("\n正在整理和分类知识...")
    organize_knowledge(knowledge_items, knowledge_base_dir)

    print("\n知识库更新完成！")

    print("\n更新报告:")
    print(f"- 提取知识条目数: {len(knowledge_items)}")
    print(f"- 知识库位置: {knowledge_base_dir}")
    print(f"- 更新时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}")

    for i, item in enumerate(knowledge_items, 1):
        print(f"\n{i}. 问题: {item['question']}")
        print(f"   分类: {item['categories']}")
        print(f"   标签: {item['tags']}")
