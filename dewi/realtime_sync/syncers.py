# Copyright 2017 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import os

from dewi.core.logger import log_debug
from dewi.realtime_sync.filesync_data import DetailedEntry, FileSyncFlags
from dewi.realtime_sync.filesystem import Filesystem


class FileSynchronizer:
    def __init__(self, local_root: str, remote_root: str, filesystem: Filesystem):
        self.local_root_directory = local_root
        self.remote_root_directory = remote_root
        self.fs = filesystem

    def sync(self, path: str, entry: DetailedEntry):
        log_debug('Sync entry', path=path)
        remote_name = os.path.join(self.remote_root_directory, entry.remote_name)

        if self.fs.exists(path):
            if self.fs.is_dir(path):
                self.fs.makedir(remote_name)
            else:
                if FileSyncFlags.RECURSIVE in entry.entry.flags:
                    self.fs.makedir(os.path.dirname(remote_name))
                self.fs.copy(path, remote_name)

                if FileSyncFlags.WITHOUT_CHMOD not in entry.entry.flags:
                    self.fs.chown(remote_name, entry.entry.owner, entry.entry.group)
                    self.fs.chmod(remote_name, entry.entry.permissions)
        else:
            self.fs.remove(remote_name)
