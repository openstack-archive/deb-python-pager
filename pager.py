#!/usr/bin/env python
"""
Page output and find dimensions of console.

This module deals with paging on Linux terminals and Windows consoles in
a cross-platform way. The major difference for paging here is line ends.
Not line end characters, but the console behavior when the last character
on a line is printed.  To get technical details, run this module without
parameters::

  python pager.py

Author:  anatoly techtonik <techtonik@gmail.com>
License: Public Domain (use MIT if Public Domain doesn't work for you)
"""

__version__ = '2.0'

import os,sys

WINDOWS = os.name == 'nt'
PY3K = sys.version_info >= (3,)

# Windows constants
# http://msdn.microsoft.com/en-us/library/ms683231%28v=VS.85%29.aspx

STD_INPUT_HANDLE  = -10
STD_OUTPUT_HANDLE = -11
STD_ERROR_HANDLE  = -12


if WINDOWS:
    # get console handle
    from ctypes import windll, Structure, byref
    try:
        from ctypes.wintypes import SHORT, WORD, DWORD
    # workaround for missing types in Python 2.5
    except ImportError:
        from ctypes import (
            c_short as SHORT, c_ushort as WORD, c_ulong as DWORD)
    console_handle = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

    # CONSOLE_SCREEN_BUFFER_INFO Structure
    class COORD(Structure):
        _fields_ = [("X", SHORT), ("Y", SHORT)]

    class SMALL_RECT(Structure):
        _fields_ = [("Left", SHORT), ("Top", SHORT),
                    ("Right", SHORT), ("Bottom", SHORT)]

    class CONSOLE_SCREEN_BUFFER_INFO(Structure):
        _fields_ = [("dwSize", COORD),
                    ("dwCursorPosition", COORD),
                    ("wAttributes", WORD),
                    ("srWindow", SMALL_RECT),
                    ("dwMaximumWindowSize", DWORD)]


def _windows_get_window_size():
    """Return (width, height) of available window area on Windows.
       (0, 0) if no console is allocated.
    """
    sbi = CONSOLE_SCREEN_BUFFER_INFO()
    ret = windll.kernel32.GetConsoleScreenBufferInfo(console_handle, byref(sbi))
    if ret == 0:
        return (0, 0)
    return (sbi.srWindow.Right - sbi.srWindow.Left + 1,
            sbi.srWindow.Bottom - sbi.srWindow.Top + 1)

def _posix_get_window_size():
    """Return (width, height) of console terminal on POSIX system.
       (0, 0) on IOError, i.e. when no console is allocated.
    """
    # see README.txt for reference information
    # http://www.kernel.org/doc/man-pages/online/pages/man4/tty_ioctl.4.html

    from fcntl import ioctl
    from termios import TIOCGWINSZ
    from array import array

    """
    struct winsize {
        unsigned short ws_row;
        unsigned short ws_col;
        unsigned short ws_xpixel;   /* unused */
        unsigned short ws_ypixel;   /* unused */
    };
    """
    winsize = array("H", [0] * 4)
    try:
        ioctl(sys.stdout.fileno(), TIOCGWINSZ, winsize)
    except IOError:
        # for example IOError: [Errno 25] Inappropriate ioctl for device
        # when output is redirected
        # [ ] TODO: check fd with os.isatty
        pass
    return (winsize[1], winsize[0])

def getwidth():
    """
    Return width of available window in characters.  If detection fails,
    return value of standard width 80.  Coordinate of the last character
    on a line is -1 from returned value. 

    Windows part uses console API through ctypes module.
    *nix part uses termios ioctl TIOCGWINSZ call.
    """
    width = None
    if WINDOWS:
        return _windows_get_window_size()[0]
    elif os.name == 'posix':
        return _posix_get_window_size()[0]
    else:
        # 'mac', 'os2', 'ce', 'java', 'riscos' need implementations
        pass

    return width or 80

def getheight():
    """
    Return available window height in characters or 25 if detection fails.
    Coordinate of the last line is -1 from returned value. 

    Windows part uses console API through ctypes module.
    *nix part uses termios ioctl TIOCGWINSZ call.
    """
    height = None
    if WINDOWS:
        return _windows_get_window_size()[1]
    elif os.name == 'posix':
        return _posix_get_window_size()[1]
    else:
        # 'mac', 'os2', 'ce', 'java', 'riscos' need implementations
        pass

    return height or 25


# --- keyboard constants and input logic ---

if WINDOWS:
    ENTER = ['\x0d']
    LEFT =  ['\xe0', 'K']
    UP =    ['\xe0', 'H']
    RIGHT = ['\xe0', 'M']
    DOWN =  ['\xe0', 'P']
else:
    ENTER = ['\n']
    LEFT =  ['\x1b', '[', 'D']
    UP =    ['\x1b', '[', 'A']
    RIGHT = ['\x1b', '[', 'C']
    DOWN =  ['\x1b', '[', 'B']
ESC = ['\x1b']

