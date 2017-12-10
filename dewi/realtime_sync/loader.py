# Copyright 2017 Tóth, László Attila
# Distributed under the terms of the GNU Lesser General Public License v3
from io import TextIOWrapper
import sys
import typing

from dewi.realtime_sync.filesync_data import FileSyncEntry, FileSyncFlags


class EntryListLoader:
    ENTRY_DEFAULT_FIELDS = ['', '', '', '', '', '']
    ENTRY_FLAGS_FIELD_IDX = len(ENTRY_DEFAULT_FIELDS) - 1

    def _map_flags(self, flags_str: str, entry: str) -> typing.List[FileSyncFlags]:
        flags = list(flags_str)
        result = []

        for flag in flags:
            found = False
            for sync_flag in FileSyncFlags:
                if sync_flag.value == flag:
                    found = True
                    result.append(sync_flag)

            if not found:
                print("Flag '{}' is not known".format(flag))
                print("Bad entry was: " + entry)
                sys.exit(1)

        return result

    def _create_entry_based_on_string(self, entry: str, skip_chmod: bool) -> FileSyncEntry:
        parts = entry.split(';')
        if len(parts) < 2:
            print("At least two fields are necessary separated by semicolon: source;target")
            print("Full format: source;target;permissions;owner;group;flags")
            sys.exit(1)

        for i in range(2, len(self.ENTRY_DEFAULT_FIELDS)):
            if len(parts) < i + 1:
                parts.append(self.ENTRY_DEFAULT_FIELDS[i])

        if skip_chmod:
            parts[self.ENTRY_FLAGS_FIELD_IDX] += 'n'

        source, target, perm, user, group, flags = parts

        return FileSyncEntry(source, target, user, group, perm, self._map_flags(flags, entry))

    def load_from_string_list(self, entries: typing.List[str], skip_chmod: bool) -> typing.List[FileSyncEntry]:
        return [self._create_entry_based_on_string(e, skip_chmod) for e in entries]

    def load_from_stream(self, stream: TextIOWrapper, skip_chmod: bool) -> typing.List[FileSyncEntry]:
        result = []
        for line in stream:
            line = line.strip()
            if line.startswith('#') or not line.strip():
                continue

            result.append(self._create_entry_based_on_string(line, skip_chmod))

        return result

    def load_from_file(self, filename: str, skip_chmod: bool) -> typing.List[FileSyncEntry]:
        with open(filename) as f:
            return self.load_from_stream(f, skip_chmod)
