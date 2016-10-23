import asyncio
import websockets

@asyncio.coroutine
def SendMessage():
    websocket = yield from websockets.connect('ws://localhost:8054/')

    try:
        while True:
            message = input("Your message: ")
            yield from websocket.send(message)
            


    finally:

        yield from websocket.close()

asyncio.get_event_loop().run_until_complete(SendMessage())
