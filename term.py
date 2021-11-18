import curses
from collections import OrderedDict
from enum import Enum

CTL_N = 14
CTL_Q = 17
CTL_W = 23
CTL_UP = 480
CTL_DOWN = 481
CTL_LEFT = 443
CTL_RIGHT = 444

STATUS_BAR_OFFSET_Y = 1

STATUS_BAR_STR = "EXIT -> ctl+q | NEW WIN -> ctl+n | DEL WIN -> ctl+w | EDIT CONFIG -> ctl+g"

COLOR_CY_BL = 1
COLOR_BL_WH = 2

def init_colors():
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)

class CursesString():
    '''
    @param stdscr curses obj
    @param text string to display
    @param x, y coordinates of string (can negative index)
    @param fill fill the rest of the line with spaces
    '''
    def __init__(self, window, text, color, x, y, fill=None, vis=True):
        self.text = text
        self.color = color
        self.x = x
        self.y = y
        self.fill = fill
        self.window = window
        self.vis = vis
        self._render()
    
    def _render(self):
        if self.vis:
            height, width = self.window.getmaxyx()
            if self.y < 0:
                self.y = height + self.y
            if self.x < 0:
                self.x = width + self.x
            self.window.attron(curses.color_pair(self.color))
            self.window.addstr(self.y, self.x, self.text)
            if self.fill == -1:
                self.window.addstr(self.y, len(self.text)+self.x, " " * 10)
            self.window.attroff(curses.color_pair(self.color))
            self.window.refresh()

class Window():
    # TODO: add handling for port
    def __init__(self, stdscr, id, lines, cols, y, x, port=None, win_id_vis=False):
        self.stdscr = stdscr
        self.win = stdscr.subwin(lines, cols, y, x)
        self.id = id
        self._win_id_vis = win_id_vis
        self.refresh()
    
    def resize(self, lines, cols, y, x):
        self.win = self.stdscr.subwin(lines, cols, y, x)
        return self
        
    # TODO clean up string show logic somehow instead of just a rogue if statement
    def refresh(self, header_highlight_vis=False):
        self.win.box()
        if self._win_id_vis == True:
            if header_highlight_vis == True:
                CursesString(self.win, str(self.id), COLOR_BL_WH, 1, 1, -1)
            else:
                CursesString(self.win, str(self.id), COLOR_CY_BL, 1, 1, -1)
        self.win.touchwin()
        self.win.refresh()

