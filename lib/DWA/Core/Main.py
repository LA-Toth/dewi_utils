# vim: sts=4 ts=8 et ai

import argparse
import os
import sys
import time

import DWA.Core.State as State
import DWA.Utils.Exceptions
import DWA.Utils.Format
from DWA.Core.FrontController import FrontController


root_dir = '/tmp'
prog_name = 'dwa'
start_time = 0


def __print_run_time():
    runtime = time.time() - start_time
    print("\nRuntime: {} ({} seconds)".format(
                        DWA.Utils.Format.humanize_time(runtime, True),
                        runtime))


def __print_run_time_and_exit(status=0):
    __print_run_time()
    sys.exit(status)


def __print_error(e):
    filename = State.get_dir('/var/exception.txt')
    f = open(filename, 'wt')
    print(DWA.Utils.Exceptions.format_exception(), file=f)
    f.close()
    print(DWA.Utils.Format.add_frame(
            ("An error occured, consult file '%s'.\n\n" +
             "Error type: %s\nMessage: %s\n") % (
                filename, e.__class__.__name__, e)))


def __get_usage():
    return """
%(progname)s - Help developing programs and managing their SCM repo
Syntax:
\t%(progname)s <options> <command> <arguments>

For details see the manual page of the commands and the %(progname)s itself:

  %(progname)s -h
  %(progname)s <command> --help
  %(progname)s help <command>
""" % { 'progname' : prog_name }


def __get_parsed_args(args):
    parser = argparse.ArgumentParser(prog=prog_name,
                                     usage='%(prog)s [options] [command [command-args]]',
                                     add_help=False)
    parser.add_argument("-h", action="help", help="Show this help message and exit")
    parser.add_argument("--help", action="store_true", dest='help', help='Show manual page');
    #parser.add_argument('-l', '--list', action='store_true', dest='list_commands', help='List available commands');
    #parser.add_argument('-L', '--list-all', action='store_true', dest='list_all_commands',
    #                    help='List available commands, including commands within zwa tools');
    #parser.add_argument('-N', '--notify-script', dest='notify_script', help='Run notification script before exit')
    #parser.add_argument('-n', '--notify', action='store_true', dest='notify', help='Run built-in notification before exit (if -N is not used)')
    parser.add_argument('command_and_args', nargs=argparse.REMAINDER,
                        help='Command to be run with its options and arguments')
    return parser.parse_args(args)



def __print_similar_names(values):
    if len(values) == 0:
        return

    if len(values) == 1:
        print("\nDid you mean this?")
    else:
        print("\nDid you mean one of these?")
    for cmd in values:
        print("\t%s" % (cmd,))


def __main(args):
    if not os.isatty(1):
        sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
        sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 0)

    parsed_args = __get_parsed_args(args)

    if parsed_args.help:
        print("man page of %s" % prog_name)
        sys.exit(0)
    #elif other options

    if len(parsed_args.command_and_args) == 0:
        print(__get_usage())
        sys.exit(0)
    elif parsed_args.command_and_args[0] == 'help':
        #Utils.print_man_page(args[1:], get_usage())
        print("help cmd - man page")
        sys.exit(0)

    import DWA.Commands as cmds
    # Avoid warning icon in eclipse
    cmds.loaded = True
    controller = FrontController()
    command_found, value = controller.process_args(parsed_args.command_and_args)
    if command_found:
        sys.exit(value)
    else:
        __print_similar_names(value)
        sys.exit(120)


def main(dwa_root_dir, dwa_prog_name, dwa_start_time):
    global root_dir, prog_name, start_time, __command
    (root_dir, prog_name, start_time) = (dwa_root_dir, dwa_prog_name, dwa_start_time)

    State.root_dir = root_dir
    try:
        ret = __main(sys.argv[1:])
        print("{0}: '{1}' is not a {0} command or alias".format(prog_name, __command))
        #__check_for_similar_name()
        #__print_similar_names()
        sys.exit(ret)
    except SystemExit:
        raise
    except Exception as e:
        __print_error(e)
        __print_run_time()
        sys.exit(1)
