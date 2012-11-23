#States for the goal keeper

from Robot.Interface.Sensors import vision, imu
from Robot.Interface import robotbody
from Robot.Actions import walk, motion
from math import pi
from help_functions import has_fallen, ball_angle, like, goal_angle
import time


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
        walk.turn_left(0)
        print("Exit gyro turn")
        
        
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

class FaceMiddleOfGoal:
    

    def entry(self):
        
        self.head_position=robotbody.get_head_position()
        walk.set_velocity(0, 0.4, self.head_position[0])
        robotbody.set_head_position(0, pi/3.2)
        print("turning towards the goal")
        
    def update(self):
        if has_fallen():
            return "fallen"
        
        if like(robotbody.get_head_position()[0],0):
            return "done"
        
    def exit(self):
        print("ending the turn")
        
class GoToLine:
    
    def __init__(self,timer=-1):
        
        self.timer=timer
        
    def entry(self):
        self.timer+=time.time()
        walk.set_velocity(0.1, 0, 0)
        print("walking towards the line")
    def update(self):
        if has_fallen():
            return "fallen"
        
        if self.timer<time.time():
            
            if vision.has_new_line_observation() and self.get_pitch_angle()<=pi/3:
                walk.set_velocity(0, 0, 0)
                return "standing on line"
            
    def exit(self):
        print ("stopped")
        

class CheckIfStandingInGoal:
    
    def entry(self):
        self.wanted_head_position=[-pi/2,0]
        robotbody.set_head_position_list(self.wanted_head_position)
        print("Test if standing in the goal")
        
    def update(self):
        
        if has_fallen():
            return "fallen"
        
        if vision.has_new_goal_observation():
            
            if like(goal_angle()[0],0):
                return "done"
            else:
                return "standing in front of the goal"
        
        self.current_head_position=robotbody.get_head_position()
        
        if like(self.current_head_position,pi/2):
            return "can't find the goal"
        
        if like(self.wanted_head_position,self.current_head_position):
            self.update_head_position()
    
    def exit(self):
        print("test finished")
        
    def update_head_position(self):
        self.wanted_head_position[0]+=pi/15
        robotbody.set_head_position_list(self.wanted_head_position)
        
        
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
            if like(head_position,[pi/2,0]):
                self.wanted_head_position=[-pi/2,pi/3.5]
        
            elif like(head_position[0],pi/2):
                self.wanted_head_position=[-pi/2,0]
        
            else:
                self.wanted_head_position[0]=head_position[0]+pi/15
            
            robotbody.set_head_position(self.wanted_head_position[0],self.wanted_head_position[1])
      

#State for making the robot stand up
class GetUp:
        
    def entry (self):
        motion.get_up()
    
    def update (self):
        if like(imu.get_angle()[1],0.001):
            return ("done")
    
    def exit (self):
        print("sitting")


"""
Sets the head position to face the middle of the goal if it can find two pillars within 180 degrees.
Sets the head position to one of the pillar if it can only find one.
Otherwise calls it a fail.
"""

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
        
        print ("searching for goal")
        
    def update(self):
        if has_fallen():
            return "fallen"
        
        self.current_head_position=robotbody.get_head_position()
        
        if like(self.wanted_head_position,self.current_head_position):

            if self.ending:
                return "focus one"
            
            elif len(self.angles)==0:
                if vision.has_new_goal_observation():
                    self.get_goal_observation()
                    self.searching_for_next()
                    
                elif like(self.current_head_position[0],pi/2):
                    return "fail"
                
                else:
                    self.set_next_head_position()
            
            elif len(self.angles)==1:
                if vision.has_new_goal_observation():
                    self.get_goal_observation()
                    self.focus_middle()
                    
                else:
                    self.set_next_head_position()
            
            else:
                return "focus middle"

    
    def exit(self):
        pass
    
    
    """Methods used by the update method"""
    def get_goal_observation(self):
        
        temp_angles=goal_angle()
        
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