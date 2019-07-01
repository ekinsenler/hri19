def run_sockets(host, port, new_client_callback, client_left_callback, message_received_callback):
    from websocket_server import WebsocketServer
    server = WebsocketServer(port, host=host)
    server.set_fn_new_client(new_client_callback)
    server.set_fn_client_left(client_left_callback)
    server.set_fn_message_received(message_received_callback)
    server.run_forever()
