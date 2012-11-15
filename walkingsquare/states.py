from Robot.Interface.Sensors import imu, vision
from Robot.Interface import robotbody
from Robot.Actions import motion, walk, kick
from help_functions import *
from math import pi, fabs

import time

"""        General motion states        """

class CircleBall:
    
    def __init__(self,intervall):
        self.rotation_intervall = intervall
    
    def entry(self):
        print("Circle this motherfucker!")
        robotbody.set_head_hardness(0.9)
        
        angles=ball_angle()
        walk.set_velocity(0, 0, 0)
        #robotbody.set_head_position(angles[0],angles[1])
        self.wanted_rotation = pi/2
        self.rotation_progress = 0
          
        self.head_position = robotbody.get_head_position()
        self.head_start = [pi/2,-pi/8]
        self.head_end = [-pi/2, -pi/8]
        self.head_ball = [0, pi/3]
        self.wanted_head_position = [self.head_start[0],self.head_start[1]]
        self.looking_for_goal = True
        robotbody.set_head_position(self.head_start[0], self.head_start[1])
        
    def set_wanted_rotation(self, rotation_intervall):
        self.rotation_intervall = rotation_intervall
        
    def init_goal_check(self):
            self.looking_for_goal = True
            self.rotation_progress = 0
            walk.set_velocity(0, 0, 0)
            robotbody.set_head_position(self.head_start[0], self.head_start[1])
            self.wanted_head_position = [self.head_start[0],self.head_start[1]]
                    
    def check_for_goal(self):
        if(self.wanted_head_position[0] > -pi/2):
            self.wanted_head_position[0] -= pi/16
        if(like(self.head_position[0],self.head_end[0])):
            self.looking_for_goal = False
            self.wanted_head_position = self.head_ball
        robotbody.set_head_position(self.wanted_head_position[0], self.wanted_head_position[1])
        
    def update(self):
        self.head_position = robotbody.get_head_position()
        
        if has_fallen():
            return "fallen"
        
        if(self.looking_for_goal):
            self.check_for_goal()
            if vision.has_new_goal_observation():
                print(goal_angle())
        else:
            angles=ball_angle()
            robotbody.set_head_position(angles[0],angles[1])
            head_position = robotbody.get_head_position()
        
            walk.set_velocity(0, 0.4, head_position[0]*1.2)
            self.rotation_progress -= head_position[0]/7.3
        
            if like(self.rotation_progress,self.rotation_intervall):
                self.init_goal_check()
        
    def exit(self):
        print("Rotation done")

class KickBall:
    
    def entry(self):
        print ("kicking the ball")
        self.time=3
        kick.forward_right()
        robotbody.set_head_position(robotbody.get_head_position()[0], 0)
        self.start_time = time.time()
        
    def update(self):
        if has_fallen():
            return "fallen"
        
        if time.time()>self.time+self.start_time:
            return "done"
        
    
    def exit(self):
        print ("kicked the ball")
    
class FollowBall:
    
    def __init__(self,distance=pi/3.8):
        self.distance=distance        
        #self.speed_change_distance=5
        #self.fast=0.1
        #self.slow=0.05
        
        self.speed=0.05
        
    def entry(self):
        print("following the ball")
        robotbody.set_head_hardness(0.95)
    
    def update(self):
        if has_fallen():
            return "fallen"
        
        if not vision.has_new_ball_observation():
            walk.set_velocity(self.speed, 0, 0)
            return "no ball"
            
        angles=ball_angle()
        robotbody.set_head_position(angles[0],angles[1])
        
        head_position = robotbody.get_head_position()
        
        if like(head_position[1],self.distance):
            return "done"
        
        #if head_position[1]>self.speed_change_distance:
          #  self.speed=self.slow
            
        #elif head_position[1]<self.speed_change_distance:
         #   self.speed=self.fast
            
        if not like(head_position[0],0,pi/18):
            walk.set_velocity(self.speed, 0.4, head_position[0])
            
        else:
            walk.set_velocity(self.speed, 0, 0)
        
            
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

class TrackGoal:
    
    def __init__(self, circle_ball):
        self.circle_ball = circle_ball
    
    def entry(self):
        print ("Tracking goal")
        robotbody.set_head_hardness(1.95)
        robotbody.set_head_position(pi/2,-pi/8)
        self.wanted_head_position = [pi/2,-pi/8]
        self.start_angle = imu.get_angle()[2]
        self.angle=2*pi
        self.rotated=0 
    
    def update(self):
        head_position=robotbody.get_head_position()
        
        self.wanted_head_position[0] -= pi/16
        robotbody.set_head_position(self.wanted_head_position[0],self.wanted_head_position[1])
        
        if head_position[0] <= pi/2:
            self.wanted_head_position = [0,pi/3]
            robotbody.set_head_position(self.wanted_head_position[0],self.wanted_head_position[1])  
        
            
        if has_fallen():
            return "fallen"
        
        if vision.has_new_goal_observation():
            angles=goal_angle()
            robotbody.set_head_position(angles[0],angles[1])     
            head_position = robotbody.get_head_position()
            
            walk.turn_left(0)
            print(head_position[0])
            self.circle_ball.set_wanted_rotation(self.rotated+head_position[0])
            return "done"
        
        if imu.get_angle()[2] > self.start_angle + self.angle:
            return "no goal found"
    
    def exit(self):
        robotbody.set_head_position(0, 0)
        print ("exit goal tracking")

class TrackBall:
    
        
    def entry(self):
        print ("Tracking ball")
        robotbody.set_head_hardness(1.95)
        current_head_position=robotbody.get_head_position()
        self.wanted_head_position=[current_head_position[0],current_head_position[1]]
        self.start_angle = imu.get_angle()[2]
        self.angle=2*pi
        
        walk.turn_left(0.4)
        robotbody.set_head_position(self.wanted_head_position[0],self.wanted_head_position[1])
        
    def update(self):
        head_position=robotbody.get_head_position()
        if like(head_position,self.wanted_head_position):
            if like(head_position[0],pi/2) and like(head_position[1],0):
                self.wanted_head_position=[-pi/2,pi/3.5]
        
            elif like(head_position[0],pi/2):
                self.wanted_head_position=[-pi/2,0]
        
            else:
                self.wanted_head_position[0]=head_position[0]+pi/15
            
            robotbody.set_head_position(self.wanted_head_position[0],self.wanted_head_position[1])
            
            
        if has_fallen():
            return "fallen"
        
        if vision.has_new_ball_observation():
            walk.turn_left(0)
            return "done"
        
        if imu.get_angle()[2] > self.start_angle + self.angle:
            return "out of sight"
        
    def exit (self):
        robotbody.set_head_position(0, 0)
        print ("exit ball tracking")
    

class Turn:
    """The robot turns for some timyawyawe"""
    
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