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

