# Copyright (c) 2017 Laszlo Attila Toth
# Distributed under the terms of the GNU General Public License v3


import argparse
import collections
import sys
import typing

from dewi.core.command import Command
from dewi.core.context import Context
from dewi.loader.plugin import Plugin
from dewi.realtime_sync.app import LocalSyncApp, SyncOverSshApp
from dewi.realtime_sync.filesync_data import FileSyncEntry, FileSyncFlags


class FileSyncCommand(Command):
    name = 'filesync'
    aliases = ['codesync', 'dirsync', 'treesync']
    description = "Sync content of a directory to a remote location controlled by mapping rules"

    ENTRY_DEFAULT_FIELDS = ['', '', '', '', '', '']
    ENTRY_FLAGS_FIELD_IDX = len(ENTRY_DEFAULT_FIELDS) - 1

    def register_arguments(self, parser: argparse.ArgumentParser):
        parsers = parser.add_subparsers(title='Subcommand for specific locations', dest='mode')

        local_parser = parsers.add_parser('local',
                                          help='Synchronize files to another part of local filesystem')
        remote_parser = parsers.add_parser('remote', help='Synchronize files to a remote server using SSH')

        self._register_directory_args(local_parser)
        self._register_directory_args(remote_parser)

        self._register_ssh_args(remote_parser)

        self._register_sync_entries(local_parser)
        self._register_sync_entries(remote_parser)

    def _register_directory_args(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            '-d', '--directory', '--source-directory', dest='directory', required=True,
            help='The local root directory which contains files to be synced'
        )
        parser.add_argument(
            '-t', '--target-directory', dest='target_directory', required=True,
            help='The target root directory, everything will be synced below this directory'
        )

    def _register_ssh_args(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            '-H', '--host', required=True,
            help='The SSH server\'s host name or IP address'
        )
        parser.add_argument(
            '-p', '--port', type=int, default=22,
            help='The SSH sever port, default is 22'
        )

        parser.add_argument(
            '-l', '--login', '-u', '--user', dest='user', required=True,
            help='The username used on the SSH server'
        )

        parser.add_argument(
            '--skip-host-key-check', action='store_true', default=False,
            help='Skip check SSH host key - it is insecure, but in trusted environment it is reasonable'
        )

    def _register_sync_entries(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            '-e', '--entry', action='append', required=True,
            help='A file sync entry describing what to synchronize to where with additional details.'
        )

        parser.add_argument(
            '-n', '--no-chmod-chown', '--skip-chmod', dest='skip_chmod', action='store_true', default=False,
            help='Always skip chmod and chown (to run as non-admin on target FS)'
        )

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

    def _parse_entry(self, entry: str, skip_chmod: bool) -> FileSyncEntry:
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

    def _parse_entries(self, entries: typing.List[str], skip_chmod: bool) -> typing.List[FileSyncEntry]:
        return [self._parse_entry(e, skip_chmod) for e in entries]

    def run(self, args: argparse.Namespace):

        entries = self._parse_entries(args.entry, args.skip_chmod)
        if args.mode == 'local':
            self._local_sync(args, entries)
        else:
            self._remote_sync(args, entries)

    def _local_sync(self, args: argparse.Namespace, entries: typing.List[FileSyncEntry]):
        app = LocalSyncApp(args.directory, args.target_directory, entries)
        app.run()

    def _remote_sync(self, args: argparse.Namespace, entries: typing.List[FileSyncEntry]):
        app = SyncOverSshApp(args.directory, args.target_directory, entries,
                             user=args.user, host=args.host, port=args.port,
                             check_host_key=not args.skip_host_key_check)
        app.run()


class FileSyncPlugin(Plugin):
    def get_description(self) -> str:
        return 'Command plugin of: ' + FileSyncCommand.description

    def get_dependencies(self) -> collections.Iterable:
        return {'dewi.core.CorePlugin'}

    def load(self, c: Context):
        c['commands'].register_class(FileSyncCommand)
