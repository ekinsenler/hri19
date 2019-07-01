PEPPER_CMD_PORT = '9559'
WEB_SOCKET_PORT = 9581
HTTP_SERVER_PORT = '9580'

from web_server import get_memory_game_url

if __name__ == '__main__':
    import argparse

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--emul", default=False, type=bool)
    arg_parser.add_argument("--pep_ip", default='10.0.1.200')
    arg_parser.add_argument("--pc_ip", default='10.0.1.204')

    args = arg_parser.parse_args()

    is_emulation = args.emul
    HTTP_SERVER = 'http://' + args.pc_ip + ':' + HTTP_SERVER_PORT + '/'

    pepper_session = None

    def get_pepper_session():
        global pepper_session
        if pepper_session is None:
            import qi
            pepper_session = qi.Session()
            try:
                pepper_session.connect("tcp://" + args.pep_ip + ":" + PEPPER_CMD_PORT)
            except RuntimeError as e:
                print("Can't connect to Naoqi at ip \"" + args.pep_ip + "\" on port " + PEPPER_CMD_PORT)
                raise e
        return pepper_session


    def launch_address(url):
        if is_emulation:
            import webbrowser as wb
            wb.open_new_tab(url)
        else:
            tablet_service = get_pepper_session().service("ALTabletService")
            print("PEPPER launching URL: ", url)
            tablet_service.showWebview(url)

    # Launch page on pepper
    launch_address(get_memory_game_url(HTTP_SERVER))

    # Called for every client connecting (after handshake)
    def new_client(client, server):
        print("New client connected and was given id %d" % client['id'])
        server.send_message_to_all("Hey all, a new client has joined us")


    # Called for every client disconnecting
    def client_left(client, server):
        print("Client(%d) disconnected" % client['id'])


    # Called when a client sends a message
    def message_received(client, server, message):
        print("Client(%d) said: %s" % (client['id'], message))


    from web_sockets import run_sockets
    run_sockets(args.pc_ip, WEB_SOCKET_PORT, new_client, client_left, message_received)
