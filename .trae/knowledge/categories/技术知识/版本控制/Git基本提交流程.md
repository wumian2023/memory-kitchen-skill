---
id: git-basic-workflow-20260304
title: Git基本提交流程
tags: [Git, 提交, 推送, 工作流程, 版本控制]
categories: [技术知识 > 版本控制, 基础知识 > 教程]
created: 2026-03-04T12:48:00
updated: 2026-03-04T12:48:00
---

# Git基本提交流程

## 概述
本文档介绍 Git 的基本提交流程，包括初始化仓库、添加文件、提交更改和推送到远程仓库的完整步骤。

## 完整流程

### 1. 初始化 Git 仓库
```bash
# 在项目目录中初始化 Git 仓库
git init
```

### 2. 配置用户信息
```bash
# 配置用户名
git config user.name "Your Name"

# 配置邮箱
git config user.email "your.email@example.com"

# 或者配置全局用户信息
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 3. 添加文件到暂存区
```bash
# 添加所有文件
git add .

# 或者添加特定文件
git add filename.txt
```

### 4. 提交更改
```bash
# 提交更改并添加提交信息
git commit -m "提交信息"

# 示例
git commit -m "feat: 添加新功能"
git commit -m "fix: 修复bug"
git commit -m "docs: 更新文档"
```

### 5. 添加远程仓库
```bash
# 添加远程仓库
git remote add origin https://github.com/username/repo.git

# 查看远程仓库
git remote -v
```

### 6. 推送到远程仓库
```bash
# 推送到远程仓库并设置上游分支
git push -u origin master

# 或者推送到 main 分支
git push -u origin main

# 后续推送可以直接使用
git push
```

## 常用命令速查

### 仓库操作
```bash
git init                    # 初始化仓库
git clone <url>            # 克隆仓库
git status                 # 查看状态
git log                    # 查看提交历史
```

### 文件操作
```bash
git add <file>             # 添加文件到暂存区
git add .                  # 添加所有文件
git rm <file>              # 删除文件
git mv <old> <new>         # 重命名文件
```

### 提交操作
```bash
git commit -m "message"    # 提交更改
git commit -am "message"   # 添加并提交
git commit --amend         # 修改最后一次提交
```

### 分支操作
```bash
git branch                 # 查看分支
git branch <name>          # 创建分支
git checkout <branch>      # 切换分支
git checkout -b <branch>   # 创建并切换分支
git merge <branch>         # 合并分支
```

### 远程操作
```bash
git remote -v              # 查看远程仓库
git remote add <name> <url> # 添加远程仓库
git fetch                  # 获取远程更新
git pull                   # 拉取远程更新
git push                   # 推送到远程仓库
```

## 提交信息规范

### 格式
```
<type>: <subject>

<body>

<footer>
```

### 类型（type）
- **feat**: 新功能
- **fix**: 修复bug
- **docs**: 文档更新
- **style**: 代码格式调整
- **refactor**: 重构代码
- **test**: 测试相关
- **chore**: 构建过程或辅助工具的变动

### 示例
```bash
git commit -m "feat: 添加用户登录功能"
git commit -m "fix: 修复内存泄漏问题"
git commit -m "docs: 更新API文档"
git commit -m "refactor: 优化数据库查询"
```

## 工作流程示例

### 场景：提交新项目到 GitHub

```bash
# 1. 进入项目目录
cd my-project

# 2. 初始化 Git 仓库
git init

# 3. 配置用户信息
git config user.name "Your Name"
git config user.email "your.email@example.com"

# 4. 添加所有文件
git add .

# 5. 提交更改
git commit -m "initial commit"

# 6. 添加远程仓库
git remote add origin https://github.com/username/my-project.git

# 7. 推送到远程仓库
git push -u origin master
```

## 注意事项

1. **首次提交前配置用户信息**：确保在首次提交前配置好用户名和邮箱
2. **编写有意义的提交信息**：提交信息应该清晰描述更改内容
3. **定期提交**：不要积累太多更改后再提交，保持提交粒度适中
4. **推送前检查**：推送前使用 `git status` 和 `git log` 检查更改
5. **处理冲突**：如果遇到冲突，先解决冲突再提交

## 常见问题

### Q: 提交时提示 "Author identity unknown"
**A**: 需要配置用户信息
```bash
git config user.email "your.email@example.com"
git config user.name "Your Name"
```

### Q: 推送时提示 "fatal: unable to access"
**A**: 检查网络连接或代理配置，参考 "Git代理配置问题及解决方案"

### Q: 如何修改最后一次提交？
**A**: 使用 `--amend` 选项
```bash
git commit --amend -m "新的提交信息"
```

## 标签
- Git
- 提交
- 推送
- 工作流程
- 版本控制

## 分类
- 技术知识 > 版本控制
- 基础知识 > 教程

## 创建时间
2026-03-04T12:48:00

## 更新时间
2026-03-04T12:48:00

## 状态
正常
