import os

import typing

import dewi.tests
from dewi.realtime_sync.filesync_data import FileSyncFlags, FileSyncEntry, DetailedEntry
from dewi.realtime_sync.filesystem import CommandTrackerFilesystem
from dewi.realtime_sync.syncers import FileSynchronizer


class VirtualCommandTrackerFilesystem(CommandTrackerFilesystem):
    def __init__(self, directories: list):
        super().__init__()
        self.directories = directories
        self.result_of_exists = True

    def is_dir(self, local_path: str):
        return local_path in self.directories

    def exists(self, local_path: str):
        return self.result_of_exists


class TestFileSynchronizer(dewi.tests.TestCase):
    EXACT_FILE_TO_A_DIR_ENTRY = FileSyncEntry('lib/example.to.dir.php', 'usr/lib/dewi/phplib/')
    EXACT_FILE_TO_A_DIR_WITH_NO_CHMOD_ENTRY = FileSyncEntry('lib/example.to.dir.php', 'usr/lib/dewi/phplib/',
                                                            flags=[FileSyncFlags.WITHOUT_CHMOD])
    EXACT_FILE_TO_EXACT_FILE_ENTRY = FileSyncEntry('config/bind.conf', 'etc/named.conf', owner='named', group='daemons',
                                                   permissions='600')
    RECURSIVE_DIR_ENTRY = FileSyncEntry('lib', 'opt/dewi/phplib2/', flags=[FileSyncFlags.RECURSIVE])
    SHELL_GLOB_ENTRY = FileSyncEntry('config/dewi/*.conf', 'etc/dewi-configs/')
    REGEX_ENTRY = FileSyncEntry("debian/[^.]+\.(.+)\.upstart", "etc/init/\g<1>.conf", flags=[FileSyncFlags.REGEX])
    SUBDIR_GLOB_ENTRY = FileSyncEntry('share/*.plugin', 'usr/share/dewi-plugins/',
                                      flags=[FileSyncFlags.SUBDIRECTORY_WITH_GLOB])

    def set_up(self):
        self.dir_name = '/path/to/a/dir'
        self.remote_root = '/remote/dir'
        self.dirs = [self.dir_name]
        self.fs = VirtualCommandTrackerFilesystem(self.dirs)
        self.tested = FileSynchronizer(self.remote_root, filesystem=self.fs)

        # NOTE: the remote name is relative path, used in DetailedEntry
        self.remote_name = 'path/to/a/remote/file'

        self.local_full_name = '/path/to/a/dir/a/file'
        self.expected_remote_name = '/remote/dir/path/to/a/remote/file'
        self.expected_remote_dir_name = '/remote/dir/path/to/a/remote'

    def get_usual_commands(self, user: str = 'root', group: str = 'root', permissions='644'):
        return [
            ['copy', [self.local_full_name, self.expected_remote_name]],
            ['chown', [self.expected_remote_name, user, group]],
            ['chmod', [self.expected_remote_name, permissions]],
        ]

    def assert_sync(self, local_name: str, entry: FileSyncEntry,
                    expected_commands: typing.List[typing.List[typing.Union['str', typing.List[typing.Any]]]]):
        detailed_entry = DetailedEntry(entry, self.remote_name)
        self.tested.sync(local_name, detailed_entry)
        self.assert_equal(expected_commands, self.fs.commands)

    def assert_file_sync(self, entry: FileSyncEntry,
                         expected_commands: typing.List[typing.List[typing.Union['str', typing.List[typing.Any]]]]):
        self.assert_sync(self.local_full_name, entry, expected_commands)

    def assert_dir_sync(self, entry: FileSyncEntry,
                        expected_commands: typing.List[typing.List[typing.Union['str', typing.List[typing.Any]]]]):
        self.assert_sync(self.dir_name, entry, expected_commands)

    def assert_removal(self, local_path: str, entry: FileSyncEntry):
        self.fs.result_of_exists = False
        self.assert_sync(local_path, entry, [['remove', [self.expected_remote_name]]])

    def assert_file_is_removed(self, entry: FileSyncEntry):
        self.assert_removal(self.local_full_name, entry)

    def assert_dir_is_removed(self, entry: FileSyncEntry):
        self.assert_removal(self.dir_name, entry)

    def test_exact_file_to_dir(self):
        self.assert_file_sync(self.EXACT_FILE_TO_A_DIR_ENTRY, self.get_usual_commands())

    def test_exact_file_to_dir_if_remove_is_needed(self):
        self.assert_file_is_removed(self.EXACT_FILE_TO_A_DIR_ENTRY)

    def test_exact_file_to_file(self):
        self.assert_file_sync(self.EXACT_FILE_TO_EXACT_FILE_ENTRY, self.get_usual_commands('named', 'daemons', '600'))

    def test_exact_file_to_file_when_remove_is_needed(self):
        self.assert_file_is_removed(self.EXACT_FILE_TO_EXACT_FILE_ENTRY)

    def test_regex(self):
        self.assert_file_sync(self.REGEX_ENTRY, self.get_usual_commands())

    def test_regex_when_remove_is_needed(self):
        self.assert_file_is_removed(self.EXACT_FILE_TO_EXACT_FILE_ENTRY)

    def test_subdir_glob(self):
        self.assert_file_sync(self.SUBDIR_GLOB_ENTRY, self.get_usual_commands())

    def test_subdir_glob_when_remove_is_needed(self):
        self.assert_file_is_removed(self.SUBDIR_GLOB_ENTRY)

    def test_recursive_entry_with_file(self):
        self.assert_file_sync(self.RECURSIVE_DIR_ENTRY,
                              [['makedir', [self.expected_remote_dir_name]]] + self.get_usual_commands())

    def test_recursive_entry_with_dir(self):
        self.assert_dir_sync(self.RECURSIVE_DIR_ENTRY,
                             [['makedir', [self.expected_remote_name]]])

    def test_recursive_entry_with_file_when_remove_is_needed(self):
        self.assert_file_is_removed(self.SUBDIR_GLOB_ENTRY)

    def test_recursive_entry_with_dir_when_remove_is_needed(self):
        self.assert_dir_is_removed(self.SUBDIR_GLOB_ENTRY)

    def test_skip_of_chmod(self):
        self.assert_file_sync(self.EXACT_FILE_TO_A_DIR_WITH_NO_CHMOD_ENTRY,
                              [['copy', [self.local_full_name, self.expected_remote_name]]])
