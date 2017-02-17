import websockets
import asyncio
from contextlib import suppress
from xbox import Controller


Controller.init()
controller = Controller(0)

async def SendMessage():
    websocket = await websockets.connect('ws://10.243.193.47:8055/')
    #this is old IP 'ws://10.243.242.98:8055/' Isaiah changed on 2/6/17
    # zerotier IP of server
    try:
        while True:
            controller.update()
            # The x,a,b,y-----------------------------------  Binary representation: abxy
            message = "{} {} {} {}".format(controller.x(), controller.y(), controller.b(), controller.a())
            if controller.x() == 1:
                message = 0b0010
            elif controller.y() == 1:
                message = 0b0001
            elif controller.a() == 1:
                message = 0b1000
            elif controller.b() == 1:
                message = 0b0100
            elif controller.right_trigger() == 1:
                message = 0b0111

            left_t = int(controller.left_trigger() / 8)
            right_t = int(controller.right_trigger() / 8)
            if left_t < 0:
                left_t = 48
            if right_t < 0:
                right_t = 48
            message = right_t
            # The left and right analog sticks--------------
            # message = "{} {} {} {}".format(controller.left_y(), controller.left_x(), controller.right_x(), controller.right_y())

            # The left and right analog trigger-------------
            # message = "{} {}".format(controller.left_trigger(), controller.right_trigger())

            # The left and right bumpers
            # message = "{} {}".format(controller.left_bumper(), controller.right_bumper())
            if(message):
                await websocket.send(str(message))
            # else:
            #     await websocket.send("false")
            with suppress(asyncio.TimeoutError):
                response = await asyncio.wait_for(websocket.recv(), 1)
                print(response)
    finally:

        await websocket.close()

asyncio.get_event_loop().run_until_complete(SendMessage())
