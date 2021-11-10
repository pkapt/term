import curses

CTL_N = 14
CTL_Q = 17
CTL_W = 23

def configure_window(stdscr, windows_queue, n):
    windows_queue.clear()
    height, width = stdscr.getmaxyx()

    def one():
        windows_queue.append(stdscr.subwin(height, width, 0, 0))

    def two():
        win_width = int(width/2)
        windows_queue.append(stdscr.subwin(height, win_width, 0, 0))
        windows_queue.append(stdscr.subwin(height, win_width, 0, win_width))
    
    def three():
        win_width = int(width/3)
        windows_queue.append(stdscr.subwin(height, win_width, 0, 0))
        windows_queue.append(stdscr.subwin(height, win_width, 0, win_width))
        windows_queue.append(stdscr.subwin(height, win_width, 0, win_width*2))
    
    def four():
        win_width = int(width/2)
        win_height = int(height/2)
        windows_queue.append(stdscr.subwin(win_height, win_width, 0, 0))
        windows_queue.append(stdscr.subwin(win_height, win_width, 0, win_width))
        windows_queue.append(stdscr.subwin(win_height, win_width, win_height, 0))
        windows_queue.append(stdscr.subwin(win_height, win_width, win_height, win_width))

    def refresh_all():
        for window in windows_queue:
            window.box()
            window.touchwin()
            window.refresh()

    win_handler_table = {
        1 : one,
        2 : two,
        3 : three,
        4 : four
    }

    handler_func = win_handler_table[n]
    if callable(handler_func):
        stdscr.clear()
        handler_func()
        refresh_all()

def add_window(stdscr, windows_queue):
    len_q = len(windows_queue)
    if 1 <= len_q <= 3:
        configure_window(stdscr, windows_queue, len_q + 1)

def remove_window(stdscr, windows_queue):
    len_q = len(windows_queue)
    if 2 <= len_q <= 4:
        configure_window(stdscr, windows_queue, len_q - 1)

keypress_callback_table = {
    CTL_N : add_window,
    CTL_W : remove_window
}

def handle_keypress(key, stdscr, windows_queue):
    try:
        keypress_callback_table[key](stdscr, windows_queue)
    except KeyError:
        pass

def draw_menu(stdscr):
    k = 0

    windows_queue = []
    configure_window(stdscr, windows_queue, 1)

    # # Loop where k is the last character pressed
    while (k != CTL_Q):
        handle_keypress(k, stdscr, windows_queue)
        k = stdscr.getch()

def main():
    curses.wrapper(draw_menu)

if __name__ == "__main__":
    main()