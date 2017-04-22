# Copyright 2017 Laszlo Attila Toth
# Distributed under the terms of the GNU General Public License v3

#
# This file contains file watchers for specific systems
#

import os
from time import time

import time
import typing

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from dewi.realtime_sync.filesync_data import FileSyncEntryManager
from dewi.realtime_sync.syncers import FileSynchronizer


class ChangeWatcher:
    """
     A watcher or observer of file changes
     The file change watching behaves as responsibility change: whichever watcher decides that
      it fully processed the file change, it returns True, that it was the watcher's responsibility.

     Argument of each methods:
         path (str): the absolute path of the changed file
     Returns: bool True if the file is processed, and no further watcher is necessary
     """

    def created(self, path: str) -> bool:
        return self.modified(path)

    def modified(self, path: str) -> bool:
        raise NotImplementedError()

    def removed(self, path: str) -> bool:
        raise NotImplementedError()


class SkippableChangeWatcher(ChangeWatcher):
    SUFFIXES = [
        '~',
        '.bak',
        '.egg_info',
        '.pyc',
        '.orig',
        '.rej',
    ]

    PREFIXES = [
        '#',
        '.git',
    ]

    FIRST_PATH_ENTRIES = [
        '.git',
        'build',
        'dist',
    ]

    def __init__(self, root_directories: typing.List[str]):
        self.directories = [(d[:-1] if d.endswith('/') else d) for d in root_directories]

    def modified(self, path: str) -> bool:
        return self._process_change(path)

    def removed(self, path: str) -> bool:
        return self._process_change(path)

    def _process_change(self, changed_file: str) -> bool:
        if self._skip_based_on_basename(os.path.basename(changed_file)):
            return True

        for directory in self.directories:
            if not changed_file.startswith(directory):
                continue

            path = changed_file[len(directory) + 1:]

            if self._skip_based_on_path(path):
                return True

        return False

    def _skip_based_on_basename(self, basename: str) -> bool:
        if basename[0] == '.':
            if basename[-4:-1] == '.sw':
                return True
        else:
            for suffix in self.SUFFIXES:
                if basename.endswith(suffix):
                    return True

            for prefix in self.PREFIXES:
                if basename.startswith(prefix):
                    return True

            if basename == '.DS_Store':
                return True

        return False

    def _skip_based_on_path(self, path: str) -> bool:
        parts = os.path.split(path)
        if parts[0] in self.FIRST_PATH_ENTRIES:
            return True

        if '__pycache__' in parts:
            return True

        return False


class FileSynchronizerWatcher(ChangeWatcher):
    def __init__(self, fs: FileSynchronizer, fm: FileSyncEntryManager):
        self._synchronizer = fs
        self._manager = fm

    def modified(self, path: str) -> bool:
        return self._process_change(path)

    def removed(self, path: str) -> bool:
        return self._process_change(path)

    def _process_change(self, changed_file: str):
        if not changed_file.startswith(self._synchronizer.local_root_directory):
            return False

        local_path = changed_file[len(self._synchronizer.local_root_directory) + 1:]

        detailed_entry = self._manager.get_entry(local_path)
        if detailed_entry is None:
            return False

        self._synchronizer.sync(changed_file, detailed_entry)

        return True


class FileSystemChangeWatcher:
    def __init__(self, directories: typing.List[str]):
        self._directories = list(directories)
        self._watchers = list()

    def register_watcher(self, watcher: ChangeWatcher):
        self._watchers.append(watcher)

    def created(self, path: str):
        self._process_change(path, 'created', 'created')

    def modified(self, path: str):
        self._process_change(path, 'modified', 'modified')

    def removed(self, path: str):
        self._process_change(path, 'deleted', 'removed')

    def _process_change(self, path: str, change_type: str, callback: str):
        print(" * File system changed: {}: {}".format(change_type.capitalize(), path))
        for watcher in self._watchers:
            processed = getattr(watcher, callback)(path)

            if processed:
                return


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
