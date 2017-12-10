# Copyright 2017 Tóth, László Attila
# Distributed under the terms of the GNU Lesser General Public License v3
# The license can be found in COPYING file or on http://www.gnu.org/licenses/

import os
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from dewi.realtime_sync.watchers import FileSystemChangeWatcher


class FileSystemChangeHandler(FileSystemEventHandler):
    def __init__(self, watcher: FileSystemChangeWatcher):
        self._watcher = watcher

    def on_moved(self, event):
        if event.is_directory:
            self.process_moved_directory(event.src_path, event.dest_path)
        else:
            self._watcher.removed(event.src_path)
            self._watcher.created(event.dest_path)

    def process_moved_directory(self, src_path: str, dst_path: str):
        dst_path_parts = dst_path.split(os.sep)
        for root, dirs, files in os.walk(dst_path):
            path = root.split(os.sep)
            for entry in dirs:
                src_filename = os.path.join(src_path, os.sep.join(path[len(dst_path_parts):]), entry)
                self._watcher.removed(src_filename)

            for file in files:
                src_filename = os.path.join(src_path, os.sep.join(path[len(dst_path_parts):]), file)
                dst_filename = os.path.join(root, file)
                self._watcher.removed(src_filename)
                self._watcher.created(dst_filename)

        self._watcher.removed(src_path)

    def on_created(self, event):
        self._watcher.created(event.src_path)

    def on_deleted(self, event):
        self._watcher.removed(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self._watcher.modified(event.src_path)


class WatchDog:
    def __init__(self, root_dir: str, event_handler: FileSystemChangeHandler):
        self._root_dir = root_dir
        self._event_handler = event_handler

    def run(self):
        observer = Observer()
        observer.schedule(self._event_handler, self._root_dir, recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(200)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
