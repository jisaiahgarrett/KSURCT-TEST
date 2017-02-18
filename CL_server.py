import asyncio
import websockets
import RPi.GPIO as GPIO

from logging import Logger
from contextlib import suppress

import Adafruit_PCA9685  # servo libraries from Adafruit

port = 8055
logger = Logger(__name__)

# Initialize the servos with default I2C address (0x40)
shoulder1 = Adafruit_PCA9685.PCA9685()
shoulder1.set_pwm_freq(60)
SHOULDER1_ALT = 300
shoulder2 = Adafruit_PCA9685.PCA9685()
shoulder2.set_pwm_freq(60)
shoulder2_alt = 492
leftMotor = Adafruit_PCA9685.PCA9685()
leftMotor.set_pwm_freq(1600)
rightMotor = Adafruit_PCA9685.PCA9685()
rightMotor.set_pwm_freq(1600)

# Servo channel information
SHOULDER1_CHA = 0
SHOULDER2_CHA = 1
LEFTM_CHA = 14
RIGHTM_CHA = 15

# Set up the GPIO pin for toggling reverse/forward motors.
GPIO.setmode(GPIO.BCM)
GPIO_FWD_PIN = 18
GPIO_REV_PIN = 17
GPIO.setup(GPIO_FWD_PIN, GPIO.OUT)
GPIO.setup(GPIO_REV_PIN, GPIO.OUT)

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
        if msg == "2":  # Left - X
            shoulder1.set_pwm(SHOULDER1_CHA, 0, SHOULDER1_ALT)
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
            shoulder1.set_pwm(SHOULDER1_CHA, 0, 2*SHOULDER1_ALT)
        else:
            shoulder1.set_pwm(SHOULDER1_CHA, 0, 0)  # Restore the servo to a safe value if not doing anything (was 392)
            if msg != "False False False False":  # If the input is an actual state change
               msg = int(msg)  # Convert the message string into an actual PWM value that the motor can use
               if msg < 0:
                    GPIO.output(GPIO_REV_PIN, GPIO.HIGH)
                    GPIO.output(GPIO_FWD_PIN, GPIO.LOW)
                    msg = -msg
               else:
                    GPIO.output(GPIO_FWD_PIN, GPIO.HIGH)
                    GPIO.output(GPIO_REV_PIN, GPIO.LOW)

               leftMotor.set_pwm(LEFTM_CHA, 0, msg)
               rightMotor.set_pwm(RIGHTM_CHA, 0, msg)
            else:
                leftMotor.set_pwm(LEFTM_CHA, 0, 0)
                rightMotor.set_pwm(RIGHTM_CHA, 0, 0)
                GPIO.output(GPIO_FWD_PIN, GPIO.LOW)
                GPIO.output(GPIO_REV_PIN, GPIO.LOW)
        # print(msg)  # debugging purposes (seeing the value change)
        await self.send(str(msg))

    async def send(self, msg):
        logger.debug('sending new message')
        for ws in self._active_connections:
            asyncio.ensure_future(ws.send(msg))

server = CLserver(port)


asyncio.get_event_loop().run_until_complete(server.start_server())

asyncio.get_event_loop().run_forever()
