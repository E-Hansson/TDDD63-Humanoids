from Robot.Interface.Sensors import imu
from Robot.Interface import robotbody
from Robot.Actions import motion, walk
from helpfunctions import *
from math import pi

import time


"""        General motion states        """

class StandStill:
    """The robot stands still and wait"""

    def __init__(self):
        self.time = 1 # 15 for webots
    def entry(self):
        print("Entry still")
        motion.stand_still()
        self.start_time = time.time()
    def update(self):
        if time.time() > self.start_time + self.time:
            return "timeout"
    def exit(self):
        print("Exit still")
        motion.start_walk()
        

"""        Walking states        """

class WalkStraight:
    """The robot walks forward some time"""

    def __init__(self, time):
        self.time = time
    def entry(self):
        print("Entry walk")
        self.start_time = time.time()

        walk.walk_forward(0.02)

    def update(self):
        if time.time() > self.start_time + self.time:
            return "timeout"
    def exit(self):
        print("Exit walk")
        

class WalkSpeed:
    """The robot walks forward some time"""

    def __init__(self, time, speed = 0.02):
        self.time = time
        self.speed = speed
    def entry(self):
        print("See the robot walk")
        self.start_time = time.time()

        walk.walk_forward(self.speed)

    def update(self):
        if time.time() > self.start_time + self.time:
            return "timeout"
    def exit(self):
        print("Exit walk")


"""        Direction states        """

class Turn:
    """The robot turns some time"""
    
    def __init__(self,time):
        self.time = time
        self.number_of_turns = 0
    def entry(self):
        print("Entry turn")
        self.start_time = time.time()
        self.number_of_turns += 1
        walk.turn_left(0.4)
    def update(self):
        if self.number_of_turns == 4:
            return "complete"
        if time.time() > self.start_time + self.time:
            return "done"
        
    def exit(self):
        print("Exit turn")


class TurnGyro:
    """The robot turn a certain angle"""

    def __init__(self,angle):
        self.angle = angle
        self.number_of_turns = 0
    def entry(self):
        print("Entry gyro turn")
        self.start_angle = imu.get_angle()[2]
        self.number_of_turns += 1
        walk.turn_left(0.4)
    def update(self):
        if self.number_of_turns == 4:
            return "complete"
        if imu.get_angle()[2] > self.start_angle + self.angle:
            return "done"
    def exit(self):
        print("Exit gyro turn")


"""        Arm states        """

class MoveArm:
    """ a state to make the robot lift the right arm """
    
    def __init__ (self,arm,angle=(0,0,0),relation="body"):
        self.relation=relation
        self.angle=angle
        self.arm="right"
        
    def entry (self):
        print("raising "+self.arm+" arm")
        if self.arm=="right":
            set_right_arm_position(self.angle[0],self.angle[1],self.angle[2],self.relation)
        
        elif self.arm=="left":
            set_left_arm_position(self.angle[0],self.angle[1],self.angle[3],self.relation)
    
    def update (self):
        if self.arm=="right" and like(get_right_arm_position(self.relation)[0],0):
            return "raised"
        
        elif self.arm=="left" and like(get_left_arm_position(self.relation)[0],0):
            return "raised"
        
    def exit (self):
        print ("done")
        

"""        Eye states        """

class SetEyeColor:
    """ Sets the Eye color of the robot"""
    
    def __init__(self,red,green,blue):
        self.color=(red,green,blue)
        
    def entry(self):
        robotbody.set_eyes_led(self.color[0],self.color[1],self.color[2])

    def update(self):
        print("changing")
        
    def exit(self):
        print("terminating")
        
        
"""        System states        """

class Exit:
    def __init__(self):
        pass
    def entry(self):
        motion.stop_walk()
    def update(self):
        pass
    def exit(self):
        pass