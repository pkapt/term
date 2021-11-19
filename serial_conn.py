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

    def start(self):
        self._ser_listener_thread = threading.Thread(target=self._get_serial_output, daemon=True)
        self._ser_listener_thread.start()

    #TODO make this actually get serial output instead of this dummy stuff
    def _get_serial_output(self):
        import time
        while True:
            packet = ("fartmanfromthegrave " + str(self.address)).encode('utf-8')
            self.socket.send(packet)
            time.sleep(.8)

