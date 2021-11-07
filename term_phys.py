import sys,os
import curses

KEY_NEW = 14

def draw_menu(stdscr):
    k = 0
    cursor_x = 0
    cursor_y = 0

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

        if k == KEY_NEW:
            q_len = len(windows_queue)
            if q_len < 3:
                stdscr.clear()
                for window in windows_queue:
                    windows_queue.remove(window)
                    del window
            if q_len == 1:
                win_width = int(width/2)
                windows_queue.append(stdscr.subwin(height, win_width, 0, 0))
                windows_queue.append(stdscr.subwin(height, win_width, 0, win_width))
            elif q_len == 2:
                pass
            elif q_len == 3:
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