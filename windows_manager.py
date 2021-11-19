from collections import OrderedDict
import const
from window import Window
from enum import Enum

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
        self._height -= const.STATUS_BAR_OFFSET_Y
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
        UP = 1,
        DOWN = 2,
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