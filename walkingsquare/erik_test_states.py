'''
Created on Nov 16, 2012

@author: erik
'''
from Robot.Interface.Sensors import imu, vision
from Robot.Interface import robotbody
from Robot.Actions import motion, walk, kick
from help_functions import *
from math import pi, fabs



class FindMiddleOfGoal:
    
    """FSM methods"""
    
    def entry(self):
        robotbody.set_head_hardness(1.95)
        self.current_head_position=robotbody.get_head_position()
        
        self.wanted_head_position=[-pi/2,0]
        robotbody.set_head_position_list(self.wanted_head_position)
           
        self.ending=False
        
        self.numbers_of_observation=0
        self.angles=[]
        
    def update(self):
        if has_fallen():
            return "fallen"
        
        self.current_head_position=robotbody.get_head_position()
        
        if like(self.wanted_head_position,self.current_head_position):
            
            if self.ending:
                return "focus_one"
            
            elif len(self.angles)==0:
                if vision.has_new_goal_observation():
                    self.get_goal_observation()
                    self.seraching_for_next()
                    
                elif like(self.current_head_position,pi/2):
                    return "fail"
            
            elif len(self.angles)==1:
                if vision.has_new_goal_observation():
                    self.get_goal_observation()
                    self.focus_middle()
            
            elif len(self.angles)==2:
                return "focus_middle"
            
            else:
                self.set_next_head_position()
    
    def exit(self):
        pass
    
    
    """Methods used by the update method"""
    def get_goal_observation(self):
        self.last_goal = vision.get_goal()
        self.goal = vision.Goal(self.last_goal.x,self.last_goal.y,self.last_goal.z,self.last_goal.t)
        temp_angles=self.goal.get_angle()
        
        if len(self.angles)==0 or not like(temp_angles,self.angles[0]):
            self.angles.append(temp_angles)
        
        else:
            self.focus_one()
            self.ending=True
        
    def searching_for_next(self):
        self.wanted_head_position=[pi/2,0]
        robotbody.set_head_position_list(self.wanted_head_position)
               
    def focus_middle(self):
        self.wanted_head_position=[(self.angles[0][0]+self.angles[1][0])/2,0]
        robotbody.set_head_position_list(self.wanted_head_position)    
            
    def focus_one(self):
        self.wanted_head_position=[self.angles[0]]
        robotbody.set_head_position_list(self.wanted_head_position)
        
    def set_next_head_position(self):
        if len(self.angles)==0:
            self.wanted_head_position[0]+=pi/15
        else:
            self.wanted_head_position[0]-=pi/15
        robotbody.set_head_position_list(self.wanted_head_position)