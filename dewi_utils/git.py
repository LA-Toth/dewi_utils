# Copyright 2020-2022 Laszlo Attila Toth
# Distributed under the terms of the Apache License, Version 2.0

import copy
import datetime
import os
import re
import subprocess
from contextlib import contextmanager

from dewi_core.config.appconfig import get_config
from dewi_core.config.node import Node, NodeList
from dewi_core.logger import log_debug, log_error
from dewi_core.projects import Project


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


class Git:
    def run(self, args: list[str], /, *,
            cwd: str | None = None, env: dict | None = None):
        log_debug(f'Running git command: {args}; cwd={cwd if cwd else "current dir"}')
        subprocess.run(['git'] + args, check=True, cwd=cwd, env=env)

    def run_output(self, args: list[str], /, *,
                   cwd: str | None = None, env: dict | None = None,
                   strip: bool = True,
                   ) -> str:
        log_debug(f'Running git command with output: {args}; cwd={cwd if cwd else "current dir"}')
        result = subprocess.check_output(['git'] + args, cwd=cwd, env=env).decode('UTF-8')
        return result.strip() if strip else result

    def cd_to_repo_root(self, *,
                        cwd: str | None = None, env: dict | None = None
                        ):
        os.chdir(self.repo_root(cwd=cwd, env=env))

    def repo_root(self, *,
                  cwd: str | None = None, env: dict | None = None) -> str:
        return self.run_output(['rev-parse', '--show-toplevel'], cwd=cwd, env=env)

    def repo_name(self, *,
                  cwd: str | None = None, env: dict | None = None):
        return os.path.basename(self.repo_root(cwd=cwd, env=env))

    def current_branch(self, *,
                       cwd: str | None = None, env: dict | None = None) -> str:
        return self.run_output(['branch', '--show-current'], cwd=cwd, env=env)

    def current_head(self, *,
                     enable_detached_head=True,
                     cwd: str | None = None, env: dict | None = None) -> str:
        if not enable_detached_head and not self.current_branch(cwd=cwd, env=env):
            raise GitError(f"Detached head, directory='{cwd or os.getcwd()}'")
        return self.run_output(['rev-list', '--max-count=1', 'HEAD'], cwd=cwd, env=env)

    def merge_base(self, branch1: str, branch2: str, /, *,
                   cwd: str | None = None, env: dict | None = None):
        return self.run_output(['merge-base', branch1, branch2], cwd=cwd, env=env)

    def stash(self, *,
              cwd: str | None = None, env: dict | None = None) -> bool:
        status = self.run_output(['status', '--porcelain'], cwd=cwd, env=env).splitlines()

        for i in status:
            if 'M' in i[:2]:
                self.run(['stash'])
                return True

        return False

    def stash_apply(self, stashed: bool, /, *,
                    cwd: str | None = None, env: dict | None = None):
        if stashed:
            self.run(['stash', 'apply'], cwd=cwd, env=env)

    @contextmanager
    def with_stash(self, *,
                   cwd: str | None = None, env: dict | None = None):
        stashed = self.stash(cwd=cwd, env=env)
        yield
        self.stash_apply(stashed, cwd=cwd, env=env)

    def grep_in_commit_msg(self, text: str, /, *,
                           cwd: str | None = None, env: dict | None = None) -> list[str]:
        return self.run_output(['-c', 'log.decorate=', 'log', '--pretty=%H %s', '--all', '--grep', text],
                               cwd=cwd, env=env).splitlines()

    def branches_containing_commit(self, commit_id: str, /, *,
                                   cwd: str | None = None, env: dict | None = None) \
            -> list[str]:
        return self.run_output(['branch', '--format', '%(refname)', '--all', '--contains', commit_id],
                               cwd=cwd, env=env).splitlines()

    def is_existing_remote(self, name: str, /, *,
                           cwd: str | None = None, env: dict | None = None
                           ):
        for line in self.run_output(['remote', '-v'], cwd=cwd, env=env).splitlines(keepends=False):
            if re.match(r'^' + name + r'\t', line):
                return True
        return False

    def is_existing_local_branch(self, name: str, /, *,
                                 cwd: str | None = None, env: dict | None = None
                                 ):
        return self.run_output(['branch', '--list', name], cwd=cwd, env=env) != ''

    def collect_commit_details(self, commit_id: str, /, *,
                               subject: str | None = None,
                               cwd: str | None = None, env: dict | None = None
                               ) -> Commit:
        timestamp = int(self.run_output(['show', '-s', '--format=%at', commit_id], cwd=cwd, env=env))
        date = datetime.datetime.fromtimestamp(timestamp)
        timestamp = int(self.run_output(['show', '-s', '--format=%ct', commit_id], cwd=cwd, env=env))
        commit_date = datetime.datetime.fromtimestamp(timestamp)
        return Commit.create(commit_id=commit_id,
                             author=self.run_output(['show', '-s', '--format=%an <%ae>', commit_id], cwd=cwd, env=env),
                             date=date,
                             commit_date=commit_date,
                             committer=self.run_output(['show', '-s', '--format=%cn <%ce>', commit_id], cwd=cwd,
                                                       env=env),
                             subject=subject or self.run_output(['show', '-s', '--format=%s', commit_id]),
                             distance=int(
                                 self.run_output(['rev-list', '--count', commit_id, '^HEAD'], cwd=cwd, env=env)))

    def find_commits_containing(self, text: str, /, *,
                                cwd: str | None = None, env: dict | None = None
                                ) -> list[str]:
        return self.run_output(
            ['-c', 'log.decorate=', 'log', '--pretty=%H %s', '--all', '--grep', text],
            cwd=cwd, env=env).splitlines()

    def refs_of_commits(self, commit_id: str, /, *,
                        cwd: str | None = None, env: dict | None = None
                        ) -> list[str]:
        return self.run_output(
            ['branch', '--format', '%(refname)', '--all', '--contains', commit_id], cwd=cwd, env=env).splitlines()


