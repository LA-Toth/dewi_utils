# Copyright 2009-2019 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3
# The license can be found in COPYING file or on http://www.gnu.org/licenses/

import sys
import textwrap
import typing


class ConfigPage:
    def __init__(self, prompt: str, help: typing.Optional[str] = None):
        self.prompt = prompt
        self.help = help

    def _print(self, *args, **kwargs):
        """Wraps builtin print() for unit testing"""
        print(*args, **kwargs)

    def _print_help(self):
        lines = textwrap.wrap(self.help, 72)
        self._print()
        for line in lines:
            self._print("  %s" % (line,))
        self._print()

    def _get_line(self) -> str:
        res = sys.stdin.readline()[0:-1]
        return res

    def yesno(self, default_true: bool = True, print_only: bool = False):
        if default_true:
            sel = "Y/n"
            default_val = 'y'
        else:
            sel = "y/N"
            default_val = 'n'

        if self.help:
            sel += "/?"

        answer = None

        if print_only:
            answer = default_val
            self._print(f"{self.prompt} [{sel}]: {answer}")

        while answer is None:
            self._print(f"{self.prompt} [{sel}]:", end=' ')
            sys.stdout.flush()
            res = self._get_line()
            if not res:
                answer = default_val
                break
            else:
                res = res.lower()
                if res == 'y' or res == 'n':
                    answer = res
                    break
                elif self.help and res == '?':
                    self._print_help()
        return answer == 'y'

    def input(self, default_val: typing.Optional[str] = None, print_only: bool = False):
        if self.help:
            sel = ' / ?:'
        else:
            sel = ':'

        answer = None

        defval_str = default_val if default_val is not None else ''

        if print_only:
            answer = default_val
            self._print(f'{self.prompt}  [{defval_str}]{sel} {answer}')

        while answer is None:
            self._print(f'{self.prompt}  [{defval_str}]{sel}', end=' ')
            sys.stdout.flush()
            ans = self._get_line()
            if self.help and ans == '?':
                self._print_help()
            elif ans:
                # not empty
                answer = ans
                break
            elif default_val is not None or not sys.stdin.isatty():
                answer = default_val
                break

        return answer
