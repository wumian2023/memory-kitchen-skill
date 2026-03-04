---
id: git-proxy-config-20260304
title: Git代理配置问题及解决方案
tags: [Git, 代理, 配置, 网络, 问题解决]
categories: [技术知识 > 版本控制, 问题解决方案 > 故障排除]
created: 2026-03-04T12:47:00
updated: 2026-03-04T12:47:00
---

# Git代理配置问题及解决方案

## 问题描述
在推送代码到 GitHub 时遇到网络连接问题，Git 无法连接到远程仓库。错误信息显示：
- `Failed to connect to ghproxy.com port 443`
- `TLS connect error: error:00000000:lib(0)::reason(0)`

## 问题原因
系统中配置了 Git URL 重写规则，将 GitHub 的 URL 自动重定向到各种代理服务器（ghproxy.com、github.com.cnpmjs.org、hub.fastgit.xyz等），但这些代理服务器不可用或已失效。

## 解决方法

### 1. 查看当前的 Git 配置
```bash
# 查看全局配置
git config --global --list

# 查看本地配置
git config --local --list
```

### 2. 移除 URL 重写规则
```bash
# 移除 ghproxy.com 重写规则
git config --global --unset url.https://ghproxy.com/https://github.com/.insteadof

# 移除 github.com.cnpmjs.org 重写规则
git config --global --unset url.https://github.com.cnpmjs.org/.insteadof

# 移除 hub.fastgit.xyz 重写规则
git config --global --unset url.https://hub.fastgit.xyz/.insteadof

# 移除其他可能的重写规则
git config --global --unset url.https://github.com/.insteadof
```

### 3. 配置本地代理（可选）
如果需要使用代理，可以配置本地代理：
```bash
# 配置 HTTP 代理
git config http.proxy http://127.0.0.1:7897

# 配置 HTTPS 代理
git config https.proxy http://127.0.0.1:7897
```

### 4. 验证配置
```bash
# 检查远程仓库 URL
git remote -v

# 测试连接
git push -u origin master
```

## 常用 Git 代理配置命令

### 设置代理
```bash
# HTTP 代理
git config --global http.proxy http://proxy.example.com:8080
git config --global https.proxy http://proxy.example.com:8080

# SOCKS5 代理
git config --global http.proxy socks5://127.0.0.1:1080
git config --global https.proxy socks5://127.0.0.1:1080
```

### 取消代理
```bash
git config --global --unset http.proxy
git config --global --unset https.proxy
```

### 查看代理配置
```bash
git config --global --get http.proxy
git config --global --get https.proxy
```

## 最佳实践

1. **避免使用第三方代理**：尽量直接连接 GitHub，避免使用可能失效的第三方代理
2. **使用本地代理工具**：如需代理，使用本地代理工具（如 Clash、V2Ray 等）
3. **定期清理配置**：定期检查和清理 Git 的全局配置，避免累积无效配置
4. **配置备份**：在修改配置前备份原有配置，便于恢复

## 相关命令

```bash
# 初始化 Git 仓库
git init

# 添加远程仓库
git remote add origin https://github.com/username/repo.git

# 修改远程仓库 URL
git remote set-url origin https://github.com/username/repo.git

# 推送代码
git push -u origin master
```

## 标签
- Git
- 代理
- 配置
- 网络
- 问题解决

## 分类
- 技术知识 > 版本控制
- 问题解决方案 > 故障排除

## 创建时间
2026-03-04T12:47:00

## 更新时间
2026-03-04T12:47:00

## 状态
正常
