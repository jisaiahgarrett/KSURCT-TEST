import websockets
import asyncio
from contextlib import suppress
from xbox import Controller
import pickle

Controller.init()
controller = Controller(0)
oldRobot = {}


async def SendMessage():
    websocket = await websockets.connect('ws://10.243.193.47:8055/')  # zerotier IP of server
    try:
        while True:
            controller.update()
            l_stick = round(controller.left_x(), 1)
            r_stick = round(controller.right_y(), 1)
            robot = {}
            robot['x'] = 1 if controller.x() else 0
            robot['y'] = 1 if controller.y() else 0
            robot['a'] = 1 if controller.a() else 0
            robot['b'] = 1 if controller.b() else 0
            robot['fwd'] = int(controller.right_trigger() >> 3)  # To implement turning, we will want to grab the left stick and adjust Fwd/Rev appropriately.
            robot['rev'] = int(controller.left_trigger() >> 3)
            robot['lstick'] = int(10*l_stick) if abs(l_stick) > 0.1 else 0
            robot['vision'] = 1 if str(controller.hat).strip() == 'd' else 0
            robot['peek'] = 1 if str(controller.hat).strip() == 'u' else 0
            robot['rstick'] = int(-10*r_stick) if abs(r_stick) > 0.1 else 0
            robot['lbump'] = 1 if controller.left_bumper() else 0

            # This needs testing, but logic seems in order.
            robot['lbx'] = 1 if controller.left_bumper() and controller.x() else 0
            robot['lbb'] = 1 if controller.left_bumper() and controller.b() else 0
            robot['lby'] = 1 if controller.left_bumper() and controller.y() else 0
            robot['lba'] = 1 if controller.left_bumper() and controller.a() else 0
            robot['rby'] = 1 if controller.right_bumper() and controller.y() else 0
            robot['rba'] = 1 if controller.right_bumper() and controller.a() else 0
            # If leftStick.X < 0 then we want to trim off the left motor to turn left.
            # If leftStick.X > 0 then we want to trim off the right motor to turn right.


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

            if(robot != oldRobot):
                print(robot)
                await websocket.send(pickle.dumps(robot))
            with suppress(asyncio.TimeoutError):
                response = await asyncio.wait_for(websocket.recv(), 1)
    finally:

        await websocket.close()

asyncio.get_event_loop().run_until_complete(SendMessage())
