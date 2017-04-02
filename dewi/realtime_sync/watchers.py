# Copyright 2017 Laszlo Attila Toth
# Distributed under the terms of the GNU General Public License v3

#
# This file contains file watchers for specific systems
#

class FileChangeWatcher:
    def __init__(self, directories: list):
        self.directories = list(directories)
