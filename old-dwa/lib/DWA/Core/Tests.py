# vim: sts=4 ts=8 et ai

import sys
import unittest
from DWA.Core import Dirs

root_dir = '/tmp'
prog_name = 'dwa'
start_time = 0


def __main(args):
    testdir = root_dir + '/tests'
    sys.path.append(testdir)

    loader = unittest.TestLoader()
    loaded_tests = loader.discover(testdir, pattern='test_*.py')

    results = unittest.TextTestRunner(verbosity=1).run(loaded_tests)
    sys.exit(1 if results.failures or results.errors else 0)


def main(dwa_root_dir, dwa_prog_name, dwa_start_time):
    global root_dir, prog_name, start_time
    (root_dir, prog_name, start_time) = \
        (dwa_root_dir, dwa_prog_name, dwa_start_time)

    Dirs.set_root_dir(root_dir)
    try:
        ret = __main(sys.argv)
        sys.exit(ret)
    except SystemExit:
        raise
