import datetime as dt
import logging
import re
import string
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping, Optional, TypeVar
from weakref import WeakValueDictionary

import yaml

from para.mixins import RandomNoteMixin, RenderMixin, SnippetMixin

T = TypeVar("Category")

DEFAULT_ROOT_NAME = "Para"

DATE_FORMAT = "%d.%m.%Y"
SPECIAL_CHARS = set(string.punctuation + string.digits + string.whitespace)
DESCRIPTION_FORBIDDEN_FIRST_CHARS = SPECIAL_CHARS - set("[]()")

ALLOWED_EXTENSIONS = [".html", ".pdf", ".csv", ".txt"]

REGEX_CHECKBOX = re.compile(r"[-\s]*\[[xX_\s]?\]")


@dataclass
class Category(RandomNoteMixin, RenderMixin, SnippetMixin):
    INDEX = WeakValueDictionary()

    path: Path = None
    level: int = 0
    name: str = ""
    id: str = ""
    short_description: str = ""
    description: str = ""
    created_at: dt.date = None
    due_to: dt.date = None
    environments: set = field(default_factory=lambda: {'all'})
    complete: bool = None
    children: Iterable = field(default_factory=list)
    files_metadata: Mapping = field(default_factory=dict)
    parent: T = None

    def __repr__(self):
        return f"<Category {self.name}>"

    @property
    def is_empty(self):
        return not self.about.exists()

    @property
    def index(self):
        return self.path.joinpath("index.md")

    @property
    def about(self):
        return (
            self.path.joinpath("about.yml")
            if self.path.joinpath("about.yaml").exists()
            else self.path.joinpath("about.yml")
        )

    @property
    def todo(self):
        return self.path.joinpath("todo.md")

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
    def file_description(self):
        return self.parent.files_metadata.get(self.path.name) or ''

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

    @property
    def relative_id(self):
        if not self.parent:
            return self.id
        return f"{self.parent.id}.{self.id}"

    def read_about(self):

        with self.about.open('r') as f:
            about = yaml.load(f, Loader=yaml.BaseLoader)

        self.name = about.get('name') or self.name
        self.short_description = about.get('short')
        self.description = about.get('description')
        self.id = about.get('id') or self.path.name
        self.files_metadata.update(about.get('files') or {})

        environments = about.get('environments')
        if isinstance(environments, list):
            self.environments = set(environments)

        created_at = about.get('created_at')
        if created_at:
            try:
                self.created_at = dt.datetime.strptime(created_at, DATE_FORMAT).date()
            except ValueError:
                logging.error(f"Failed to parse created_at date {created_at} from {self.about.as_posix()}")

        due_to = about.get('due_to')
        if due_to:
            try:
                self.due_to = dt.datetime.strptime(due_to, DATE_FORMAT).date()
            except ValueError:
                logging.error(f"Failed to parse due_to date {due_to} from {self.about.as_posix()}")

    def read_entry(self):
        name = description = None
        self.id = self.path.name
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

    def read_todo(self):
        with self.todo.open("r") as f:
            for line in f:
                if REGEX_CHECKBOX.match(line):
                    self.children.append(
                        Category(
                            name=REGEX_CHECKBOX.sub("", line).strip(),
                            path=self.todo,
                            description="",
                            short_description="",
                            complete="[x]" in line.lower(),
                            id=f"{self.id}.todo",
                            level=self.level + 1,
                            parent=self,
                        )
                    )

    def read(self):
        if self.is_category:
            if self.about.exists():
                self.read_about()
            if self.todo.exists():
                self.read_todo()
        elif self.is_entry:
            self.read_entry()

    def create_subcategory(self, name):
        path = self.path.joinpath(name)
        path.mkdir()
        return Category(path=path, level=self.level + 1, name=name)

    @classmethod
    def scan(cls, path, name: Optional[str] = None, environment: str = 'all') -> None:
        root = cls(path=path, level=0, name=name or DEFAULT_ROOT_NAME, id="root")
        root.read()
        categories = [root]

        while categories:
            category = categories.pop(0)
            cls.INDEX.setdefault(category.id, category)
            cls.INDEX.setdefault(category.relative_id, category)

            for child in category.path.iterdir():
                if child.name.startswith(".") or child.name in ["index.md", "about.yaml", "about.yml", "todo.md"]:
                    continue

                subcategory = cls(path=child, level=category.level + 1, name=child.name, parent=category)
                subcategory.read()

                if environment != 'all' and environment not in subcategory.environments:
                    continue

                category.children.append(subcategory)
                if subcategory.is_category:
                    categories.append(subcategory)
                else:
                    cls.INDEX.setdefault(category.relative_id, category)

        return root

    @property
    def ids(self):
        return list(self.INDEX.keys())
