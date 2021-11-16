import curses
from collections import OrderedDict

CTL_N = 14
CTL_Q = 17
CTL_W = 23
CTL_UP = 480
CTL_DOWN = 481
CTL_LEFT = 443
CTL_RIGHT = 444

STATUS_BAR_OFFSET_Y = 1

STATUS_BAR_STR = "EXIT -> ctl+q | NEW WIN -> ctl+n | DEL WIN -> ctl+w"

class CursesString():
    '''
    @param stdscr curses obj
    @param text string to display
    @param x, y coordinates of string (can negative index)
    @param fill fill the rest of the line with spaces
    '''
    def __init__(self, stdscr, text, color, x, y, fill=None):
        self.text = text
        self.color = color
        self.x = x
        self.y = y
        self.fill = fill
        self.stdscr = stdscr
        self._render()
    
    def _render(self):
        height, width = self.stdscr.getmaxyx()
        if self.y < 0:
            self.y = height + self.y
        if self.x < 0:
            self.x = width + self.x
        self.stdscr.attron(curses.color_pair(self.color))
        self.stdscr.addstr(self.y, self.x, self.text)
        if self.fill == -1:
            self.stdscr.addstr(self.y, len(self.text), " " * (width - len(self.text) - 1))
        self.stdscr.attroff(curses.color_pair(self.color))
        self.stdscr.refresh()

class Window():
    # TODO: add handling for port
    def __init__(self, stdscr, lines, cols, y, x, port=None):
        self.stdscr = stdscr
        self.win = stdscr.subwin(lines, cols, y, x)
        self._refresh()
    
    def resize(self, lines, cols, y, x):
        self.win = self.stdscr.subwin(lines, cols, y, x)
        self._refresh()
        return self

    def _refresh(self):
        self.win.box()
        self.win.touchwin()
        self.win.refresh()

class ContextHandler():
    '''
    This class should be used as a singleton. Only need one of these bad boy to manage context
    '''

    MAX_WINDOWS = 4

    def __init__(self):
        self._windows = {}
    
    def init_stdscr(self, stdscr):
        self.stdscr = stdscr
        self._height, self._width = self.stdscr.getmaxyx()
        self._height -= STATUS_BAR_OFFSET_Y

    def add_window(self):
        if len(self._windows) <= self.MAX_WINDOWS:
            self._windows[len(self._windows)+1] = Window(self.stdscr,0,0,0,0)
            self._configure_window_sizes(len(self._windows))

    def del_current_window():
        pass

    def _configure_window_sizes(self, n):
        def one():
            self._windows[1] = self._windows[1].resize(self._height, self._width, 0, 0)

        def two():
            win_width = int(self._width/2)
            self._windows[1] = self._windows[1].resize(self._height, win_width, 0, 0)
            self._windows[2] = self._windows[2].resize(self._height, win_width, 0, win_width)
        
        def three():
            win_width = int(self._width/3)
            self._windows[1] = self._windows[1].resize(self._height, win_width, 0, 0)
            self._windows[2] = self._windows[2].resize(self._height, win_width, 0, win_width)
            self._windows[3] = self._windows[3].resize(self._height, win_width, 0, win_width*2)
        
        def four():
            win_width = int(self._width/2)
            win_height = int(self._height/2)
            self._windows[1] = self._windows[1].resize(win_height, win_width, 0, 0)
            self._windows[2] = self._windows[2].resize(win_height, win_width, 0, win_width)
            self._windows[3] = self._windows[3].resize(win_height, win_width, win_height, 0)
            self._windows[4] = self._windows[4].resize(win_height, win_width, win_height, win_width)

        win_handler_table = {
            1 : one,
            2 : two,
            3 : three,
            4 : four
        }

        handler_func = win_handler_table[n]
        if callable(handler_func):
            self.stdscr.clear()
            handler_func()

# make this big so everyone knows it's a singleton
CONTEXT_HANDLER = ContextHandler()

keypress_callback_table = {
    CTL_N     : CONTEXT_HANDLER.add_window,
    CTL_W     : None,
    CTL_UP    : None,
    CTL_DOWN  : None,
    CTL_LEFT  : None,
    CTL_RIGHT : None,
}

def handle_keypress(key):
    try:
        handler_func = keypress_callback_table[key]
        if callable(handler_func):
            handler_func()
    except KeyError:
        pass

COLOR_CY_BL = 1
COLOR_BL_WH = 2
def init_colors():
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)

def draw_menu(stdscr):
    k = 0

    CONTEXT_HANDLER.init_stdscr(stdscr)
    CONTEXT_HANDLER.add_window()

    init_colors()

    # windows_queue = []
    # configure_window(stdscr, windows_queue, 1)

    # # Loop where k is the last character pressed
    while (k != CTL_Q):
        handle_keypress(k)

        CursesString(stdscr, text = STATUS_BAR_STR, color = COLOR_BL_WH, x = 0, y = -1, fill = -1)

        k = stdscr.getch()

def main():
    curses.wrapper(draw_menu)

if __name__ == "__main__":
    main()