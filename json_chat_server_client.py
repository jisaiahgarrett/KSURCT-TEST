import websockets
import sys
import asyncio
import json
from contextlib import suppress


class AioStdin(object):
    def __init__(self):
        self._queue = asyncio.Queue()
        asyncio.get_event_loop().add_reader(
            sys.stdin.fileno(),
            lambda: self._queue.put_nowait(sys.stdin.readline()))

    async def read(self):
        return await self._queue.get()

aio_stdin = AioStdin()


async def send_encoded():
    websocket = await websockets.connect('ws://localhost:8054/')

    try:
        while True:
            # message = input()
            message = await aio_stdin.read()
            print(message)
            encoded_message = {
                'msg': message,
            }
            d = json.dumps(encoded_message) #encodes the dictionary "d"
            await websocket.send(d)

            with suppress(asyncio.TimeoutError):
                msg = await asyncio.wait_for(websocket.recv(), .1)
                json.loads(msg)
    finally:

        await websocket.close()

asyncio.get_event_loop().run_until_complete(send_encoded())
