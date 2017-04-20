The server works by opening a socket and port on its hardware to receive incoming network connections.
The code was written using Python 3.5 and incorporated Xbox controller code from a prior
KSURCT member, Aaron Schif.

Author: Dan Wagner, lead programmer 2016-2018  
Contact: danwagner@ksu.edu

# Libraries
* asyncio, Python's asynchronous I/O library for running servers/clients
* websockets, the core network utilities for this server implementation
* pickle, a means of encoding a robot status object into bytes for sending over a websocket
* RPi.GPIO, the GPIO libraries for the Raspberry Pi Model 3
* thread, Python's multithreading libraries for running processes in the background
* subprocess, library for executing code outside of the original file, typically shell scripts in Linux
* time, Python's library for timing on our network reconnection function
* os, an Operating System library for quitting out of the entire program (program + thread) safely
* logging, a Python reporting mechanism for debugging

# Code Methodology

## Initialization
The code then initializes a delay timer and dummy variable (both used in the reconnect function)
and sets up a file to suppress the output from the network connection subprocess.
#### Servos
The servos was connected to an I2C board with I2C address 0x40.  This was confirmed through
i2c-detect on the Pi.  The code initializes each servo required for the 2017 Mercury robot and sets
the PWM frequency to 60 Hz.
* Depending upon your design considerations, you may need a different number of servos
* Make sure to check specifications for the correct operating frequency

#### Motors
The motors was connected to an I2C board with I2C address 0x41.  This was confirmed through
i2c-detect on the Pi. The code sets the PWM frequency to 1600 Hz, which was from the datasheet.

#### Constants
Constant values were used for each pin on the Pi that was wired for the servos and motors.  This
was because of good programming practice: any change to the variable required only that constant
to be changed rather than each instance throughout the code.

Our design with the camera and body allowed us to have two presets for vision that gave us better
views of the course.  Initially, we wanted the robot to start in a preset that allowed us to see well,
hence the PWM initialization for the shoulder, elbow, wrist, and fingers.

#### GPIO
Next, the GPIO pins on the Pi were set up to be outputs for the motors in order to implement the
forward and reverse operations.  Be sure to check the mode (GPIO.BCM or GPIO.BOARD).  We
used GPIO.BCM so we could go off of the numbering on the pinout diagram.  Warnings were
disabled due to annoyances during compilation.

## TextColors Class
The TextColors class was defined for formatting output messages.  This was exclusively used in the
network connection test function that will be described later.

## CLserver class
The CLserver class was the heart of the server software.  It was in charge of opening connections,
taking messages from the client, and making changes to the component settings.  The class has
a couple of members:
* active_connections, a list of websocket clients that were currently connected to it
* port, the port number of the server

#### start_server(self)
On startup, the server waits to serve any incoming connections on the given port, and sets the TCP
timeout to 1 second.  This timeout was unnecessary and did not seem to affect the code in any way.
When a connection was made to the server, `handle_new_connection(self, ws, path)` was run.  

#### handle_new_connection(self, ws, path)
This function registers the client with the server and starts the network connection thread.  
The global value p was used to tell Python that it refers to the same value from
**Initialization**. The server then loops forever and compares the return value of `test_connection(self)`.
If the connection was lost, then the motors was stopped to prevent damage to the robot and/or course.
Otherwise, the server retrieves the message sent from the client and handles it.

#### send(self, msg)
This function attempts to send the message it received back to the client.  If it fails in any way, the
robot was stopped, the connection was removed from the list of active connections, and the event queue
was closed to prevent execution of future events and exceptions.

#### test_connection(self)
This function periodically checks the Internet connection on the Pi.  The global values p and delay
were used to tell Python that they refer to the same values from **Initialization**.  The code loops
forever in the thread.  For every second that passes from our current time (given by delay), the shell
script `ip_ping.sh` was run.  This script pings Google's main DNS server.  If the subprocess call returns
a value of 2, that signifies that the network connection has been lost and the robot was stopped.  Then,
the program exits cleanly through the OS library.  Otherwise, the server resumes and resets the delay.

#### handle_msg(self, msg)
This function was the core of the server.  The global variables shoulder2_alt and shoulder1_alt were
used to tell Python that they refer to the same values from **Initialization**.  The message received
from `handle_new_connection(self, ws, path)` is decoded using the pickle library.  The message is
a string array of values with indexes for each status:

Index  | Status
------- | ---------
x  | X pressed
y  | Y pressed
a  | A pressed
b  | B pressed
lstick | left stick position
rstick | right stick position
lbx | left bumper & x pressed
lby | left bumper & y pressed
lba | left bumper & a pressed
lbb | left bumper & b pressed
rba | right bumper & a pressed
rby | right bumper & y pressed
fwd | right trigger position
rev | left trigger position
vision | vision preset enabled
peek | peek preset enabled

The robot's status changed based upon the values of the message at each index.  The status was
changed by modulating the PWM signal to each component.  The code should be intuitive and
straightforward in its operation.
