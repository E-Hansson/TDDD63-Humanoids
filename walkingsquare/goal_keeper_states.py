#States for the goal keeper

from Robot.Interface.Sensors import vision, imu
from Robot.Interface import robotbody
from Robot.Actions import walk, motion
from math import pi
from help_functions import has_fallen, ball_angle, like
import time

#State for guarding the goal while standing on the goal line
class Guarding:
    
    def __init__(self):
        self.max_traveled_time=3
        self.accepted_out_of_sight_time=2
        self.traveled_time=0
    
    #FSM methods   
    def entry(self):
        
        robotbody.set_head_hardness(1.95)
        current_head_position=robotbody.get_head_position()
        self.wanted_head_position=[current_head_position[0],current_head_position[1]]        
        
        self.last_distance=0
        self.last_observation=0
        self.start_travel=[]
        self.direction="stand still"
            
    def update(self):
        if has_fallen():
            return("fallen")
        
        self.update_traveled_time()
        
        self.update_head_position()
                
        if vision.has_new_ball_observation():
            self.update_last()
            self.left_or_right()
            
        elif self.last_observation+self.accepted_out_of_sight_time<time.time():
            return ("out of sight")
                
        self.walk_sideways()
            
        
    def exit(self):
        print("Lost ball")

    
    #Methods used in update
    
    def update_last(self):
        self.last_distance=self.distace_to_ball()
        self.last_observation=time.time()
        
    def left_or_right(self):
        head_position=robotbody.get_head_position()
        
        if head_position[0]<-pi/18:
            self.direction="left"
            self.start_travel=[time.time(),"-"]
        elif head_position[0]>pi/18:
            self.start_travel=[time.time(),"+"]
            self.direction="right"
        else:
            self.direction="stand still"
            self.start_travel=[]
    
    def walk_sideways(self):
        
        if self.direction=="left" and self.traveled_time>-self.max_traveled_time:
            walk.set_velocity(0,0.4,-pi)
        elif self.direction=="right" and self.traveled_time<self.max_traveled_time:
            walk.set_velocity(0,0.4,pi)
        else:
            walk.set_velocity(0, 0, 0)
            
    def update_traveled_time(self):
        if self.start_travel:
            if self.start_travel[1]=="+":
                self.traveled_time+=(time.time()-self.start_travel[0])
            else:
                self.traveled_time-=(time.time()-self.start_travel[0])
    
    def update_head_position(self):
        angles=ball_angle()
        robotbody.set_head_position(angles[0],angles[1])

#State for finding the ball while standing on the goal line
class BallTracking:
    
    #FSM methods
    def entry(self):
        robotbody.set_head_hardness(1.95)
        current_head_position=robotbody.get_head_position()
        self.wanted_head_position=[current_head_position[0],current_head_position[1]]
    
    def update(self):
        
        if has_fallen():
            return("fallen")
        
        self.update_head_position()
        
        if vision.has_new_ball_observation():
            return ("done")
        
    def exit(self):
        print("found the ball")
    
    
    #Methods used in update
    def update_head_position(self):
        
        head_position=robotbody.get_head_position()
        if like(head_position,self.wanted_head_position):
            if like(head_position[0],pi/2) and like(head_position[1],0):
                self.wanted_head_position=[-pi/2,pi/3.5]
        
            elif like(head_position[0],pi/2):
                self.wanted_head_position=[-pi/2,0]
        
            else:
                self.wanted_head_position[0]=head_position[0]+pi/15
            
            robotbody.set_head_position(self.wanted_head_position[0],self.wanted_head_position[1])
        
#State for going to the middle of the goal and face the opponents
class GoToTheGoal:
    
    def entry (self):
        pass
    def update (self):
        pass
    def exit (self):
        pass

#State for making the robot stand up
class GetUp:
        
    def entry (self):
        motion.get_up()
    
    def update (self):
        if like(imu.get_angle()[1],0.001):
            return ("done")
    
    def exit (self):
        print("sitting")