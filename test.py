import asyncio
import websockets

@asyncio.coroutine
def hello():
	websocket = yield from websockets.connect('ws://localhost:8054/')

	try:
		while True:
			message = input("Type anything, it will echo back")
			yield from websocket.send(message)
			print(message)

			response = yield from websocket.recv()
			print(response)
	finally:

		yield from websocket.close()

asyncio.get_event_loop().run_until_complete(hello())
