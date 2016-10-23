import websockets 
import asyncio

async def hello(websocket, path):
	try:	
		while True:
			name = await websocket.recv()
			print("< {}".format(name))

			greeting = "Hello {}!".format(name)
			await websocket.send(greeting)
			print("> {}".format(greeting))
	except websockets.exceptions.ConnectionClosed: pass

start_server = websockets.serve(hello, 'localhost', 8054)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
