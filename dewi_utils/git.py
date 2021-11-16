# Copyright 2020-2021 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import copy
import datetime
import os
import re
import subprocess
import typing
from contextlib import contextmanager

from dewi_core.config.appconfig import get_config
from dewi_core.config.node import Node, NodeList
from dewi_core.logger import log_debug


class GitError(Exception):
    pass


class Commit(Node):
    def __init__(self):
        self.commit_id: str = ''
        self.author: str = ''
        self.date: datetime.datetime = datetime.datetime.now()
        self.commit_date: datetime.datetime = datetime.datetime.now()
        self.committer: str = ''
        self.subject: str = ''
        self.distance: int = -1

    @classmethod
    def create(cls, commit_id: str, /, author: str, date: datetime.datetime,
               commit_date: datetime.datetime, committer: str,
               subject: str, distance: int):
        commit = cls()
        commit.commit_id = commit_id
        commit.author = author
        commit.date = date
        commit.commit_date = commit_date
        commit.committer = committer
        commit.subject = subject
        commit.distance = distance
        return commit


class Git:
    def run(self, args: typing.List[str], /, *,
            cwd: typing.Optional[str] = None, env: typing.Optional[dict] = None):
        log_debug(f'Running git command: {args}; cwd={cwd if cwd else "current dir"}')
        subprocess.run(['git'] + args, check=True, cwd=cwd, env=env)

    def run_output(self, args: typing.List[str], /, *,
                   cwd: typing.Optional[str] = None, env: typing.Optional[dict] = None,
                   strip: bool = True,
                   ) -> str:
        log_debug(f'Running git command with output: {args}; cwd={cwd if cwd else "current dir"}')
        result = subprocess.check_output(['git'] + args, cwd=cwd, env=env).decode('UTF-8')
        return result.strip() if strip else result

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

    def is_existing_remote(self, name: str, /, *,
                           cwd: typing.Optional[str] = None, env: typing.Optional[dict] = None
                           ):
        for line in self.run_output(['remote', '-v'], cwd=cwd, env=env).splitlines(keepends=False):
            if re.match(r'^' + name + r'\t', line):
                return True
        return False

    def collect_commit_details(self, commit_id: str, /, *,
                               subject: typing.Optional[str] = None,
                               cwd: typing.Optional[str] = None, env: typing.Optional[dict] = None
                               ) -> Commit:
        timestamp = int(self.run_output(['show', '-s', '--format=%at', commit_id], cwd=cwd, env=env))
        date = datetime.datetime.fromtimestamp(timestamp)
        timestamp = int(self.run_output(['show', '-s', '--format=%ct', commit_id], cwd=cwd, env=env))
        commit_date = datetime.datetime.fromtimestamp(timestamp)
        return Commit.create(commit_id,
                             author=self.run_output(['show', '-s', '--format=%an <%ae>', commit_id], cwd=cwd, env=env),
                             date=date,
                             commit_date=commit_date,
                             committer=self.run_output(['show', '-s', '--format=%cn <%ce>', commit_id], cwd=cwd,
                                                       env=env),
                             subject=subject or self.run_output(['show', '-s', '--format=%s', commit_id]),
                             distance=int(
                                 self.run_output(['rev-list', '--count', commit_id, '^HEAD'], cwd=cwd, env=env)))

    def find_commits_containing(self, text: str, /, *,
                                cwd: typing.Optional[str] = None, env: typing.Optional[dict] = None
                                ) -> typing.List[str]:
        return self.run_output(
            ['-c', 'log.decorate=', 'log', '--pretty=%H %s', '--all', '--grep', text],
            cwd=cwd, env=env).splitlines()

    def refs_of_commits(self, commit_id: str, /, *,
                        cwd: typing.Optional[str] = None, env: typing.Optional[dict] = None
                        ) -> typing.List[str]:
        return self.run_output(
            ['branch', '--format', '%(refname)', '--all', '--contains', commit_id], cwd=cwd, env=env).splitlines()


class RepoClonerRemoteConfig(Node):
    def __init__(self):
        self.name: str = ''
        self.username_cfg_entry: str = ''
        self.host_cfg_entry: str = ''
        self.prefix: str = ''
        self.url_template: str = ''
        self.excluded: typing.List[str] = []
        self.name_map: typing.Dict[str, str] = dict()
        self.custom_prefix_map: typing.Dict[str, str] = dict()


class RepoClonerConfig(Node):
    def __init__(self):
        self.primary_remote: str = ''
        self.primary_only: typing.List[str] = []
        self.remotes = NodeList(RepoClonerRemoteConfig)

    def load_from(self, data: dict):
        super().load_from(data)
        for remote in self.remotes:
            if remote.name == self.primary_remote:
                continue

            remote.excluded += self.primary_only


class RepoCloner:
    def __init__(self, config: RepoClonerConfig, base_dir: str, *, bare: bool):
        self._config = copy.deepcopy(config)
        self._basedir = base_dir
        self._bare_repos = bare
        self._primary_repo_config = [x for x in self._config.remotes if x.name == self._config.primary_remote][0]
        self._other_repo_configs = [x for x in self._config.remotes if x != self._primary_repo_config]
        self._git = Git()

    def clone(self, repo: str, *, require_fetch: bool = True, only_remotes: typing.Optional[typing.List[str]] = None):
        repo_directory = f'{self._basedir}/{repo}'
        existing = os.path.exists(repo_directory)
        if not existing:
            os.makedirs(repo_directory)
            self._git.run(['init'] + (['--bare'] if self._bare_repos else []), cwd=repo_directory)

        self._add_remote(repo, repo_directory, self._primary_repo_config, [])
        for cfg in self._other_repo_configs:
            self._add_remote(repo, repo_directory, cfg, only_remotes)

        if existing and require_fetch:
            self._git.run(['fetch', '--all'], cwd=repo_directory)

    def _add_remote(self, repo: str, repo_directory: str, remote: RepoClonerRemoteConfig,
                    remotes: typing.Optional[typing.List[str]] = None):
        if repo not in remote.excluded and (
                not remotes or remote.name in remotes) and not self._git.is_existing_remote(remote.name,
                                                                                            cwd=repo_directory):
            log_debug(f'Fetching remote: {remote.name} @ {repo}')
            self._git.run(['remote', 'add', '-f', remote.name, self._get_repo_url(repo, remote)], cwd=repo_directory)
        else:
            log_debug(f'Ignoring remote: {remote.name} @ {repo}')

    def _get_repo_url(self, repo: str, remote: RepoClonerRemoteConfig):
        username = host = prefix = ''
        if remote.username_cfg_entry:
            username = get_config().get(*remote.username_cfg_entry.rsplit('.', 1))
            if not username:
                raise Exception(f'Missing username for {remote.name} (config: core.{remote.username_cfg_entry})')
        if remote.host_cfg_entry:
            host = get_config().get(*remote.host_cfg_entry.rsplit('.', 1))
            if not host:
                raise Exception(f'Missing username  for {remote.name}(config: core.{remote.host_cfg_entry})')
        if remote.prefix:
            prefix = remote.prefix
            for r, v in remote.custom_prefix_map.items():
                if r == repo:
                    prefix = v
                    break
        if not remote.url_template:
            raise Exception(f'Missing URL template  for {remote.name} in clone-repo.yaml')
        url = remote.url_template.format(username=username, host=host, prefix=prefix, repo=repo)
        log_debug('Prepared URL', repo=repo, remote=remote.name, url=url)
        return url
