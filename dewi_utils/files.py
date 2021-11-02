# Copyright 2019-2021 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import hashlib
import os
import os.path
import typing

from dewi_core.logger import log_info


def find_file_recursively(filename: str, directory_name: typing.Optional[str] = None) -> typing.Optional[str]:
    """
    Searches a filename in directory_name directory or in current directory
    if directory_name is None, or in their parent directories if the filename file
    is not found in the specific directory.

    The behaviour is the same as how git finds .gitignore, .git/ and other entries.

    :param filename: the filename to be found
    :param directory_name: the start directory, or if it is None: current directory
    :return: the absolute path of the searched file or None if it is not found
    """

    def maybe_file(filename: str, directory_name: str) -> typing.Optional[str]:
        full_path = os.path.join(directory_name, filename)
        if os.path.exists(full_path):
            return full_path
        else:
            return None

    directory_name = os.path.abspath(directory_name) if directory_name else os.getcwd()
    fname = maybe_file(filename, directory_name)
    while fname is None and directory_name and directory_name != os.path.sep:
        directory_name = os.path.dirname(directory_name)
        fname = maybe_file(filename, directory_name)

    return fname


def _collect_entries(rootdir: str, basedir: str):
    """
    Collectes entries in rootdir's basedir directory which is always relateive to rootdir.
    """

    files = []
    dirs = []

    for entry in os.listdir(os.path.join(rootdir, basedir)):
        rel_path = os.path.join(basedir, entry)
        full_path = os.path.join(rootdir, rel_path)
        isdir = os.path.isdir(full_path)
        if isdir and (rel_path in ('./.git', './.pytest_cache') or entry == '__pycache__'):
            continue

        st = os.stat(full_path, follow_symlinks=False)

        (dirs if isdir else files).append((rel_path, dict(isdir=isdir, path=rel_path, size=(0 if isdir else st.st_size),
                                                          mode=st.st_mode, omode=f'{st.st_mode:04o}',
                                                          mtime=int(st.st_mtime))))

    for rel_path, entry in sorted(dirs):
        yield entry
        yield from _collect_entries(rootdir, rel_path)

    for _, entry in sorted(files):
        yield entry


def python_repo_hash_md5(root_dir: str, *, verbose: bool = False):
    """
    Return MD5 hash's hexdigest bases on non-git non-pycache entries of the root_dir.

    The purpose is to check if two directory is identical except the modification dates.
    The two directories can be on different machines when the file transfer would be costly.
    """
    m = hashlib.md5()
    for e in _collect_entries(root_dir, '.'):
        if verbose:
            log_info('Processing e', e)
        m.update(
            f"path={e['path']}\tisdir={e['isdir']}\tsize={e['size']}\tmode={e['mode']:03o}\tmtime={e['mtime']}\n"
                .encode('UTF-8'))

    return m.hexdigest()
