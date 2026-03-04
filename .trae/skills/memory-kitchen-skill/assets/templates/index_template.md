# 知识库索引

## 概述
{{overview}}

## 分类目录

{% for category in categories %}
### {{category.name}}
{{category.description}}
{% endfor %}

## 知识统计
- 总知识条目：{{total_items}}
- 总分类数：{{total_categories}}
- 总标签数：{{total_tags}}
- 最后更新：{{last_updated}}

## 最近添加

{% for item in recent_items %}
- [{{item.title}}]({{item.file_path}}) - {{item.created}}
{% endfor %}

## 热门知识

{% for item in popular_items %}
- [{{item.title}}]({{item.file_path}}) - 使用次数：{{item.usage_count}}
{% endfor %}
