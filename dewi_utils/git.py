# Copyright 2020-2021 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import os
import subprocess
import typing
from contextlib import contextmanager

from dewi_core.logger import log_debug


class Git:
    def run(self, args: typing.List[str], /, *, env: typing.Optional[dict] = None):
        log_debug(f'Running git command: {args}')
        subprocess.run(['git'] + args, check=True, env=env)

    def run_output(self, args: typing.List[str], /, *, env: typing.Optional[dict] = None) -> str:
        log_debug(f'Running git command with output: {args}')
        return subprocess.check_output(['git'] + args, env=env).decode('UTF-8').strip()

    def cd_to_repo_root(self):
        os.chdir(self.repo_root())

    def repo_root(self) -> str:
        return self.run_output(['rev-parse', '--show-toplevel'])

    def repo_name(self):
        return os.path.basename(self.repo_root())

    def current_branch(self) -> str:
        return subprocess.check_output(['git', 'branch', '--show-current']).decode('UTF-8').strip()

    def merge_base(self, branch1: str, branch2: str):
        return self.run_output(['merge-base', branch1, branch2])

    def stash(self) -> bool:
        status = self.run_output(['status', '--porcelain']).splitlines()

        for i in status:
            if 'M' in i[:2]:
                self.run(['stash'])
                return True

        return False

    def stash_apply(self, stashed: bool):
        if stashed:
            self.run(['stash', 'apply'])

    @contextmanager
    def with_stash(self):
        stashed = self.stash()
        yield
        self.stash_apply(stashed)
