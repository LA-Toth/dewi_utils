# -*- vim: sts=4 ts=8 et ai

from __future__ import print_function

import os
import re
import sys

# Copied from Gentoo's emerge command
# /usr/lib64/portage/pym/portage/output.py
havecolor=1
dotitles=1

esc_seq = "\x1b["

g_attr = {}
g_attr["normal"]       =  0

g_attr["bold"]         =  1
g_attr["faint"]        =  2
g_attr["standout"]     =  3
g_attr["underline"]    =  4
g_attr["blink"]        =  5
g_attr["overline"]     =  6  # Why is overline actually useful?
g_attr["reverse"]      =  7
g_attr["invisible"]    =  8

g_attr["no-attr"]      = 22
g_attr["no-standout"]  = 23
g_attr["no-underline"] = 24
g_attr["no-blink"]     = 25
g_attr["no-overline"]  = 26
g_attr["no-reverse"]   = 27
# 28 isn't defined?
# 29 isn't defined?
g_attr["black"]        = 30
g_attr["red"]          = 31
g_attr["green"]        = 32
g_attr["yellow"]       = 33
g_attr["blue"]         = 34
g_attr["magenta"]      = 35
g_attr["cyan"]         = 36
g_attr["white"]        = 37
# 38 isn't defined?
g_attr["default"]      = 39
g_attr["bg_black"]     = 40
g_attr["bg_red"]       = 41
g_attr["bg_green"]     = 42
g_attr["bg_yellow"]    = 43
g_attr["bg_blue"]      = 44
g_attr["bg_magenta"]   = 45
g_attr["bg_cyan"]      = 46
g_attr["bg_white"]     = 47
g_attr["bg_default"]   = 49

# make_seq("blue", "black", "normal")
def color(fg, bg="default", attr=["normal"]):
    mystr = esc_seq[:] + "%02d" % g_attr[fg]
    for x in [bg]+attr:
        mystr += ";%02d" % g_attr[x]
    return mystr+"m"

codes={}
codes["reset"]     = esc_seq + "39;49;00m"

codes["bold"]      = esc_seq + "01m"
codes["faint"]     = esc_seq + "02m"
codes["standout"]  = esc_seq + "03m"
codes["underline"] = esc_seq + "04m"
codes["blink"]     = esc_seq + "05m"
codes["overline"]  = esc_seq + "06m"  # Who made this up? Seriously.
codes["reverse"]   = esc_seq + "07m"

ansi_color_codes = []
for x in range(30, 38):
    ansi_color_codes.append("%im" % x)
    ansi_color_codes.append("%i;01m" % x)

rgb_ansi_colors = ['0x000000', '0x555555', '0xAA0000', '0xFF5555', '0x00AA00',
    '0x55FF55', '0xAA5500', '0xFFFF55', '0x0000AA', '0x5555FF', '0xAA00AA',
    '0xFF55FF', '0x00AAAA', '0x55FFFF', '0xAAAAAA', '0xFFFFFF']

for x in range(len(rgb_ansi_colors)):
    codes[rgb_ansi_colors[x]] = esc_seq + ansi_color_codes[x]

del x

codes["black"]     = codes["0x000000"]
codes["darkgray"]  = codes["0x555555"]

codes["red"]       = codes["0xFF5555"]
codes["darkred"]   = codes["0xAA0000"]

codes["green"]     = codes["0x55FF55"]
codes["darkgreen"] = codes["0x00AA00"]

codes["yellow"]    = codes["0xFFFF55"]
codes["brown"]     = codes["0xAA5500"]

codes["blue"]      = codes["0x5555FF"]
codes["darkblue"]  = codes["0x0000AA"]

codes["fuchsia"]   = codes["0xFF55FF"]
codes["purple"]    = codes["0xAA00AA"]

codes["turquoise"] = codes["0x55FFFF"]
codes["teal"]      = codes["0x00AAAA"]

codes["white"]     = codes["0xFFFFFF"]
codes["lightgray"] = codes["0xAAAAAA"]

