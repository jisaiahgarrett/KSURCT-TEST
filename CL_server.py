import asyncio
import websockets
import pickle
import RPi.GPIO as GPIO
import sys
import socket

# Web connectivity imports
import subprocess
import time
import os

from urllib.request import urlopen
from logging import Logger
from contextlib import suppress

import Adafruit_PCA9685  # servo libraries from Adafruit

port = 8055
logger = Logger(__name__)

delay = time.time()

# Suppress output from subprocess
DEVNULL = open(os.devnull, 'w')

# Initialize the servos with default I2C address (0x40)
shoulder1 = Adafruit_PCA9685.PCA9685(0x40)
shoulder1.set_pwm_freq(60)				# !! Sets the PWM FOR ALL CHANNELS on 0x40 !!
shoulder1_alt = 300
shoulder2 = Adafruit_PCA9685.PCA9685(0x40)
shoulder2_alt = 492					#Preset for the shoulder at t0
wrist = Adafruit_PCA9685.PCA9685(0x40)
fingers = Adafruit_PCA9685.PCA9685(0x40)
elbow = Adafruit_PCA9685.PCA9685(0x40)

# Initialize the Drive Motors with I2C address (0x41)
leftMotor = Adafruit_PCA9685.PCA9685(0x41)
leftMotor.set_pwm_freq(1600)				# !!  Sets the PWM FOR ALL channels on 0x41 !!
rightMotor = Adafruit_PCA9685.PCA9685(0x41)

# Servo channel information
SHOULDER1_CHA = 0
SHOULDER2_CHA = 1
EYES_CHA = 2
WRIST_CHA = 3
FINGERS_CHA = 4
ELBOW_CHA = 5
LEFTM_CHA = 14
RIGHTM_CHA = 15

#Initialize servos to the Vision preset
shoulder2.set_pwm(SHOULDER2_CHA, 0, 480)
elbow.set_pwm(ELBOW_CHA, 0, 300)
wrist.set_pwm(WRIST_CHA, 0, 400)
fingers.set_pwm(FINGERS_CHA, 0, 200)

# Set up the GPIO pin for toggling reverse/forward motors.
GPIO.setmode(GPIO.BCM)
GPIO_FWD_PIN = 18
GPIO_REV_PIN = 17
GPIO.setwarnings(False)
GPIO.setup(GPIO_FWD_PIN, GPIO.OUT)
GPIO.setup(GPIO_REV_PIN, GPIO.OUT)

# The following is a set of definitions for terminal text color
class textColors:
	WARN = '\033[93m'	# Color used for warnings!
	CONF = '\033[94m'	# Color used for confirmations
	PRINT = '\033[92m'	# Color used to distinguish the standard output of p
	BOLD = '\033[1m'	# Bold text to amplify textclass textColors
	
