server = ClientlessWebSocketServer(config.port)

while True:
    server.start_server()
