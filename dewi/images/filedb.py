# Copyright (C) 2017 Tóth, László Attila
# Distributed under the terms of GNU  General Public License v3
# The license can be found in COPYING file or on http://www.gnu.org/licenses/

import sqlite3
import typing

from dewi.images.fileentry import FileEntry


class FileDatabase:
    def __init__(self, filename: str):
        self.filename = filename
        self.in_memory = filename == ':memory:'

        self._conn = sqlite3.connect(self.filename)
        self._ensure_tables()
        self._changed = False

    def _ensure_tables(self):
        c = self._conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS photo_file_info (
                            orig_filename text,
                            mod_date_as_dirname text,
                            upper_basename text,
                            filesize integer,
                            mod_date integer,
                            checksum text
                     )''')

        c.execute('''CREATE INDEX IF NOT EXISTS photo_orig_file_name_idx ON photo_file_info (orig_filename)''')
        c.execute('''CREATE UNIQUE INDEX IF NOT EXISTS photo_file_info_uniq_rows
                                  ON photo_file_info
                                  (orig_filename, upper_basename, filesize, mod_date, checksum)
                           ''')
        self._conn.commit()

    def close(self):
        self.commit()
        self._conn.close()

    def commit(self):
        if self._changed:
            self._conn.commit()
            self._changed = False

    def insert(self, file_entry: FileEntry, checksum: typing.Optional[str] = None):
        self._conn.execute('INSERT INTO photo_file_info'
                           ' VALUES (?,?,?, ?,?,?)',
                           [
                               file_entry.orig_path,
                               file_entry.target_dir_part,
                               file_entry.uppercase_basename,
                               file_entry.size,
                               file_entry.mod_date,
                               checksum or '',
                           ])
        self._changed = True

    def iterate(self):
        c = self._conn.cursor()
        for row in c.execute('SELECT * FROM photo_file_info ORDER BY orig_filename'):
            yield row

    def __contains__(self, item: str):
        c = self._conn.cursor()
        t = (item,)
        return c.execute('SELECT orig_filename FROM photo_file_info WHERE orig_filename=?', t).fetchone() is not None
