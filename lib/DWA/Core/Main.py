# vim: sts=4 ts=8 et ai

import argparse
import os
import sys
import time

import DWA.Core.State as State
import DWA.Utils.Exceptions
import DWA.Utils.Format
import DWA.Utils.Algorithm
from DWA.Core.FrontController import FrontController


root_dir = '/tmp'
prog_name = 'dwa'
start_time = 0

__command = None
__command_list = []
__cmd_list_w = {}
__possible_commands = []


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


#
# Run command or alias
#

def __handle_command(args):
    import DWA.Commands as Commands
    import DWA.Core.Command as Command

    global __command
    cmd = args[0]
    __command = cmd

    found = False
    for cmdname in dir(Commands):
        cmdclass = getattr(Commands, cmdname)
        if type(cmdclass) == type and issubclass(cmdclass, Command.Command):
            if (cmd == cmdclass.get_name() or cmd in cmdclass.aliases):
                found = True
                break
            else:
                __command_list.append(cmdclass.get_name())
                if cmdclass.aliases:
                    __command_list.append(cmdclass.aliases)

    if not found:
        return False

    try:
        Command.running_command = cmd
        cmdobj = cmdclass()
        __print_run_time_and_exit(cmdobj.perform(args[1:]))
    except KeyboardInterrupt:
        print("Interrupted!")
        __print_run_time_and_exit(1)
    #except DWAError as e:
    #    print(Utils.add_frame("General failure: \n%s" % e))
    #    __print_run_time_and_exit(2)
    except SystemExit:
        raise
    except Exception as e:
        __print_error(e)
        __print_run_time_and_exit(3)


def __handle_alias(args):
    return None
    #aliases = ...
    newcmd = aliases.get_alias(args[0])

    if newcmd:
        shell = '/bin/sh'
        if newcmd[0] == '!' or newcmd[0] =='?':
            if newcmd[0] == '?':
                shell = '/bin/bash'
            cmd = args[1:]
            cmd[0:0] = [ newcmd[1:] ]
            Utils.run_command(string.join(cmd), silent=1, shell=shell)
            sys.exit(0)
        else:
            args[0:1] = newcmd.split(' ')
            return args


def __levenshtein_compare(s1, s2):
    l1 = __cmd_list_w[s1]
    l2 = __cmd_list_w[s2]
    if l1 != l2:
        return l1 - l2
    else:
        return s1 <= s2


def __check_for_similar_name():
    if not __command:
        return
    global __command_list
    global __cmd_list_w
    __command_list = DWA.Utils.Algorithm.qsort(__command_list)

    for cmd in __command_list:
        __cmd_list_w[cmd] = DWA.Utils.Algorithm.levenhstein(__command, cmd, 0, 2, 1, 4)

    command_list = DWA.Utils.Algorithm.qsort(__command_list, __levenshtein_compare)

    best_similarity = __cmd_list_w[__command_list[0]]
    n = 1
    l = len(command_list)
    while (n < l and best_similarity == __cmd_list_w[__command_list[n]]):
        n=n+1

    if n < 6:
        for i in range(0, n):
            __possible_commands.append(__command_list[i])


def __print_similar_names():
    if len(__possible_commands) == 0:
        return

    if len(__possible_commands) == 1:
        print("\nDid you mean this?")
    else:
        print("\nDid you mean one of these?")
    for cmd in __possible_commands:
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
    sys.exit(controller.process_args(parsed_args.command_and_args))

def __old_handler(args):
    done = False
    while True:
        __handle_command(args)

        if done:
            return 2

        args = __handle_alias(args)
        if not args:
            return 2
        done = True


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
