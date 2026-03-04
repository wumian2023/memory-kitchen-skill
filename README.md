# Memory Kitchen Skill

自动记忆知识库技能，用于收集、整理、存储和检索知识，建立个人或项目知识库，实现知识的自动化积累和智能化应用。

## 功能特性

- **自动环境检测**：自动识别 Claude、Cursor、Qoder、Trae、Trae-CN 等不同的 AI 工具环境
- **跨项目共享**：知识库存储在用户目录下，支持跨项目共享知识
- **智能知识管理**：自动收集、整理、分类和检索知识
- **多维度检索**：支持关键词、标签、分类等多维度检索
- **知识关联**：建立知识之间的关联关系，形成知识网络

## 安装方法

### 方法 1：直接使用

将 `memory-kitchen-skill` 文件夹复制到您的 AI 工具的技能目录中：

- **Trae**: `~/.trae/skills/`
- **Trae-CN**: `~/.trae-cn/skills/`
- **Cursor**: `~/.cursor/skills/`
- **Claude**: `~/.claude/skills/`
- **Qoder**: `~/.qoder/skills/`

### 方法 2：从 GitHub 安装

```bash
git clone https://github.com/wumian2023/memory-kitchen-skill.git
cp -r memory-kitchen-skill/.trae/skills/memory-kitchen-skill ~/.trae/skills/
```

## 使用方法

### 调用技能

在对话中输入以下命令激活技能：

```
Skill: memory-kitchen-skill
```

### 自动环境检测

技能会自动检测当前运行的 AI 工具环境，并将知识库存储在对应的配置目录中：

| AI 工具 | 配置目录 | 知识库路径 |
|---------|---------|-------------|
| Claude | `~/.claude/` | `~/.claude/knowledge/` |
| Cursor | `~/.cursor/` | `~/.cursor/knowledge/` |
| Qoder | `~/.qoder/` | `~/.qoder/knowledge/` |
| Trae | `~/.trae/` | `~/.trae/knowledge/` |
| Trae-CN | `~/.trae-cn/` | `~/.trae-cn/knowledge/` |

### 手动指定环境

可以通过设置环境变量手动指定 AI 工具：

```bash
export AI_TOOL=claude  # Linux/Mac
set AI_TOOL=claude       # Windows PowerShell
```

## 知识库结构

```
~/.{ai-tool}/knowledge/    # 知识库根目录
  categories/                # 分类目录
    技术知识/                # 技术知识分类
      前端开发/              # 前端开发子分类
      后端开发/              # 后端开发子分类
      云原生/                # 云原生子分类
      数据库/                # 数据库子分类
      版本控制/              # 版本控制子分类
    项目知识/                # 项目知识分类
    问题解决方案/            # 问题解决方案分类
      教程/                  # 教程子分类
      故障排除/              # 故障排除子分类
    最佳实践/                # 最佳实践分类
  tags/                      # 标签索引目录
  index.md                   # 知识库索引文件
  recent-updates.md          # 最近更新文件
```

## 核心功能

### 1. 知识收集

自动从对话中收集有价值的信息和解决方案：

```python
from scripts.knowledge_collector import collect_knowledge, save_collected_knowledge

# 收集知识
knowledge_items = collect_knowledge(dialogue_history)

# 保存知识
save_collected_knowledge(knowledge_items)
```

### 2. 知识整理

智能整理和分类收集到的知识：

```python
from scripts.knowledge_organizer import organize_knowledge

# 整理知识
organize_knowledge(knowledge_items)
```

### 3. 知识检索

多维度检索知识库中的信息：

```python
from scripts.knowledge_retriever import (
    retrieve_knowledge,
    search_by_tags,
    search_by_category
)

# 关键词检索
results = retrieve_knowledge("Python 内存泄漏")

# 标签检索
results = search_by_tags(["Git", "代理"])

# 分类检索
results = search_by_category("技术知识 > 版本控制")
```

### 4. 知识更新

