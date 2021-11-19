import curses

screen = curses.initscr()

try:
    screen.border(0)
    box1 = screen.subwin(20, 20, 5, 5)
    box1.box()
    box1.addstr("hello")
    box1.touchwin()
    box1.refresh()
    box1.getch()
    box2 = screen.subwin(20, 20, 5, 25)
    box2.box()
    box2.touchwin()
    box2.refresh()
    screen.getch()

finally:
    curses.endwin()