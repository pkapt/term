import const
from curses_string import CursesString
from serial_conn import SerialConnection
from multiprocessing.connection import Client
import threading

class Window():
    # TODO: add handling for port
    def __init__(self, stdscr, id, lines, cols, y, x, port=None, win_id_vis=False):
        self.stdscr = stdscr
        self.win = stdscr.subwin(lines, cols, y, x)
        self.id = id
        self._win_id_vis = win_id_vis
        self.ser = SerialConnection(self.id, 'COM1', 115200)
        self.refresh()
    
    def resize(self, lines, cols, y, x):
        self.win = self.stdscr.subwin(lines, cols, y, x)
        return self
        
    # TODO clean up string show logic somehow instead of just a rogue if statement
    def refresh(self, header_highlight_vis=False):
        self.win.box()
        if self._win_id_vis == True:
            if header_highlight_vis == True:
                CursesString(self.win, str(self.id), const.COLOR_BL_WH, 1, 1, -1)
            else:
                CursesString(self.win, str(self.id), const.COLOR_CY_BL, 1, 1, -1)
        self.win.touchwin()
        self.win.refresh()
    
    def start_serial(self):
        self.ser.start()
        self._serial_listener = threading.Thread(target=self._listen, daemon=True)
        self._serial_listener.start()
    
    def _listen(self):
        with Client(self.ser.address, authkey=self.ser.authkey) as conn:
            while True:
                try:
                    bytes = conn.recv_bytes().decode('utf-8')
                    CursesString(self.win, bytes, const.COLOR_CY_BL, 2, 2, -1)
                    self.refresh()
                except UnicodeDecodeError:
                    # Usually just a serial connection issue - just ignore it.
                    pass
                except EOFError:
                    print('Connection lost - exiting.')
                    break