codes["darkteal"]   = codes["turquoise"]
# Some terminals have darkyellow instead of brown.
codes["0xAAAA00"]   = codes["brown"]
codes["darkyellow"] = codes["0xAAAA00"]

codes["bg_black"]      = esc_seq + "40m"
codes["bg_darkred"]    = esc_seq + "41m"
codes["bg_darkgreen"]  = esc_seq + "42m"
codes["bg_brown"]      = esc_seq + "43m"
codes["bg_darkblue"]   = esc_seq + "44m"
codes["bg_purple"]     = esc_seq + "45m"
codes["bg_teal"]       = esc_seq + "46m"
codes["bg_lightgray"]  = esc_seq + "47m"

codes["bg_darkyellow"] = codes["bg_brown"]

# Colors from /etc/init.d/functions.sh
codes["NORMAL"]     = esc_seq + "0m"
codes["GOOD"]       = codes["green"]
codes["WARN"]       = codes["yellow"]
codes["BAD"]        = codes["red"]
codes["HILITE"]     = codes["teal"]
codes["BRACKET"]    = codes["blue"]

# Portage functions
codes["INFORM"]                  = codes["darkgreen"]
codes["UNMERGE_WARN"]            = codes["red"]
codes["SECURITY_WARN"]           = codes["red"]
codes["MERGE_LIST_PROGRESS"]     = codes["yellow"]
codes["PKG_BLOCKER"]             = codes["red"]
codes["PKG_BLOCKER_SATISFIED"]   = codes["darkblue"]
codes["PKG_MERGE"]               = codes["darkgreen"]
codes["PKG_MERGE_SYSTEM"]        = codes["darkgreen"]
codes["PKG_MERGE_WORLD"]         = codes["green"]
codes["PKG_UNINSTALL"]           = codes["red"]
codes["PKG_NOMERGE"]             = codes["darkblue"]
codes["PKG_NOMERGE_SYSTEM"]      = codes["darkblue"]
codes["PKG_NOMERGE_WORLD"]       = codes["blue"]
codes["PROMPT_CHOICE_DEFAULT"]   = codes["green"]
codes["PROMPT_CHOICE_OTHER"]     = codes["red"]

codes["GIT_FETCH"]               = codes["green"]
codes["GIT_FETCH_TAG"]           = codes["blue"]

def nc_len(mystr):
    tmp = re.sub(esc_seq + "^m]+m", "", mystr);
    return len(tmp)

_legal_terms_re = re.compile(r'^(xterm|xterm-color|Eterm|aterm|rxvt|screen|kterm|rxvt-unicode|gnome|interix)')
_disable_xtermTitle = None
_max_xtermTitle_len = 253

def xtermTitle(mystr, raw=False):
    global _disable_xtermTitle
    if _disable_xtermTitle is None:
        _disable_xtermTitle = not (sys.stderr.isatty() and \
        'TERM' in os.environ and \
        _legal_terms_re.match(os.environ['TERM']) is not None)

    if dotitles and not _disable_xtermTitle:
        # If the title string is too big then the terminal can
        # misbehave. Therefore, truncate it if it's too big.
        if len(mystr) > _max_xtermTitle_len:
            mystr = mystr[:_max_xtermTitle_len]
        if not raw:
            mystr = '\x1b]0;%s\x07' % mystr
        sys.stderr.write(mystr)
        sys.stderr.flush()

default_xterm_title = None

def xtermTitleReset():
    global default_xterm_title
    if default_xterm_title is None:
        prompt_command = os.getenv('PROMPT_COMMAND')
        if prompt_command == "":
            default_xterm_title = ""
        elif prompt_command is not None:
            if dotitles and "TERM" in os.environ and sys.stderr.isatty():
                from portage.process import find_binary, spawn
                shell = os.environ.get("SHELL")
                if not shell or not os.access(shell, os.EX_OK):
                    shell = find_binary("sh")
                if shell:
                    spawn([shell, "-c", prompt_command], env=os.environ,
                        fd_pipes={0:sys.stdin.fileno(),1:sys.stderr.fileno(),
                        2:sys.stderr.fileno()})
                else:
                    os.system(prompt_command)
            return
        else:
            pwd = os.getenv('PWD','')
            home = os.getenv('HOME', '')
            if home != '' and pwd.startswith(home):
                pwd = '~' + pwd[len(home):]
            default_xterm_title = '\x1b]0;%s@%s:%s\x07' % (
                os.getenv('LOGNAME', ''), os.getenv('HOSTNAME', '').split('.', 1)[0], pwd)
    xtermTitle(default_xterm_title, raw=True)

