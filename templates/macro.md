{%- macro render_entry(entry) -%}
* {% if entry.complete is none %}{% elif entry.complete %}[X] {% else %}[ ] {% endif %}[{{ entry.name }}]({{ entry.relative_path }}){% if entry.short_description %}: {{ entry.short_description }}{% endif -%}
{%- endmacro -%}

{%- macro render_category(category, current) -%}
* [{{ category.name }}]({{ category.path.relative_to(current.path) }}/index.md){% if category.short_description %}: {{ category.short_description }}{% endif -%}
{%- endmacro -%}
