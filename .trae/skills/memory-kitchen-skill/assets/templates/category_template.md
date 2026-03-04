# {{category_name}}

## 分类描述
{{category_description}}

## 知识条目

{% for item in knowledge_items %}
- [{{item.title}}]({{item.file_path}})
{% endfor %}

## 统计信息
- 知识条目数量：{{item_count}}
- 最后更新：{{last_updated}}
