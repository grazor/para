import os
import random
from subprocess import call


class RandomNoteMixin:
    def get_random_note(self, exclude=None):
        entries = list(self.entries)
        subcategories = [self]
        while subcategories:
            category = subcategories.pop(0)
            if category.id in exclude:
                continue
            subcategories.extend(category.subcategories)
            entries.extend(category.entries)

        return random.choice(entries)


def random_note_loop(node, exclude=None):
    editor = os.environ.get('EDITOR', 'vim')
    try:
        while True:
            note = node.get_random_note(exclude)
            response = input(f'Open {note.parent.name}: {note.name} (Y/n): ')
            if response.lower() not in ['n', 'no']:
                call([editor, note.path.as_posix()])
    except KeyboardInterrupt:
        pass
