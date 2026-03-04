#!/usr/bin/env python3
"""
高级自动知识收集器 (Advanced Knowledge Collector) - 改进版

此脚本用于深度分析对话内容，提取真正有价值的知识：
- 故障排除记录（问题+根因+解决方案）
- 架构决策（选型对比+决策理由+实施结果）
- 最佳实践（场景+做法+效果）
- 高质量代码片段（完整可运行+使用说明）
"""

import re
import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict

# --- 配置与容错处理 ---
try:
    from config import get_knowledge_base_dir
except ImportError:
    def get_knowledge_base_dir():
        return "./knowledge_base"

# --- 常量定义 ---
TECH_STACK_KEYWORDS = {
    'Languages': ['Python', 'Java', 'JavaScript', 'TypeScript', 'Go', 'Rust', 'C++', 'SQL', 'Shell'],
    'Frontend': ['React', 'Vue', 'Angular', 'Svelte', 'HTML', 'CSS', 'Webpack', 'Vite'],
    'Backend': ['Django', 'Flask', 'FastAPI', 'Spring', 'Node.js', 'Express', 'Nginx'],
    'DevOps': ['Docker', 'Kubernetes', 'Jenkins', 'GitLab CI', 'GitHub Actions', 'Terraform', 'Ansible'],
    'Database': ['MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch', 'SQLite'],
    'Cloud': ['AWS', 'Azure', 'GCP', 'AliCloud', 'S3', 'EC2', 'Lambda'],
    'Tools': ['Git', 'VS Code', 'PyCharm', 'Postman', 'Jira', 'Linux', 'MacOS']
}

# 问题模式（需要匹配到具体问题）
PROBLEM_PATTERNS = [
    r'报错', r'错误', r'异常', r'Exception', r'Error', r'Failed', r'Bug', r'故障',
    r'无法', r'不能', r'崩溃', r'泄漏', r'超时', r'404', r'500', r'502', r'503',
    r'连接失败', r'拒绝连接', r'权限不足', r'内存溢出', r'CPU.*高', r'卡顿', r'慢'
]

# 解决方案模式（需要匹配到具体解决动作）
SOLUTION_PATTERNS = [
    r'解决', r'修复', r'搞定', r'Workaround', r'方案', r'通过', r'使用',
    r'配置', r'更新', r'升级', r'重装', r'重启', r'修改', r'调整', r'添加',
    r'删除', r'替换', r'优化', r'改进', r'设置', r'安装', r'部署'
]

# 决策模式
DECISION_PATTERNS = [
    r'决定', r'选择', r'采用', r'放弃', r'计划', r'架构', r'设计', r'重构',
    r'迁移', r'升级', r'降级', r'替换', r'对比', r'优于', r'不如', r'性能.*好',
    r'更适合', r'不推荐', r'建议'
]

# 寒暄过滤词
TRIVIAL_WORDS = ['你好', '谢谢', '再见', 'ok', '好的', '收到', '嗯', '哦', '啊', '在吗']


class KnowledgeItem:
    """知识条目类，用于聚合相关片段"""
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.timestamp = datetime.now().isoformat()
        self.type = 'General'  # QA, Troubleshooting, Decision, BestPractice, Code
        self.question = ''
        self.answer = ''
        self.problem = ''  # 问题描述
        self.cause = ''    # 根因分析
        self.solution = '' # 解决方案
        self.context = []  # 相关上下文
        self.tags = set()
        self.categories = set()
        self.confidence = 0.5
        self.needs_review = False  # 是否需要人工审核
        self.source_fragments = []  # 来源片段

    def to_dict(self) -> Dict:
        """转换为字典格式"""
        # 根据类型构建最终内容
        if self.type == 'Troubleshooting':
            content_parts = []
            if self.problem:
                content_parts.append(f"**问题现象**：{self.problem}")
            if self.cause:
                content_parts.append(f"**根因分析**：{self.cause}")
            if self.solution:
                content_parts.append(f"**解决方案**：{self.solution}")
            if self.context:
                content_parts.append(f"**补充说明**：{' '.join(self.context)}")
            final_answer = '\n\n'.join(content_parts) if content_parts else self.answer
        elif self.type == 'Decision':
            content_parts = []
            if self.problem:  # 决策背景
                content_parts.append(f"**决策背景**：{self.problem}")
            if self.solution:  # 决策内容
                content_parts.append(f"**决策内容**：{self.solution}")
            if self.cause:  # 决策理由
                content_parts.append(f"**决策理由**：{self.cause}")
            if self.context:
                content_parts.append(f"**实施效果**：{' '.join(self.context)}")
            final_answer = '\n\n'.join(content_parts) if content_parts else self.answer
        else:
            final_answer = self.answer
            if self.context:
                final_answer += f"\n\n**补充信息**：{' '.join(self.context)}"

        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "source_type": self.type,
            "question": self.question,
            "answer": final_answer,
            "tags": list(self.tags),
            "categories": list(self.categories),
            "confidence": self.confidence,
            "needs_review": self.needs_review
        }


