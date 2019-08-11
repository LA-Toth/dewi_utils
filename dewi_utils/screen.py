# Copyright 2019 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3


def add_frame(s: str):
    lines = s.split('\n')
    res = '#' * 80
    res += '\n'
    for line in lines:
        res += f'# {line}\n'

    res += '#' * 80
    res += '\n'
    return res
