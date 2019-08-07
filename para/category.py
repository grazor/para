import datetime as dt
import logging
import re
import string
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, TypeVar

from para.render import render_template

T = TypeVar("Category")


DATE_FORMAT = "%d.%m.%Y"
SPECIAL_CHARS = set(string.punctuation + string.digits + string.whitespace)
DESCRIPTION_FORBIDDEN_FIRST_CHARS = SPECIAL_CHARS - set("[]()")

ALLOWED_EXTENSIONS = [".html", ".pdf", ".csv", ".txt"]

REGEX_CHECKBOX = re.compile(r"\[[xX_\s]?\]")

logging.basicConfig(level=logging.DEBUG)


@dataclass
class Category:
    path: Path = None
    level: int = 0
    name: str = ""
    short_description: str = ""
    description: str = ""
    created_at: dt.date = None
    due_to: dt.date = None
    complete: bool = None
    children: Iterable = field(default_factory=list)
    parent: T = None

    @property
    def is_empty(self):
        return not self.about.exists()

    @property
    def index(self):
        return self.path.joinpath("index.md")

    @property
    def about(self):
        return self.path.joinpath("about.md")

    @property
    def is_category(self):
        return self.path.is_dir()

    @property
    def is_entry(self):
        return not self.path.is_dir() and self.path.suffix == ".md"

    @property
    def is_referencable(self):
        return not self.path.is_dir() and self.path.suffix in ALLOWED_EXTENSIONS

    @property
    def subcategories(self):
        return sorted(filter(lambda x: x.is_category, self.children), key=Category.sort_key)

    @property
    def entries(self):
        return sorted(filter(lambda x: x.is_entry, self.children), key=Category.sort_key)

    @property
    def referencable(self):
        return sorted(filter(lambda x: x.is_referencable, self.children), key=Category.sort_key)

    @property
    def nonactionable(self):
        return sorted(filter(lambda x: x.complete is None, self.entries), key=Category.sort_key)

    @property
    def completed(self):
        return sorted(filter(lambda x: x.complete is True, self.entries), key=Category.sort_key)

    @property
    def incompleted(self):
        return sorted(filter(lambda x: x.complete is False, self.entries), key=Category.sort_key)

    @property
    def relative_path(self):
        if self.parent:
            return self.path.relative_to(self.parent.path)
        return self.path

    @property
    def breadcumbs(self):
        parent = self.parent
        items = []
        while parent:
            items.append(parent)
            parent = parent.parent
        return items[::-1]

    @staticmethod
    def sort_key(entry):
        if entry.is_entry:
            complete = {None: 2, False: 1, True: 3}
            return (complete[entry.complete], entry.path.name)
        return entry.path.name

    def read_about(self):
        with self.about.open("r") as f:
            lines = f.readlines()
            name = next(filter(lambda l: l.startswith("#"), lines), None)
            created_at = next(filter(lambda l: l.startswith("Created:"), lines), None)
            due_to = next(filter(lambda l: l.startswith("Due:"), lines), None)
            description_lines = list(
                (filter(lambda l: not any([l.startswith("#"), l.startswith("Created:"), l.startswith("Due:")]), lines))
            )
            short_description = next(filter(lambda l: len(l.strip()) > 0, description_lines), "").strip()
            description = "".join(description_lines).strip()

        self.name = name and name.split("#")[1].strip() or self.name
        self.short_description = short_description
        self.description = description
        if created_at:
            try:
                datestr = created_at.split("Created:")[1].strip()
                self.created_at = self.created_at or created_at and dt.datetime.strptime(datestr, DATE_FORMAT).date()
            except ValueError:
                logging.error(f"Failed to parse created_at date {datestr} from {about.as_posix()}")

        if due_to:
            try:
                datestr = due_to.split("Due:")[1].strip()
                self.due_to = self.due_to or due_to and dt.datetime.strptime(datestr, DATE_FORMAT).date()
            except ValueError:
                logging.error(f"Failed to parse due_to date {datestr} from {about.as_posix()}")

    def read_entry(self):
        name = description = None
        with self.path.open("r") as f:
            for line in f:
                if not name and line.startswith("#"):
                    name = line[1:].strip()
                elif not description and line[0] not in DESCRIPTION_FORBIDDEN_FIRST_CHARS:
                    description = line.strip()
                if name and description:
                    break
        if name:
            self.name = REGEX_CHECKBOX.sub("", name).strip()
            if REGEX_CHECKBOX.match(name):
                self.complete = "[x]" in name.lower()

        if description:
            self.description = self.short_description = description

    def read(self):
        if self.is_category:
            if self.about.exists():
                self.read_about()
        elif self.is_entry:
            self.read_entry()

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

    @classmethod
    def scan(cls, path, name='Para') -> None:
        root = cls(path=path, level=0, name=name)
        root.read()
        categories = [root]

        while categories:
            category = categories.pop(0)

            for child in category.path.iterdir():
                if child.name.startswith(".") or child.name in ["index.md", "about.md"]:
                    continue

                subcategory = cls(path=child, level=category.level + 1, name=child.name, parent=category)
                subcategory.read()
                category.children.append(subcategory)
                if subcategory.is_category:
                    categories.append(subcategory)

        return root