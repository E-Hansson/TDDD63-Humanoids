from Robot.Interface.Sensors import imu, vision
from Robot.Interface import robotbody
from Robot.Actions import motion, walk
from helpfunctions import *
from math import pi

import time

"""        General motion states        """

class CircleBall:
    
    def entry(self):
        print("Circle this motherfucker!")
        robotbody.set_head_hardness(0.9)
        
        last_ball = vision.get_ball()
        ball = vision.Ball(last_ball.x,last_ball.y,last_ball.t)
        angles=ball.get_angle()
        robotbody.set_head_position(angles[0],angles[1])
        self.wanted_rotation = pi/2
        self.rotation_progress = 0
        
    def update(self):
        last_ball = vision.get_ball()
        ball = vision.Ball(last_ball.x,last_ball.y,last_ball.t)
        angles=ball.get_angle()
        robotbody.set_head_position(angles[0],angles[1])
        head_position = robotbody.get_head_position()
        
        walk.set_velocity(0, 0.4, head_position[0])
        self.rotation_progress -= head_position[0]/7.7
        
        print(self.rotation_progress)
        if like(self.rotation_progress,self.wanted_rotation):
            print("Rotation done")
            return "done"
        
    def exit(self):
        pass

class TrackBall:
    
    def entry(self):
        robotbody.set_head_hardness(0.9)
        
        last_ball = vision.get_ball()
        ball = vision.Ball(last_ball.x,last_ball.y,last_ball.t)
        angles=ball.get_angle()
        robotbody.set_head_position(angles[0],angles[1])
    
    def update(self):
        if has_fallen():
            return "fallen"
        
        last_ball = vision.get_ball()
        ball = vision.Ball(last_ball.x,last_ball.y,last_ball.t)
        angles=ball.get_angle()
        robotbody.set_head_position(angles[0],angles[1])
        
        head_position = robotbody.get_head_position()
        
        if like(head_position[1],pi/3.5):
            return "done"
        
        elif not like(head_position[0],0,pi/18):
            walk.set_velocity(0.05, 0.4, head_position[0])
            
        else:
            walk.set_velocity(0.05, 0, 0)
        
            
    def exit(self):
        print ("standing in front of ball")


class StandStill:
    """The robot stands still and wait"""

    def __init__(self,timer=1):
        self.time = timer # 15 for webots
    def entry(self):
        print("Entry still")
        motion.stand_still()
        self.start_time = time.time()
    def update(self):
        if has_fallen():
            return "fallen"
        elif time.time() > self.start_time + self.time:
            return "timeout"
    def exit(self):
        print("Exit still")
        motion.start_walk()
        

class GetUp:
    
    def __init__(self,previous_state="initiat_walking"):
        self.previous_state=previous_state
        
    def entry (self):
        motion.get_up()
    
    def update (self):
        if like(imu.get_angle()[1],0.001):
            return ("done")
    
    def exit (self):
        print("sitting")
        

"""        Walking states        """


class StartWalk:
    
    def __init__(self,speed):
        self.speed=speed
        
    def entry(self):
        print("start walking")
        walk.walk_forward(self.speed)
        
    def update(self):
        if has_fallen():
            return "fallen"
        else:
            return "done"
    
    def exit(self):
        print ("walking at speed "+str(self.speed))
        
class WalkStraight:
    """The robot walks forward some time"""

    def __init__(self, time):
        self.time = time
    def entry(self):
        print("Entry walk")
        self.start_time = time.time()

        walk.walk_forward(0.02)

    def update(self):
        if has_fallen():
            return "fallen"
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
        if has_fallen():
            return "fallen"
        if time.time() > self.start_time + self.time:
            return "timeout"
    def exit(self):
        print("Exit walk")


"""        Direction states        """

class Turn:
    """The robot turns for some time"""
    
    def __init__(self,time):
        self.time = time
        self.number_of_turns = 0
    def entry(self):
        print("Entry turn")
        self.start_time = time.time()
        self.number_of_turns += 1
        walk.turn_left(0.4)
    def update(self):
        if has_fallen():
            return "fallen"
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
        if has_fallen():
            return "fallen"
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
        self.arm=arm
        self.init_angle=angle
        
    def entry (self):
        print("moving "+self.arm+" arm")
        if self.arm=="right":
            self.angle=set_right_arm_position(self.init_angle[0],self.init_angle[1],self.init_angle[2],self.relation)
        
        elif self.arm=="left":
            self.angle=set_left_arm_position(self.init_angle[0],self.init_angle[1],self.init_angle[2],self.relation)
    
    def update (self):
        if has_fallen():
            return "fallen"
        if self.arm=="right" and like(get_right_arm_position()[0],self.angle[0]):
            return "done"
        
        elif self.arm=="left" and like(get_left_arm_position()[0],self.angle[0]):
            return "done"
        
    def exit (self):
        print ("done")
        

"""        Eye states        """

class SetEyeColor:
    """ Sets the Eye color of the robot"""
    
    def __init__(self,red,green,blue):
        self.color=(red,green,blue)
        print ("Changing eye color")
        
    def entry(self):
        robotbody.set_eyes_led(self.color[0],self.color[1],self.color[2])

    def update(self):
        if has_fallen():
            return "fallen"
        else:
            return "done"
        
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