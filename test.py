import sys
import curses

screen = curses.initscr()
screen.keypad(True)

curses.noecho()
curses.cbreak()
curses.curs_set(False)
if curses.has_colors():
    curses.start_color()

opt = "nothing, yet"

while opt != "q":
    screen.clear()
    screen.addstr(0, 0, f"you entered {opt}")
    screen.refresh()

    opt = screen.getkey()


curses.echo()
curses.nocbreak()
curses.curs_set(True)
screen.keypad(False)
curses.echo()
curses.endwin()

sys.exit(0)
