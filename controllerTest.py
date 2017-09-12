from time import sleep
from xbox import *

Controller.init()
controller = Controller(0)
oldRobot = {}

while True:
    controller.update()
    l_stick = round(controller.left_x(), 1)
    r_stick = round(controller.right_y(), 1)
    robot = {}
    oldRobot = {}
    robot['x'] = 1 if controller.x() else 0
    robot['y'] = 1 if controller.y() else 0
    robot['a'] = 1 if controller.a() else 0
    robot['b'] = 1 if controller.b() else 0
    robot['fwd'] = int(controller.right_trigger() >> 3)  # To implement turning, we will want to grab the left stick and adjust Fwd/Rev appropriately.
    robot['rev'] = int(controller.left_trigger() >> 3)
    robot['lstick'] = int(10*l_stick) if abs(l_stick) > 0.1 else 0
    #robot['vision'] = 1 if str(controller.hat).strip() == 'd' else 0
    #robot['peek'] = 1 if str(controller.hat).strip() == 'u' else 0
    #robot['neutral'] = 1 if str(controller.hat).strip() == 'r' else 0
    robot['rstick'] = int(-10*r_stick) if abs(r_stick) > 0.1 else 0
    robot['lbump'] = 1 if controller.left_bumper() else 0
    robot['tunnel'] = 1 if controller.select_button() else 0
    robot['default'] = 1 if controller.start_button() else 0
    # This needs testing, but logic seems in order.
    robot['lbx'] = 1 if controller.left_bumper() and controller.x() else 0
    robot['lbb'] = 1 if controller.left_bumper() and controller.b() else 0
    robot['lby'] = 1 if controller.left_bumper() and controller.y() else 0
    robot['lba'] = 1 if controller.left_bumper() and controller.a() else 0
    #robot['rby'] = 1 if controller.right_bumper() and controller.y() else 0
    #robot['rba'] = 1 if controller.right_bumper() and controller.a() else 0
    #robot['rbx'] = 1 if controller.right_bumper() and controller.x() else 0
    #robot['rbb'] = 1 if controller.right_bumper() and controller.b() else 0
    # If leftStick.X < 0 then we want to trim off the left motor to turn left.
    # If leftStick.X > 0 then we want to trim off the right motor to turn right.
    robot['valid'] = 1  # Was testing not spamming controller but that is impossible.

    print(robot)
    sleep(.5)
