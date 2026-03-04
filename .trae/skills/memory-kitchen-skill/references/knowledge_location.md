# 知识库位置配置

## 默认位置

知识库默认存储在用户目录下的 `.trae-cn/knowledge` 目录中：

- **Windows**: `C:\Users\Administrator\.trae-cn\knowledge`
- **Linux/Mac**: `~/.trae-cn/knowledge`

## 手动创建知识库

由于安全限制，技能无法自动在用户目录下创建文件。请手动创建知识库目录：

### Windows

1. 打开文件资源管理器
2. 导航到 `C:\Users\Administrator\`
3. 创建 `.trae-cn` 文件夹
4. 在 `.trae-cn` 文件夹中创建 `knowledge` 文件夹
5. 在 `knowledge` 文件夹中创建以下子文件夹：
   - `categories`
   - `tags`

或者使用 PowerShell 命令：
```powershell
New-Item -ItemType Directory -Path "$env:USERPROFILE\.trae-cn\knowledge\categories" -Force
New-Item -ItemType Directory -Path "$env:USERPROFILE\.trae-cn\knowledge\tags" -Force
```

### Linux/Mac

```bash
mkdir -p ~/.trae-cn/knowledge/categories
mkdir -p ~/.trae-cn/knowledge/tags
```

## 目录结构

创建完成后，知识库目录结构如下：

```
~/.trae-cn/knowledge/        # 知识库根目录
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

## 跨项目共享

由于知识库存储在用户目录下，所有项目都可以访问和共享同一个知识库：

1. **项目 A** 创建的知识，**项目 B** 可以读取
2. 避免知识碎片化，实现知识的积累和复用
3. 统一管理个人知识资产

## 备份和迁移

### 备份知识库

```bash
# Windows
Copy-Item -Path "$env:USERPROFILE\.trae-cn\knowledge" -Destination "D:\Backup\knowledge-backup" -Recurse

# Linux/Mac
cp -r ~/.trae-cn/knowledge ~/backup/knowledge-backup
```

### 迁移知识库

```bash
# 导出
zip -r knowledge-backup.zip ~/.trae-cn/knowledge

# 导入到新环境
unzip knowledge-backup.zip -d ~/
```

## 配置自定义位置（高级）

如果需要自定义知识库位置，可以设置环境变量：

### Windows
```powershell
[Environment]::SetEnvironmentVariable("MEMORY_KITCHEN_KB", "D:\MyKnowledge", "User")
```

### Linux/Mac
```bash
echo 'export MEMORY_KITCHEN_KB=/path/to/knowledge' >> ~/.bashrc
source ~/.bashrc
```

然后在脚本中读取环境变量：
```python
import os

knowledge_base_dir = os.environ.get('MEMORY_KITCHEN_KB', os.path.expanduser('~/.trae-cn/knowledge'))
```

## 注意事项

1. **权限问题**：确保有权限在用户目录下创建文件夹
2. **磁盘空间**：定期检查知识库的磁盘使用情况
3. **定期备份**：建议定期备份知识库到安全位置
4. **版本控制**：可以使用 Git 对知识库进行版本控制