class RepoClonerRemoteConfig(Node):
    name: str
    username_cfg_entry: str
    host_cfg_entry: str
    prefix: str
    url_template: str
    excluded: list[str]
    name_map: dict[str, str]
    custom_prefix_map: dict[str, str]

    def __init__(self):
        self.name = ''
        self.username_cfg_entry = ''
        self.host_cfg_entry = ''
        self.prefix = ''
        self.url_template = ''
        self.excluded = []
        self.name_map = dict()
        self.custom_prefix_map = dict()


class RepoClonerConfig(Node):
    primary_remote: str
    primary_only: list[str]
    remotes: list[RepoClonerRemoteConfig]

    def __init__(self):
        self.primary_remote = ''
        self.primary_only = []
        self.remotes = NodeList(RepoClonerRemoteConfig)

    def load_from(self, data: dict, *, raise_error: bool = False):
        super().load_from(data, raise_error=raise_error)
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

    def clone(self, repo: str, *, require_fetch: bool = True, only_remotes: list[str] | None = None):
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
                    remotes: list[str] | None = None):
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


class BranchCreator:
    def __init__(self, project: Project, repo_base_dir: str, *,
                 require_fetch: bool = True,
                 use_worktrees: bool = False,
                 print_repo_path: bool = False,
                 ):
        """
        Create a branch based on the provided Project object for one or more repositories.

        The parameters are common for every repository. The optional rebase for existing branches
        can be specified per-call
        :param project: the current Project providing branch details
        :param repo_base_dir: A directory containing the repositories in the branch should be created
                              (or the worktree belongs to)
        :param require_fetch: Defines if the project's upstream remote is fetched initially
        :param use_worktrees: Set True if git worktrees are used, or False otherwise
        :param print_repo_path: Set True to print the project repo path for each repo
        """
        self._project = project
        self._repo_base_dir = repo_base_dir
        self._require_fetch = require_fetch
        self._use_work_trees = use_worktrees
        self._print_repo_path = print_repo_path

        self._git = Git()
        self._remote_branch = f'{self._project.remote}/{self._project.upstream_branch}'

    def create(self, repo: str):
        self.create_or_rebase_branch(repo, disable_rebase=True)

    def rebase(self, repo: str):
        project_repo_dir = self._project.repo_dir(repo)
        if not os.path.exists(project_repo_dir):
            log_error('The git repo directory is missing, clone it first', repo_dir=project_repo_dir)
            raise GitError('Missing git repo: ' + project_repo_dir)

        self._git.run(['rebase', self._remote_branch], cwd=project_repo_dir)

    def create_or_rebase_branch(self, repo: str, *, disable_rebase: bool = False):
        project_repo_dir = self._project.repo_dir(repo)
        repo_dir = f'{self._repo_base_dir}/{repo}'

        self._check_dirs(project_repo_dir, repo_dir)

        if self._print_repo_path:
            self._print_directory_path(repo)

        if self._require_fetch:
            self._git.run(['fetch', self._project.remote], cwd=repo_dir)

        self._create_or_rebase_internal(project_repo_dir, repo_dir, disable_rebase)

    def _check_dirs(self, project_repo_dir: str, repo_dir: str):
        if not self._use_work_trees and repo_dir != project_repo_dir:
            log_error('Repo directory mismatch with worktrees', repo_dir=repo_dir, repo_dir_in_project=project_repo_dir,
                      use_worktrees=self._use_work_trees)
            raise GitError('Cannot create branch without worktrees and with different repo dirs')

        if not os.path.exists(repo_dir):
            log_error('The git repo directory is missing, clone it first', repo_dir=repo_dir)
            raise GitError('Missing git repo: ' + repo_dir)

    def _create_or_rebase_internal(self, project_repo_dir: str, repo_dir: str, disable_rebase: bool):
        if self._requires_checkout_or_worktree(project_repo_dir):
            self._ensure_git_branch(repo_dir)

            if self._use_work_trees:
                self._git.run(['worktree', 'add', project_repo_dir, self._project.branch], cwd=repo_dir)
            else:
                self._git.run(['checkout', self._project.branch], cwd=repo_dir)

        elif not disable_rebase:
            self._git.run(['rebase', self._remote_branch], cwd=project_repo_dir)

    def _requires_checkout_or_worktree(self, project_repo_dir: str) -> bool:
        return not os.path.exists(project_repo_dir) or (
                not self._use_work_trees and self._git.current_branch(cwd=project_repo_dir) != self._project.branch)

    def _ensure_git_branch(self, repo_dir: str):
        if not self._git.is_existing_local_branch(self._project.branch, cwd=repo_dir):
            try:
                self._git.run(['branch', self._project.branch, self._remote_branch], cwd=repo_dir)
            except subprocess.CalledProcessError:
                if self._require_fetch:
                    log_error('Required remote branch is missing after fetch', required_branch=self._remote_branch)
                    raise

                self._git.run(['fetch', self._project.remote], cwd=repo_dir)
                try:
                    self._git.run(['branch', self._project.branch, self._remote_branch], cwd=repo_dir)
                except subprocess.CalledProcessError:
                    log_error('Required remote branch is missing after fetch', required_branch=self._remote_branch)
                    raise

    def _print_directory_path(self, repo: str):
        print('--')
        print('Directory:')
        print(f' {self._project.repo_dir(repo)}')
        print('--')
