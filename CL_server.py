import asyncio
import websockets

from logging import Logger
from contextlib import suppress

import Adafruit_PCA9685 # servo libraries from Adafruit

port = 8055
logger = Logger(__name__)

# Initialize the servo with default I2C address (0x40)
servo = Adafruit_PCA9685.PCA9685()
servo.set_pwm_freq(60)

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
        msg = msg.split() # This DOES add latency to the messages (having to parse all 4 buttons rather than a single); change this to bitmasking a number for speed.
        if msg[0] == "True": # If the X button is held down, turn the servo.
            servo.set_pwm(0, 0, 650) # Configuration high for Hirec HS-605MG servo.  CHANGE THIS TO SERVO YOU ARE USING.
        elif msg[0] == "False": # If the X button is released, restore the servo.
            servo.set_pwm(0, 0, 170) # Configuration low for Hirec HS-605MG servo.  CHANGE THIS TO SERVO YOU ARE USING.  
        await self.send(msg[0])

    async def send(self, msg):
        logger.debug('sending new message')
        for ws in self._active_connections:
            asyncio.ensure_future(ws.send(msg))

server = CLserver(port)


asyncio.get_event_loop().run_until_complete(server.start_server())

asyncio.get_event_loop().run_forever()
