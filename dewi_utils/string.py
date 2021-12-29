# Copyright 2018-2021 Laszlo Attila Toth
# Distributed under the terms of the Apache License, Version 2.0

import typing


def rjust(s: str, width: int, fillchars: typing.Optional[str] = None):
    if fillchars is None:
        return s.rjust(width)
    elif len(fillchars) == 1:
        return s.rjust(width, fillchars)

    remaining = width - len(s)

    if remaining < 0:
        return s

    else:
        padding_ = fillchars * (remaining // len(fillchars))
        padding_ += fillchars[0:remaining - len(padding_)]

        return padding_ + s


def ljust(s: str, width: int, fillchars: typing.Optional[str] = None):
    if fillchars is None:
        return s.ljust(width)
    elif len(fillchars) == 1:
        return s.ljust(width, fillchars)

    remaining = width - len(s)

    if remaining < 0:
        return s

    else:
        padding_ = fillchars * (remaining // len(fillchars))
        padding_ += fillchars[0:remaining - len(padding_)]

        return s + padding_


def center(s: str, width: int, fillchars: typing.Optional[str] = None):
    if fillchars is None:
        return s.center(width)
    elif len(fillchars) == 1:
        return s.center(width, fillchars)

    size = len(s)
    remaining = width - size

    if remaining < 0:
        return s

    else:
        left = remaining // 2
        return ljust(rjust(s, left + size, fillchars), width, fillchars)
