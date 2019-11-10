{% from 'macro.md' import render_category, render_entry -%}
{% if root.level > 0 -%}
{%- for breadcumb in root.breadcumbs -%}
[{{ breadcumb.name }}]({% for i in range(root.level - loop.index0) %}../{% endfor %}index.md){% if not loop.last %} ⮁ {% endif %}
{% endfor %}
{% endif -%}
# {{ root.name }}

{% if root.description -%}
{{ root.description }}

{% endif -%}
{% for category in root.subcategories -%}
{% if not category.is_empty -%}
## [{{ category.name }}]({{ category.relative_path.name }}/index.md)

{% if category.description -%}
{{ category.description }}

{% endif -%}
{% for child in category.subcategories -%}{{ render_category(child, root) }}
{% endfor %}
{% for entry in category.entries %}{{ render_entry(entry, category.parent) }}
{% endfor %}
{% endif -%}{% endfor %}
{% if root.level >= 0 -%}
{% for entry in root.entries %}{{ render_entry(entry) }}
{% endfor %}
{% endif -%}

