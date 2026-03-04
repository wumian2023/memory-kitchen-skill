---
id: {{id}}
title: {{title}}
tags: {{tags}}
categories: {{categories}}
created: {{created}}
updated: {{updated}}
---

# {{title}}

## 答案
{{answer}}

## 标签
{% for tag in tags %}
- {{tag}}
{% endfor %}

## 分类
{% for category in categories %}
- {{category}}
{% endfor %}

## 创建时间
{{created}}

## 更新时间
{{updated}}

## 状态
正常
