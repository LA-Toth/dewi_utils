# Copyright 2017-2022 Laszlo Attila Toth
# Distributed under the terms of the Apache License, Version 2.0

import os
import sys


def find_binary(binary: str, *, exact: bool = False) -> str | None:
    """
    Find binary in PATH.

    On UNIX systems 'binary' must match the basename of the found binary.
    On Windows depending the 'exact' parameter:
      * exact=True: the basename must match
      * exact=False: the basename must match or appending the extensions in PATHEXT the extended name must match

    An example:
    find_binary('python') results either '/usr/bin/python' or 'C:\Program Files\Python\Python35\python.exe'
    find_binary('python', exact=True) results '/usr/bin/python' on Unix or None on Windows

    Args:
        binary (str): basename - command - to be found. On Windows, it can be with or without extension
        exact (bool): on Windows, if it is False, use PATHEXT variable, too

    Returns:
        str|None: The full path of the binary if found, otherwise None
    """

    paths = os.environ.get('PATH', '').split(os.path.pathsep)

    path_exts = ['']
    if sys.platform == 'win32' and not exact:
        path_exts += os.environ.get('PATHEXT', '').split(os.path.pathsep)

    for path in sorted(paths):
        for path_ext in path_exts:
            filename = os.path.join(path, binary + path_ext)
            if os.access(filename, os.X_OK) and os.path.isfile(filename):
                return filename

    return None


def which(binary: str, *, exact: bool = False) -> str | None:
    return find_binary(binary, exact=exact)