def dumpkey(key):
    """
    Helper to convert a list (returned from getch()) or string to hex string.
    """
    def hex3fy(key):
        """Helper to convert string into hex string (Python 3 compatible)"""
        from binascii import hexlify
        # Python 3 strings are no longer binary, encode them for hexlify()
        if PY3K:
           key = key.encode('utf-8')
        keyhex = hexlify(key).upper()
        if PY3K:
           keyhex = keyhex.decode('utf-8')
        return keyhex
    if type(key) == str:
        return hex3fy(key)
    else:
        return ' '.join( [hex3fy(s) for s in key] )

def getch():
    """
    Wait for keypress(es), return list of chars generated as a result.

    Arrows and special keys generate such sequence after a single
    keypress. Sequences may differ between platforms, so make sure to
    use constants defined in this module to recognize keys back.
    """

    # check that Ctrl-C and Ctrl-Break break this function
    #
    # Ctrl-C       [n] Windows  [y] Linux  [ ] OSX
    # Ctrl-Break   [y] Windows  [n] Linux  [ ] OSX

    chars = []
    try:
        if PY3K:
            from msvcrt import kbhit, getwch as _getch
        else:
            from msvcrt import kbhit, getch as _getch
        chars = [_getch()]  # wait for the keypress
        while kbhit():      # deplete input buffer
            chars.append(_getch())
    except ImportError:
        ''' we're not on Windows, try Unix-like approach '''

        # --- current algorithm ---
        # 1. switch to char-by-char input mode
        # 2. turn off echo
        # 3. wait for at least one char to appear
        # 4. read the rest of the character buffer
        # 5. return list of characters
        import sys, termios

        fd = sys.stdin.fileno()
        # save old terminal settings
        old_settings = termios.tcgetattr(fd)
        try:
            # change terminal settings - turn off canonical mode and echo
            # in canonical mode read from stdin returns one line at a time
            # and we need one char at a time (see DESIGN.rst for more info)
            newattr = list(old_settings)
            newattr[3] &= ~termios.ICANON
            newattr[3] &= ~termios.ECHO
            newattr[6][termios.VMIN] = 1   # block until one char received
            newattr[6][termios.VTIME] = 0
            # TCSANOW below means apply settings immediately
            termios.tcsetattr(fd, termios.TCSANOW, newattr)

            # [ ] this fails when stdin is redirected, like
            #       ls -la | pager.py
            #   [ ] also check on Windows
            ch = sys.stdin.read(1)
            chars = [ch]

            # move rest of chars (if any) from input buffer
            # change terminal settings - enable non-blocking read
            newattr = termios.tcgetattr(fd)
            newattr[6][termios.VMIN] = 0      # CC structure
            newattr[6][termios.VTIME] = 0
            termios.tcsetattr(fd, termios.TCSANOW, newattr)

            while True:
                ch = sys.stdin.read(1)
                if ch != '':
                    chars.append(ch)
                else:
                    break
        finally:
            # restore terminal settings. Do this when all output is
            # finished - TCSADRAIN flag
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    return chars
    
# --- /getch() stuff ---


def echo(msg):
    """
    Print msg to the screen without linefeed and flush the output.
    
    Standard print() function doesn't flush, see:
    https://groups.google.com/forum/#!topic/python-ideas/8vLtBO4rzBU
    """
    sys.stdout.write(msg)
    sys.stdout.flush()

def prompt(pagenum):
    """
    Show default prompt to continue and process keypress.

    It assumes terminal/console understands carriage return \r character.
    """
    prompt = "Page -%s-. Press any key to continue . . . " % pagenum
    echo(prompt)
    getch()
    echo('\r' + ' '*(len(prompt)-1) + '\r')

def page(content, pagecallback=prompt):
    """
    Output content, call `pagecallback` after every page with page number as
    a parameter.

    Default callback just shows prompt and waits for keypress.
    """
    width = getwidth()
    height = getheight()
    pagenum = 1

    try:
        try:
            line = content.next().rstrip("\r\n")
        except AttributeError:
            # Python 3 compatibility
            line = content.__next__().rstrip("\r\n")
    except StopIteration:
        pagecallback(pagenum)
        return

    while True:     # page cycle
        linesleft = height-1 # leave the last line for the prompt callback
        while linesleft:
            linelist = [line[i:i+width] for i in range(0, len(line), width)]
            if not linelist:
                linelist = ['']
            lines2print = min(len(linelist), linesleft)
            for i in range(lines2print):
                if WINDOWS and len(line) == width:
                    # avoid extra blank line by skipping linefeed print
                    echo(linelist[i])
                else:
                    print(linelist[i])
            linesleft -= lines2print
            linelist = linelist[lines2print:]

            if linelist: # prepare symbols left on the line for the next iteration
                line = ''.join(linelist)
                continue
            else:
                try:
                    try:
                        line = content.next().rstrip("\r\n")
                    except AttributeError:
                        # Python 3 compatibility
                        line = content.__next__().rstrip("\r\n")
                except StopIteration:
                    pagecallback(pagenum)
                    return
        pagecallback(pagenum)
        pagenum += 1



