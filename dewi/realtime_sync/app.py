# Copyright 2017 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import typing

from dewi.realtime_sync.filesync_data import FileSyncEntry, FileSyncEntryManager
from dewi.realtime_sync.filesystem import Filesystem, LocalFilesystem, RemoteFilesystem
from dewi.realtime_sync.syncers import FileSynchronizer
from dewi.realtime_sync.watchers import FileSynchronizerWatcher, FileSystemChangeWatcher, SkippableChangeWatcher
from dewi.realtime_sync.watchers.watchdog import FileSystemChangeHandler, WatchDog


class SyncApp:
    def __init__(self, directory: str, target_directory: str,
                 entries: typing.List[FileSyncEntry],
                 filesystem: Filesystem):
        self._directory = directory
        self._target_directory = target_directory
        self._entries = entries
        self._filesystem = filesystem

    def run(self):
        handler = self._create_watchdog_handler()
        w = WatchDog(self._directory, handler)
        w.run()

    def _create_watchdog_handler(self) -> FileSystemChangeHandler:
        entry_manager = FileSyncEntryManager(self._entries)
        synchronizer = FileSynchronizer(self._directory, self._target_directory, self._filesystem)
        fsw = FileSystemChangeWatcher([self._directory])
        fsw.register_watcher(SkippableChangeWatcher([self._directory]))
        fsw.register_watcher(FileSynchronizerWatcher(synchronizer, entry_manager))
        handler = FileSystemChangeHandler(fsw)
        return handler


class LocalSyncApp(SyncApp):
    def __init__(self, directory: str, target_directory: str,
                 entries: typing.List[FileSyncEntry]):
        super().__init__(directory, target_directory, entries, LocalFilesystem())


class SyncOverSshApp(SyncApp):
    def __init__(self, directory: str, target_directory: str,
                 entries: typing.List[FileSyncEntry],
                 user: str, host: str, port: int,
                 check_host_key: bool = True
                 ):
        super().__init__(directory, target_directory, entries, RemoteFilesystem(user, host, port, check_host_key))
