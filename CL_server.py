import asyncio
import websockets

from logging import Logger
from contextlib import suppress

port = 8055
logger = Logger(__name__)


class CLserver(object):
    def __init__(self, port):
        self._active_connections = set()
        self.port = port

    async def start_server(self):
        self.server = await websockets.serve(self.handle_new_connection, '0.0.0.0', self.port)

    async def handle_new_connection(self, ws, path):
        self._active_connections.add(ws)
        # print(ws)
        with suppress(websockets.ConnectionClosed):
            while True:
                result = await ws.recv()
                await self.handle_msg(result)
        self._active_connections.remove(ws)

    async def handle_msg(self, msg):
        print(msg)
        await self.send(msg)

    async def send(self, msg):
        for ws in self._active_connections:
            asyncio.ensure_future(ws.send(msg))

server = CLserver(port)


asyncio.get_event_loop().run_until_complete(server.start_server())

asyncio.get_event_loop().run_forever()
