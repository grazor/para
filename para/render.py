from jinja2 import Environment, FileSystemLoader

from para.paths import TEMPLATES_DIR

env = Environment(loader=FileSystemLoader(TEMPLATES_DIR.as_posix()))


def render_template(template_name, dest, **kwargs):
    template = env.get_template(template_name)
    with dest.open("w") as f:
        f.write(template.render(**kwargs))


class RenderMixin:
    def render_indexes(self):
        subcategories = [self]
        while subcategories:
            category = subcategories.pop(0)
            subcategories.extend(category.subcategories)
            template_name = "category.md" if category.level < 2 else "subcategory.md"
            render_template(template_name, category.index, root=category)

    def remove_indexes(self):
        subcategories = [self]
        while subcategories:
            category = subcategories.pop(0)
            subcategories.extend(category.subcategories)
            if category.index.exists() and not category.index.is_dir():
                category.index.unlink()
