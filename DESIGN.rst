Design notes and decisions
==========================

Send updates and comments to techtonik@gmail.com



Get console width function name
-------------------------------
common variants
  pager.getwidth()
  pager.get_width()
  pager.width()

curses module in python 2.6
  pager.getmaxyx()

PDCurses
  pager.get_columns()

Console by Fredrik Lundh
  pager.size()

libtcod
  pager.console_get_width()

Used pager.getwidth() as it is consistent with getch()
and easier to type.



Other implementations
---------------------
Windows Console Driver by Fredrik Lundh
http://effbot.org/zone/console-index.htm

libtcod, a.k.a. "The Doryen Library" python bindings
http://doryen.eptalys.net/libtcod/



Platform specific notes
-----------------------
Linux doesn't have a concept of `console`, because there
is another historical concept of `terminal`. There are many
terminal types and the closest one to `console` is `tty`.

For the sake of clarity the `console` here is a window with
defined width and height in characters.

Linux terminal doesn't have a concept of a window. Terminal
is a file, which is read to get input from keyboard, and
written to print to the screen. Access to the file is made
with the help of file descriptior, which doesn't have width
and height properties. To overcome this limitation Linux
has a set of special calls named I/O control calls (ioctl).
Given file descriptor, it is possible to query system for
additional information associated with it.


Getting console size on Linux
-----------------------------
termios.tcgetattr() can not be used to get console size
because it handles only text stream of information. There
are no any references to any kind of terminal `size` in
http://www.kernel.org/doc/man-pages/online/pages/man3/termios.3.html


Getting console size on Windows
-------------------------------
Windows console consists of two parts - visible window
and scroll buffer. Usually window has scrollbars for
navigation over scroll buffer area. Window coordinates
depend on position of scroll area, and therefore its top
left corner is not necessary has 0,0 coordinate.
http://www.adrianxw.dk/SoftwareSite/Consoles/Consoles6.html

