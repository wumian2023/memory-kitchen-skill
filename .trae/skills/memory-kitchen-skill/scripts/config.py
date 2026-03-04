#!/usr/bin/env python3
"""
知识库配置模块

此模块用于自动识别不同的 AI 工具环境，并返回对应的配置目录。
"""

import os
import sys
from pathlib import Path


def detect_ai_environment():
    """
    自动检测当前运行的 AI 工具环境
    
    Returns:
        str: AI 工具名称（claude、cursor、qoder、trae、trae-cn 等）
    """
    # 检查环境变量
    env_tool = os.environ.get('AI_TOOL', '').lower()
    if env_tool:
        return env_tool
    
    # 检查可执行文件路径
    executable_path = sys.executable.lower()
    
    # 检测不同的 AI 工具
    if 'claude' in executable_path:
        return 'claude'
    elif 'cursor' in executable_path:
        return 'cursor'
    elif 'qoder' in executable_path:
        return 'qoder'
    elif 'trae-cn' in executable_path:
        return 'trae-cn'
    elif 'trae' in executable_path:
        return 'trae'
    else:
        # 默认使用 trae-cn
        return 'trae-cn'


def get_config_directory():
    """
    获取 AI 工具的配置目录
    
    Returns:
        Path: 配置目录路径
    """
    ai_tool = detect_ai_environment()
    
    # 根据不同的 AI 工具返回对应的配置目录
    config_dirs = {
        'claude': '.claude',
        'cursor': '.cursor',
        'qoder': '.qoder',
        'trae': '.trae',
        'trae-cn': '.trae-cn'
    }
    
    config_dir_name = config_dirs.get(ai_tool, '.trae-cn')
    
    # 获取用户主目录
    home_dir = Path.home()
    config_dir = home_dir / config_dir_name
    
    return config_dir


def get_knowledge_base_dir():
    """
    获取知识库目录路径
    
    Returns:
        Path: 知识库目录路径
    """
    config_dir = get_config_directory()
    knowledge_dir = config_dir / 'knowledge'
    
    return knowledge_dir


def get_knowledge_base_dir_str():
    """
    获取知识库目录路径（字符串格式）
    
    Returns:
        str: 知识库目录路径字符串
    """
    return str(get_knowledge_base_dir())


def ensure_knowledge_base_exists():
    """
    确保知识库目录存在，如果不存在则创建
    
    Returns:
        Path: 知识库目录路径
    """
    knowledge_dir = get_knowledge_base_dir()
    
    # 创建知识库目录
    categories_dir = knowledge_dir / 'categories'
    tags_dir = knowledge_dir / 'tags'
    
    categories_dir.mkdir(parents=True, exist_ok=True)
    tags_dir.mkdir(parents=True, exist_ok=True)
    
    return knowledge_dir


def get_environment_info():
    """
    获取当前环境信息
    
    Returns:
        dict: 包含环境信息的字典
    """
    ai_tool = detect_ai_environment()
    config_dir = get_config_directory()
    knowledge_dir = get_knowledge_base_dir()
    
    return {
        'ai_tool': ai_tool,
        'config_dir': str(config_dir),
        'knowledge_dir': str(knowledge_dir),
        'python_executable': sys.executable,
        'platform': sys.platform
    }


if __name__ == '__main__':
    # 测试环境检测
    print("环境信息:")
    info = get_environment_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
