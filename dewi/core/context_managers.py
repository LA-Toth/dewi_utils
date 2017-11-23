# Copyright 2016-2017 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3
import os


def in_directory(directory: str):
    class InDirectory:
        def __init__(self, directory: str):
            self._directory = directory
            self._old_directories = list()

        def __enter__(self):
            self._old_directories.append(os.getcwd())
            os.chdir(self._directory)

        def __exit__(self, exc_type, exc_val, exc_tb):
            os.chdir(self._old_directories.pop())

    return InDirectory(directory)
