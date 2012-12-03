from Robot.Interface.Sensors import imu, vision
from Robot.Interface import robotbody
from Robot.Actions import motion, walk, kick
from Robot.Util import robotid
from help_functions import *
from math import pi, fabs, tan

import time

"""        General motion states        """
    

""" Circles approximately, due to the unsteady walking, 180 degrees around the ball """

class CircleBall:
    
    def entry(self):
        self.wanted_rotation=pi
        walk.set_velocity(0, 0.4, 0)
        self.rotation_progress = 0
        self.const_forward_velocity=0.02
        self.forward_velocity=0
        
        self.wanted_head_position=[0,pi/8]
        set_head_position(self.wanted_head_position)
        
        self.start_time = time.time()
        self.time = 10
        
        print ("Turning away from our goal")
		
		self.lost_ball_timer=time.time()+5
        
    def update(self):
        if has_fallen():
            return "fallen"
        
		self.current_time=time.time()
        
		if self.current_time>=self.lost_ball_timer:
			robotbody.set_eyes_led(31, 0, 0)
			print ("lost the ball")
			return "lost ball"
		
		elif vision.has_new_ball_observation():
			self.lost_ball_timer=self.current_time()
			
        self.set_new_head_position()
        if distance_to_ball() > pi*3:
            self.forward_velocity = self.const_forward_velocity;
        else:
                self.forward_velocity = 0
        
                walk.set_velocity(self.forward_velocity, 0.4, ball_angle()[0]*1.2)
        
        if self.current_time > self.start_time + self.time:
            print("aiming away from our goal")
            return "done"
        
    def exit(self):
        pass
        
        
    def set_new_head_position(self):
        if like(self.wanted_head_position,robotbody.get_head_position()):
            current_ball_angle=ball_angle()
            if current_ball_angle[1]>pi/8:
                self.wanted_head_position[1]=pi/8
            else:
                self.wanted_head_position[1]=current_ball_angle[1]
        
            self.wanted_head_position[0]=current_ball_angle[0]
            set_head_position(self.wanted_head_position)


""" Searches for a goal while walking in a circle around the ball
    If no goal has been found during, approximately, 360 degrees
    it kicks the ball anyhow wishing for the best outcome """

class CrudeGoalAdjusting:
    
    def __init__(self,direction):
        self.direction=direction
        self.forward_velocity=0
        self.const_forward_velocity=0.01
        
        #Turning timers
        self.time = 20
        
    def entry(self):
        print("Looking for a goal")
        
        #HeadTimers
        self.max_angle_timer=pi/8
        self.min_angle_timer=-pi/9
        self.timer=time.time()
        self.up_and_down="up"
        
        #Turning timers
        self.start_time = self.timer
		
		#Lost ball timer
		self.lost_ball_timer=self.timer
        
    def update(self):
        
        if has_fallen():
            return "fallen"
        if vision.has_new_goal_observation():
            if like(goal_angle()[0],0):
                robotbody.set_eyes_led(0, 31, 0)
                print("found goal")
                return "done"
	
		self.current_time=time.time()
		
		if self.current_time>=self.lost_ball_timer:
			robotbody.set_eyes_led(31, 0, 0)
			print ("lost the ball")
			return "lost ball"
        
        self.update_head_position()
        
        if distance_to_ball() > pi*3:
            self.forward_velocity = self.const_forward_velocity;
        else:
            self.forward_velocity = 0
        
        walk.set_velocity(self.forward_velocity, 0.4*self.direction, ball_angle()[0]*1.2)
        
        if self.current_time > self.start_time + self.time:
            robotbody.set_eyes_led(0, 0, 31)
            print("lucky shot")
            return "fail"
        
    def exit(self):
        walk.set_velocity(0, 0, 0)
        
    def update_head_position(self):
        if self.up_and_down=="down":
            if self.current_time>=self.timer+self.max_angle_timer:
                self.timer=self.current_time+self.max_angle_timer
                self.up_and_down="up"
            else:
                set_head_position([0,self.current_time-self.timer])
        
        else:
            if self.current_time>=self.timer-self.min_angle_timer:
                self.timer=self.current_time-self.min_angle_timer
                self.up_and_down="down"
            else:
                set_head_position([0,self.timer-self.current_time])


""" The robot kicks the ball and waits for some time after kicking it
    to avoid getting in a loop in which it believes it's still in front of the ball """

class KickBall:
    
    def entry(self):
        print ("kicking the ball")
        self.time=4
        self.wanted_head_position=[0,pi/8]
        set_head_position(self.wanted_head_position)
        self.start_time=False
        
    def update(self):
        if has_fallen():
            return "fallen"
        
        if not self.start_time:
            if like(self.wanted_head_position,robotbody.get_head_position()):
                self.ball_angle=ball_angle()[0]

                if like(self.ball_angle,0):
                    walk.set_velocity(0, 0.4, 0)
                else:
                    walk.set_velocity(0, 0, 0)
                    set_head_position([0,0])
                    self.start_time = time.time()
                    if self.ball_angle>0:
                        kick.forward_left()
                    else:
                        kick.forward_right()
        
        if self.start_time and time.time()>self.time+self.start_time:
            return "done"
        
    
    def exit(self):
        print ("kicked the ball")


