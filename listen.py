""" Listener class for inter-process communication.

This can be used to allow other scripts to attach to the main process to view
other information, such as serial logs and MQTT messages.
"""

from multiprocessing.connection import Listener
import threading
import queue

class BackgroundListener(Listener):
    """ Listener for inter-process communication. """

    def __init__(self, address, authkey):
        super().__init__(address, authkey=authkey)
        self._queue = queue.Queue()
        self._conn = None
        self._thread = None

    def start(self):
        """ Start the listener loop in a daemon thread. """
        self._thread = threading.Thread(target=self.run, daemon=True)
        self._thread.start()

    def run(self):
        """ Start the listener loop in the current thread.

        Normally this is called by the internal listener thread and does not
        need to be called externally.
        """
        while True:
            # Wait for connection
            if self._conn is None:
                self._conn = self.accept()
            bytes_to_send = self._queue.get()
            try:
                self._conn.send_bytes(bytes_to_send)
            except BrokenPipeError:
                # Client has disconnected - just reset it to wait for a new
                # one.
                self._conn = None
            except ConnectionResetError:
                # [WinError 10054] An existing connection was forcibly closed by the remote host
                break
            except ConnectionAbortedError:
                # [WinError 10053] An established connection was aborted by the software in your host machine
                break

    @property
    def is_connected(self):
        """ Determine if this listener has any attached clients. """
        return self._conn is not None

    def send(self, byte_string):
        """ Send a byte string to any attached clients.

        If no clients are available, this will have no effect.
        """
        if self._conn is not None:
            self._queue.put(byte_string)
