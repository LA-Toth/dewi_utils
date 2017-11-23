# Copyright 2017 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import os

import subprocess


class Filesystem:
    def is_dir(self, local_path: str):
        pass

    def exists(self, local_path: str):
        pass

    def makedir(self, remote_path: str):
        pass

    def copy(self, local_path: str, remote_path: str):
        pass

    def chown(self, remote_path: str, user: str, group: str):
        pass

    def chmod(self, remote_path: str, permissions: str):
        pass

    def remove(self, remote_path: str):
        pass


class CommandTrackerFilesystem(Filesystem):
    def __init__(self):
        self.commands = list()

    def makedir(self, remote_path: str):
        self.commands.append(['makedir', [remote_path]])

    def copy(self, local_path: str, remote_path: str):
        self.commands.append(['copy', [local_path, remote_path]])

    def chown(self, remote_path: str, user: str, group: str):
        self.commands.append(['chown', [remote_path, user, group]])

    def chmod(self, remote_path: str, permissions: str):
        self.commands.append(['chmod', [remote_path, permissions]])

    def remove(self, remote_path: str):
        self.commands.append(['remove', [remote_path]])


class _RealFileSystem(Filesystem):
    def is_dir(self, local_path: str):
        return os.path.isdir(local_path)

    def exists(self, local_path: str):
        return os.path.exists(local_path)

    def call_subprocess(self, args: list):
        subprocess.call(args)


class RemoteFilesystem(_RealFileSystem):
    def __init__(self, user: str, host: str, port: int = 22, check_host_key: bool = True):
        self._user = user
        self._host = host
        self._port = port
        self._check_host_key = check_host_key
        self._remote_copy = ['scp']
        self._remote_exec = ['ssh']

        self._create_commands()

    def _create_commands(self):
        args = ['-oPort={}'.format(self._port)]
        if self._check_host_key:
            args += ['-oStrictHostKeyChecking=yes']
        else:
            args += ['-oUserKnownHostsFile=/dev/null', '-oStrictHostKeyChecking=no']
        self._remote_copy += args
        self._remote_exec += args + ['-l', self._user, self._host]

    def makedir(self, remote_path: str):
        self.call_subprocess(self._remote_exec + ['mkdir', '-p', remote_path])

    def copy(self, local_path: str, remote_path: str):
        self.call_subprocess(self._remote_copy + [local_path, '{}@{}:{}'.format(self._user, self._host, remote_path)])

    def chown(self, remote_path: str, user: str, group: str):
        self.call_subprocess(self._remote_exec + ['chown', '{}:{}'.format(user, group), remote_path])

    def chmod(self, remote_path: str, permissions: str):
        self.call_subprocess(self._remote_exec + ['chmod', permissions, remote_path])

    def remove(self, remote_path):
        self.call_subprocess(self._remote_exec + ['rm', '-r', remote_path])


class LocalFilesystem(_RealFileSystem):
    def makedir(self, remote_path: str):
        self.call_subprocess(['mkdir', '-p', remote_path])

    def copy(self, local_path: str, remote_path: str):
        self.call_subprocess(['cp', '-p', local_path, remote_path])

    def chown(self, remote_path: str, user: str, group: str):
        self.call_subprocess(['chown', '{}:{}'.format(user, group), remote_path])

    def chmod(self, remote_path: str, permissions: str):
        self.call_subprocess(['chmod', permissions, remote_path])

    def remove(self, remote_path):
        self.call_subprocess(['rm', '-r', remote_path])