class CLserver(object):
    def __init__(self, port):
        self._active_connections = set()
        self.port = port
        self.counter = 0
        self.online = True

    async def start_server(self):
        logger.info('server starting up')
        self.server = await websockets.serve(self.handle_new_connection, '0.0.0.0', self.port, timeout=1)

    async def handle_new_connection(self, ws, path):
        global p
        logger.debug('new connection to server')
        self._active_connections.add(ws)
        while True:
            await self.test_connection(ws)
        self._active_connections.remove(ws)

    async def send(self, msg):  
        logger.debug('sending new message')
        try:
            for ws in self._active_connections:
                asyncio.ensure_future(ws.send(msg))
        except:
            shoulder2.set_all_pwm(0, 0)
            self._active_connections = set()
            asyncio.get_event_loop().close()
            sys.exit(0)
           
    async def test_connection(self, ws):
        global p
        global delay
        if (1): #(time.time() - delay) >= 0):
            p = subprocess.call(['./ip_ping.sh'], shell=True, stdout=DEVNULL, stderr=DEVNULL) 
            if p == 2:
                print(textColors.WARN + "!!! IP unconfirmed !!!")	
                delay = time.time()
                leftMotor.set_all_pwm(0,0)
                rightMotor.set_all_pwm(0,0)
            else:
                #print(textColors.CONF + " IP Confirmed ")
                delay = time.time()
                result = await ws.recv()
                self.handle_msg(result)
            		
    def handle_msg(self, msg):
        try:
            logger.debug('new message handled')
            global shoulder2_alt
            global shoulder1_alt
            msg = pickle.loads(msg)
            if msg['valid']:
                if msg['lbx']:
                    print("lbump + x")
                elif msg['x']:  # Left - X
                   # print(shoulder1_alt)
                    shoulder1.set_pwm(SHOULDER1_CHA, 0, 400)
                    shoulder1_alt += 5
                if msg['lbb']:
                    print("lbump + b")
                elif msg['b']:
                    shoulder1.set_pwm(SHOULDER1_CHA, 0, 380)
                    shoulder1_alt -= 5
                else:
                    shoulder1.set_pwm(SHOULDER1_CHA, 0, 0)
                    shoulder1_alt = 300
                if msg['lby']:
                    print("lbump + y")
                elif msg['rby']:
                    print("rbump + y")
                elif msg['y']:  # Up - Y
                   # print("Servo up")
                    if shoulder2_alt >= 600: # servo maximum, make sure we do not go over this value
                        shoulder2_alt = 599
                    shoulder2.set_pwm(SHOULDER2_CHA, 0, shoulder2_alt)
                    shoulder2_alt += 5 # CHANGE THIS INCREMENT IF NOT FAST/SLOW ENOUGH
                else:
                    shoulder2.set_pwm(SHOULDER2_CHA, 0, shoulder2_alt)
                if msg['lba']:
                    print("lbump + a")
                elif msg['rba']:
                    print("rbump + a")
                elif msg['a']:  # Down - A
                   # print("Servo down")
                    if shoulder2_alt <= 299:  # servo minimum, make sure we do not go under this value
                        shoulder2_alt = 300
                    shoulder2.set_pwm(SHOULDER2_CHA, 0, shoulder2_alt)
                    shoulder2_alt -= 5  # CHANGE THIS DECREMENT IF NOT FAST/SLOW ENOUGH
                else:
                    shoulder2.set_pwm(SHOULDER2_CHA, 0, shoulder2_alt)
    #             if msg['vision'] == 1:
    #                shoulder2.set_pwm(SHOULDER2_CHA, 0, 480)
    #                wrist.set_pwm(WRIST_CHA, 0, 400)
    #                elbow.set_pwm(ELBOW_CHA, 0, 300)
    #                fingers.set_pwm(FINGERS_CHA, 0, 200)
    #             elif msg['peek'] == 1:
    #                shoulder2.set_pwm(SHOULDER2_CHA, 0, 450)
    #                elbow.set_pwm(ELBOW_CHA, 0, 400)
    #                wrist.set_pwm(WRIST_CHA, 0, 500)
                if msg['rstick'] > 0:  # Open the fingers
                    fingers.set_pwm(FINGERS_CHA, 0, 530) #msg['rstick'] << 6)
                else:
                    fingers.set_pwm(FINGERS_CHA, 0, 300) #200)
                if msg['rev'] >= 0:
                    # print("Reverse")
                    GPIO.output(GPIO_REV_PIN, GPIO.HIGH)
                    GPIO.output(GPIO_FWD_PIN, GPIO.HIGH)
                    if msg['lstick'] > 0:
                        leftMotor.set_pwm(LEFTM_CHA, 0, msg['rev'])
                        rightMotor.set_pwm(RIGHTM_CHA, 0,  msg['rev'] - (msg['rev']*msg['lstick'] >> 4))
                    elif msg['lstick'] < 0:
                        leftMotor.set_pwm(LEFTM_CHA, 0, msg['rev'] + (msg['rev']*msg['lstick'] >> 4))
                        rightMotor.set_pwm(RIGHTM_CHA, 0, msg['rev'])
                    else:
                        leftMotor.set_pwm(LEFTM_CHA, 0, msg['rev'])
                        rightMotor.set_pwm(RIGHTM_CHA, 0, msg['rev'])
                elif msg['fwd'] >= 0:
                   # print("Forward")
                    GPIO.output(GPIO_FWD_PIN, GPIO.LOW)
                    GPIO.output(GPIO_REV_PIN, GPIO.LOW)
                    if msg['lstick'] < 0:
                        leftMotor.set_pwm(LEFTM_CHA, 0, msg['fwd'] + (msg['fwd']*msg['lstick'] >> 4))
                        rightMotor.set_pwm(RIGHTM_CHA, 0,  msg['fwd'])
                    elif msg['lstick'] > 0:
                       leftMotor.set_pwm(LEFTM_CHA, 0, msg['fwd'])
                       rightMotor.set_pwm(RIGHTM_CHA, 0, msg['fwd'] - (msg['fwd']*msg['lstick'] >> 4))
                    else:
                       leftMotor.set_pwm(LEFTM_CHA, 0, msg['fwd'])
                       rightMotor.set_pwm(RIGHTM_CHA, 0, msg['fwd'])
                else:
                 #   print("Default")
                    GPIO.output(GPIO_FWD_PIN, GPIO.HIGH) # right
                    GPIO.output(GPIO_REV_PIN, GPIO.HIGH) # left
                    if msg['lstick'] < 0:
                        GPIO.output(GPIO_FWD_PIN, GPIO.LOW)
                        leftMotor.set_pwm(LEFTM_CHA, 0, -(4096*msg['lstick']) >> 4)
                        rightMotor.set_pwm(RIGHTM_CHA, 0, -(4096*msg['lstick']) >> 4)
                    elif msg['lstick'] > 0:
                       GPIO.output(GPIO_REV_PIN, GPIO.LOW)
                       leftMotor.set_pwm(LEFTM_CHA, 0, (4096*msg['lstick']) >> 4)
                       rightMotor.set_pwm(RIGHTM_CHA, 0, (4096*msg['lstick']) >> 4)
                    else:
                       # print('default state')
                       leftMotor.set_pwm(LEFTM_CHA, 0, 0)
                       rightMotor.set_pwm(RIGHTM_CHA, 0, 0)
                       GPIO.output(GPIO_FWD_PIN, GPIO.LOW)
                       GPIO.output(GPIO_REV_PIN, GPIO.LOW)
                self.send(pickle.dumps(msg))
        except Exception as e:
            print(e)
            shoulder2.set_all_pwm(0, 0)
            leftMotor.set_all_pwm(0, 0)
            sys.exit(0)
            asyncio.get_event_loop().close()

try:
    server = CLserver(port)
    asyncio.get_event_loop().run_until_complete(server.start_server())
    asyncio.get_event_loop().run_forever()
except:
    shoulder2.set_all_pwm(0, 0)
    leftMotor.set_all_pwm(0, 0)
    sys.exit(0)
    asyncio.get_event_loop().close()
