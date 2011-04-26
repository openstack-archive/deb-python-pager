
Python module to page screen output and get dimensions
of available console space.

It is meant to be finally included into standard library
http://bugs.python.org/issue8408

| Author:  anatoly techtonik <techtonik@gmail.com>
| License: Public Domain (or MIT if a license is required)


Status
------

0.1 (stable)
 - shows content page by page
 - allows to get console/terminal dimensions
 - works on Windows
 - works on Linux


API
---

..function:: getwidth()

  Return width of available window in characters.  If detection fails,
  return value of standard width 80.  Coordinate of the last character
  on a line is -1 from returned value. 


..function:: getheight()

  Return available window height in characters or 25 if detection fails.
  Coordinate of the last line is -1 from returned value. 


..function:: getch()

  Wait for keypress and return character in a cross-platform way.
  Credits: Danny Yoo, Python Cookbook


..function:: page(content, [pagecallback=prompt])

  Output `content` iterable, calling `pagecallback` function after each
  page. Default :func:`prompt` callback shows 'Press any key . . . ' prompt
  and waits for keypress.


References
----------

Excellent tutorials for Win32 Console by Adrian Worley
http://www.adrianxw.dk/SoftwareSite/index.html
Console Reference on MSDN
http://msdn.microsoft.com/en-us/library/ms682087%28VS.85%29.aspx

Public Domain Curses library maintained by William McBrine
http://pdcurses.sourceforge.net/

Ioctl (input/output control) introduction from Wikipedia
http://en.wikipedia.org/wiki/Ioctl
Linux Programmer's Manual - ioctls for terminals and serial lines
http://www.kernel.org/doc/man-pages/online/pages/man4/tty_ioctl.4.html
