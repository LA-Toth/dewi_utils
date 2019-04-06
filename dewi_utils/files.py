# Copyright 2019 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3
import os.path
import typing


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

    directory_name = os.path.abspath(directory_name)
    fname = maybe_file(filename, directory_name)
    while fname is None and directory_name and directory_name != os.path.sep:
        directory_name = os.path.dirname(directory_name)
        fname = maybe_file(filename, directory_name)

    return fname
