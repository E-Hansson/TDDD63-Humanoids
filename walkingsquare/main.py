from Robot.Interface import robotbody
from Robot.Interface.Sensors import vision
from Robot.Actions import motion
from Robot.Util import robotid
import time

#Imports the right state machine for the robots position depending on the number

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
    vision.update()



vision.entry()
# Main loop
while not robotbody.is_middle_button_pressed():
    update()
    time.sleep(_tDelay)
    vision.update()
    
vision.exit()
"""
from help_functions import ball_angle, set_head_position
from math import pi

robotbody.set_head_hardness(0.95)
set_head_position([0,pi/8])
motion.stand_still()
vision.entry()
#0.47 left foot
#-0.47 right foot
while not robotbody.is_middle_button_pressed():
    motion.update()
    vision.update()
    print (ball_angle())
    
vision.exit()
"""