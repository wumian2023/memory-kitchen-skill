---
description: 自动记忆知识库技能，用于收集、整理、存储和检索知识，建立个人或项目知识库，实现知识的自动化积累和智能化应用。当用户需要管理知识、存储解决方案、建立知识库时使用此技能。知识库存储在用户目录下的 .trae-cn/knowledge 中，支持跨项目共享。
name: memory-kitchen-skill
---

# memory-kitchen-skill

## Overview

自动记忆知识库技能是一个专注于知识管理的智能技能，旨在帮助用户建立和管理个人或项目知识库。它能够自动收集对话中的重要信息，智能整理和分类知识，结构化存储知识，并提供快速检索和提取功能。

## 知识库位置

技能会自动检测当前运行的 AI 工具环境，并将知识库存储在对应的配置目录中：

| AI 工具 | 配置目录 | 知识库路径 |
|---------|---------|-------------|
| Claude | `~/.claude/` | `~/.claude/knowledge/` |
| Cursor | `~/.cursor/` | `~/.cursor/knowledge/` |
| Qoder | `~/.qoder/` | `~/.qoder/knowledge/` |
| Trae | `~/.trae/` | `~/.trae/knowledge/` |
| Trae-CN | `~/.trae-cn/` | `~/.trae-cn/knowledge/` |

这样可以实现跨项目共享知识，避免知识碎片化。

### 手动指定环境

如果自动检测不准确，可以通过设置环境变量手动指定 AI 工具：

```bash
export AI_TOOL=claude  # Linux/Mac
set AI_TOOL=claude       # Windows PowerShell
```

## When to Use

使用此技能当您需要：
- 建立个人或项目知识库
- 存储和管理技术解决方案
- 收集和整理学习资料
- 快速检索和提取已存储的知识
- 建立知识之间的关联关系

## Workflow

1. **信息收集**：监控对话内容，识别和提取有价值的信息
2. **信息处理**：对收集到的信息进行分析、分类和结构化处理
3. **知识存储**：将处理后的知识存储到知识库中
4. **知识索引**：为存储的知识建立索引，便于快速检索
5. **知识检索**：根据用户需求，从知识库中检索相关信息
6. **知识更新**：定期更新和维护知识库内容

## Resources

### Scripts

- `scripts/knowledge_collector.py`：自动收集对话中的重要信息
- `scripts/knowledge_organizer.py`：智能整理和分类知识
- `scripts/knowledge_retriever.py`：快速检索和提取知识库中的信息
- `scripts/knowledge_updater.py`：更新和维护知识库内容

### References

- `references/knowledge_location.md`：知识库位置配置和手动创建指南
- `references/knowledge_structure.md`：知识库结构和组织方式
- `references/retrieval_strategies.md`：知识检索策略和方法
- `references/best_practices.md`：知识库管理最佳实践

### Assets

- `assets/templates/knowledge_template.md`：知识条目模板
- `assets/templates/category_template.md`：分类目录模板
- `assets/templates/index_template.md`：知识库索引模板

## Examples

### 示例 1：收集技术解决方案

**用户输入**：如何解决 Python 中的内存泄漏问题？

**技能处理**：
1. 收集关于 Python 内存泄漏的解决方案
2. 将信息分类到 "技术知识 > Python > 性能优化" 类别
3. 存储到知识库中
4. 建立相关知识的关联

**输出**：已将 Python 内存泄漏解决方案存储到知识库中，您可以通过关键词 "Python 内存泄漏" 检索。

### 示例 2：检索已存储的知识

**用户输入**：我之前存储的关于 Docker 容器编排的信息在哪里？

**技能处理**：
1. 分析用户查询
2. 从知识库中检索相关信息
3. 整理和呈现检索结果

**输出**：找到了您之前存储的关于 Docker 容器编排的信息，包括 Kubernetes 基本概念、Docker Compose 使用方法等内容。

### 示例 3：更新知识库

**用户输入**：我有新的关于 React 18 的信息需要添加到知识库中。

**技能处理**：
1. 收集新的 React 18 相关信息
2. 检查知识库中是否已有相关内容
3. 更新或添加新的知识条目
4. 重新建立知识关联

**输出**：已成功更新知识库中的 React 18 相关内容，包括新的特性和最佳实践。
