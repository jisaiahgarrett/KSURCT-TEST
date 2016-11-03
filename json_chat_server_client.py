import websockets
import asyncio
import json
from contextlib import suppress


async def send_encoded():
    websocket = await websockets.connect('ws://localhost:8054/')

    try:
        while True:
            message = input()
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
