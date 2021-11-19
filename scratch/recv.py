import listen
import time
import threading
from multiprocessing.connection import Client

address = ('localhost', 6000)
authkey = b'password'


def _get_text():
    # conn = Client(address, authkey=authkey)
    # while True:
    #     a = conn.recv_bytes()
    #     print('asdf')
    #     if a != None:
    #         print(a)

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

# thread1 = threading.Thread(target=_put_text, daemon=True)
# thread2 = threading.Thread(target=_get_text, daemon=True)
# thread1.start()

_get_text()

# _put_text()