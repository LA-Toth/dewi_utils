# Copyright 2018-2021 Laszlo Attila Toth
# Distributed under the terms of the Apache License, Version 2.0

import os
import subprocess
from zipfile import ZipFile

from dewi_core.context_managers import in_directory


class UnZip:
    def __init__(self, zip_file, output_dir):
        self._zip_file = zip_file
        self._output_dir = output_dir

    def extract(self, filtered: bool = False):
        if not filtered and os.path.exists("C:\\Program Files\\7-Zip\\7z.exe"):
            subprocess.run(
                [
                    "C:\\Program Files\\7-Zip\\7z.exe",
                    "x",
                    "-o" + self._output_dir,
                    self._zip_file
                ])
        elif not filtered and os.path.exists("/usr/bin/7z"):
            subprocess.run(
                [
                    "/usr/bin/7z",
                    "x",
                    "-o" + self._output_dir,
                    self._zip_file
                ])
        else:
            with ZipFile(self._zip_file) as f:
                with in_directory(self._output_dir):
                    members = self._get_member_list(f, filtered)
                    f.extractall(members=members)

    def extract_all(self):
        self.extract()

    def extract_filtered(self):
        self.extract(True)

    def _get_member_list(self, f: ZipFile, filtered: bool):
        members = None
        if filtered:
            members = [m.filename for m in f.infolist() if self._filter(m.filename)]
        return members

    def _filter(self, path: str):
        """
        Example:
        return path.startswith('info') or path == 'a.file.txt'
        """
        return True
