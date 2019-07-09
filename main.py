PEPPER_CMD_PORT = '9559'
WEB_SOCKET_PORT = 9581
HTTP_SERVER_PORT = '9580'

PEPPER_BWSR_ID = 'Linux; Android 5.1; LPT_200AR Build/LMY47I'

from web_server import get_memory_game_url, get_welcomepage_url
from humanGreeter import HumanGreeter

if __name__ == '__main__':
    import argparse

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--emul", default=False, type=bool)
    arg_parser.add_argument("--pep_ip", default='10.0.1.200')
    arg_parser.add_argument("--pc_ip", default='10.0.1.204')

    args = arg_parser.parse_args()

    is_emulation = args.emul
    HTTP_SERVER = 'http://' + args.pc_ip + ':' + HTTP_SERVER_PORT + '/'

    pepper_application = None

    def get_pepper_application():
        global pepper_application
        if pepper_application is None:
            import qi
            try:
                pepper_application = qi.Application(["HumanGreeter", "SpeechRecognition", "--qi-url=" + "tcp://" + args.pep_ip + ":" + PEPPER_CMD_PORT])
                pepper_application.start()
            except RuntimeError as e:
                print("Can't connect to Naoqi at ip \"" + args.pep_ip + "\" on port " + PEPPER_CMD_PORT)
                raise e
        return pepper_application


    def launch_address(url):
        if is_emulation:
            import webbrowser as wb
            wb.open_new_tab(url)
        else:
            tablet_service = get_pepper_application().session.service("ALTabletService")
            print("PEPPER launching URL: ", url)
            tablet_service.showWebview(url)

    # Launch page on pepper
    #launch_address(get_memory_game_url(HTTP_SERVER))
    get_pepper_application()

    # Called for every client connecting (after handshake)
    def new_client(client, server):
        print("New client connected and was given id %d" % client['id'])
        server.send_message_to_all("Hey all, a new client has joined us")
        launch_address(get_welcomepage_url(HTTP_SERVER))
        human_greeter = HumanGreeter(get_pepper_application())
        human_greeter.run()

    # Called for every client disconnecting
    def client_left(client, server):
        print("Client(%d) disconnected" % client['id'])


    # Called when a client sends a message
    def message_received(client, server, message):
        print("Client(%d) said: %s" % (client['id'], message))
        if message == "WELCOME_SCREEN":
            human_greeter = HumanGreeter(get_pepper_application())
            human_greeter.run()
            launch_address()
        elif message == "GAME_INIT":
            launch_address(get_memory_game_url(HTTP_SERVER))
        elif message == "GAME_WINNER":
            pass
        elif message == "GAME_MISTAKES_2":
            pass
        elif message == "GAME_MISTAKES_4":
            pass
        elif message == "GAME_GOOD_1":
            pass
        elif message == "GAME_GOOD_2":
            pass


    from web_sockets import run_sockets
    #run_sockets(args.pc_ip, WEB_SOCKET_PORT, new_client, client_left, message_received)
    #launch_address(get_welcomepage_url(HTTP_SERVER))
    human_greeter = HumanGreeter(get_pepper_application())
    human_greeter.run()
    launch_address(get_welcomepage_url(HTTP_SERVER))
