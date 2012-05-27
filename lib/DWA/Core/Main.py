# vim: sts=4 ts=8 et ai

import os
import sys
import time

import DWA.Utils.Format


root_dir = '/tmp'
prog_name = 'dwa'
start_time = 0


def print_run_time():
    runtime = time.time() - start_time
    print("\nRuntime: %s (%s seconds)" % (
                        DWA.Utils.Format.humanize_time(runtime, True),
                        runtime))


def print_run_time_and_exit(status=0):
    print_run_time()
    sys.exit(status)


def get_usage():
    return """
%(progname)s - Help developing programs and managing their SCM repo
Syntax:
\t%(progname)s <options> <command> <arguments>

For details see the manual page of the commands and the %(progname)s itself:

  %(progname)s -h
  %(progname)s <command> --help
  %(progname)s help <command>
""" % { 'progname' : prog_name }


def __main(args):
    return len(args)


def main(dwa_root_dir, dwa_prog_name, dwa_start_time):
    global root_dir, prog_name, start_time
    (root_dir, prog_name, start_time) = (dwa_root_dir, dwa_prog_name, dwa_start_time)

    try:
        ret = __main(sys.argv)
        #print("{0}: '{1}' is not a {0} command or alias" % (prog_name, command))
        #check_for_similar_name()
        #print_similar_names()
        sys.exit(ret)
    except SystemExit:
        raise
    except:
        #print(Utils.format_exception())
        print_run_time()
