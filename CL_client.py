import websockets
import asyncio
from contextlib import suppress
from xbox import Controller


Controller.init()
controller = Controller(0)

async def SendMessage():
    websocket = await websockets.connect('ws://localhost:8055/')

    try:
        while True:
            controller.update()
            message = controller.y()
            if(message):
                await websocket.send(str(message))
            else:
                await websocket.send("false")
            with suppress(asyncio.TimeoutError):
                response = await asyncio.wait_for(websocket.recv(), 1)
                print(response)
    finally:

        await websocket.close()

asyncio.get_event_loop().run_until_complete(SendMessage())
