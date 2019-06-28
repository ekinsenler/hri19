PEPPER_IP = '10.0.1.200'
PEPPER_CMD_PORT = '9559'
PC_IP = '10.0.1.202'
WEB_SOCKET_PORT = '9581'
HTTP_SERVER_PORT = '9580'

HTTP_SERVER = 'http://' + PC_IP + '/'

pepper_session = None


def get_pepper_session():
    global pepper_session
    if pepper_session is None:
        import qi
        pepper_session = qi.Session()
        try:
            pepper_session.connect("tcp://" + PEPPER_IP + ":" + PEPPER_CMD_PORT)
        except RuntimeError as e:
            print("Can't connect to Naoqi at ip \"" + PEPPER_IP + "\" on port " + PEPPER_CMD_PORT)
            raise e
    return pepper_session


def launch_address(url):
    tablet_service = get_pepper_session().service("ALTabletService")
    print("PEPPER launching URL: ", url)
    tablet_service.showWebview(url)


# Launch HTTP server
from web_server import WebServer, get_memory_game_url
import time

http_server = WebServer()
http_server.run_non_blocking(HTTP_SERVER_PORT)
# Wait server to start
time.sleep(3)

# Launch page on pepper
launch_address(get_memory_game_url(HTTP_SERVER))

# Launch websocket server
from websocket_server import WebsocketServer

# Called for every client connecting (after handshake)
def new_client(client, server):
    print("New client connected and was given id %d" % client['id'])
    server.send_message_to_all("Hey all, a new client has joined us")


# Called for every client disconnecting
def client_left(client, server):
    print("Client(%d) disconnected" % client['id'])


# Called when a client sends a message
def message_received(client, server, message):
    if len(message) > 200:
        message = message[:200] + '..'
    print("Client(%d) said: %s" % (client['id'], message))


server = WebsocketServer(WEB_SOCKET_PORT)
server.set_fn_new_client(new_client)
server.set_fn_client_left(client_left)
server.set_fn_message_received(message_received)
server.run_forever()