class WindowsManager():
    '''
    @descr Manages adding/remove windows. Manages handling context to pipe inputs to the correct screen
    @note Use as a singleton
    '''

    MAX_WINDOWS = 4

    def __init__(self, win_id_vis=False):
        self._windows = OrderedDict()
        self._active_window = 1
        self._win_id_vis = win_id_vis
    
    '''
    @param stdscr  Curses stdscr object
    '''
    def init_stdscr(self, stdscr):
        self.stdscr = stdscr
        self._height, self._width = self.stdscr.getmaxyx()
        self._height -= STATUS_BAR_OFFSET_Y
        self._init_directional_context_handlers()

    def add_window(self):
        if len(self._windows) < self.MAX_WINDOWS:
            window_id = len(self._windows)+1
            self._windows[window_id] = Window(self.stdscr,window_id,0,0,0,0,win_id_vis=self._win_id_vis)
            self._configure_windows(len(self._windows))

        # window.scrollok(flag)
        # Control what happens when the cursor of a window is moved off the edge of the window or scrolling region, either as a result of a newline action on the bottom line, or typing the last character of the last line. If flag is False, the cursor is left on the bottom line. If flag is True, the window is scrolled up one line. Note that in order to get the physical scrolling effect on the terminal, it is also necessary to call idlok().    

    def del_active_window(self):
        if len(self._windows) > 1:
            if self._active_window > 1 and self._active_window == len(self._windows):
                self._active_window -= 1
            self._windows.popitem()
            self._configure_windows(len(self._windows))

    def _refresh_all(self):
        for window in self._windows:
            if self._active_window == self._windows[window].id:
                self._windows[window].refresh(header_highlight_vis=True)
            else:
                self._windows[window].refresh()

    def _configure_windows(self, n):
        def one():
            self._windows[1] = self._windows[1].resize(self._height, self._width, 0, 0)

        def two():
            win_width = int(self._width/2)
            self._windows[1] = self._windows[1].resize(self._height, win_width, 0, 0)
            self._windows[2] = self._windows[2].resize(self._height, win_width, 0, win_width)
        
        def three():
            win_width = int(self._width/3)
            # self._windows = [self._windows[x+1].resize(self._height, win_width, 0, win_width*x) for x in range(2)]
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
            self._refresh_all()

    class Directions(Enum):
        UP = CTL_UP,
        DOWN = CTL_DOWN,
        LEFT = 3,
        RIGHT = 4
    
    def _set_active_window(self, win_id):
        self._active_window = win_id
        return win_id

    def _init_directional_context_handlers(self):
        '''
        @descr handle_n() corresponds to the current number of windows
        '''
        def handle_one(self, dir):
            pass
                
        def handle_two(self, dir):
            if dir == self.Directions.RIGHT:
                if self._active_window == 1:
                    return self._set_active_window(self._active_window + 1)
            elif dir == self.Directions.LEFT:
                if self._active_window == 2:
                    return self._set_active_window(self._active_window - 1)

        def handle_three(self, dir):
            if dir == self.Directions.RIGHT:
                if self._active_window < 3:
                    return self._set_active_window(self._active_window + 1)
            elif dir == self.Directions.LEFT:
                if self._active_window > 1:
                    return self._set_active_window(self._active_window - 1)

        def handle_four(self, dir):
            if dir == self.Directions.RIGHT:
                if self._active_window == 1 or self._active_window == 3:
                    return self._set_active_window(self._active_window + 1)
            elif dir == self.Directions.LEFT:
                if self._active_window == 2 or self._active_window == 4:
                    return self._set_active_window(self._active_window - 1)
            if dir == self.Directions.UP:
                if self._active_window == 3 or self._active_window == 4:
                    return self._set_active_window(self._active_window - 2)
            if dir == self.Directions.DOWN:
                if self._active_window == 1 or self._active_window == 2:
                    return self._set_active_window(self._active_window + 2)

        self._directional_context_give_handlers = {
            1 : handle_one,
            2 : handle_two,
            3 : handle_three,
            4 : handle_four
        }

    def give_context_up(self):
        directional_context_give_func = self._directional_context_give_handlers[len(self._windows)]
        res = directional_context_give_func(self, self.Directions.UP)
        if res != None:
            self._refresh_all()

    def give_context_down(self):
        directional_context_give_func = self._directional_context_give_handlers[len(self._windows)]
        res = directional_context_give_func(self, self.Directions.DOWN)
        if res != None:
            self._refresh_all()

    def give_context_left(self):
        directional_context_give_func = self._directional_context_give_handlers[len(self._windows)]
        res = directional_context_give_func(self, self.Directions.LEFT)
        if res != None:
            self._refresh_all()

    def give_context_right(self):
        directional_context_give_func = self._directional_context_give_handlers[len(self._windows)]
        res = directional_context_give_func(self, self.Directions.RIGHT)
        if res != None:
            self._refresh_all()

# make this big so everyone knows it's a singleton
WIN_MANAGER = WindowsManager(win_id_vis=True)

keypress_callback_table = {
    CTL_N     : WIN_MANAGER.add_window,
    CTL_W     : WIN_MANAGER.del_active_window,
    CTL_UP    : WIN_MANAGER.give_context_up,
    CTL_DOWN  : WIN_MANAGER.give_context_down,
    CTL_LEFT  : WIN_MANAGER.give_context_left,
    CTL_RIGHT : WIN_MANAGER.give_context_right,
}

def handle_keypress(key):
    try:
        handler_func = keypress_callback_table[key]
        if callable(handler_func):
            handler_func()
    except KeyError:
        pass

def draw_menu(stdscr):
    k = 0

    WIN_MANAGER.init_stdscr(stdscr)
    WIN_MANAGER.add_window()

    init_colors() 
    curses.curs_set(0)

    # # Loop where k is the last character pressed
    while (k != CTL_Q):
        handle_keypress(k)  

        CursesString(stdscr, text = STATUS_BAR_STR, color = COLOR_BL_WH, x = 0, y = -1, fill = -1)

        curses.beep()

        k = stdscr.getch()

def main():
    curses.wrapper(draw_menu)

if __name__ == "__main__":
    main()