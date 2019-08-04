# Para
{% for category in root.children %}{% if not category.is_empty %}
## {{ category.name }}

{% if category.goal %}{{ category.goal }}{% endif %}
{% for child in category.children %}
* [{{ child.name }}]({{ child.index.as_posix() }}){% if child.goal %}: {{child.goal}}{% endif %}
{% endfor %}
{% endif %}{% endfor %}