""" The robot follows the ball until it's close enough.
    Standard value for how close it will go is two times pi.
    However, the distance is an optional input as well as
    the option to force the robot to look at the ground """

class FollowBall:
    
    def __init__(self,distance=2*pi,look_down=False):
        self.distance=distance
        self.speed=0.02
        self.last_distance=1000
        self.look_down=look_down
        
    #FSM methods
    def entry(self):
        print("following the ball")
        robotbody.set_head_hardness(0.95)
        self.last_observation_of_ball=time.time()
        if self.look_down:
            self.wanted_head_position=[0,pi/8]
        else:
            self.wanted_head_position=robotbody.get_head_position()
        
        set_head_position(self.wanted_head_position)
		
    def update(self):
        
        if has_fallen():
            return "fallen"
        
        if not vision.has_new_ball_observation():
            if self.last_observation_of_ball+5<time.time():
                walk.set_velocity(0, 0, 0)
                robotbody.set_eyes_led(31, 0, 0)
                print("lost ball")
				if ball_angle()[0]<=0:
					return "no ball left"
				else:
					return "no ball right"
		
		else:
			self.last_observation_of_ball=time.time()
		
        self.current_head_position = robotbody.get_head_position()
        
        self.update_head_position()
           
        
        self.last_distance=distance_to_ball()
            
        if self.last_distance>0 and self.last_distance<self.distance:
            robotbody.set_eyes_led(0, 31, 0)
            print ("standing in front of ball")
            return "done"
                
        if not like(self.current_head_position[0],0,pi/18):
            walk.set_velocity(self.speed, 0.4, self.current_head_position[0])
                
        else:
            walk.set_velocity(self.speed, 0, 0)
        
            
    def exit(self):
        pass
    
    #Methods used by the FSM
    def update_head_position(self):
        angles=ball_angle()
        if angles[0]>pi/3:
            self.wanted_head_position[0]=pi/3
        elif angles[0]<-pi/3:
            self.wanted_head_position[0]=-pi/3
        else:
            self.wanted_head_position[0]=angles[0]
        
        if angles[1]>pi/8:
            self.wanted_head_position[1]=pi/8
        else:
            self.wanted_head_position[1]=angles[1]
            
        set_head_position(self.wanted_head_position)


""" A very simple state which makes the robot stand still for some time.
    Default time is 1 but it can be set with an optional input. """

class StandStill:
    """The robot stands still and wait"""

    def __init__(self,timer=1):
        self.time = timer # 15 for webots
    def entry(self):
        print("Entry still")
        motion.stand_still()
        self.start_time = time.time()
        robotbody.set_eyes_led(0, 0, 31)
    def update(self):
        if has_fallen():
            return "fallen"
        if time.time() > self.start_time + self.time:
            return "timeout"
    def exit(self):
        print("Exit still")
        motion.start_walk()
        

""" A state that makes the robot stand after it has fallen """

class GetUp:
        
    def entry (self):
        robotbody.set_eyes_led(31, 0, 0)
        motion.get_up()
    
    def update (self):
        if like(imu.get_angle()[1],0.001):
            return ("done")
    
    def exit (self):
        print ("sitting")
        robotbody.set_eyes_led(0, 0, 31)
        

""" The robot walks forward for some the given time.
    Optional input is the walking speed which is set to 0.02 by default """

class WalkSpeed:
    """The robot walks forward some time"""

    def __init__(self, time, speed = 0.02):
        self.time = time
        self.speed = speed
    def entry(self):
        print("See the robot walk")
        self.start_time = time.time()
        
        robotbody.set_eyes_led(0, 0, 31)

        walk.walk_forward(self.speed)

    def update(self):
        if has_fallen():
            return "fallen"
        if time.time() > self.start_time + self.time:
            return "timeout"
    def exit(self):
        print("Exit walk")


""" A state which checks which team the goal in the last
    goal observation belongs to. """

class CheckTeam:
    
    def entry(self):
        print ("checking which goal")
        self.wanted_head_position=[0,0]
        self.team_id=robotid.get_team_number()
        self.first_turn=True
        
    def update(self):
        if has_fallen():
            return "fallen"
        
        if self.opponents_goal():
            
            robotbody.set_eyes_led(0, 31, 0)
            print("fire at opponents goal")
            return "fire"
        else:
            robotbody.set_eyes_led(0, 0, 31)
            print ("turning towards opponents goal")
            return "turn"
        
    def exit(self):
        pass
    
    def opponents_goal(self):
        goal_team_number = vision.get_goal().team
        return not self.team_id==goal_team_number
    
""" The robot adjust it's position around the ball so that the ball is between the robot
    and the middle of the goal """
            
