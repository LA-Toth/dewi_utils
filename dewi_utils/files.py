# Copyright 2019-2021 Laszlo Attila Toth
# Distributed under the terms of the Apache License, Version 2.0

import hashlib
import os
import os.path

from dewi_core.logger import log_info


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
