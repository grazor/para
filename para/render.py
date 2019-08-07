from pathlib import Path

from jinja2 import Environment, FileSystemLoader

script_dir = Path(__file__).parent.parent
env = Environment(loader=FileSystemLoader(script_dir.joinpath("templates/").as_posix()))


def render_template(template_name, dest, **kwargs):
    template = env.get_template(template_name)
    with dest.open("w") as f:
        f.write(template.render(**kwargs))

