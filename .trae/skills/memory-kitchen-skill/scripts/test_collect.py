#!/usr/bin/env python3
"""
测试从对话和上下文中提取知识
"""

from knowledge_collector import collect_knowledge

# 测试用例1: 包含对话和上下文的字典
print("测试用例1: 包含对话和上下文的字典")
test_data = {
    "messages": [
        {
            "role": "user",
            "content": "如何使用 Python 进行数据分析？"
        },
        {
            "role": "assistant",
            "content": "Python 进行数据分析通常使用 pandas、numpy 和 matplotlib 等库。首先需要安装这些库，然后导入并使用它们来处理数据。"
        }
    ],
    "system": "你是一个技术助手，擅长回答编程和技术相关的问题。",
    "context": "用户正在学习数据科学，需要了解如何使用 Python 进行数据分析。Python 是一种广泛使用的编程语言，特别适合数据科学和机器学习。"
}

knowledge_items = collect_knowledge(test_data)
print(f"收集到 {len(knowledge_items)} 条知识")
for item in knowledge_items:
    print(f"\n问题: {item['question']}")
    print(f"答案: {item['answer']}")
    print(f"标签: {item['tags']}")
    print(f"分类: {item['categories']}")

# 测试用例2: 纯文本对话
print("\n\n测试用例2: 纯文本对话")
test_dialogue = """
用户: 如何解决 Git 提交时的代理配置问题？
助手: Git 提交时的代理配置问题通常是由于 Git 配置了错误的代理设置导致的。解决方法如下：
1. 查看当前 Git 代理配置：git config --global --get http.proxy
2. 如果配置了错误的代理，可以取消代理设置：git config --global --unset http.proxy
3. 如果需要使用代理，可以正确配置代理：git config --global http.proxy http://127.0.0.1:7897

[系统]: 这是一个关于 Git 代理配置的问题，用户需要了解如何解决 Git 提交时的代理问题。
[上下文]: Git 是一个分布式版本控制系统，常用于代码管理。代理配置问题是开发者常见的问题之一。
"""

knowledge_items2 = collect_knowledge(test_dialogue)
print(f"收集到 {len(knowledge_items2)} 条知识")
for item in knowledge_items2:
    print(f"\n问题: {item['question']}")
    print(f"答案: {item['answer']}")
    print(f"标签: {item['tags']}")
    print(f"分类: {item['categories']}")