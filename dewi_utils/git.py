# Copyright 2020-2021 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import os
import subprocess
import typing
from contextlib import contextmanager

from dewi_core.logger import log_debug


class GitError(Exception):
    pass


class Git:
    def run(self, args: typing.List[str], /, *,
            cwd: typing.Optional[str] = None, env: typing.Optional[dict] = None):
        log_debug(f'Running git command: {args}; cwd={cwd if cwd else "current dir"}')
        subprocess.run(['git'] + args, check=True, cwd=cwd, env=env)

    def run_output(self, args: typing.List[str], /, *,
                   cwd: typing.Optional[str] = None, env: typing.Optional[dict] = None
                   ) -> str:
        log_debug(f'Running git command with output: {args}; cwd={cwd if cwd else "current dir"}')
        return subprocess.check_output(['git'] + args, cwd=cwd, env=env).decode('UTF-8').strip()

    def cd_to_repo_root(self, *,
                        cwd: typing.Optional[str] = None, env: typing.Optional[dict] = None
                        ):
        os.chdir(self.repo_root(cwd=cwd, env=env))

    def repo_root(self, *,
                  cwd: typing.Optional[str] = None, env: typing.Optional[dict] = None) -> str:
        return self.run_output(['rev-parse', '--show-toplevel'], cwd=cwd, env=env)

    def repo_name(self, *,
                  cwd: typing.Optional[str] = None, env: typing.Optional[dict] = None):
        return os.path.basename(self.repo_root(cwd=cwd, env=env))

    def current_branch(self, *,
                       cwd: typing.Optional[str] = None, env: typing.Optional[dict] = None) -> str:
        return self.run_output(['branch', '--show-current'], cwd=cwd, env=env)

    def current_head(self, *,
                     enable_detached_head=True,
                     cwd: typing.Optional[str] = None, env: typing.Optional[dict] = None) -> str:
        if not enable_detached_head and not self.current_branch(cwd=cwd, env=env):
            raise GitError(f"Detached head, directory='{cwd or os.getcwd()}'")
        return self.run_output(['rev-list', '--max-count=1', 'HEAD'], cwd=cwd, env=env)

    def merge_base(self, branch1: str, branch2: str, /, *,
                   cwd: typing.Optional[str] = None, env: typing.Optional[dict] = None):
        return self.run_output(['merge-base', branch1, branch2], cwd=cwd, env=env)

    def stash(self, *,
              cwd: typing.Optional[str] = None, env: typing.Optional[dict] = None) -> bool:
        status = self.run_output(['status', '--porcelain'], cwd=cwd, env=env).splitlines()

        for i in status:
            if 'M' in i[:2]:
                self.run(['stash'])
                return True

        return False

    def stash_apply(self, stashed: bool, /, *,
                    cwd: typing.Optional[str] = None, env: typing.Optional[dict] = None):
        if stashed:
            self.run(['stash', 'apply'], cwd=cwd, env=env)

    @contextmanager
    def with_stash(self, *,
                   cwd: typing.Optional[str] = None, env: typing.Optional[dict] = None):
        stashed = self.stash(cwd=cwd, env=env)
        yield
        self.stash_apply(stashed, cwd=cwd, env=env)

    def grep_in_commit_msg(self, text: str, /, *,
                           cwd: typing.Optional[str] = None, env: typing.Optional[dict] = None) -> typing.List[str]:
        return self.run_output(['-c', 'log.decorate=', 'log', '--pretty=%H %s', '--all', '--grep', text],
                               cwd=cwd, env=env).splitlines()

    def branches_containing_commit(self, commit_id: str, /, *,
                                   cwd: typing.Optional[str] = None, env: typing.Optional[dict] = None) \
            -> typing.List[str]:
        return self.run_output(['branch', '--format', '%(refname)', '--all', '--contains', commit_id],
                               cwd=cwd, env=env).splitlines()
