import sys
import easygui
import serial
import time
import collections

from datetime import datetime
from pynput.keyboard import Key, KeyCode, Listener

class MyException(Exception): pass

KeyboardControl = True # set to "False" if the Arduino is not connected to the Raspberry Pi via USB 
        
### predefined motor speeds
slow = 500
medium = 500
fast = 500
speed = medium #start-up speed:medium, Ctrl key changes the speed

arrowkey_mode = False #Alt key toggles this variable to select between X-Y (start-up) and Rotate-Tilt control
recording_mode = False #Tab key toggles between the photo mode (start-up) and the video mode
recording = False #variable to set during recording

### serial communication with Arduino
if KeyboardControl == True:
    ser = serial.Serial('/dev/ttyACM0',57600) # type "ls /dev/tty*" to the terminal to check the serial port 

def init():
    pass

def destroy():
    pass

class StepMoto:
    def __init__(self, code):
        self.code = code
        self.speed = "300"
        self.status = "stop"

    def forward(self):
        if self.status == "forward":
            return
        self.speed = "500"
        data = self.speed + self.code + ","
        ser.write(data.encode())
        self.status = "forward"

    def backward(self):
        if self.status == "backword":
            return
        self.speed = "400"
        data = "-" + self.speed + self.code + ","
        ser.write(data.encode())
        self.status = "backword"
    
    def stop(self):
        if self.status == "stop":
            return
        ser.write(b"0O,") ## send to Arduino "0O," to stop the motors
        self.status = "stop"

    def setSpeed(self, speed):
        self.speed = speed

    def __str__(self):
         return "Moto: " + self.code + "'s status is " + self.status + " and speed is " + self.speed

class ArdunioBoard:
    def __init__(self):
        self._motos = {
            'X': StepMoto("X")
                }

    def getMoto(self, name):
        return self._motos[name]

actions = {
        'x': StepMoto.forward,
        'y': StepMoto.backward
        }

actions = collections.defaultdict(lambda: lambda obj: None , actions)
ardunio = ArdunioBoard()
moto = ardunio.getMoto('X')

def on_press(key):
    print(key)
    try:
        if key == Key.esc:
            print('esc press')
            return False

        actions[key.char](moto)

        print(moto)
    except AttributeError:
        print("Exception")

def on_release(key):
    print(key)
    try:
        stop_list =['x','y']
        print(key.char)
        if key.char in stop_list:
            moto.stop()
    except AttributeError:
        print("Exception")

if __name__ == '__main__':
    init()
    with Listener(
        on_press = on_press,
        on_release = on_release) as listener:
        try:
            listener.join()
        except MyException as e:
            print('{0} was pressed'.format(e.args[0]))
            destroy()
