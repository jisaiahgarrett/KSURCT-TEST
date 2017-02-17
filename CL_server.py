import asyncio
import websockets

from logging import Logger
from contextlib import suppress

import Adafruit_PCA9685  # servo libraries from Adafruit

port = 8055
logger = Logger(__name__)

# Initialize the servos with default I2C address (0x40)
shoulder1 = Adafruit_PCA9685.PCA9685()
shoulder1.set_pwm_freq(60)
shoulder2 = Adafruit_PCA9685.PCA9685()
shoulder2.set_pwm_freq(60)
shoulder2_alt = 426
leftMotor = Adafruit_PCA9685.PCA9685()
leftMotor_pwr = 0
leftMotor.set_pwm_freq(20000)
rightMotor = Adafruit_PCA9685.PCA9685()
rightMotor_pwr = 0
rightMotor.set_pwm_freq(20000)

# Servo channel information
SHOULDER1_CHA = 0
SHOULDER2_CHA = 1
LEFTM_CHA = 15
RIGHTM_CHA = 14

class CLserver(object):
    def __init__(self, port):
        self._active_connections = set()
        self.port = port

    async def start_server(self):
        logger.info('server starting up')
        self.server = await websockets.serve(self.handle_new_connection, '0.0.0.0', self.port)

    async def handle_new_connection(self, ws, path):
        logger.debug('new connection to server')
        self._active_connections.add(ws)
        with suppress(websockets.ConnectionClosed):
            while True:
                result = await ws.recv()
                await self.handle_msg(result)
        self._active_connections.remove(ws)

    async def handle_msg(self, msg):
        logger.debug('new message handled')
        global shoulder2_alt
        global leftMotor_pwr
        global rightMotor_pwr
        if msg == "2":  # Left - X
            shoulder1.set_pwm(0, 0, 398)
        elif msg == "1":  # Up - Y
            if shoulder2_alt >= 600: # servo maximum, make sure we do not go over this value
                shoulder2_alt = 599
            shoulder2.set_pwm(SHOULDER2_CHA, 0, shoulder2_alt)
            shoulder2_alt += 1 # CHANGE THIS INCREMENT IF NOT FAST/SLOW ENOUGH
        elif msg == "8":  # Down - A
            if shoulder2_alt <= 299:  # servo minimum, make sure we do not go under this value
                shoulder2_alt = 300
            shoulder2.set_pwm(SHOULDER2_CHA, 0, shoulder2_alt)
            shoulder2_alt -= 1  # CHANGE THIS DECREMENT IF NOT FAST/SLOW ENOUGH
        elif msg == "4":  # Right - B
            shoulder1.set_pwm(SHOULDER1_CHA, 0, 385)
        elif msg == "3":  # Left Trigger (reverse)
            leftMotor_pwr = rightMotor_pwr = 0
            leftMotor.set_pwm(LEFTM_CHA, 0, leftMotor_pwr)
            rightMotor.set_pwm(RIGHTM_CHA, 0, rightMotor_pwr)
        elif msg == "7":  # Right Trigger (forward)
            leftMotor_pwr = rightMotor_pwr = 4000
            leftMotor.set_pwm(LEFTM_CHA, 0, leftMotor_pwr)
            rightMotor.set_pwm(RIGHTM_CHA, 0, rightMotor_pwr)
        else:
            shoulder1.set_pwm(SHOULDER1_CHA, 0, 392)  # Restore the servo to a safe value if not doing anything
            leftMotor.set_pwm(LEFTM_CHA, 0, int(msg))  # Convert the message string into an acutal PWM value that the motor can use
        print(shoulder2_alt)  # debugging purposes (seeing the value change)
        await self.send(msg)

    async def send(self, msg):
        logger.debug('sending new message')
        for ws in self._active_connections:
            asyncio.ensure_future(ws.send(msg))

server = CLserver(port)


asyncio.get_event_loop().run_until_complete(server.start_server())

asyncio.get_event_loop().run_forever()
