import logging
from configparser import ConfigParser
from dataclasses import dataclass, field
from itertools import zip_longest
from pathlib import Path
from typing import List

from jinja2 import Environment, FileSystemLoader

from para.paths import SNIPPETS_DIR

env = Environment(loader=FileSystemLoader(SNIPPETS_DIR.as_posix()))

PARAMS = ("name",)


def split_words(src: str, delimiter: str = ","):
    return list(filter(bool, map(lambda x: x.strip().lower(), src.split(delimiter))))


@dataclass
class Snippet:
    name: str = ""
    config_path: Path = None
    prototype_path: Path = None
    required_args: List[str] = field(default_factory=list)
    optional_args: List[str] = field(default_factory=list)
    destination_id: str = ""

    @property
    def is_category(self):
        return self.prototype_path.is_dir()

    def _render_snippet_template(self, template_path, dest, params):
        template = env.get_template(str(template_path.relative_to(SNIPPETS_DIR)))
        with dest.joinpath(template_path.name).open("w") as f:
            f.write(template.render(**params))

    def create(self, root, args):
        dest_node = root.INDEX[self.destination_id or args.pop(0)]
        params_list = self.required_args + self.optional_args
        params = dict(zip(params_list, args))
        if not set(self.required_args).issubset(set(params.keys())):
            logging.error(
                "Missing required params: {}".format(", ".join(set(self.required_args).difference(set(params.keys()))))
            )
            logging.info(
                "Params sequence: {} [{}]".format(", ".join(self.required_args), ", ".join(self.optional_args))
            )
            return
        if self.is_category:
            dest_node = dest_node.create_subcategory(params["name"])
            templates = self.prototype_path.glob("*.md")
        else:
            templates = self.prototype_path

        for template in templates:
            self._render_snippet_template(template, dest_node.path, params)

    def read_config(self):
        config = ConfigParser()
        config.read(self.config_path)
        section = config["Snippet"]
        self.prototype_path = SNIPPETS_DIR.joinpath(section["prototype"])
        self.required_args = list(PARAMS) + split_words(section.get("required", ""))
        self.optional_args = split_words(section.get("optional", ""))
        self.destination_id = section.get("destination_id", "")

    @classmethod
    def load(cls, name):
        snippet = Snippet(name=name, config_path=SNIPPETS_DIR.joinpath(f"{name}.ini"))
        snippet.read_config()
        return snippet


class SnippetMixin:
    def create_from_snippet(self, snippet_name, args):
        snippet = Snippet.load(snippet_name)
        snippet.create(self, args)
