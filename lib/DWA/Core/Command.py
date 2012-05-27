import argparse
import sys


class ShowManPageAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        parser.current_command._print_manpage()
        #Utils.set_need_runtime(False)
        sys.exit(0)


class Command(object):
    description = "Basic command, base class"
    aliases = []
    parser_args = ''


    def __init__(self, prog=None):
        if not prog:
            import DWA.Core.Main
            prog = DWA.Core.Main.prog_name
        self.usage_name = self.get_name()
        self.parser = argparse.ArgumentParser(description=self.description, prog=prog, usage='%(prog)s {0} [options] {1}'.format(self.usage_name, self.parser_args), add_help=False)
        self.parser.add_argument("-h", action="help", help="Show this help message and exit")
        self.parser.add_argument("--help", action=ShowManPageAction, nargs=0, dest='help', help='Show manual page');
        self.parser.current_command = self

    @classmethod
    def get_name(cls):
        name = cls.__name__
        if name[-7:] == 'Command':
            name = name[:-7].lower()

        if not name:
            name = 'unknown'

        return name


    def _print_manpage(self):
        print("Here they come")


    def perform(self, args):
        self.opts = self.parser.parse_args(args)
        return self._perform_command()


    def _perform_command(self):
        raise NotImplementedError()
