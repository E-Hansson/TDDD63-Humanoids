from Robot.Interface.Sensors import imu, vision
from Robot.Interface import robotbody
from Robot.Actions import motion, walk, kick
from Robot.Util import robotid
from help_functions import *
from math import pi, fabs, tan

import time

"""        General motion states        """

#A new version of circle ball based on imu angle instead of random guessing
#Hopefully more accurate than the previous
class CircleBall:
    
    def entry(self):
        self.wanted_rotation=-pi+0.8
        self.const_forward_velocity=0.02
        self.forward_velocity=0
        
        self.start_angle = imu.get_angle()[2]
        
        self.wanted_head_position=[0,pi/4.5]
        set_head_position(self.wanted_head_position)
        
    def update(self):
        
        if has_fallen():
            return "fallen"
        
        set_head_position(ball_angle())
        
        if distance_to_ball() > pi/3.8:
            self.forward_velocity = self.const_forward_velocity;
        else:
            self.forward_velocity = 0
        
        walk.set_velocity(self.forward_velocity, 0.4, self.wanted_head_position[0]*1.2)
        
        if imu.get_angle()[2]<self.start_angle+self.wanted_rotation:
            print("aiming away from our goal")
            return "done"
    
    def exit(self):
        pass

#A bit more slimed version of (what I presume) is the same state
#Yes that means it's a new one
class LineUpShot:
    
    def entry(self):
        print("lining up...")
        robotbody.set_head_hardness(0.95)
        self.goal_angle=robotbody.get_head_position()[0]
        
        self.wanted_head_position=[self.goal_angle,pi/4.5]
        set_head_position(self.wanted_head_position)
        
        self.timer=time.time()+self.goal_angle*10
        
        self.first_ball_angle=None
        self.last_ball_angle=None
        
    def update(self):
        
        if has_fallen():
            return "fallen"
        
        if time.time()>self.timer:
            return "check again"
        
        self.current_head_position=robotbody.get_head_position()
        
        if like(self.current_head_position,self.wanted_head_position):
            if like(self.current_head_position[0],self.goal_angle,0.2):
                print("lined up")
                return "lined up"
            
            if not self.first_ball_angle:
                if vision.has_new_ball_observation():
                    self.first_ball_angle=ball_angle()[0]
                    self.last_ball_angle=self.first_ball_angle
                    self.timer=time.time()+fabs(self.first_ball_angle)*10
                else:
                    print("lost the ball")
                    return "lost ball"
                    
            else:
                set_head_position(ball_angle())
                    
            if self.first_ball_angle<0:
                walk.set_velocity(0, -0.4, self.last_ball_angle)
            else:
                walk.set_velocity(0, 0.4, self.last_ball_angle)
            
    def exit(self):
        walk.set_velocity(0, 0, 0)



#A new version of TrackBall that uses time instead of specific angles
#Hopefully it gives a bit more accuracy than the specific angle version
class TrackBall:
    
    def __init__(self):
        self.max_time_difference=pi/3
        self.angle=2*pi
        self.time_between=1
    
    def entry(self):
        print("Tracking ball")
        robotbody.set_head_hardness(0.95)
        self.wanted_head_position=robotbody.get_head_position()
        
        self.start_angle = imu.get_angle()[2]
        
        self.start_time=time.time()
        self.timer=self.start_time+self.time_between
        
        self.left_or_right="right"
        
        walk.turn_left(0.2)
        set_head_position(self.wanted_head_position)
        
    def update(self):
        
        self.update_head_position()
        
        if vision.has_new_ball_observation():
            walk.turn_left(0)
            robotbody.set_eyes_led(0, 31, 0)
            print("found ball")
            return "done"
        
        if imu.get_angle()[2] > self.start_angle + self.angle:
            walk.turn_left(0)
            robotbody.set_eyes_led(31,0,0)
            print ("can't find the ball")
            return "out of sight"
        
    def exit(self):
        pass
        
        
    def update_head_position(self):
        self.current_time=time.time()
        if self.left_or_right=="left":
            if self.current_time>=self.timer+self.max_time_difference:
                self.timer=self.current_time+self.max_time_difference
                self.wanted_head_position[1]=0
                self.left_or_right="right"
            else:
                self.wanted_head_position[0]=self.current_time-self.timer
        
        else:
            if self.current_time>=self.timer+self.max_time_difference:
                self.timer=self.current_time+self.max_time_difference
                self.wanted_head_position[1]=pi/4.5
                self.up_or_down="left"
            else:
                self.wanted_head_position[0]=-(self.current_time-self.timer)
            
        set_head_position(self.wanted_head_position)

#Not quite perfect Goal Update needs to be adjusted
class CrudeGoalAdjusting:
    
    def __init__(self,direction):
        self.direction=direction
        self.forward_velocity=0
        self.const_forward_velocity=0.02
        
    def entry(self):
        self.max_rotation=(pi*2-1.6)*self.direction
        self.start_rotation=imu.get_angle()[2]
        self.max_time_difference=pi/4.5
        self.timer=time.time()
        self.up_and_down="upp"
    
    def update(self):
        
        if has_fallen():
            return "fallen"
        if vision.has_new_goal_observation():
            if like(goal_angle()[0],0):
                print("found goal")
                return "done"
        if (self.direction==1 and imu.get_angle()[2]>self.start_rotation+self.max_rotation)\
            or (self.direction==-1 and imu.get_angle()[2]<self.start_rotation+self.max_ritation):
            print("couldn't find a goal")
            return ("failed")
        
        self.update_head_position()
        
        if distance_to_ball() > 1:
            self.forward_velocity = self.const_forward_velocity;
        else:
            self.forward_velocity = 0
        
        walk.set_velocity(self.forward_velocity, 0.4*self.direction, ball_angle()[0]*1.2)
        
    def exit(self):
        pass
        
    def update_head_position(self):
        self.current_time=time.time()
        if self.up_and_down=="down":
            if self.current_time>=self.timer+self.max_time_difference:
                self.timer=self.current_time
                self.up_and_down="up"
            else:
                set_head_position([0,self.current_time-self.timer])
        
        else:
            if self.current_time-self.max_time_difference>=self.timer:
                self.timer=self.current_time
                self.up_and_down="down"
            else:
                set_head_position([0, self.timer+self.max_time_difference-self.current_time])