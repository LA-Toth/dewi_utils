# Copyright 2018 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import csv


def load_csv_from_file(f):
    reader = csv.DictReader(f)
    data = [r for r in reader]
    return data


def load_csv(filename, encoding='UTF-8'):
    with open(filename, encoding=encoding) as f:
        return load_csv_from_file(f)
