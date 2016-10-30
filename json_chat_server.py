import websockets
import asyncio
import json

async def receive_encoded(websocket, path):

    try:
        while True:
            encoded_message = await websocket.recv()
            dictionary = json.loads(encoded_message)
            print(dictionary['msg'])

    except websockets.exceptions.ConnectionClosed: pass


start_server = websockets.serve(receive_encoded, "0.0.0.0", 8054)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
