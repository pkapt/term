import curses
from windows_manager import WindowsManager
from curses_string import CursesString
import const



STATUS_BAR_STR = "EXIT -> ctl+q | NEW WIN -> ctl+n | DEL WIN -> ctl+w | EDIT CONFIG -> ctl+g"

# make this big so everyone knows it's a singleton
WIN_MANAGER = WindowsManager(win_id_vis=True)

keypress_callback_table = {
    const.CTL_N     : WIN_MANAGER.add_window,
    const.CTL_W     : WIN_MANAGER.del_active_window,
    const.CTL_UP    : WIN_MANAGER.give_context_up,
    const.CTL_DOWN  : WIN_MANAGER.give_context_down,
    const.CTL_LEFT  : WIN_MANAGER.give_context_left,
    const.CTL_RIGHT : WIN_MANAGER.give_context_right,
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
    while (k != const.CTL_Q):
        handle_keypress(k)  

        CursesString(stdscr, text = STATUS_BAR_STR, color = const.COLOR_BL_WH, x = 0, y = -1, fill = -1)

        curses.beep()

        k = stdscr.getch()

def init_colors():
    # COLOR_CY_BL = 1
    # COLOR_BL_WH = 2
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)

def main():
    curses.wrapper(draw_menu)

if __name__ == "__main__":
    main()