import logging
import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from para.category import Category


class ParaEventHandler(FileSystemEventHandler):
    def __init__(self, path, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path, self.name = path, name

    def on_any_event(self, event):
        if event.src_path.endswith('index.md'):
            return

        logging.info(f'Rebuilding index; reason: {event.event_type} {event.src_path}')
        root = Category.scan(self.path, name=self.name)
        root.render_indexes()


def monitor(path: Path, name=None) -> None:
    observer = Observer()
    event_handler = ParaEventHandler(path, name)
    observer.schedule(event_handler, path.as_posix(), recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
