import threading
import listen

class SerialConnection:
    BASE_PORT = 6000
    def __init__(self, id, port, baud):
        self.address = ('localhost', self.BASE_PORT + id)
        self.authkey = b'password'
        self.port = port
        self.baud = baud
        self.socket = listen.BackgroundListener(self.address, self.authkey)
        self.socket.start()
        self._ser_listener_thread = None
        self._kill_serial_output = False

    def start(self):
        if self._ser_listener_thread == None:
            self._ser_listener_thread = threading.Thread(target=self._get_serial_output, daemon=True)
            self._ser_listener_thread.start()

    def close(self):
        self.socket.close()
        self._kill_serial_output = True
    
    @property
    def is_running(self):
        return (self._ser_listener_thread != None) and (self._ser_listener_thread.is_alive())

    #TODO make this actually get serial output instead of this dummy stuff
    def _get_serial_output(self):
        import time
        c = 0
        while True:
            if self._kill_serial_output == True:
                break
            packet = ("time " + str(c) + " " + str(self.address)).encode('utf-8')
            self.socket.send(packet)
            time.sleep(.8)
            c += 1

