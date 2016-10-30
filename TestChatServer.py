import websockets
import asyncio

async def SendMessage(websocket, path):
    #figure out websocket, path


    try:

        while True:
            message = await websocket.recv()
            print("< {}".format(message))

            await websocket.send(message)
            print("> {}".format(message))

    except websockets.exceptions.ConnectionClosed: pass



start_server = websockets.serve(SendMessage, "0.0.0.0" , 8054)
                #update what function its looping

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
