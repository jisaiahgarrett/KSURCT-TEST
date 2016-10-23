import websockets
import asyncio

async def SendMessage(websocket, path):
    try:

        while True:
            message = await websocket.recv()
            print("< {}".format(message))
    except websockets.exceptions.ConnectionClosed: pass

start_server = websockets.serve(SendMessage, 'localhost', 8054)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
