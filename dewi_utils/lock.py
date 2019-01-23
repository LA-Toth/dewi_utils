# Copyright 2019 Tóth, László Attila
# Distributed under the terms of the GNU Lesser General Public License v3
# The license can be found in COPYING file or on http://www.gnu.org/licenses/

import fcntl
import os


class FileLock:
    def __init__(self, filename: str):
        self._filename = filename
        self._fd = None

    def lock(self):
        while not self.is_locked:
            self.try_lock()

    def unlock(self):
        if self.is_locked:
            self._unlock()

    def try_lock(self):
        fd = os.open(self._filename, os.O_CREAT | os.O_TRUNC | os.O_RDWR)

        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (IOError, OSError):
            os.close(fd)
        else:
            self._fd = fd

    def _unlock(self):
        fd = self._fd
        self._fd = None
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)

    @property
    def is_locked(self):
        return self._fd is not None

    def __enter__(self):
        self.lock()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unlock()
        return self


def lock_directory(directory: str):
    return FileLock(os.path.join(directory, '.lock_file_'))
