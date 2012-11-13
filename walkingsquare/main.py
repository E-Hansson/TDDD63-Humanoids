from state_machine import Program
from Robot.Interface import robotbody
from Robot.Interface.Sensors import vision
from Robot.Actions import motion
import time
#import urllib2

# Instantiate the program class
_program = Program()
# Starts the Finite State Machine
_program.entry()
motion.entry()

#  Loop every 5ms
_tDelay = 0.005

# Update function, should be called on regular basis
def update():
    _program.update()
    motion.update()
    robotbody.update()
    vision.update()
    #opener = urllib2.build_opener()
    #opener.addheaders = [('User-agent', 'Bawlinator')]
    #infile = opener.open(_program.robocom)
    #page = infile.read()
    #print(page)


vision.entry()
# Main loop
while not robotbody.is_middle_button_pressed():
    update()
    time.sleep(_tDelay)
    vision.update()
    
vision.exit()