# --- Manual tests when pager executed as a module ---

def _manual_test_console():
    print("\nconsole size: width %s, height %s" % (getwidth(), getheight()))
    echo("--<enter>--")
    getch()
    echo("\n")

    print("\nsys.stdout.write() doesn't insert newlines automatically,")
    print("that's why it is used for console output in non-trivial")
    print("cases here.\n")
    sys.stdout.write("--<enter>--")
    sys.stdout.flush()
    getch()
    print("\rHowever, sys.stdout.write() requires explicit flushing")
    print("to make the output immediately appear on the screen.")
    print("echo() function from this module does this automatically.")
    echo("\n--<enter>--")
    getch()

    print("\n\nThe following test outputs string equal to the width of the\n"
          "screen and waits for you to press <enter>. It behaves\n"
          "differently on Linux and Windows - W. scrolls the window and\n"
          "places cursor on the next line immediately, while L. window\n"
          "doesn't scroll until the next character is output.\n"
         )
    print("Tested on:")
    print("  Windows Vista - cmd.exe console")
    print("  Debian Lenny - native terminal")
    print("  Debian Lenny - PuTTY SSH terminal from Windows Vista")
    echo("\n--<enter>--")
    getch()
    echo("\n")

    echo("<" + "-"*(getwidth()-2) + ">")
    getch()
    print("^ note there is no newline when the next character is printed")
    print("")
    print("At least this part works similar on all platforms. It is just\n"
          "the state of the console after the last character on the line\n"
          "is printed that is different.")
    print("")
    echo("--<enter>--")
    getch()
    print("")

    print("\nBut there is one special case.")
    print("")
    print("It is when the next character is a newline.")
    print("")
    print("The following test prints line equal to the width of the\n"
          "console, waits for <enter>, then outputs newline '\\n',\n"
          "waits for another key press, then outputs 'x' char.")
    print("")
    echo("--<enter>--")
    getch()
    print("")

    echo("<" + "-"*(getwidth()-2) + ">")
    getch()
    echo("\n")
    getch()
    echo("x")
    getch()

    print("\n^ here is the difference:")
    print("")
    print("On Windows you will get:\n"
          "  <----------->\n"
          "  \n"
          "  x")
    print("")
    print("Linux will show you:\n"
          "  <----------->\n"
          "  x")
    print("")
    echo("--<enter>--")
    getch()
    print("")

    print("\nThe next test will fill the screen with '1' digits\n"
          "numbering each line staring from 1.")
    print("")
    print("It works the same on Linux and Windows, because the next\n"
          "character after the last on the line is not linefeed.\n")
    echo("--<enter>--")
    getch()
    print("")
    numwidth = len(str(getwidth()))
    strlen = getwidth() - numwidth - 2 # 2 = '. ' after the line number
    filler = '1' * strlen
    for i in range(getheight()-1):     # -1 to leave last line for --<enter>--
        lineno = ("%" + str(numwidth) + "s. ") % (i+1)
        sys.stdout.write(lineno + filler)
    echo("--<enter>--")
    getch()
    print("")

    print("\nNext test prints this source code using page() function")
    print("")
    echo("--<enter>--")
    getch()
    print("")
    content = open(__file__)
    page(content)
    echo("--<enter>--")
    getch()
    print("")


def _manual_test_getch():
    echo("\n")
    # special keys
    keys = 'ENTER LEFT UP RIGHT DOWN ESC'.split()
    for key in keys:
      value = globals()[key]
      echo("Press %s key: " % key)
      key = getch()
      if key == value:
        echo("OK\n")
      else:
        echo("FAILED: getch() returned %s (hex %s)\n" % (key, dumpkey(key)))



# [ ] recognize multiple-character sequences such as arrow keys

if __name__ == '__main__':
    # check if pager.py is running in interactive mode
    # (without stdin redirection)
    stdin_fd = sys.stdin.fileno()
    if os.isatty(stdin_fd):
        if not sys.argv[1:]:
            print("pager v%s" % __version__)
            print("usage: pager.py <file>")
            print("       pager.py --test\n")
            sys.exit(-1)

        #       pager.py --test
        elif sys.argv[1] == '--test':
            print("Manual tests for pager module.")
            ch = []
            while True:
                print("\n1. Test output")
                print("2. Test input")
                print("0. Exit")
                ch = getch()
                if ch == ['1']:
                    _manual_test_console()
                elif ch == ['2']:
                    _manual_test_getch()
                elif ch in (['0'], ESC):
                    break

        #       pager.py <file>
        else:
            with open(sys.argv[1]) as f:
                page(f)

    else:
        # mode with piped stdin needs more tuits
        pass
        # print("       pager.py < <file>")
        # print("       <command> | pager.py")
        #page(sys.stdin)

