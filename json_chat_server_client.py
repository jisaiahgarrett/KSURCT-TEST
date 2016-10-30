import websockets
import asyncio
import json


@asyncio.coroutine
def send_encoded():
    websocket = yield from websockets.connect('ws://localhost:8054/')

    try:
        while True:
            message = input()
            encoded_message = {
                'msg': message,
            }
            d = json.dumps(encoded_message)  #encodes the dictionary "d"
            yield from websocket.send(d)

    finally:

        yield from websocket.close()

asyncio.get_event_loop().run_until_complete(send_encoded())
