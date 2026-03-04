#!/usr/bin/env python3
"""
自动收集对话知识的主脚本

此脚本用于自动从对话中收集有价值的信息，并存储到知识库中。
"""

import sys
import os
import json
from datetime import datetime

# 导入配置和功能模块
from config import get_knowledge_base_dir_str, ensure_knowledge_base_exists
from knowledge_collector import collect_knowledge, save_collected_knowledge
from knowledge_organizer import organize_knowledge


def auto_collect_from_dialogue(dialogue_text, auto_organize=True):
    """
    自动从对话中收集知识

    Args:
        dialogue_text (str): 对话文本内容
        auto_organize (bool): 是否自动整理和分类知识

    Returns:
        dict: 收集结果统计
    """
    # 确保知识库目录存在
    knowledge_base_dir = ensure_knowledge_base_exists()

    print(f"知识库目录: {knowledge_base_dir}")

    # 收集知识
    print("\n正在收集知识...")
    knowledge_items = collect_knowledge(dialogue_text)

    if not knowledge_items:
        print("未收集到任何知识")
        return {
            'total': 0,
            'collected': 0,
            'organized': 0,
            'message': '未收集到任何知识'
        }

    print(f"收集到 {len(knowledge_items)} 条知识")

    # 保存收集的知识
    print("\n正在保存知识...")
    save_collected_knowledge(knowledge_items)

    # 自动整理和分类
    if auto_organize:
        print("\n正在整理和分类知识...")
        organize_knowledge(knowledge_items, knowledge_base_dir)

    # 返回统计结果
    result = {
        'total': len(knowledge_items),
        'collected': len(knowledge_items),
        'organized': len(knowledge_items) if auto_organize else 0,
        'knowledge_base_dir': str(knowledge_base_dir),
        'message': f'成功收集并整理了 {len(knowledge_items)} 条知识'
    }

    print(f"\n{result['message']}")
    print(f"知识库位置: {result['knowledge_base_dir']}")

    return result


def auto_collect_from_file(file_path, auto_organize=True):
    """
    自动从文件中收集知识

    Args:
        file_path (str): 对话文件路径
        auto_organize (bool): 是否自动整理和分类知识

    Returns:
        dict: 收集结果统计
    """
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        dialogue_text = f.read()

    return auto_collect_from_dialogue(dialogue_text, auto_organize)


def auto_collect_from_session(session_data, auto_organize=True):
    """
    自动从会话数据中收集知识

    Args:
        session_data (dict): 会话数据，包含对话历史
        auto_organize (bool): 是否自动整理和分类知识

    Returns:
        dict: 收集结果统计
    """
    # 将会话数据转换为文本
    dialogue_text = ""

    if 'messages' in session_data:
        for message in session_data['messages']:
            role = message.get('role', 'unknown')
            content = message.get('content', '')
            dialogue_text += f"[{role}]: {content}\n\n"
    else:
        # 直接使用字符串格式
        dialogue_text = str(session_data)

    return auto_collect_from_dialogue(dialogue_text, auto_organize)


def create_sample_dialogue():
    """
    创建示例对话数据

    Returns:
        str: 示例对话文本
    """
    # 直接返回结构化的知识条目，避免文本解析问题
    return [
        {
            "id": "1",
            "question": "如何解决 Git 提交时的代理配置问题？",
            "answer": '''Git 提交时的代理配置问题通常是由于 Git 配置了错误的代理设置导致的。解决方法如下：

1. 查看当前 Git 代理配置：
```bash
git config --global --get http.proxy
git config --global --get https.proxy
```

2. 如果配置了错误的代理，可以取消代理设置：
```bash
git config --global --unset http.proxy
git config --global --unset https.proxy
```

3. 如果需要使用代理，可以正确配置代理：
```bash
git config --global http.proxy http://127.0.0.1:7897
git config --global https.proxy http://127.0.0.1:7897
```

4. 配置完成后，可以正常提交代码：
```bash
git add .
git commit -m "your message"
git push
```''',
            "timestamp": "2026-03-04T13:00:00",
            "tags": ["Git", "问题", "教程"],
            "categories": ["技术知识 > 版本控制"]
        },
        {
            "id": "2",
            "question": "如何使用代理克隆 GitHub 仓库？",
            "answer": '''使用代理克隆 GitHub 仓库有以下几种方法：

方法1：配置 Git 代理
```bash
git config --global http.proxy http://127.0.0.1:7897
git config --global https.proxy http://127.0.0.1:7897
git clone https://github.com/user/repo.git
```

方法2：使用环境变量
```bash
export http_proxy=http://127.0.0.1:7897
export https_proxy=http://127.0.0.1:7897
git clone https://github.com/user/repo.git
```

方法3：临时使用代理
```bash
git -c http.proxy=http://127.0.0.1:7897 clone https://github.com/user/repo.git
```''',
            "timestamp": "2026-03-04T13:01:00",
            "tags": ["Git", "GitHub", "教程"],
            "categories": ["技术知识 > 版本控制"]
        },
        {
            "id": "3",
            "question": "Python 中如何处理内存泄漏问题？",
            "answer": '''Python 中的内存泄漏通常由以下原因引起：

1. 循环引用：对象之间存在循环引用，导致引用计数无法归零
   解决方法：使用 weakref 模块或显式断开引用

2. 全局变量：全局变量持有大量数据，不会被垃圾回收
   解决方法：及时清理不再使用的全局变量

3. 闭包：闭包函数持有外部变量的引用
   解决方法：使用 del 语句或重新赋值为 None

4. 第三方库：某些第三方库存在内存泄漏问题
   解决方法：升级到最新版本或使用替代库

检测内存泄漏的工具：
- memory_profiler：分析内存使用情况
- objgraph：可视化对象引用关系
- tracemalloc：跟踪内存分配''',
            "timestamp": "2026-03-04T13:02:00",
            "tags": ["Python", "内存泄漏", "解决方案"],
            "categories": ["技术知识 > 前端开发"]
        }
    ]


def main():
    """
    主函数
    """
    print("=" * 60)
    print("自动记忆知识库 - 知识收集工具")
    print("=" * 60)

    # 确保知识库目录存在
    knowledge_base_dir = ensure_knowledge_base_exists()
    print(f"知识库目录: {knowledge_base_dir}")

    # 检查命令行参数
    if len(sys.argv) > 1:
        # 从文件收集
        file_path = sys.argv[1]
        print(f"\n从文件收集知识: {file_path}")
        auto_collect_from_file(file_path)
    else:
        # 使用示例对话
        print("\n使用示例对话进行演示...")
        knowledge_items = create_sample_dialogue()

        print(f"\n收集到 {len(knowledge_items)} 条知识")

        # 保存知识
        print("\n正在保存知识...")
        save_collected_knowledge(knowledge_items)

        # 整理知识
        print("\n正在整理和分类知识...")
        organize_knowledge(knowledge_items, knowledge_base_dir)

    print("\n" + "=" * 60)
    print("知识收集完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
