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



Platform specific terminology
-----------------------------
Linux doesn't have a concept of `console`. Thing that plays
the role of the console on Linux is called `text terminal`.

For the sake of clarity the `console` here is a window with
defined width and height in characters.

Linux terminal doesn't have a concept of a window. Terminal
is a file, which is read to get input from keyboard, and
written to print to the screen. Access to the file is made
with the help of file descriptior, which doesn't have width
and height properties. To overcome this limitation Linux
has a set of special calls named I/O control calls (ioctl).
Given file descriptor, it is possible to query system for
additional information associated with it, or change
behavior of the attached terminal.


Understanding Linux terminal
----------------------------
Terminal under Linux is a complicated thing to get right
without a proper entrypoint. Good starter is Wikipedia
article about text terminals and especially paragraph about
 `dumb terminals`.
http://en.wikipedia.org/wiki/Text_terminal#Text_terminals

For completeteness, I post some relevant info here. Text
terminal is keyboard + display. Keyboard is used to type
input and display to show some stuff::

    +-------------------+
    |   Text terminal   |
    |   +-----------+            +-----------+
    |   |           |  #0 stdin  |           |
    |   | Keyboard  +----------->|  Program  |
    |   |           |   |        |           |
    |   +-----------+   |        +---+---+---+
    |                                |   |
    |   +-----------+    #1 stdout   |   |
    |   |           |<---------------+   |
    |   |  Display  |      #2 stderr     |
    |   |           |<-------------------+
    |   +-----------+   |
    +-------------------+

This picture looks like your program filters input and
decide what will be sent to display. Not quite right. The
need to show input on the screen immediately was so
frequent that terminal devices do this themselves, and to
turn this feature off you have to configure them.

Configuration is done through calls to Linux "terminal
input/output system" (termios) with #0, #1 and #2 file
descriptors. This is a common Linux API to change terminal
behavior.

Turning off canonical mode
~~~~~~~~~~~~~~~~~~~~~~~~~~
Some terminals allowed users to prepare line before sending
it to the program. Users were able to edit line with cursor
and backspace keys, and keyboard <-> display interaction
was done completely inside terminal. Program received the
input only after user hit `enter` button. This was called
`canonical mode`. `pager` turns off canonical mode, because
it needs every single keypress as soon as it occurs.


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


Ideal (CHAOS) interface for catching keypresses
-----------------------------------------------
Case01: Hit any single key, get a number that corresponds to
        this key.
Notes: Total keys 101, potential keys 1024+. One byte is not
       enough, two bytes may be enough. Namespace + two bytes
       should be enough.

Case02: Hit any single key with a single "modifier" key such
        as `Ctrl`, `Alt`, `Shift`.
Notes: For a limited set of "modifier" keys the total amount
       of key combination numbers is (101-3)*3 == 294.

Case03: Hit any single key with a combination of "modifier"
        keys.
Notes: Total combinations are (101-3)*2^3 == 784.

Case04: Hit any combination of keys with a sane LIMIT.
Notes: Combinatorics. LIMIT=15. Any key suits.

--- key catching 01 ---
Quite evident that with Case04 we are out of any sane limit
of bytes for preserving state. That's why we need to analyze
the matrix and send limited list of keys that are pressed
simultaneously. The list (called "buffer list") starts to
fill when the first key is pressed and continues record
pressed key during some small time (try 50ms or so).

LIMIT = 15
READTIME = 50 # ms

After READTIME, the buffer is immediately passed further.
The drawback is how to distinguish very fast typing.

--- key catching 02 ---
When a new key pressed, the buffer is filled with all pressed
keys simultaneously and immediately sent. This should work
for modifier keys and office tools. This probably won't work
for active games with 2+ players on the same keyboard.