class KnowledgeCollector:
    def __init__(self):
        self.knowledge_items = []
        self.raw_fragments = []  # 原始片段，用于后续合并

    def collect(self, input_data: Any) -> List[Dict]:
        """主入口：处理输入并收集知识"""
        dialogue_text = self._normalize_input(input_data)

        # 1. 提取所有候选片段
        self.raw_fragments = self._extract_fragments(dialogue_text)

        # 2. 按主题聚合并合并相关片段
        merged_items = self._merge_fragments(self.raw_fragments)

        # 3. 过滤低价值内容
        valuable_items = [item for item in merged_items if self._is_valuable(item)]

        # 4. 增强元数据
        for item in valuable_items:
            self._enrich_item(item)
            self.knowledge_items.append(item.to_dict())

        return self.knowledge_items

    def _normalize_input(self, input_data: Any) -> str:
        """统一输入格式为字符串"""
        if isinstance(input_data, dict):
            parts = []
            if 'system' in input_data:
                parts.append(f"[System]: {input_data['system']}")
            if 'messages' in input_data:
                for msg in input_data['messages']:
                    role = msg.get('role', 'unknown')
                    content = msg.get('content', '')
                    parts.append(f"[{role}]: {content}")
            if 'context' in input_data:
                parts.append(f"[Context]: {input_data['context']}")
            return "\n".join(parts)
        return str(input_data)

    def _extract_fragments(self, text: str) -> List[Dict]:
        """提取所有候选片段"""
        fragments = []
        lines = text.split('\n')

        current_role = None
        current_content = []
        last_question = None
        last_question_role = None

        user_re = re.compile(r'^\s*\[?(用户|User|user|U)\]?\s*[:：]')
        assistant_re = re.compile(r'^\s*\[?(助手|Assistant|assistant|A|AI)\]?\s*[:：]')

        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue

            if user_re.match(line_stripped):
                # 保存之前的 QA
                if last_question and current_content:
                    fragments.append({
                        'type': 'qa',
                        'question': last_question,
                        'answer': "\n".join(current_content),
                        'has_problem': self._has_problem(last_question + " " + "\n".join(current_content)),
                        'has_solution': self._has_solution("\n".join(current_content)),
                        'tech_mentioned': self._extract_tech_keywords(last_question + " " + "\n".join(current_content))
                    })

                current_content = []
                last_question = re.sub(r'^\s*\[?.*?\]?\s*[:：]\s*', '', line_stripped)
                last_question_role = 'user'
                current_role = 'user'

            elif assistant_re.match(line_stripped):
                if last_question:
                    content = re.sub(r'^\s*\[?.*?\]?\s*[:：]\s*', '', line_stripped)
                    current_content.append(content)
                current_role = 'assistant'

            elif current_role == 'assistant' and last_question:
                current_content.append(line_stripped)

        # 处理最后一对
        if last_question and current_content:
            fragments.append({
                'type': 'qa',
                'question': last_question,
                'answer': "\n".join(current_content),
                'has_problem': self._has_problem(last_question + " " + "\n".join(current_content)),
                'has_solution': self._has_solution("\n".join(current_content)),
                'tech_mentioned': self._extract_tech_keywords(last_question + " " + "\n".join(current_content))
            })

        # 提取代码块
        code_fragments = self._extract_code_snippets(text)
        fragments.extend(code_fragments)

        return fragments

    def _has_problem(self, text: str) -> bool:
        """检查是否包含问题描述"""
        return any(re.search(p, text, re.IGNORECASE) for p in PROBLEM_PATTERNS)

    def _has_solution(self, text: str) -> bool:
        """检查是否包含解决方案"""
        return any(re.search(p, text, re.IGNORECASE) for p in SOLUTION_PATTERNS)

    def _has_decision(self, text: str) -> bool:
        """检查是否包含决策"""
        return any(re.search(p, text, re.IGNORECASE) for p in DECISION_PATTERNS)

    def _extract_tech_keywords(self, text: str) -> List[str]:
        """提取技术关键词"""
        techs = []
        for category, tools in TECH_STACK_KEYWORDS.items():
            for tool in tools:
                if re.search(rf'\b{re.escape(tool)}\b', text, re.IGNORECASE):
                    techs.append(tool)
        return techs

    def _extract_code_snippets(self, text: str) -> List[Dict]:
        """提取 Markdown 代码块"""
        fragments = []
        pattern = re.compile(r'```(\w*)\n(.*?)```', re.DOTALL)
        matches = pattern.findall(text)

        for lang, code in matches:
            code = code.strip()
            if len(code) > 30:  # 提高代码长度门槛
                fragments.append({
                    'type': 'code',
                    'lang': lang if lang else 'text',
                    'content': code,
                    'has_problem': False,
                    'has_solution': True,  # 代码视为解决方案
                    'tech_mentioned': self._extract_tech_keywords(code)
                })
        return fragments

    def _merge_fragments(self, fragments: List[Dict]) -> List[KnowledgeItem]:
        """按主题聚合并合并相关片段"""
        items = []

        # 按技术关键词分组
        tech_groups = defaultdict(list)
        other_fragments = []

        for frag in fragments:
            techs = frag.get('tech_mentioned', [])
            if techs:
                # 使用第一个技术关键词作为主键
                tech_groups[techs[0]].append(frag)
            else:
                other_fragments.append(frag)

        # 处理每个技术组
        for tech, frags in tech_groups.items():
            item = self._create_knowledge_item(frags, tech)
            if item:
                items.append(item)

        # 处理其他片段
        for frag in other_fragments:
            if frag.get('type') == 'qa':
                item = KnowledgeItem()
                item.question = frag['question']
                item.answer = frag['answer']
                item.type = 'QA'
                item.source_fragments = [frag]
                items.append(item)

        return items

    def _create_knowledge_item(self, fragments: List[Dict], main_tech: str) -> Optional[KnowledgeItem]:
        """从一组片段创建知识条目"""
        item = KnowledgeItem()
        item.tags.add(main_tech)

        # 分类片段
        problem_frags = []
        solution_frags = []
        code_frags = []
        context_frags = []
        all_qa_frags = []

        for frag in fragments:
            if frag.get('type') == 'code':
                code_frags.append(frag)
            elif frag.get('type') == 'qa':
                all_qa_frags.append(frag)
                if frag.get('has_problem') and not frag.get('has_solution'):
                    problem_frags.append(frag)
                elif frag.get('has_solution') and not frag.get('has_problem'):
                    solution_frags.append(frag)
                elif frag.get('has_problem') and frag.get('has_solution'):
                    # 既有问题又有解决方案
                    solution_frags.append(frag)
                else:
                    context_frags.append(frag)
            else:
                context_frags.append(frag)

        # 确定知识类型 - 改进逻辑
        # 1. 首先检查是否是故障排除（问题和解决方案在不同片段中）
        has_problem_anywhere = any(f.get('has_problem') for f in all_qa_frags)
        has_solution_anywhere = any(f.get('has_solution') for f in all_qa_frags)

        if has_problem_anywhere and has_solution_anywhere:
            item.type = 'Troubleshooting'
            item.categories.add('故障排除')

            # 构建问题描述（从所有包含问题的片段）
            problems = []
            for frag in all_qa_frags:
                if frag.get('has_problem'):
                    if frag.get('question'):
                        problems.append(frag['question'])
                    if frag.get('answer'):
                        problems.append(frag['answer'])
            item.problem = self._deduplicate_text(' '.join(problems))

            # 构建解决方案（从所有包含解决方案的片段）
            solutions = []
            for frag in all_qa_frags:
                if frag.get('has_solution'):
                    if frag.get('answer'):
                        solutions.append(frag['answer'])
                    if frag.get('question'):
                        solutions.append(frag['question'])
            item.solution = self._deduplicate_text(' '.join(solutions))

            # 设置问题标题
            item.question = f"【故障排除】{main_tech}：{self._extract_problem_summary(item.problem)}"

            # 添加代码
            if code_frags:
                item.solution += "\n\n**参考代码**：\n```" + code_frags[0]['lang'] + "\n" + code_frags[0]['content'] + "\n```"
                item.tags.add('Code')

        elif self._has_decision(' '.join([f.get('question', '') + f.get('answer', '') for f in all_qa_frags])):
            item.type = 'Decision'
            item.categories.add('架构决策')

            # 构建决策记录
            for frag in all_qa_frags:
                if frag.get('has_problem'):
                    item.problem = frag['question']
                if frag.get('has_solution'):
                    item.solution = frag['answer']

            # 如果没有明确的解决方案，使用第一个有内容的回答
            if not item.solution and all_qa_frags:
                for frag in all_qa_frags:
                    if frag.get('answer'):
                        item.solution = frag['answer']
                        break

            item.question = f"【架构决策】{main_tech}技术选型"

        else:
            # 普通QA或最佳实践
            if solution_frags:
                item.type = 'BestPractice'
                item.categories.add('最佳实践')

                main_frag = solution_frags[0]
                item.question = main_frag.get('question', f'{main_tech}使用经验')
                item.answer = main_frag.get('answer', '')

                if code_frags:
                    item.answer += "\n\n**示例代码**：\n```" + code_frags[0]['lang'] + "\n" + code_frags[0]['content'] + "\n```"
            elif all_qa_frags:
                # 使用第一个QA作为内容
                main_frag = all_qa_frags[0]
                item.type = 'QA'
                item.question = main_frag.get('question', f'{main_tech}相关')
                item.answer = main_frag.get('answer', '')

                if code_frags:
                    item.answer += "\n\n**示例代码**：\n```" + code_frags[0]['lang'] + "\n" + code_frags[0]['content'] + "\n```"
            else:
                # 没有有价值的内容
                return None

        # 添加上下文
        for frag in context_frags[:2]:  # 最多取2个上下文
            if frag.get('type') == 'qa':
                item.context.append(frag.get('answer', ''))

        item.source_fragments = fragments
        return item

    def _extract_problem_summary(self, problem_text: str) -> str:
        """提取问题摘要"""
        # 提取关键错误信息
        for pattern in PROBLEM_PATTERNS:
            match = re.search(rf'.{{0,20}}{pattern}.{{0,30}}', problem_text, re.IGNORECASE)
            if match:
                return match.group(0).strip()

        # 如果没有匹配到，返回前30个字符
        return problem_text[:30] + "..." if len(problem_text) > 30 else problem_text

    def _deduplicate_text(self, text: str) -> str:
        """去除重复文本"""
        sentences = re.split(r'[。！？\n]', text)
        seen = set()
        unique = []
        for sent in sentences:
            sent = sent.strip()
            if sent and sent not in seen:
                seen.add(sent)
                unique.append(sent)
        return '。'.join(unique)

    def _is_valuable(self, item: KnowledgeItem) -> bool:
        """价值判断 - 平衡质量和数量"""
        # 1. 必须包含实质内容
        if not item.question or (not item.answer and not item.solution):
            return False

        # 2. 过滤寒暄
        content = item.question + " " + item.answer + " " + item.solution
        if any(t in content for t in TRIVIAL_WORDS) and len(content) < 50:
            return False

        # 3. 故障排除类型：必须有问题和解决方案
        if item.type == 'Troubleshooting':
            if not item.problem or not item.solution:
                return False
            if len(item.solution) < 10:  # 降低门槛
                item.needs_review = True
            item.confidence = 0.9 if len(item.solution) >= 20 else 0.75
            return True

        # 4. 架构决策类型：必须有决策内容
        if item.type == 'Decision':
            if not item.solution:
                return False
            item.confidence = 0.85
            return True

        # 5. 最佳实践类型：必须有具体做法
        if item.type == 'BestPractice':
            if len(item.answer) < 20:  # 降低门槛
                return False
            # 检查是否包含具体步骤或代码
            has_code = '```' in item.answer
            has_steps = any(re.search(r'\d+[、.]', item.answer) for _ in range(1))
            if not has_code and not has_steps:
                item.needs_review = True
            item.confidence = 0.75 if (has_code or has_steps) else 0.65
            return True

        # 6. 普通QA：降低门槛，但标记低质量内容
        if len(item.answer) < 20:
            return False

        # 检查是否包含技术关键词
        has_tech = bool(item.tags)
        has_detail = len(item.answer) > 50 or '```' in item.answer

        if not has_tech:
            item.needs_review = True
            item.confidence = 0.5
        elif not has_detail:
            item.needs_review = True
            item.confidence = 0.6
        else:
            item.confidence = 0.7

        return True

    def _enrich_item(self, item: KnowledgeItem):
        """添加元数据、标签和分类"""
        content = f"{item.question} {item.answer} {item.solution}"

        # 提取所有技术标签
        for category, tools in TECH_STACK_KEYWORDS.items():
            for tool in tools:
                if tool.lower() in content.lower():
                    item.tags.add(tool)
                    item.tags.add(category)

        # 根据内容添加分类
        if any(re.search(p, content) for p in PROBLEM_PATTERNS):
            item.categories.add('故障排除')
        if any(re.search(p, content) for p in DECISION_PATTERNS):
            item.categories.add('架构决策')
        if '```' in content:
            item.categories.add('代码片段')

        # 如果没有分类，标记为待审核
        if not item.categories:
            item.categories.add('未分类')
            item.needs_review = True

    def save(self, output_dir: Optional[str] = None, min_confidence: float = 0.8, project_name: Optional[str] = None):
        """保存知识并尝试组织

        Args:
            output_dir: 输出目录
            min_confidence: 最小置信度阈值，低于此值的知识不会被保存（默认0.8）
            project_name: 项目名称，如果提供则保存到项目知识库
        """
        if output_dir is None:
            output_dir = get_knowledge_base_dir()

        # 根据项目名称调整输出目录
        if project_name:
            output_dir = os.path.join(output_dir, 'projects', project_name)
            print(f"📁 使用项目知识库: {project_name}")

        os.makedirs(output_dir, exist_ok=True)

        # 过滤低置信度知识
        filtered_items = [item for item in self.knowledge_items if item.get('confidence', 0) >= min_confidence]
        filtered_count = len(self.knowledge_items) - len(filtered_items)

        if filtered_count > 0:
            print(f"📝 置信度低于 {min_confidence} 的知识已过滤: {filtered_count} 条")

        if not filtered_items:
            print("⚠️ 没有符合置信度要求的知识需要保存")
            return

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'knowledge_dump_{timestamp}.json'
        filepath = os.path.join(output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(filtered_items, f, ensure_ascii=False, indent=2)

        print(f"✅ 已保存 {len(filtered_items)} 条知识到 {filepath}")

        # 统计信息
        review_count = sum(1 for item in filtered_items if item.get('needs_review'))
        if review_count > 0:
            print(f"⚠️ 其中 {review_count} 条知识标记为需要人工审核")

        # 尝试调用组织器
        try:
            from knowledge_organizer import organize_knowledge
            organize_knowledge(filtered_items, output_dir)
        except ImportError:
            print("⚠️ 未找到 knowledge_organizer 模块，跳过自动组织步骤。")
        except Exception as e:
            print(f"⚠️ 组织知识库时出错：{e}")

    def save_project_knowledge(self, project_name: str, problem: str, solution: str,
                               output_dir: Optional[str] = None, tags: Optional[List[str]] = None):
        """保存项目对话中的问题和解决方法到项目知识库

        Args:
            project_name: 项目名称
            problem: 问题描述
            solution: 解决方法
            output_dir: 输出目录
            tags: 标签列表
        """
        if output_dir is None:
            output_dir = get_knowledge_base_dir()

        # 项目知识库目录
        project_dir = os.path.join(output_dir, 'projects', project_name)
        os.makedirs(project_dir, exist_ok=True)

        # 创建知识条目
        item = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'type': 'ProjectIssue',
            'question': problem,
            'answer': solution,
            'categories': ['项目问题', project_name],
            'tags': tags or [],
            'confidence': 0.9,  # 项目问题默认高置信度
            'project': project_name
        }

        # 保存到项目知识库文件
        project_knowledge_file = os.path.join(project_dir, 'project_knowledge.json')

        # 加载现有知识
        existing_items = []
        if os.path.exists(project_knowledge_file):
            try:
                with open(project_knowledge_file, 'r', encoding='utf-8') as f:
                    existing_items = json.load(f)
            except:
                existing_items = []

        # 添加新条目
        existing_items.append(item)

        # 保存
        with open(project_knowledge_file, 'w', encoding='utf-8') as f:
            json.dump(existing_items, f, ensure_ascii=False, indent=2)

        print(f"✅ 已保存项目问题到 {project_name} 知识库: {problem[:50]}...")

        # 尝试更新项目知识库HTML
        try:
            self._update_project_html(project_dir, project_name, existing_items)
        except Exception as e:
            print(f"⚠️ 更新项目知识库HTML时出错：{e}")

    def _update_project_html(self, project_dir: str, project_name: str, items: List[Dict]):
        """更新项目知识库的HTML页面"""
        html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name} - 项目知识库</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 0.5rem;
        }}
        .knowledge-item {{
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .knowledge-item h3 {{
            margin-top: 0;
            color: #2196F3;
        }}
        .problem {{
            background-color: #ffebee;
            border-left: 4px solid #f44336;
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 4px;
        }}
        .solution {{
            background-color: #e8f5e9;
            border-left: 4px solid #4CAF50;
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 4px;
        }}
        .meta {{
            font-size: 0.85rem;
            color: #666;
            margin-top: 0.5rem;
        }}
        .tag {{
            display: inline-block;
            background-color: #e3f2fd;
            color: #1976d2;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            margin-right: 0.5rem;
            font-size: 0.8rem;
        }}
    </style>
</head>
<body>
    <h1>📁 {project_name} - 项目知识库</h1>
    <p>共记录 {len(items)} 个问题及解决方案</p>
'''

        for item in items:
            html_content += f'''
    <div class="knowledge-item">
        <h3>📝 {item['question'][:80]}{'...' if len(item['question']) > 80 else ''}</h3>
        <div class="problem">
            <strong>问题：</strong><br>
            {item['question']}
        </div>
        <div class="solution">
            <strong>解决方案：</strong><br>
            {item['answer']}
        </div>
        <div class="meta">
            <span>📅 {item['timestamp'][:10]}</span>
            {' '.join([f'<span class="tag">{tag}</span>' for tag in item.get('tags', [])])}
        </div>
    </div>
'''

        html_content += '''
</body>
</html>
'''

        html_path = os.path.join(project_dir, 'index.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"📄 已更新项目知识库页面: {html_path}")


# --- 主程序入口 ---
if __name__ == '__main__':
    # 测试数据，包含多种类型
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

    collector = KnowledgeCollector()
    results = collector.collect(sample_data)
    collector.save()

    # 打印摘要
    print("\n" + "=" * 60)
    print("知识提取摘要")
    print("=" * 60)

    for item in results:
        print(f"\n[{item['source_type']}] {item['question']}")
        print(f"  分类：{', '.join(item['categories'])}")
        print(f"  标签：{', '.join(item['tags'][:5])}")
        print(f"  置信度：{item['confidence']}")
        if item['needs_review']:
            print(f"  ⚠️ 需要审核")
        print("-" * 60)
