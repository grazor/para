#!/usr/bin/env python3

import datetime as dt
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from jinja2 import Environment, FileSystemLoader

DATE_FORMAT = "%d.%m.%Y"

logging.basicConfig(level=logging.DEBUG)
script_dir = Path(__file__).parent
env = Environment(loader=FileSystemLoader(script_dir.joinpath('templates/').as_posix()))


@dataclass
class Entry:
    path: Path
    name: str
    heading: str


@dataclass
class Category:
    path: Path = None
    level: int = 0
    name: str = ""
    goal: str = ""
    created_at: dt.date = None
    due_to: dt.date = None
    children: Iterable = field(default_factory=list)
    entries: Iterable[Entry] = field(default_factory=list)

    @property
    def is_empty(self):
        return not self.entries and not self.children

    @property
    def index(self):
        return self.path.joinpath('index.md')

    def update_from_about(self, about):
        with about.open("r") as f:
            lines = f.readlines()
            name = next(filter(lambda l: l.startswith("Name:"), lines), None)
            goal = next(filter(lambda l: l.startswith("Goal:"), lines), None)
            created_at = next(filter(lambda l: l.startswith("Created:"), lines), None)
            due_to = next(filter(lambda l: l.startswith("Due:"), lines), None)

        self.name = name and name.split('Name:')[1].strip() or self.name
        self.goal = goal and goal.split('Goal:')[1].strip() or self.goal
        if created_at:
            try:
                datestr = created_at.split('Created:')[1].strip()
                self.created_at = self.created_at or created_at and dt.datetime.strptime(datestr, DATE_FORMAT).date()
            except ValueError:
                logging.error(f"Failed to parse created_at date {datestr} from {about.as_posix()}")

        if due_to:
            try:
                datestr = due_to.split('Due:')[1].strip()
                self.due_to = self.due_to or due_to and dt.datetime.strptime(datestr, DATE_FORMAT).date()
            except ValueError:
                logging.error(f"Failed to parse due_to date {datestr} from {about.as_posix()}")


def render_template(template_name, dest, **kwargs):
    template = env.get_template(template_name)
    with dest.open('w') as f:
        f.write(template.render(**kwargs))


def build_index(root) -> None:
    categories = [root]

    while categories:
        category = categories.pop(0)

        for child in category.path.iterdir():
            if child.name.startswith('.') or child.name == 'index.md':
                continue

            if child.is_dir():
                subcategory = Category(path=child, level=category.level + 1, name=child.name)
                category.children.append(subcategory)
                categories.append(subcategory)
            elif child.name == "about.md":
                category.update_from_about(child)
            elif child.name.endswith('.md'):
                category.entries.append(Entry(path=child, name=child.name, heading=child.name))

        category.children = sorted(category.children, key=lambda child: child.name)
        category.entries = sorted(category.entries, key=lambda entry: entry.name)


if __name__ == "__main__":
    root = Category(path=Path("./"), level=0)
    build_index(root)

    render_template('root.md', root.index, root=root)