定期更新和维护知识库内容：

```python
from scripts.knowledge_updater import update_knowledge_base

# 更新知识库
update_knowledge_base()
```

## 使用场景

### 场景 1：收集技术解决方案

**用户输入**：如何解决 Python 中的内存泄漏问题？

**技能处理**：
1. 收集关于 Python 内存泄漏的解决方案
2. 将信息分类到 "技术知识 > Python > 性能优化" 类别
3. 存储到知识库中
4. 建立相关知识的关联

**输出**：已将 Python 内存泄漏解决方案存储到知识库中，您可以通过关键词 "Python 内存泄漏" 检索。

### 场景 2：检索已存储的知识

**用户输入**：我之前存储的关于 Docker 容器编排的信息在哪里？

**技能处理**：
1. 分析用户查询
2. 从知识库中检索相关信息
3. 整理和呈现检索结果

**输出**：找到了您之前存储的关于 Docker 容器编排的信息，包括 Kubernetes 基本概念、Docker Compose 使用方法等内容。

### 场景 3：更新知识库

**用户输入**：我有新的关于 React 18 的信息需要添加到知识库中。

**技能处理**：
1. 收集新的 React 18 相关信息
2. 检查知识库中是否已有相关内容
3. 更新或添加新的知识条目
4. 重新建立知识关联

**输出**：已成功更新知识库中的 React 18 相关内容，包括新的特性和最佳实践。

## 配置选项

### 知识库位置

默认情况下，技能会自动检测 AI 工具环境并使用对应的配置目录。如果需要自定义知识库位置，可以设置环境变量：

```bash
export MEMORY_KITCHEN_KB=/path/to/knowledge  # Linux/Mac
set MEMORY_KITCHEN_KB=D:\MyKnowledge          # Windows PowerShell
```

### 代理设置

如果需要使用代理访问网络资源，可以在脚本中配置代理：

```python
import os
os.environ['http_proxy'] = 'http://127.0.0.1:7897'
os.environ['https_proxy'] = 'http://127.0.0.1:7897'
```

## 最佳实践

1. **定期更新**：定期更新知识库，保持知识的时效性
2. **合理分类**：使用合理的分类体系，便于知识检索
3. **标签管理**：使用一致的标签命名规范
4. **备份知识库**：定期备份知识库到安全位置
5. **版本控制**：可以使用 Git 对知识库进行版本控制

## 故障排除

### 问题 1：无法创建知识库目录

**解决方案**：手动创建知识库目录

```bash
# Windows PowerShell
New-Item -ItemType Directory -Path "$env:USERPROFILE\.trae-cn\knowledge\categories" -Force
New-Item -ItemType Directory -Path "$env:USERPROFILE\.trae-cn\knowledge\tags" -Force

# Linux/Mac
mkdir -p ~/.trae-cn/knowledge/categories
mkdir -p ~/.trae-cn/knowledge/tags
```

### 问题 2：环境检测错误

**解决方案**：手动设置 AI_TOOL 环境变量

```bash
export AI_TOOL=trae-cn  # Linux/Mac
set AI_TOOL=trae-cn       # Windows PowerShell
```

### 问题 3：知识库为空

**解决方案**：检查知识库路径是否正确，或手动添加知识条目

```python
from scripts.knowledge_organizer import generate_knowledge_file

# 手动创建知识条目
knowledge_item = {
    "id": "unique-id",
    "question": "问题",
    "answer": "答案",
    "timestamp": "2026-03-04T12:00:00",
    "tags": ["标签1", "标签2"],
    "categories": ["分类1", "分类2"]
}

generate_knowledge_file(knowledge_item, knowledge_base_dir)
```

## 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

MIT License

## 联系方式

- GitHub: https://github.com/wumian2023/memory-kitchen-skill
- Issues: https://github.com/wumian2023/memory-kitchen-skill/issues

## 致谢

感谢所有为本项目做出贡献的开发者！
