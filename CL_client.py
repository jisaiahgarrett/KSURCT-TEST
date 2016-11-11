import websockets
import asyncio

async def SendMessage():
    websocket = await websockets.connect('ws://localhost:8055/')

    try:
        while True:
            # message = input("Your message: ")
            # await websocket.send(message)

            response = await websocket.recv()
            print(response)
    finally:

        await websocket.close()

asyncio.get_event_loop().run_until_complete(SendMessage())
