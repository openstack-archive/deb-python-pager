import os,sys

# Windows constants
# http://msdn.microsoft.com/en-us/library/ms683231%28v=VS.85%29.aspx

STD_INPUT_HANDLE  = -10
STD_OUTPUT_HANDLE = -11
STD_ERROR_HANDLE  = -12

if os.name == 'nt':
    # get console handle
    from ctypes import windll, Structure
    console_handler = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

    # CONSOLE_SCREEN_BUFFER_INFO Structure
    # class COORD(Structure):


def get_width():
    """
    Return width of availble window in characters. Coordinate of the last
    character is -1 from this value.

    Windows part uses console API through ctypes module.
    """
    width = None
    if os.name == 'nt':
        pass
    elif os.name == 'posix':
        pass
    else:
        # 'mac', 'os2', 'ce', 'java', 'riscos' need implementations
        pass

    return width or 80


if __name__ == '__main__':
    print("console width: %s" % get_width())
    print
    print("sys.stdout is preferred way of output than print")
    print("print,")
    print("<" + "-"*(get_width()-2) + ">"),
    print "x"
    print("sys.stdout.write()")
    sys.stdout.write("<" + "-"*(get_width()-2) + ">")
    print "x"
    print
    