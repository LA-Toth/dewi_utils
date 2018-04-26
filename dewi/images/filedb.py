# Copyright 2017-2018 Tóth, László Attila
# Distributed under the terms of the GNU Lesser General Public License v3
# The license can be found in COPYING file or on http://www.gnu.org/licenses/

import os.path
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
                            orig_filename TEXT,
                            mod_date_as_dirname TEXT,
                            upper_basename TEXT,
                            filesize INTEGER,
                            mod_date INTEGER,
                            checksum TEXT
                     )''')

        c.execute('''CREATE INDEX IF NOT EXISTS photo_orig_file_name_idx ON photo_file_info (orig_filename)''')
        c.execute('''CREATE UNIQUE INDEX IF NOT EXISTS photo_file_info_uniq_rows
                                  ON photo_file_info
                                  (orig_filename, upper_basename, filesize, mod_date, checksum)
                           ''')

        c.execute('''CREATE TABLE IF NOT EXISTS photo_file_info_new_path_map (
                            file_info_id INTEGER,
                            new_filename TEXT,
                            FOREIGN KEY(file_info_id) REFERENCES photo_file_info(rowid)
                      )''')

        c.execute('''CREATE UNIQUE INDEX IF NOT EXISTS photo_file_info_new_path_map_uniq_rows
                                      ON photo_file_info_new_path_map
                                      (file_info_id, new_filename)
                               ''')

        self._conn.commit()

    def close(self):
        self.commit()
        self._conn.close()

    def commit(self):
        if self._changed:
            self._conn.commit()
            self._changed = False

    def rollback(self):
        if self._changed:
            self._conn.rollback()
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

    def insert_new_path(self, file_info_id: int, path: str):
        self._conn.execute('INSERT INTO photo_file_info_new_path_map VALUES(?, ?)', [file_info_id, path])
        self._changed = True

    def has_new_path_info(self):
        c = self._conn.cursor()
        return c.execute('SELECT count(*) FROM photo_file_info_new_path_map').fetchone()[0] > 0

    def iterate(self):
        c = self._conn.cursor()
        for row in c.execute('SELECT *,rowid FROM photo_file_info ORDER BY orig_filename'):
            yield row

    def iterate_photo_entries(self) -> typing.Iterable[FileEntry]:
        c = self._conn.cursor()
        for db_entry in c.execute('SELECT *,rowid FROM photo_file_info ORDER BY orig_filename'):
            yield FileEntry(db_entry[0], os.path.basename(db_entry[0]),
                            db_entry[2], db_entry[4], db_entry[3], db_entry[5], db_entry[6])

    def iterate_target_path_entries(self) -> typing.Iterable[typing.Tuple[str, FileEntry]]:
        c = self._conn.cursor()
        c2 = self._conn.cursor()
        for entry_id, path in c.execute('SELECT * FROM photo_file_info_new_path_map ORDER BY new_filename'):
            db_entry = c2.execute('SELECT  *,rowid FROM photo_file_info WHERE rowid=?', (entry_id,)).fetchone()
            yield path, FileEntry(db_entry[0], os.path.basename(db_entry[0]),
                                  db_entry[2], db_entry[4], db_entry[3], db_entry[5], db_entry[6])

    def __contains__(self, item: str):
        c = self._conn.cursor()
        t = (item,)
        return c.execute('SELECT orig_filename FROM photo_file_info WHERE orig_filename=?', t).fetchone() is not None

    def count(self):
        c = self._conn.cursor()
        return c.execute('SELECT count(*) FROM photo_file_info').fetchone()[0]
