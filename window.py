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
        self._serial_listener = None
        self._kill_listener_thread = False
        self._is_active_context = False
        self.refresh()

    @property
    def is_active_context(self):
        return self._is_active_context
    
    @is_active_context.setter
    def is_active_context(self, val):
        self._is_active_context = val
    
    def resize(self, lines, cols, y, x):
        self.win = self.stdscr.subwin(lines, cols, y, x)
        return self
        
    # TODO clean up string show logic somehow instead of just a rogue if statement
    def refresh(self):
        self.win.box()
        if self._win_id_vis == True:
            if self._is_active_context == True:
                CursesString(self.win, str(self.id), const.COLOR_BL_WH, 1, 1, -1)
            else:
                CursesString(self.win, str(self.id), const.COLOR_CY_BL, 1, 1, -1)
        self.win.touchwin()
        self.win.refresh()
    
    def start_serial(self):
        if self.ser.is_running == False:
            self.ser.start()
        if self._serial_listener == None:
            self._serial_listener = threading.Thread(target=self._listen, daemon=True)
            self._serial_listener.start()
    
    def stop_serial(self):
        self._kill_listener_thread = True
        self.ser.close()
        self.ser = None
    
    def _listen(self):
        with Client(self.ser.address, authkey=self.ser.authkey) as conn:
            while True:
                if self._kill_listener_thread == True:
                    break
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