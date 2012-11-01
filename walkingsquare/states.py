from Robot.Interface.Sensors import imu
from Robot.Interface import robotbody
from Robot.Actions import motion, walk

import time

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
        
class LiftRightArm:
        
    def __init__ (self):
        self.time=0.02
        
    def entry (self):
        print("Heil!")
        robotbody.set_right_arm_position(0,0,0)
    
    def update (self):
        print (robotbody.get_right_arm_position())
        if robotbody.get_right_arm_position()[0]<=1.5707964 and robotbody.get_right_arm_position()[0]>=1.570796:
            return "done"
        
    def exit (self):
        print ("done")
        
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


class Exit:
    def __init__(self):
        pass
    def entry(self):
        motion.stop_walk()
    def update(self):
        pass
    def exit(self):
        pass