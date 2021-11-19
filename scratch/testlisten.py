import listen
import time
import threading
from multiprocessing.connection import Client

address = ('localhost', 6001)
authkey = b'password'
listener = listen.BackgroundListener(address, authkey)
listener.start()

def _put_text():
    while True:
        listener.send(b'heres some text')
        time.sleep(.5)

def _get_text():
    with Client(address, authkey=authkey) as conn:
        while True:
            try:
                print(conn.recv_bytes().decode('utf-8'), end='', flush=True)
            except UnicodeDecodeError:
                # Usually just a serial connection issue - just ignore it.
                pass
            except EOFError:
                print('Connection lost - exiting.')
                break

thread1 = threading.Thread(target=_put_text, daemon=True)
thread1.start()

_get_text()
