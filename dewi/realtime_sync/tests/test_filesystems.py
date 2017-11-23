# Copyright 2017 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

from unittest.mock import patch, MagicMock

import dewi.tests
from dewi.realtime_sync.filesystem import RemoteFilesystem, LocalFilesystem


class RemoteFilesystemTest(dewi.tests.TestCase):
    def set_up(self):
        self.strict_fs = RemoteFilesystem('a-user', 'a-host', 42)
        self.nonstrict_fs = RemoteFilesystem('a-user', 'a-host', 42, check_host_key=False)
        self.strict_prefix = ['ssh', '-oPort=42', '-oStrictHostKeyChecking=yes', '-l', 'a-user', 'a-host']
        self.nonstrict_prefix = ['ssh', '-oPort=42', '-oUserKnownHostsFile=/dev/null', '-oStrictHostKeyChecking=no',
                                 '-l', 'a-user', 'a-host']

    @patch('subprocess.call')
    def test_makedir_of_strict(self, call_mock: MagicMock):
        self.strict_fs.makedir('/some/path')
        call_mock.assert_called_once_with(self.strict_prefix + ['mkdir', '-p', '/some/path'])

    @patch('subprocess.call')
    def test_makedir_of_non_strict(self, call_mock: MagicMock):
        self.nonstrict_fs.makedir('/some/path')
        call_mock.assert_called_once_with(self.nonstrict_prefix + ['mkdir', '-p', '/some/path'])

    @patch('subprocess.call')
    def test_chmod_of_strict(self, call_mock: MagicMock):
        self.strict_fs.chmod('/some/path', '1725')
        call_mock.assert_called_once_with(self.strict_prefix + ['chmod', '1725', '/some/path'])

    @patch('subprocess.call')
    def test_chmod_of_non_strict(self, call_mock: MagicMock):
        self.nonstrict_fs.chmod('/some/path', '1725')
        call_mock.assert_called_once_with(self.nonstrict_prefix + ['chmod', '1725', '/some/path'])

    @patch('subprocess.call')
    def test_chown_of_strict(self, call_mock: MagicMock):
        self.strict_fs.chown('/some/path', 'somebody', 'somegroup')
        call_mock.assert_called_once_with(self.strict_prefix + ['chown', 'somebody:somegroup', '/some/path'])

    @patch('subprocess.call')
    def test_chown_of_non_strict(self, call_mock: MagicMock):
        self.nonstrict_fs.chown('/some/path', 'somebody', 'somegroup')
        call_mock.assert_called_once_with(self.nonstrict_prefix + ['chown', 'somebody:somegroup', '/some/path'])

    @patch('subprocess.call')
    def test_copy_of_strict(self, call_mock: MagicMock):
        self.strict_fs.copy('/local/file', '/remote/file')
        call_mock.assert_called_once_with(
            ['scp', '-oPort=42', '-oStrictHostKeyChecking=yes', '/local/file', 'a-user@a-host:/remote/file'])

    @patch('subprocess.call')
    def test_copy_of_non_strict(self, call_mock: MagicMock):
        self.nonstrict_fs.copy('/local/file', '/remote/file')
        call_mock.assert_called_once_with(
            ['scp', '-oPort=42', '-oUserKnownHostsFile=/dev/null', '-oStrictHostKeyChecking=no', '/local/file',
             'a-user@a-host:/remote/file'])

    @patch('subprocess.call')
    def test_remove_of_strict(self, call_mock: MagicMock):
        self.strict_fs.remove('/some/path')
        call_mock.assert_called_once_with(self.strict_prefix + ['rm', '-r', '/some/path'])

    @patch('subprocess.call')
    def test_remove_of_nonstrict(self, call_mock: MagicMock):
        self.nonstrict_fs.remove('/some/path')
        call_mock.assert_called_once_with(self.nonstrict_prefix + ['rm', '-r', '/some/path'])

    @patch('os.path.isdir')
    def test_is_dir_of_strict_if_param_is_dir(self, call_mock: MagicMock):
        call_mock.return_value = True
        self.assert_true(self.strict_fs.is_dir('/local/path'))
        call_mock.assert_called_once_with('/local/path')

    @patch('os.path.isdir')
    def test_is_dir_of_strict_if_param_is_not_dir(self, call_mock: MagicMock):
        call_mock.return_value = False
        self.assert_false(self.strict_fs.is_dir('/local/path'))
        call_mock.assert_called_once_with('/local/path')

    @patch('os.path.exists')
    def test_is_dir_if_param_exists(self, call_mock: MagicMock):
        call_mock.return_value = True
        self.assert_true(self.strict_fs.exists('/local/path'))
        call_mock.assert_called_once_with('/local/path')

    @patch('os.path.exists')
    def test_exists_if_param_is_missing(self, call_mock: MagicMock):
        call_mock.return_value = False
        self.assert_false(self.strict_fs.exists('/local/path'))
        call_mock.assert_called_once_with('/local/path')


class LocalFilesystemTest(dewi.tests.TestCase):
    def set_up(self):
        self.fs = LocalFilesystem()

    @patch('subprocess.call')
    def test_makedir(self, call_mock: MagicMock):
        self.fs.makedir('/some/path')
        call_mock.assert_called_once_with(['mkdir', '-p', '/some/path'])

    @patch('subprocess.call')
    def test_chmod(self, call_mock: MagicMock):
        self.fs.chmod('/some/path', '1725')
        call_mock.assert_called_once_with(['chmod', '1725', '/some/path'])

    @patch('subprocess.call')
    def test_chown(self, call_mock: MagicMock):
        self.fs.chown('/some/path', 'somebody', 'somegroup')
        call_mock.assert_called_once_with(['chown', 'somebody:somegroup', '/some/path'])

    @patch('subprocess.call')
    def test_copy(self, call_mock: MagicMock):
        self.fs.copy('/local/file', '/remote/file')
        call_mock.assert_called_once_with(['cp', '-p', '/local/file', '/remote/file'])

    @patch('subprocess.call')
    def test_remove(self, call_mock: MagicMock):
        self.fs.remove('/some/path')
        call_mock.assert_called_once_with(['rm', '-r', '/some/path'])

    @patch('os.path.isdir')
    def test_is_dir_if_param_is_dir(self, call_mock: MagicMock):
        call_mock.return_value = True
        self.assert_true(self.fs.is_dir('/local/path'))
        call_mock.assert_called_once_with('/local/path')

    @patch('os.path.isdir')
    def test_is_dir_if_param_is_not_dir(self, call_mock: MagicMock):
        call_mock.return_value = False
        self.assert_false(self.fs.is_dir('/local/path'))
        call_mock.assert_called_once_with('/local/path')

    @patch('os.path.exists')
    def test_is_dir_if_param_exists(self, call_mock: MagicMock):
        call_mock.return_value = True
        self.assert_true(self.fs.exists('/local/path'))
        call_mock.assert_called_once_with('/local/path')

    @patch('os.path.exists')
    def test_exists_if_param_is_missing(self, call_mock: MagicMock):
        call_mock.return_value = False
        self.assert_false(self.fs.exists('/local/path'))
        call_mock.assert_called_once_with('/local/path')
