# Copyright 2017 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import dewi.tests
from dewi.realtime_sync.filesync_data import FileSyncEntryManager, FileSyncFlags, FileSyncEntry


class TestGetMappingEntriesAndRemoteNames(dewi.tests.TestCase):
    EXACT_FILE_TO_A_DIR_ENTRY = FileSyncEntry('lib/example.to.dir.php', 'usr/lib/dewi/phplib/')
    EXACT_FILE_TO_EXACT_FILE_ENTRY = FileSyncEntry('config/bind.conf', 'etc/named.conf', owner='named', group='daemons',
                                                   permissions='600')
    RECURSIVE_DIR_ENTRY = FileSyncEntry('lib', 'opt/dewi/phplib2/', flags=[FileSyncFlags.RECURSIVE])
    SHELL_GLOB_ENTRY = FileSyncEntry('config/dewi/*.conf', 'etc/dewi-configs/')
    RECURSIVE_BEST_MATCH_ENTRY = FileSyncEntry('dewi/', 'opt/dewi/pylib/',
                                               flags=[FileSyncFlags.RECURSIVE, FileSyncFlags.CONTINUE_FOR_BEST_MATCH])
    DEWI_PLUGIN_ENTRY = FileSyncEntry('dewi/*.plugin', 'etc/dewi-plugins/')
    REGEX_ENTRY = FileSyncEntry("debian/[^.]+\.(.+)\.upstart", "etc/init/\g<1>.conf", flags=[FileSyncFlags.REGEX])
    SUBDIR_GLOB_ENTRY = FileSyncEntry('share/*.plugin', 'usr/share/dewi-plugins/',
                                      flags=[FileSyncFlags.SUBDIRECTORY_WITH_GLOB])

    def set_up(self):
        self.fs = FileSyncEntryManager([
            self.RECURSIVE_DIR_ENTRY,
            self.EXACT_FILE_TO_A_DIR_ENTRY,
            self.SHELL_GLOB_ENTRY,
            self.RECURSIVE_BEST_MATCH_ENTRY,
            self.EXACT_FILE_TO_EXACT_FILE_ENTRY,
            self.DEWI_PLUGIN_ENTRY,
            self.REGEX_ENTRY,
            self.SUBDIR_GLOB_ENTRY,
        ])

    def assert_not_found(self, local_path: str):
        self.assert_is_none(self.fs.get_entry(local_path))

    def assert_matching_entry(self, local_path: str, entry: FileSyncEntry):
        details = self.fs.get_entry(local_path)
        self.assert_is_not_none(details)
        self.assert_equal(entry, details.entry)

    def assert_remote_name(self, local_path: str, expected_remote_name: str):
        details = self.fs.get_entry(local_path)
        self.assert_is_not_none(details)
        self.assert_equal(expected_remote_name, details.remote_name)

    def test_that_nonlisted_filename_has_no_entry(self):
        self.assert_not_found('non-existent')

    def test_that_exact_file_name_belongs_to_the_expected_entry(self):
        self.assert_matching_entry('lib/example.to.dir.php', self.EXACT_FILE_TO_A_DIR_ENTRY)

    def test_that_exact_file_name_has_same_remote_filename(self):
        self.assert_remote_name('lib/example.to.dir.php', 'usr/lib/dewi/phplib/example.to.dir.php')

    def test_that_exact_file_name_with_exact_remote_name_has_expected_entry(self):
        self.assert_matching_entry('config/bind.conf', self.EXACT_FILE_TO_EXACT_FILE_ENTRY)

    def test_that_exact_file_name_with_exact_remote_name_has_expected_remote_name(self):
        self.assert_remote_name('config/bind.conf', 'etc/named.conf')

    def test_that_recursive_entry_with_child_filename_returns_this_entry(self):
        self.assert_matching_entry('lib/example.py', self.RECURSIVE_DIR_ENTRY)

    def test_that_recursive_entry_with_child_directory_and_filename_has_expected_remote_name(self):
        self.assert_remote_name('lib/example.py', 'opt/dewi/phplib2/example.py')

    def test_that_recursive_entry_with_child_directory_and_filename_returns_this_entry(self):
        self.assert_matching_entry('lib/subdir/subsubdir/example.py', self.RECURSIVE_DIR_ENTRY)

    def test_that_recursive_entry_with_child_directory_and_filename_adds_directory_to_remote_name(self):
        self.assert_remote_name('lib/subdir/subsubdir/example.py', 'opt/dewi/phplib2/subdir/subsubdir/example.py')

    def test_that_shell_glob_is_supported_for_entry_lookup(self):
        self.assert_matching_entry('config/dewi/path.conf', self.SHELL_GLOB_ENTRY)

    def test_that_recursive_best_match_usually_returns_the_recursive_entry(self):
        self.assert_matching_entry('dewi/example.py', self.RECURSIVE_BEST_MATCH_ENTRY)

    def test_that_recursive_best_match_results_best_matching_entry(self):
        self.assert_matching_entry('dewi/example.plugin', self.DEWI_PLUGIN_ENTRY)

    def test_that_shell_glob_remote_name_is_the_expected(self):
        self.assert_remote_name('config/dewi/path.conf', 'etc/dewi-configs/path.conf')

    def test_that_recursive_best_match_has_expected_remote_name(self):
        self.assert_remote_name('dewi/example.py', 'opt/dewi/pylib/example.py')

    def test_that_the_continued_best_match_has_the_expected_remote_name(self):
        self.assert_remote_name('dewi/example.plugin', 'etc/dewi-plugins/example.plugin')

    def test_regex_entry(self):
        self.assert_matching_entry('debian/dewi.example.upstart', self.REGEX_ENTRY)

    def test_regex_entry_remote_name(self):
        self.assert_remote_name('debian/python3-dewi.example.upstart', 'etc/init/example.conf')

    def test_subdirectory_glob_entry(self):
        self.assert_matching_entry('share/example.plugin', self.SUBDIR_GLOB_ENTRY)
        self.assert_matching_entry('share/a-dir/a-plugin.plugin', self.SUBDIR_GLOB_ENTRY)
        self.assert_matching_entry('share/b-dir/another-plugin.plugin', self.SUBDIR_GLOB_ENTRY)

    def test_subdirectry_glob_entry_remote_file_name(self):
        self.assert_remote_name('share/example.plugin', 'usr/share/dewi-plugins/example.plugin')
        self.assert_remote_name('share/a-dir/a-plugin.plugin', 'usr/share/dewi-plugins/a-plugin.plugin')
        self.assert_remote_name('share/b-dir/a-subdir/another-plugin.plugin',
                                'usr/share/dewi-plugins/another-plugin.plugin')
