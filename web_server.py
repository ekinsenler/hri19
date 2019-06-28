import threading

from flask import Flask, request, send_from_directory


def get_memory_game_url(pc_address):
    return pc_address + 'memorygame/game.html'


class WebServer:

    def __init__(self) -> None:
        super().__init__()

        self.app = Flask(__name__, static_url_path='')

        @self.app.route('/memorygame/<path:filename>')
        def memorygame(filename):
            print(filename)
            return send_from_directory('./memorygame', filename)

        @self.app.route('/<path:filename>')
        def root(filename):
            return send_from_directory('./', filename)

        @self.app.route('/')
        def default():
            return send_from_directory('./', 'index.html')

    def run(self, port):
        self.app.run(host='0.0.0.0', port=port)

    def run_non_blocking(self, port):
        def work():
            self.run(port)

        thread = threading.Thread(target=work)
        thread.start()

import socket
import time
PC_IP = socket.gethostbyname(socket.gethostname())
HTTP_SERVER_PORT = '9585'
HTTP_SERVER = 'http://' + PC_IP + '/'
print (HTTP_SERVER)

http_server = WebServer()
http_server.run_non_blocking(HTTP_SERVER_PORT)