class LineUpShot:
    
    def entry(self):
        print("lining up...")
        robotbody.set_head_hardness(0.95)
        self.goal_angle=robotbody.get_head_position()[0]
        
        self.wanted_head_position=[self.goal_angle,pi/8]
        set_head_position(self.wanted_head_position)
        
        self.timer=None
        self.lost_ball_timer=time.time()+5
        
        self.first_ball_angle=None
        self.last_ball_angle=None
        
    def update(self):
        
        self.current_time=time.time()
        
        if has_fallen():
            return "fallen"
        
        if self.current_time>=self.lost_ball_timer:
            robotbody.set_eyes_led(31, 0, 0)
            print ("lost ball")
            return "lost ball"
        
        if self.timer and self.current_time>self.timer:
            robotbody.set_eyes_led(0, 0, 31)
            return "check again"
        
        if not self.timer:
            if vision.has_new_ball_observation():
                self.first_ball_angle=ball_angle()[0]
                self.last_ball_angle=self.first_ball_angle
                self.timer=time.time()+fabs(self.first_ball_angle)*100
                self.lost_ball_timer=self.current_time+10
        
        else:
            if like(self.first_ball_angle,self.goal_angle,pi/9):
                robotbody.set_eyes_led(0, 31, 0)
                print("lined up")
                return "lined up"
            
            else:
                set_head_position(ball_angle())
                    
            if self.first_ball_angle<0:
                walk.set_velocity(0, -0.4, self.last_ball_angle)
            else:
                walk.set_velocity(0, 0.4, self.last_ball_angle)
            
    def exit(self):
        walk.set_velocity(0, 0, 0)


""" Sets the head position to face the middle of the goal,
    if it can find two pillars within 180 degrees.
    Sets the head position to one of the pillar if itonly can find one.
    Otherwise calls it a fail. """

class FindMiddleOfGoal:
    
    """FSM methods"""
    
    def entry(self):
        robotbody.set_head_hardness(0.95)
        self.current_head_position=robotbody.get_head_position()
        
        self.wanted_head_position=[-pi/2,-pi/16]
        set_head_position(self.wanted_head_position)
           
        self.ending=False
        
        self.numbers_of_observation=0
        self.angles=[]
        
        print ("searching for goal")
        
    def update(self):      
        self.current_head_position=robotbody.get_head_position()
        if has_fallen():
            return "fallen"
        
        if like(self.wanted_head_position,self.current_head_position):

            if self.ending:
                robotbody.set_eyes_led(0, 31, 0)
                return "focus one"
            
            elif len(self.angles)==0:
                if vision.has_new_goal_observation():
                    self.get_goal_observation()
                    self.searching_for_next()
                    print("got first observation")
                    
                elif like(self.current_head_position[0],pi/2):
                    robotbody.set_eyes_led(31, 0, 0)
                    print("fail")
                    return "fail"
                
                else:
                    self.set_next_head_position()
            
            elif len(self.angles)==1:
                if vision.has_new_goal_observation():
                    self.get_goal_observation()
                    if len(self.angles)==2:
                        self.focus_middle()
                        print("got second observation")
                    else:
                        self.ending=True
                    
                else:
                    self.set_next_head_position()
            
            else:
                robotbody.set_eyes_led(0, 31, 0)
                print("focus middle")
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
        self.wanted_head_position=[pi/2,-pi/16]
        set_head_position(self.wanted_head_position)
               
    def focus_middle(self):
        self.wanted_head_position=[(self.angles[0][0]+self.angles[1][0])/2,0]
        set_head_position(self.wanted_head_position)    
            
    def focus_one(self):
        self.wanted_head_position=self.angles[0]
        set_head_position(self.wanted_head_position)
        
    def set_next_head_position(self):
        if len(self.angles)==0:
            self.wanted_head_position[0]+=pi/15
        else:
            self.wanted_head_position[0]-=pi/15
        set_head_position(self.wanted_head_position)


""" A state in which the robot tracks the ball over the field.
    If it can't find the goal while having turned in a, approximately, complete circle
    it calls out that it can't find the ball and goes to the next state """

class TrackBall:
    
    def __init__(self,direction):
        self.max_time_difference=pi/3
        self.angle=2*pi
        self.time_between=1
		self.direction=direction
		
    def entry(self):
        print("Tracking ball")
        robotbody.set_head_hardness(0.95)
        self.wanted_head_position=robotbody.get_head_position()
        
        self.start_angle = imu.get_angle()[2]
        
        self.start_time=time.time()
        self.timer=self.start_time+self.time_between
        
        self.left_or_right="right"
        
		if self.direction=="left":
			walk.turn_left(0.2)
		else:
			walk.turn_right(0.2)
			
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
                self.wanted_head_position[1]=pi/8
                self.left_or_right="left"
            else:
                self.wanted_head_position[0]=-(self.current_time-self.timer)
            
        set_head_position(self.wanted_head_position)
        
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
		
		
""" New states that must be added """
_track_ball --> _track_ball_left & _track_ball_right
""" New transitions that needs to be added """

self.add_transition(_circle_away_from_own_goal,"lost ball",_track_ball_left)
self.add_transition(_finding_the_goal,"lost ball",_track_ball_left)
_follow_ball, "lost ball", _track_ball --> _follow_ball, "lost ball left", _track_ball_right &_follow_ball, "lost ball right", _track_ball_right