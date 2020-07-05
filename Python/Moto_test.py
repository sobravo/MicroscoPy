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
        self.status = "stop"

    def setSpeed(self, speed):
        self.speed = speed

    def __str__(self):
         return "Moto: " + self.code + "'s status is " + self.status + " and speed is " + self.speed

class ArdunioBoard:
    def __init__(self):
        self._motos = {}
        self._moto_id = ['X', 'Y', 'Z', 'C', 'R', 'T']
        for moto_id in self._moto_id:
            self._motos[moto_id] = StepMoto(str(moto_id))

    def getMoto(self, name):
        return self._motos[name]

    def stopMoto(self):
        print("stop Moto")
        for moto_id in self._moto_id:
            self._motos[moto_id].stop()
        ser.write(b"0O,") ## send to Arduino "0O," to stop the motors


ardunio = ArdunioBoard()

actions = {
        'a': (StepMoto.forward, ardunio.getMoto('X')),
        'b': (StepMoto.backward, ardunio.getMoto('X')),
        'c': (StepMoto.forward, ardunio.getMoto('Y')),
        'd': (StepMoto.backward, ardunio.getMoto('Y')),
        'e': (StepMoto.forward, ardunio.getMoto('Z')),
        'f': (StepMoto.backward, ardunio.getMoto('Z')),
        'g': (StepMoto.forward, ardunio.getMoto('C')),
        'h': (StepMoto.backward, ardunio.getMoto('C')),
        'i': (StepMoto.forward, ardunio.getMoto('R')),
        'j': (StepMoto.backward, ardunio.getMoto('R')),
        'k': (StepMoto.forward, ardunio.getMoto('T')),
        'l': (StepMoto.backward, ardunio.getMoto('T'))
        }

actions = collections.defaultdict(lambda: (lambda obj: None, None) , actions)

def on_press(key):
    try:
        if key == Key.esc:
            print('esc press')
            return False

        act = actions[key.char]
        act[0](act[1])
        print(act[1])

    except AttributeError as e:
        print('{0} was pressed'.format(e.args[0]))

def on_release(key):
    try:
        stop_list =['a','b','c','d', 'e', 'f', 'j', 'h', 'i', 'j', 'k', 'l']
        if key.char in stop_list:
            ardunio.stopMoto()
    except AttributeError:
        print("Exception")

if __name__ == '__main__':
    init()
    with Listener(
        on_press = on_press,
        on_release = on_release) as listener:
        try:
            listener.join()
        except Exception as e:
            print('{0} was pressed'.format(e.args[0]))
            destroy()

        print("Finish normally")
