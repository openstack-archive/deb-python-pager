
Python module to page output to the screen, read keys and get
console dimensions.

It was meant to be included in standard library
http://bugs.python.org/issue8408

| Author:  anatoly techtonik <techtonik@gmail.com>
| License: Public Domain (or MIT if a license is required)


Demo
----
::

  # this runs manual tests that are also a showcase of
  # module capabilities

  python -m pager


Status
------

1.2 (stable)
 - add names for ENTER LEFT UP RIGHT DOWN ESC keys
 - manual tests for getch() (fixes bug #4)
 - dumpkey() helper function to get hex dump of a value
   returned by getch()
1.1 (stable)
 - Python 3 compatibility
 - echo() helper function for unbuffered output (in Py3
   output doesn't appear immediately on screen unless it
   ends with newline)
1.0 (stable)
 - getch() now returns list of chars for special keys
   (fixes bug #1 when special key skipped several pages)
 - page() callbacks receive obligatory pagenumber param
 - default page() callback now shows page number
0.2 (stable)
 - do not insert blank line between pages
0.1 (stable)
 - shows content page by page
 - allows to get console/terminal dimensions
 - works on Windows
 - works on Linux


API
---

..function:: **getwidth()**

  Return width of available window in characters.  If detection fails,
  return value of standard width 80.  Coordinate of the last character
  on a line is -1 from returned value. 


..function:: **getheight()**

  Return available window height in characters or 25 if detection fails.
  Coordinate of the last line is -1 from returned value. 


..function:: **getch()**

  Wait for keypress and return character or a list of characters. Arrows
  and special keys generate a sequence of characters, so if there are
  extra symbols in input buffer, this function returns list.


..function:: **page(content, [pagecallback=prompt])**

  Output `content` iterable, calling `pagecallback` function after each
  page with page number as a parameter. Default `prompt()` callback shows
  page number with 'Press any key . . . ' prompt and waits for keypress.


..function:: **echo(msg)**

  Print msg to the screen without linefeed and flush the output.

..function:: **dumpkey(key)**

  Return hexadecimal representation of a key value returned by getch().


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
