import websockets
import asyncio
from contextlib import suppress
from xbox import Controller
import pickle

Controller.init()
controller = Controller(0)
counter = 0

async def SendMessage():
    websocket = await websockets.connect('ws://10.243.193.47:8055/')  # zerotier IP of server
    try:
        while True:
            controller.update()
            robot = {}
            robot['x'] = 1 if controller.x() else 0
            robot['y'] = 1 if controller.y() else 0
            robot['a'] = 1 if controller.a() else 0
            robot['b'] = 1 if controller.b() else 0
            robot['fwd'] =  int(controller.left_trigger() >> 3)
            robot['rev'] = int(controller.right_trigger() >> 3)

    #        if controller.x() == 1:
    #            message = 0b0010
    #        elif controller.y() == 1:
    #            message = 0b0001
    #        elif controller.a() == 1:
    #            message = 0b1000
    #        elif controller.b() == 1:
    #            message = 0b0100
    #        else:
    #            left_t = int(controller.left_trigger() >> 3)
    #            right_t = int(controller.right_trigger() >> 3)
    #            if right_t > 0:
    #                message = right_t  # Forward (positive value)
    #            elif left_t > 0:
    #                message = -left_t  # Reverse (hence the negative)

            if(robot):
                await websocket.send(pickle.dumps(robot))

            with suppress(asyncio.TimeoutError):
                global counter
                response = await asyncio.wait_for(websocket.recv(), 1)
                print(pickle.load(response))
    finally:

        await websocket.close()

asyncio.get_event_loop().run_until_complete(SendMessage())
