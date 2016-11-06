import websockets
import asyncio
import json

all_websockets = set()


async def receive_encoded(websocket, path):
    all_websockets.add(websocket)
    print("WEBSOCKET ADDED")
    try:
        while True:
            encoded_message = await websocket.recv()
            dictionary = json.loads(encoded_message)
            for websocket_ in all_websockets:
                print(dictionary['msg'])
                await websocket_.send(encoded_message)
                # print(all_websockets)

    except websockets.exceptions.ConnectionClosed:
        pass

    finally:
        all_websockets.remove(websocket)
        print("WEBSOCKET REMOVED")

start_server = websockets.serve(receive_encoded, "0.0.0.0", 8054)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
