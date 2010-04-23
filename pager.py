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


def get_width():
    """
    Return width of available window in characters.  If detection fails,
    return value of standard width 80.  Coordinate of the last character
    on a line is -1 from returned value. 

    Windows part uses console API through ctypes module.
    """
    width = None
    if os.name == 'nt':
        sbi = CONSOLE_SCREEN_BUFFER_INFO()
        windll.kernel32.GetConsoleScreenBufferInfo(console_handle, byref(sbi))
        width = sbi.srWindow.Right + 1
    elif os.name == 'posix':
        pass
    else:
        # 'mac', 'os2', 'ce', 'java', 'riscos' need implementations
        pass

    return width or 80


if __name__ == '__main__':
    print("console width: %s" % get_width())
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
    