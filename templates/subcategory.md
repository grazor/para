{% from 'macro.md' import render_entry -%}

{%- for breadcumb in root.breadcumbs -%}
[{{ breadcumb.name }}]({% for i in range(root.level - loop.index0) %}../{% endfor %}index.md){% if not loop.last %} ⮁ {% endif %}
{%- endfor %}

# {{ root.name }}

{% if root.description -%}
{{ root.description }}

{% endif -%}

{% for entry in root.incompleted -%}{{ render_entry(entry) }}
{% endfor %}
{% for entry in root.nonactionable -%}{{ render_entry(entry) }}
{% endfor %}
{% if root.completed -%}
- - -

{% for entry in root.completed -%}
{{ render_entry(entry) }}
{% endfor %}
{% endif -%}

{% for category in root.subcategories -%}
{% if not category.is_empty -%}
## [{{ category.name }}]({{ category.path.name }}/index.md)

{% if category.description -%}
{{ category.description }}

{% endif -%}

{% for child in category.subcategories -%}{{ render_category(child, category) }}
{% endfor %}
{% endif -%}{% endfor %}

{% for ref in root.referencable -%}{{ render_entry(ref) }}
{% endfor %}
