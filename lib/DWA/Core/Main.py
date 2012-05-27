# vim: sts=4 ts=8 et ai

import os
import sys
import time

import DWA.Utils.Format


root_dir = '/tmp'
prog_name = 'dwa'
start_time = 0

__command = None


def print_run_time():
    runtime = time.time() - start_time
    print("\nRuntime: %s (%s seconds)" % (
                        DWA.Utils.Format.humanize_time(runtime, True),
                        runtime))


def print_run_time_and_exit(status=0):
    print_run_time()
    sys.exit(status)


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

    if not found:
        return False

    try:
        Command.running_command = cmd
        cmdobj = cmdclass()
        print_run_time_and_exit(cmdobj.perform(args[1:]))
    except KeyboardInterrupt:
        print("Interrupted!")
        print_run_time_and_exit(1)
    #except ZWAError as e:
    #    print(Utils.add_frame("General failure: \n%s" % e))
    #    print_run_time_and_exit(2)
    except SystemExit:
        raise
    except Exception as e:
        #print_error(e)
        print(e)
        print_run_time_and_exit(3)

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


def __main(args):
    if not os.isatty(1):
        sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
        sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 0)

    if len(args) == 0:
        print(__get_usage())
        sys.exit(0)
    elif args[0] == 'help':
        #Utils.print_man_page(args[1:], get_usage())
        sys.exit(0)

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

    try:
        ret = __main(sys.argv[1:])
        print("{0}: '{1}' is not a {0} command or alias".format(prog_name, __command))
        #check_for_similar_name()
        #print_similar_names()
        sys.exit(ret)
    except SystemExit:
        raise
    except Exception as e:
        print(e)
        #print(Utils.format_exception())
        print_run_time()
