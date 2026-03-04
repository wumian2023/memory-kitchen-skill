#!/usr/bin/env python3
"""
自动项目知识收集器

在每次对话后自动执行，分析对话内容并提取项目相关的问题和解决方法，
自动保存到项目知识库中。

使用方法:
1. 在对话结束时调用: python auto_project_collector.py
2. 或者导入使用: from auto_project_collector import collect_session_knowledge
"""

import re
import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path

# 添加脚本目录到路径
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

try:
    from knowledge_collector_v2 import KnowledgeCollector, get_knowledge_base_dir
except ImportError:
    def get_knowledge_base_dir():
        return os.path.expanduser("~/.trae-cn/knowledge")


class SessionKnowledgeExtractor:
    """会话知识提取器 - 从当前对话中提取问题和解决方案"""

    # 问题模式
    PROBLEM_INDICATORS = [
        r'报错', r'错误', r'异常', r'Exception', r'Error', r'Failed', r'Bug', r'故障',
        r'无法', r'不能', r'崩溃', r'泄漏', r'超时', r'404', r'500', r'502', r'503',
        r'连接失败', r'拒绝连接', r'权限不足', r'内存溢出', r'CPU.*高', r'卡顿', r'慢',
        r'问题', r'issue', r'problem', r'bug', r'error', r'fail'
    ]

    # 解决方案模式
    SOLUTION_INDICATORS = [
        r'解决', r'修复', r'搞定', r'Workaround', r'方案', r'通过', r'使用',
        r'配置', r'更新', r'升级', r'重装', r'重启', r'修改', r'调整', r'添加',
        r'删除', r'替换', r'优化', r'改进', r'设置', r'安装', r'部署',
        r'fixed', r'solved', r'resolved', r'solution', r'workaround'
    ]

    # 项目识别模式
    PROJECT_INDICATORS = [
        r'项目[：:]\s*(.+?)(?:\n|$)',
        r'project[：:]\s*(.+?)(?:\n|$)',
        r'在\s*(.+?)\s*项目中',
        r'关于\s*(.+?)\s*项目'
    ]

    def __init__(self):
        self.collector = KnowledgeCollector()

    def extract_from_conversation(self, conversation_data: Dict) -> List[Dict]:
        """
        从对话数据中提取问题和解决方案对

        Args:
            conversation_data: 包含对话消息的字典
                {
                    "messages": [
                        {"role": "user", "content": "..."},
                        {"role": "assistant", "content": "..."}
                    ],
                    "context": "项目背景信息",
                    "project_name": "可选的项目名称"
                }

        Returns:
            List[Dict]: 提取的知识条目列表
        """
        messages = conversation_data.get('messages', [])
        project_name = conversation_data.get('project_name', self._detect_project_name(messages))

        if not project_name:
            print("⚠️ 未检测到项目名称，跳过项目知识收集")
            return []

        print(f"📁 检测到项目: {project_name}")

        # 识别问题和解决方案对
        problem_solution_pairs = self._identify_problem_solution_pairs(messages)

        knowledge_items = []
        for problem, solution in problem_solution_pairs:
            if self._is_valuable_problem(problem, solution):
                item = {
                    'project': project_name,
                    'problem': problem,
                    'solution': solution,
                    'timestamp': datetime.now().isoformat(),
                    'tags': self._extract_tags(problem + ' ' + solution)
                }
                knowledge_items.append(item)
                print(f"✅ 提取到问题和解决方案: {problem[:50]}...")

        return knowledge_items

    def _detect_project_name(self, messages: List[Dict]) -> Optional[str]:
        """从消息中检测项目名称"""
        # 合并所有消息内容
        all_content = ' '.join([msg.get('content', '') for msg in messages])

        # 尝试匹配项目指示器
        for pattern in self.PROJECT_INDICATORS:
            match = re.search(pattern, all_content, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        # 如果没有明确的项目名称，尝试从工作目录推断
        try:
            cwd = os.getcwd()
            # 使用当前目录名作为项目名
            project_name = os.path.basename(cwd)
            if project_name and project_name not in ['.', '/', '\\']:
                return project_name
        except:
            pass

        return None

    def _identify_problem_solution_pairs(self, messages: List[Dict]) -> List[Tuple[str, str]]:
        """识别对话中的问题和解决方案对"""
        pairs = []
        current_problem = None
        current_solution_parts = []

        for i, msg in enumerate(messages):
            content = msg.get('content', '')
            role = msg.get('role', '')

            if role == 'user':
                # 检查是否是问题描述
                if self._is_problem_description(content):
                    # 如果之前有未保存的问题-解决方案对，先保存
                    if current_problem and current_solution_parts:
                        pairs.append((current_problem, '\n'.join(current_solution_parts)))

                    current_problem = content
                    current_solution_parts = []

            elif role == 'assistant':
                # 检查是否包含解决方案
                if current_problem and self._is_solution_content(content):
                    current_solution_parts.append(content)

                # 检查是否是最终解决方案（包含代码块或明确的成功指示）
                if current_problem and self._is_final_solution(content):
                    pairs.append((current_problem, '\n'.join(current_solution_parts)))
                    current_problem = None
                    current_solution_parts = []

        # 处理最后一对
        if current_problem and current_solution_parts:
            pairs.append((current_problem, '\n'.join(current_solution_parts)))

        return pairs

    def _is_problem_description(self, text: str) -> bool:
        """判断文本是否是问题描述"""
        # 包含问题指示器
        has_problem = any(re.search(p, text, re.IGNORECASE) for p in self.PROBLEM_INDICATORS)

        # 包含问号
        has_question = '?' in text or '？' in text

        # 长度适中（不是简单的问候）
        is_substantial = len(text) > 20

        return (has_problem or has_question) and is_substantial

    def _is_solution_content(self, text: str) -> bool:
        """判断文本是否包含解决方案"""
        # 包含解决方案指示器
        has_solution = any(re.search(p, text, re.IGNORECASE) for p in self.SOLUTION_INDICATORS)

        # 包含代码块
        has_code = '```' in text

        # 包含步骤说明
        has_steps = bool(re.search(r'\d+[、.．]', text))

        return has_solution or has_code or has_steps

    def _is_final_solution(self, text: str) -> bool:
        """判断是否是最终解决方案"""
        # 包含成功关键词
        success_keywords = ['解决', '搞定', '完成', '成功', 'fixed', 'solved', 'resolved', 'done']
        has_success = any(kw in text.lower() for kw in success_keywords)

        # 包含代码块
        has_code = '```' in text

        # 包含配置示例
        has_config = any(kw in text for kw in ['配置', '设置', '修改', '添加'])

        return has_success or (has_code and has_config)

    def _is_valuable_problem(self, problem: str, solution: str) -> bool:
        """判断问题-解决方案对是否有价值"""
        # 问题不能太短
        if len(problem) < 10:
            return False

        # 解决方案不能太短
        if len(solution) < 20:
            return False

        # 不能是纯寒暄
        trivial_words = ['你好', '谢谢', '再见', 'ok', '好的', '收到']
        if any(w in problem for w in trivial_words) and len(problem) < 30:
            return False

        return True

    def _extract_tags(self, text: str) -> List[str]:
        """从文本中提取标签"""
        tags = []

        # 技术栈关键词
        tech_keywords = {
            'Python', 'Java', 'JavaScript', 'TypeScript', 'Go', 'Rust',
            'React', 'Vue', 'Angular', 'Django', 'Flask', 'FastAPI',
            'Docker', 'Kubernetes', 'MySQL', 'PostgreSQL', 'MongoDB',
            'Redis', 'Git', 'Linux', 'AWS', 'Nginx'
        }

        for tech in tech_keywords:
            if re.search(rf'\b{re.escape(tech)}\b', text, re.IGNORECASE):
                tags.append(tech)

        return tags[:5]  # 最多返回5个标签

    def save_to_project_knowledge(self, knowledge_items: List[Dict]):
        """保存提取的知识到项目知识库"""
        if not knowledge_items:
            print("ℹ️ 没有需要保存的项目知识")
            return

        for item in knowledge_items:
            project_name = item['project']
            problem = item['problem']
            solution = item['solution']
            tags = item.get('tags', [])

            self.collector.save_project_knowledge(
                project_name=project_name,
                problem=problem,
                solution=solution,
                tags=tags
            )


def collect_session_knowledge(conversation_data: Optional[Dict] = None):
    """
    收集当前会话的知识并保存到项目知识库

    这是主要的入口函数，可以在对话结束时调用。

    Args:
        conversation_data: 对话数据，如果为None则尝试从环境或文件读取
    """
    extractor = SessionKnowledgeExtractor()

    # 如果没有提供对话数据，尝试读取当前会话记录
    if conversation_data is None:
        conversation_data = load_current_session()

    if not conversation_data or not conversation_data.get('messages'):
        print("⚠️ 没有找到对话数据")
        return

    # 提取知识
    knowledge_items = extractor.extract_from_conversation(conversation_data)

    # 保存到项目知识库
    extractor.save_to_project_knowledge(knowledge_items)

    if knowledge_items:
        print(f"\n✅ 成功保存 {len(knowledge_items)} 条项目知识")
    else:
        print("\nℹ️ 本次对话未提取到项目知识")


def load_current_session() -> Optional[Dict]:
    """加载当前会话数据"""
    # 尝试从环境变量读取
    session_file = os.environ.get('CURRENT_SESSION_FILE')

    if session_file and os.path.exists(session_file):
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass

    # 尝试从默认位置读取
    kb_dir = get_knowledge_base_dir()
    default_session = os.path.join(kb_dir, 'current_session.json')

    if os.path.exists(default_session):
        try:
            with open(default_session, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass

    return None


def save_session_messages(messages: List[Dict], project_name: Optional[str] = None):
    """
    保存会话消息，供后续自动收集使用

    Args:
        messages: 对话消息列表
        project_name: 可选的项目名称
    """
    session_data = {
        'messages': messages,
        'timestamp': datetime.now().isoformat(),
        'project_name': project_name
    }

    kb_dir = get_knowledge_base_dir()
    os.makedirs(kb_dir, exist_ok=True)

    session_file = os.path.join(kb_dir, 'current_session.json')

    with open(session_file, 'w', encoding='utf-8') as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)


# --- 主程序入口 ---
if __name__ == '__main__':
    print("=" * 60)
    print("自动项目知识收集器")
    print("=" * 60)
    print()

    # 检查是否有命令行参数传入对话数据
    if len(sys.argv) > 1:
        # 从文件读取对话数据
        session_file = sys.argv[1]
        if os.path.exists(session_file):
            with open(session_file, 'r', encoding='utf-8') as f:
                conversation_data = json.load(f)
            collect_session_knowledge(conversation_data)
        else:
            print(f"❌ 文件不存在: {session_file}")
    else:
        # 自动收集当前会话
        collect_session_knowledge()
