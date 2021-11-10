import sys,os
import curses

CTL_N = 14
CTL_W = 23

def configure_window(stdscr, windows_queue, n):
    windows_queue.clear()
    height, width = stdscr.getmaxyx()

    def one():
        win_width = int(width/2)
        windows_queue.append(stdscr.subwin(height, win_width, 0, 0))
        windows_queue.append(stdscr.subwin(height, win_width, 0, win_width))

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

    handler_func = win_handler_table(n)
    if callable(handler_func):
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
    keypress_callback_table[key](stdscr, windows_queue)

def draw_menu(stdscr):
    k = 0

    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()

    # Start colors in curses
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    height, width = stdscr.getmaxyx()
    windows_queue = []
    box1 = stdscr.subwin(height, width, 0, 0)
    box1.box()
    box1.touchwin()
    box1.refresh()
    windows_queue.append(box1)

    # # Loop where k is the last character pressed
    while (k != ord('q')):

        # Initialization
        height, width = stdscr.getmaxyx()

        handle_keypress(k, stdscr, windows_queue)

        if k == CTL_N:
            q_len = len(windows_queue)
            if q_len < 4:
                windows_queue = []
                stdscr.clear()
            if q_len == 1:
                win_width = int(width/2)
                windows_queue.append(stdscr.subwin(height, win_width, 0, 0))
                windows_queue.append(stdscr.subwin(height, win_width, 0, win_width))
            elif q_len == 2:
                win_width = int(width/3)
                windows_queue.append(stdscr.subwin(height, win_width, 0, 0))
                windows_queue.append(stdscr.subwin(height, win_width, 0, win_width))
                windows_queue.append(stdscr.subwin(height, win_width, 0, win_width*2))
            elif q_len == 3:
                win_width = int(width/2)
                win_height = int(height/2)
                windows_queue.append(stdscr.subwin(win_height, win_width, 0, 0))
                windows_queue.append(stdscr.subwin(win_height, win_width, 0, win_width))
                windows_queue.append(stdscr.subwin(win_height, win_width, win_height, 0))
                windows_queue.append(stdscr.subwin(win_height, win_width, win_height, win_width))
                pass
            else:
                print('max number of windows reached')

            for window in windows_queue:
                window.box()
                window.touchwin()
                window.refresh()
        
        k = stdscr.getch()
        
        
    #     for win in windows_queue:
    #         win.box()
    #         win.touchwin()
    #         win.refresh()

    #     # Refresh the screen
    #     stdscr.refresh()

    #     # Wait for next input
    #     k = stdscr.getch()

def main():
    curses.wrapper(draw_menu)

if __name__ == "__main__":
    main()