import websockets
import asyncio
from contextlib import suppress
from xbox import Controller


Controller.init()
controller = Controller(0)

async def SendMessage():
    websocket = await websockets.connect('ws://10.243.193.47:8055/')
    # zerotier IP of server
    # was ws://localhost:8055/
    try:
        while True:
            controller.update()
            # The x,a,b,y-----------------------------------
            # message = "{} {} {} {}".format(controller.x(), controller.y(), controller.b(), controller.a())

            # The left and right analog sticks--------------
            # message = "{} {} {} {}".format(controller.left_y(), controller.left_x(), controller.right_x(), controller.right_y())

            # The left and right analog trigger-------------
            # message = "{} {}".format(controller.left_trigger(), controller.right_trigger())

            # The left and right bumpers
            message = "{} {}".format(controller.left_bumper(), controller.right_bumper())
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
