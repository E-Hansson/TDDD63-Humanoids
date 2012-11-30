from Robot.Interface import robotbody
from Robot.Interface.Sensors import vision
from Robot.Actions import motion
from Robot.Util import robotid
import time
#import urllib2

#Imports the right statemachine depending on the number

if robotid.get_player_number() in (1,2,3):
    from state_machine_for_darwin import Program

else:
    from goal_keeper import Program

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
    #robotbody.update()
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