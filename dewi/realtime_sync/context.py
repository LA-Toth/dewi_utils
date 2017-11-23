# Copyright 2017 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3


class SyncContext:
    def __init__(self):
        self.directories = list()

    def register_directory(self, directory: str):
        self.directories.append(directory)