def notitles():
    "turn off title setting"
    dotitles=0

def nocolor():
    "turn off colorization"
    global havecolor
    havecolor=0

def resetColor():
    return codes["reset"]

def colorize(color_key, text):
    global havecolor
    if havecolor:
        return codes[color_key] + text + codes["reset"]
    else:
        return text

compat_functions_colors = ["bold","white","teal","turquoise","darkteal",
    "fuchsia","purple","blue","darkblue","green","darkgreen","yellow",
    "brown","darkyellow","red","darkred"]

def create_color_func(color_key):
    def derived_func(*args):
        newargs = list(args)
        newargs.insert(0, color_key)
        return colorize(*newargs)
    return derived_func

for c in compat_functions_colors:
    globals()[c] = create_color_func(c)

def get_term_size():
    """
    Get the number of lines and columns of the tty that is connected to
    stdout.  Returns a tuple of (lines, columns) or (-1, -1) if an error
    occurs. The curses module is used if available, otherwise the output of
    `stty size` is parsed.
    """
    if not sys.stdout.isatty():
        return -1, -1
    try:
        import curses
        try:
            curses.setupterm()
            return curses.tigetnum('lines'), curses.tigetnum('cols')
        except curses.error:
            pass
    except ImportError:
        pass
    try:
        out = run_command('stty size', silent=True, fetch_out=True)
        out = out.split()
        if len(out) == 2:
            try:
                return int(out[0]), int(out[1])
            except ValueError:
                pass
    except:
        pass
    return -1, -1

def set_term_size(lines, columns, fd):
    """
    Set the number of lines and columns for the tty that is connected to fd.
    For portability, this simply calls `stty rows $lines columns $columns`.
    """
    from portage.process import spawn
    cmd = ["stty", "rows", str(lines), "columns", str(columns)]
    try:
        spawn(cmd, env=os.environ, fd_pipes={0:fd})
    except CommandNotFound:
        writemsg("portage: stty: command not found\n", noiselevel=-1)

