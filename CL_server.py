import asyncio
import websockets

from logging import Logger
from contextlib import suppress

import Adafruit_PCA9685 # servo libraries from Adafruit

port = 8055
logger = Logger(__name__)

# Initialize the servos with default I2C address (0x40)
shoulder1 = Adafruit_PCA9685.PCA9685()
shoulder1.set_pwm_freq(60)
shoulder2 = Adafruit_PCA9685.PCA9685()
shoulder2.set_pwm_freq(60)
shoulder2_alt = 426

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
        # print(ws)
        with suppress(websockets.ConnectionClosed):
            while True:
                result = await ws.recv()
                await self.handle_msg(result)
        self._active_connections.remove(ws)

    async def handle_msg(self, msg):
        logger.debug('new message handled')
        global shoulder2_alt
      #  print(msg)
       # if msg[0] == "True": # If the X button is held down, turn the servo.
       #    servo.set_pwm(0, 0, 385) # Configuration high for Parallax servo.  CHANGE THIS TO SERVO YOU ARE USING.
       # elif msg[0] == "False": # If the X button is released, restore the servo.
       #     servo.set_pwm(0, 0, 391) # Configuration low for Parallax servo.  CHANGE THIS TO SERVO YOU ARE USING.  
       # elif msg[2] == "True":
       #     servo.set_pwm(0, 0, 398)
        if msg == "2": # Left - X
            shoulder1.set_pwm(0, 0, 398)
        elif msg == "1": # Up - Y
            if shoulder2_alt >= 600: # servo maximum
                shoulder2_alt = 599
          #  shoulder2.set_pwm(1, 0, 398)
            shoulder2.set_pwm(1, 0, shoulder2_alt)
            shoulder2_alt += 1 # CHANGE THIS INCREMENT IF NOT FAST/SLOW ENOUGH
        elif msg == "8": # Down - A
          #  shoulder2.set_pwm(1, 0, 382)
            if shoulder2_alt <= 299:  # servo minimum
                shoulder2_alt = 300
            shoulder2.set_pwm(1, 0, shoulder2_alt)
            shoulder2_alt -= 1 # CHANGE THIS DECREMENT IF NOT FAST/SLOW ENOUGH
        elif msg == "4": # Right - B
            shoulder1.set_pwm(0, 0, 385)
        else:
            shoulder1.set_pwm(0, 0, 392)
          #  shoulder2.set_pwm(1, 0, 390)
          #  shoulder2.set_pwm(1, 0, 240)
        print(shoulder2_alt)
        await self.send(msg)

    async def send(self, msg):
        logger.debug('sending new message')
        for ws in self._active_connections:
            asyncio.ensure_future(ws.send(msg))

server = CLserver(port)


asyncio.get_event_loop().run_until_complete(server.start_server())

asyncio.get_event_loop().run_forever()
