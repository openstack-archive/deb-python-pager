import os,sys

# Windows constants
# http://msdn.microsoft.com/en-us/library/ms683231%28v=VS.85%29.aspx

STD_INPUT_HANDLE  = -10
STD_OUTPUT_HANDLE = -11
STD_ERROR_HANDLE  = -12

if os.name == 'nt':
    # get console handle
    from ctypes import windll, Structure, byref
    from ctypes.wintypes import SHORT, WORD, DWORD
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
    """Return (width, height) of available window area on Windows"""
    sbi = CONSOLE_SCREEN_BUFFER_INFO()
    windll.kernel32.GetConsoleScreenBufferInfo(console_handle, byref(sbi))
    return (sbi.srWindow.Right+1, sbi.srWindow.Bottom+1)

def _posix_get_window_size():
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
    winsize = array.array("H", [0] * 4)
    ioctl(sys.stdout.fileno(), TIOCGWINSZ, winsize)
    return (winsize[1], winsize[0])

def get_width():
    """
    Return width of available window in characters.  If detection fails,
    return value of standard width 80.  Coordinate of the last character
    on a line is -1 from returned value. 

    Windows part uses console API through ctypes module.
    *nix part uses termios ioctl TIOCGWINSZ call.
    """
    width = None
    if os.name == 'nt':
        return _windows_get_window_size()[0]
    elif os.name == 'posix':
        return _posix_get_window_size()[0]
    else:
        # 'mac', 'os2', 'ce', 'java', 'riscos' need implementations
        pass

    return width or 80

def get_height():
    """
    Return available window height in characters or 25 if detection fails.
    Coordinate of the last line is -1 from returned value. 

    Windows part uses console API through ctypes module.
    *nix part uses termios ioctl TIOCGWINSZ call.
    """
    height = None
    if os.name == 'nt':
        return _windows_get_window_size()[1]
    elif os.name == 'posix':
        return _posix_get_window_size()[1]
    else:
        # 'mac', 'os2', 'ce', 'java', 'riscos' need implementations
        pass

    return height or 25



if __name__ == '__main__':
    print("console size width, height: %s, %s" % (get_width(), get_height()))
    print
    print("sys.stdout.write() is preferred way of output than print")
    """
    This should yell
    <---------------->
     x
    <---------------->
    x
    """
    print("print,")
    print("<" + "-"*(get_width()-2) + ">"),
    print "x"
    print("sys.stdout.write()")
    sys.stdout.write("<" + "-"*(get_width()-2) + ">")
    print "x"
    print
    