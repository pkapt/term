import curses 
import threading

class FieldConfigEntry:
    def __init__(self, type=None, value=None):
        self.type = type
        self.value = value

'''
This is a widget to input text fields eg.
    Text Field 1     ████████████    
    Text Field 2     ████████████    
    Text Field n     ████████████    
'''
class FieldInput():
    def __init__(self, stdscr, config):
        self.stdscr = stdscr
        self._config = config
        self.data = None
        for key in self._config:
            self.data[key] = FieldConfigEntry(type=self._config[key])

    def draw(self):
        self._update()
        self._worker_thread = threading.Thread(target=self._listen_user_input)

    def _update(self):
        pass

    def _listen_user_input(self):
        while True:
            if False: # some flag to kill thread
                break
            input = self.stdscr.getch()
            # do something with input