class EOutput(object):
    """
    Performs fancy terminal formatting for status and informational messages.

    The provided methods produce identical terminal output to the eponymous
    functions in the shell script C{/sbin/functions.sh} and also accept
    identical parameters.

    This is not currently a drop-in replacement however, as the output-related
    functions in C{/sbin/functions.sh} are oriented for use mainly by system
    init scripts and ebuilds and their output can be customized via certain
    C{RC_*} environment variables (see C{/etc/conf.d/rc}). B{EOutput} is not
    customizable in this manner since it's intended for more general uses.
    Likewise, no logging is provided.

    @ivar quiet: Specifies if output should be silenced.
    @type quiet: BooleanType
    @ivar term_columns: Width of terminal in characters. Defaults to the value
        specified by the shell's C{COLUMNS} variable, else to the queried tty
        size, else to C{80}.
    @type term_columns: IntType
    """

    def __init__(self, quiet=False):
        self.__last_e_cmd = ""
        self.__last_e_len = 0
        self.quiet = quiet
        lines, columns = get_term_size()
        if columns <= 0:
            columns = 80
        # Adjust columns so that eend works properly on a standard BSD console.
        if os.environ.get("TERM") in ("cons25", "dumb"):
            columns = columns - 1
        self.term_columns = columns
        sys.stdout.flush()
        sys.stderr.flush()

    def __eend(self, caller, errno, msg):
        if errno == 0:
            status_brackets = colorize("BRACKET", "[ ") + colorize("GOOD", "ok") + colorize("BRACKET", " ]")
        else:
            status_brackets = colorize("BRACKET", "[ ") + colorize("BAD", "!!") + colorize("BRACKET", " ]")
            if msg:
                if caller == "eend":
                    self.eerror(msg[0])
                elif caller == "ewend":
                    self.ewarn(msg[0])
        if self.__last_e_cmd != "ebegin":
            self.__last_e_len = 0
        if not self.quiet:
            out = sys.stdout
            out.write("%*s%s\n" % ((self.term_columns - self.__last_e_len - 6),
                "", status_brackets))
            out.flush()

    def ebegin(self, msg):
        """
        Shows a message indicating the start of a process.

        @param msg: A very brief (shorter than one line) description of the
            starting process.
        @type msg: StringType
        """
        msg += " ..."
        if not self.quiet:
            self.einfon(msg)
        self.__last_e_len = len(msg) + 4
        self.__last_e_cmd = "ebegin"

    def eend(self, errno, *msg):
        """
        Indicates the completion of a process, optionally displaying a message
        via L{eerror} if the process's exit status isn't C{0}.

        @param errno: A standard UNIX C{errno} code returned by processes upon
            exit.
        @type errno: IntType
        @param msg: I{(optional)} An error message, typically a standard UNIX
            error string corresponding to C{errno}.
        @type msg: StringType
        """
        if not self.quiet:
            self.__eend("eend", errno, msg)
        self.__last_e_cmd = "eend"

    def eerror(self, msg):
        """
        Shows an error message.

        @param msg: A very brief (shorter than one line) error message.
        @type msg: StringType
        """
        out = sys.stderr
        if not self.quiet:
            if self.__last_e_cmd == "ebegin":
                out.write("\n")
            out.write(colorize("BAD", " * ") + msg + "\n")
            out.flush()
        self.__last_e_cmd = "eerror"

    def einfo(self, msg):
        """
        Shows an informative message terminated with a newline.

        @param msg: A very brief (shorter than one line) informative message.
        @type msg: StringType
        """
        out = sys.stdout
        if not self.quiet:
            if self.__last_e_cmd == "ebegin":
                out.write("\n")
            out.write(colorize("GOOD", " * ") + msg + "\n")
            out.flush()
        self.__last_e_cmd = "einfo"

    def einfon(self, msg):
        """
        Shows an informative message terminated without a newline.

        @param msg: A very brief (shorter than one line) informative message.
        @type msg: StringType
        """
        out = sys.stdout
        if not self.quiet:
            if self.__last_e_cmd == "ebegin":
                out.write("\n")
            out.write(colorize("GOOD", " * ") + msg)
            out.flush()
        self.__last_e_cmd = "einfon"

    def ewarn(self, msg):
        """
        Shows a warning message.

        @param msg: A very brief (shorter than one line) warning message.
        @type msg: StringType
        """
        out = sys.stderr
        if not self.quiet:
            if self.__last_e_cmd == "ebegin":
                out.write("\n")
            out.write(colorize("WARN", " * ") + msg + "\n")
            out.flush()
        self.__last_e_cmd = "ewarn"

    def ewend(self, errno, *msg):
        """
        Indicates the completion of a process, optionally displaying a message
        via L{ewarn} if the process's exit status isn't C{0}.

        @param errno: A standard UNIX C{errno} code returned by processes upon
            exit.
        @type errno: IntType
        @param msg: I{(optional)} A warning message, typically a standard UNIX
            error string corresponding to C{errno}.
        @type msg: StringType
        """
        if not self.quiet:
            self.__eend("ewend", errno, msg)
        self.__last_e_cmd = "ewend"

# end of copied code

# force immediate setup of havecolor and _disable_xtermTitle
if _disable_xtermTitle is None:
    _disable_xtermTitle = not (sys.stderr.isatty() and \
    'TERM' in os.environ and \
    _legal_terms_re.match(os.environ['TERM']) is not None)

if _disable_xtermTitle:
    nocolor()

# Output object exists always...
out = EOutput()


def set_screen_title(str):
    xtermTitle(str);

def info(str):
    if type(str) == type([]):
        str = ''.join(str)
    out.einfo(str)

def error(str):
    if type(str) == type([]):
        str = ''.join(str)
    out.eerror(str)
