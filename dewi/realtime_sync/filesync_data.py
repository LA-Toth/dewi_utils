# Copyright 2017 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3
import enum
import fnmatch
import os
import re

import typing


class FileSyncFlags(enum.Enum):
    RECURSIVE = 'r'
    WITHOUT_CHMOD = 'n'
    REGEX = 'R'
    CONTINUE_FOR_BEST_MATCH = 'c'  # eg. most files are copied recursively (r), but others have a subdir match (s)
    SUBDIRECTORY_WITH_GLOB = 's'  # basedir/subdir/*.txt synced to target/dir/; basedir/*.txt is in use


class FileSyncEntry:
    def __init__(self,
                 local_path: str,
                 target_path: str,
                 owner: typing.Optional[str] = None,
                 group: typing.Optional[str] = None,
                 permissions: typing.Optional[str] = None,
                 flags: typing.Optional[typing.List[FileSyncFlags]] = None
                 ):
        self.local_path = local_path
        self.target_path = target_path
        self.owner = owner or 'root'
        self.group = group or 'root'
        self.permissions = permissions or '644'
        self.flags = flags or list()

    def __str__(self):
        return self.__class__.__name__ + '(' + \
               ', '.join(["{}='{}'".format(k, getattr(self, k))
                          for k in [
                              'local_path', 'target_path', 'owner', 'group', 'permissions', 'flags']
                          ]) + ')'

    def __repr__(self):
        return self.__str__()


class DetailedEntry:
    def __init__(self, entry: FileSyncEntry, remote_name: str):
        self.entry = entry
        self.remote_name = remote_name


class FileSyncEntryManager:
    def __init__(self, entries: typing.List[FileSyncEntry]):
        self._entries = dict()
        for e in entries:
            self._entries[e.local_path] = e

    def get_entry(self, filename: str) -> typing.Optional[DetailedEntry]:
        entry = self._get_filesync_entry_by_path(filename)

        if entry:
            return DetailedEntry(entry=entry, remote_name=self._get_remote_name(filename, entry))
        else:
            return None

    def _get_filesync_entry_by_path(self, filename: str) -> typing.Optional[FileSyncEntry]:
        if filename in self._entries:
            return self._entries[filename]

        else:
            return self._get_filesync_entry_by_path_patterns(filename)

    def _get_filesync_entry_by_path_patterns(self, filename: str) -> typing.Optional[FileSyncEntry]:
        result = None
        for (pattern, entry) in self._entries.items():
            if fnmatch.fnmatchcase(filename, pattern):
                return entry

            if FileSyncFlags.REGEX in entry.flags:
                if re.match(pattern, filename):
                    return entry

            if FileSyncFlags.RECURSIVE in entry.flags:
                dirname = pattern

                if filename.startswith(dirname):
                    if FileSyncFlags.CONTINUE_FOR_BEST_MATCH in entry.flags:
                        result = entry
                    else:
                        return entry

            if FileSyncFlags.SUBDIRECTORY_WITH_GLOB in entry.flags:
                # copy same type of file from different directories into a single one,
                # such as init scripts to /etc/init.d/
                # format:
                # base/dir/*.plugin to target_dir
                directory, fileglob = pattern.rsplit('/', 1)
                if filename.startswith(directory + '/') and \
                        fnmatch.fnmatchcase(os.path.basename(filename), fileglob):
                    return entry

        return result

    def _get_remote_name(self, filename: str, entry: FileSyncEntry) -> str:
        if FileSyncFlags.REGEX in entry.flags:
            return re.sub(entry.local_path, entry.target_path, filename)

        elif entry.target_path.endswith('/'):
            remote_name = filename
            if FileSyncFlags.RECURSIVE in entry.flags:
                remote_name = remote_name[len(entry.local_path):]
            else:
                remote_name = os.path.basename(filename)

            if remote_name.startswith('/'):
                remote_name = remote_name[1:]

            return entry.target_path + remote_name

        else:
            return entry.target_path
