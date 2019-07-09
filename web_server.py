import threading

from flask import Flask, request, send_from_directory


def get_memory_game_url(pc_address):
    return pc_address + 'memorygame/game.html'

def get_welcomepage_url(pc_address):
    return pc_address + 'welcome/welcome.html'

class WebServer:

    def __init__(self):

        self.app = Flask(__name__, static_url_path='')

        @self.app.route('/memorygame/<path:filename>')
        def memorygame(filename):
            print(filename)
            return send_from_directory('./memorygame', filename)

        @self.app.route('/welcome/<path:filename>')
        def welcome(filename):
            print(filename)
            return send_from_directory('./welcome', filename)

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


if __name__ == '__main__':
    import argparse
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--port", default='9580')

    args = arg_parser.parse_args()

    http_server = WebServer()
    http_server.run(args.port)
