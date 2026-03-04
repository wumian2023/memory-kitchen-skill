#!/usr/bin/env python3
"""
会话管理器 - 自动收集和保存对话知识

此脚本用于在每次对话后自动执行，将对话中的问题和解决方案
保存到项目知识库中。

使用方法:
1. 在对话结束时自动调用（通过钩子或脚本）
2. 手动调用: python session_manager.py --collect
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# 添加脚本目录到路径
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from auto_project_collector import collect_session_knowledge, save_session_messages
from knowledge_collector_v2 import KnowledgeCollector, get_knowledge_base_dir


class SessionManager:
    """会话管理器 - 管理对话历史和知识收集"""

    def __init__(self):
        self.kb_dir = get_knowledge_base_dir()
        self.session_file = os.path.join(self.kb_dir, 'current_session.json')
        self.session_history_dir = os.path.join(self.kb_dir, 'session_history')
        os.makedirs(self.session_history_dir, exist_ok=True)

    def start_session(self, project_name: Optional[str] = None):
        """开始一个新的会话"""
        session_data = {
            'messages': [],
            'project_name': project_name,
            'start_time': datetime.now().isoformat(),
            'status': 'active'
        }

        self._save_session(session_data)
        print(f"✅ 会话已启动" + (f" [项目: {project_name}]" if project_name else ""))

    def add_message(self, role: str, content: str):
        """添加消息到当前会话"""
        session = self._load_session()
        if not session:
            # 自动创建新会话
            self.start_session()
            session = self._load_session()

        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }

        session['messages'].append(message)
        self._save_session(session)

    def end_session(self, auto_collect: bool = True):
        """结束会话并可选自动收集知识"""
        session = self._load_session()
        if not session:
            print("⚠️ 没有活动的会话")
            return

        session['end_time'] = datetime.now().isoformat()
        session['status'] = 'completed'

        # 保存到历史记录
        self._archive_session(session)

        # 自动收集知识
        if auto_collect and session.get('messages'):
            print("\n🔍 正在分析对话内容并提取项目知识...")
            collect_session_knowledge(session)

        # 清除当前会话
        if os.path.exists(self.session_file):
            os.remove(self.session_file)

        print("\n✅ 会话已结束")

    def get_session_summary(self) -> Dict:
        """获取当前会话摘要"""
        session = self._load_session()
        if not session:
            return {}

        messages = session.get('messages', [])
        user_msgs = [m for m in messages if m.get('role') == 'user']
        assistant_msgs = [m for m in messages if m.get('role') == 'assistant']

        return {
            'project_name': session.get('project_name'),
            'message_count': len(messages),
            'user_messages': len(user_msgs),
            'assistant_messages': len(assistant_msgs),
            'start_time': session.get('start_time'),
            'duration': self._calculate_duration(session)
        }

    def _load_session(self) -> Optional[Dict]:
        """加载当前会话"""
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return None
        return None

    def _save_session(self, session_data: Dict):
        """保存当前会话"""
        os.makedirs(self.kb_dir, exist_ok=True)
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)

    def _archive_session(self, session_data: Dict):
        """归档会话到历史记录"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        project_name = session_data.get('project_name', 'unknown')
        filename = f"{timestamp}_{project_name}.json"

        filepath = os.path.join(self.session_history_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)

    def _calculate_duration(self, session: Dict) -> str:
        """计算会话时长"""
        try:
            start = datetime.fromisoformat(session.get('start_time', ''))
            end = datetime.now()
            duration = end - start
            minutes = int(duration.total_seconds() / 60)
            return f"{minutes}分钟"
        except:
            return "未知"


def create_hook_script():
    """创建钩子脚本，用于在对话结束时自动触发"""
    hook_content = '''#!/bin/bash
# 自动知识收集钩子脚本
# 将此脚本添加到对话结束时的回调中

cd "$(dirname "$0")"
python session_manager.py --end --auto-collect
'''

    hook_path = os.path.join(script_dir, 'auto_collect_hook.sh')
    with open(hook_path, 'w', encoding='utf-8') as f:
        f.write(hook_content)

    # Windows版本
    hook_content_win = '''@echo off
REM 自动知识收集钩子脚本
REM 将此脚本添加到对话结束时的回调中

cd /d "%~dp0"
python session_manager.py --end --auto-collect
'''

    hook_path_win = os.path.join(script_dir, 'auto_collect_hook.bat')
    with open(hook_path_win, 'w', encoding='utf-8') as f:
        f.write(hook_content_win)

    print(f"✅ 钩子脚本已创建:")
    print(f"   Linux/Mac: {hook_path}")
    print(f"   Windows: {hook_path_win}")


# --- 命令行接口 ---
def main():
    parser = argparse.ArgumentParser(description='会话管理器 - 自动收集对话知识')
    parser.add_argument('--start', action='store_true', help='开始新会话')
    parser.add_argument('--end', action='store_true', help='结束会话')
    parser.add_argument('--auto-collect', action='store_true', help='自动收集知识')
    parser.add_argument('--project', type=str, help='指定项目名称')
    parser.add_argument('--status', action='store_true', help='查看会话状态')
    parser.add_argument('--collect-only', action='store_true', help='仅收集知识（不结束会话）')
    parser.add_argument('--create-hooks', action='store_true', help='创建钩子脚本')

    args = parser.parse_args()

    manager = SessionManager()

    if args.create_hooks:
        create_hook_script()
        return

    if args.start:
        manager.start_session(args.project)
    elif args.end:
        manager.end_session(auto_collect=args.auto_collect)
    elif args.status:
        summary = manager.get_session_summary()
        if summary:
            print("📊 当前会话状态:")
            print(f"   项目: {summary.get('project_name', '未指定')}")
            print(f"   消息数: {summary.get('message_count', 0)}")
            print(f"   用户消息: {summary.get('user_messages', 0)}")
            print(f"   助手消息: {summary.get('assistant_messages', 0)}")
            print(f"   开始时间: {summary.get('start_time', '未知')}")
            print(f"   时长: {summary.get('duration', '未知')}")
        else:
            print("ℹ️ 没有活动的会话")
    elif args.collect_only:
        session = manager._load_session()
        if session:
            print("🔍 正在收集知识...")
            collect_session_knowledge(session)
        else:
            print("⚠️ 没有活动的会话")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
