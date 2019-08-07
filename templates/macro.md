{%- macro render_entry(entry, current=None) -%}
* {% if entry.complete is none %}{% elif entry.complete %}[X] {% else %}[ ] {% endif %}[{{ entry.name }}]({% if current %}{{ entry.path.relative_to(current.path) }}{% else %}{{ entry.relative_path }}{% endif %}){% if entry.short_description %}: {{ entry.short_description }}{% endif -%}
{%- endmacro -%}

{%- macro render_category(category, current) -%}
* [{{ category.name }}]({{ category.path.relative_to(current.path) }}/index.md){% if category.short_description %}: {{ category.short_description }}{% endif -%}
{%- endmacro -%}
