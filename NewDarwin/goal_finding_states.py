from math import pi
from help_functions import set_head_position,like,goal_angle, ball_angle, distance_to_ball, goal_type
from Robot.Interface import robotbody
from Robot.Actions import walk
import time
from Robot.Interface.Sensors import vision, imu
from Robot.Util import robotid


""" A state that looks for a goal within 120 degrees """
class LookingForFirstObservation:
    
    def __init__(self):
        self.max_angles=pi/3
        self.time_between=1
        self.highest_head_position=-0.733
    
    def entry(self):
        
        self.start_time=time.time()
        self.timer=self.start_time+self.time_between
        
        robotbody.set_head_hardness(0.95)
        
        self.wanted_head_position=[self.max_angles,self.highest_head_position]
        
        set_head_position(self.wanted_head_position)
        
        self.move_head_timer=None
        
        robotbody.set_eyes_led(0,0,31)
        
        self.last_goal_observation=None
        
        print ("looking for first observation")
        
    def update(self):
        
        self.current_time=time.time()
        
        if self.move_head_timer and self.move_head_timer<=self.current_time:
            print ("found post")
            return "post"
        
        else:
            self.last_goal_observation=self.has_new_goal_observation()

            if self.last_goal_observation=="post":
                self.move_head_timer=0.1
            elif self.last_goal_observation=="whole right":
                print ("found goal")
                return "whole right"
            elif self.last_goal_observation=="whole left":
                print ("found goal")
                return "whole left"
            
            elif self.last_goal_observation=="left post, adjust left":
                print("found left post")
                return "left left"
            
            elif self.last_goal_observation=="left post, adjust right":
                print("found left post")
                return "left right"
            
            elif self.last_goal_observation=="right post, adjust left":
                print("found right post")
                return "right left"
        
            elif self.last_goal_observation=="right post, adjust right":
                print("found right post")
                return "right right"
            
            elif self.update_head_position():
                print("couldn't find anything")
                return "nothing"
        
    def exit(self):
        pass
    
    #Updates the head position with time as the variable.
    def update_head_position(self):
        
        if self.current_time>self.timer+self.max_angles:
            return True
        
        self.wanted_head_position[0]=-(self.current_time-self.timer)
        set_head_position(self.wanted_head_position)
        
        
    def has_new_goal_observation(self):
        if vision.has_new_goal_observation():
            self.goal_type=goal_type()
            print (str(self.goal_type) + "      :       " + str(goal_angle()[0]))
            if self.goal_type==3:
                if goal_angle()[0]>=0:
                    return "whole right"
                else:
                    return "whole left"
            
            elif self.goal_type==1:
                if goal_angle()[0]>=0:
                    return "left post, adjust left"
                else:
                    return "left post, adjust right"
            
            elif self.goal_type==2:
                if goal_angle()[0]>=0:
                    return "right post, adjust right"
                else:
                    return "right post, adjust left"
                
            else:
                self.wanted_head_position=list(goal_angle())
                set_head_position(self.wanted_head_position)
                return "post"
        else:
            return "none"


""" Circle around the ball for a quarter of a circle with default value """
class CircleBall:
    
    def __init__(self,circle_time=6,direction="left"):
        #setting a few standard variables that will be the same all the time
        
        if direction=="left":
            self.circling_velocity=0.025
        else:
            self.circling_velocity=-0.025
            
        self.const_forward_velocity=0.02
        
        self.time=circle_time
        
    def entry(self):
        #Reseting the forward velocity from the last time the state was used
        self.forward_velocity=0
        
        #Updating the head position so that DARwIn will look down at the ball
        self.wanted_head_position=[0,pi/8]
        set_head_position(self.wanted_head_position)
        
        #Starting the sideways walk
        walk.set_velocity(self.forward_velocity, self.circling_velocity, 0)
        
        #Starting the turning timer
        self.start_time = time.time()
        
        #starting the lost ball timer
        self.lost_ball_timer=time.time()+5
        
        print ("Turning around the ball")
        
    def update(self):
        
        #Storing the current time for the update
        self.current_time=time.time()
        
        #Testing if it has lost the ball
        if self.has_lost_ball():
            print ("lost the ball")
            return "lost ball"
        
        #Test if it has finished it's turn
        if self.current_time > self.start_time + self.time:
            print("Turned roughly a quarter of a circle")
            return "done"
        
        #Updating the speed at which the robot moves
        self.update_speed()
        
    def exit(self):
        pass
    
    #The test that decides if it has lost the ball
    #and a test that updates the lost ball timer if it has a new observation
    def has_lost_ball(self):
        if self.current_time>=self.lost_ball_timer:
            robotbody.set_eyes_led(31, 0, 0)
            return True
        
        elif vision.has_new_ball_observation():
            self.lost_ball_timer=self.current_time+5
            return False
        
        if distance_to_ball()<0:
            return True
        
        else:
            return False
    
    #A method that updates which forward speed the robot should use
    #depending on the distance to the ball
    def update_speed(self):
        self.distance_to_ball=distance_to_ball()
        if self.distance_to_ball> pi*3:
            self.forward_velocity = self.const_forward_velocity;
        elif self.distance_to_ball< pi and self.distance_to_ball>0:
            self.forward_velocity = -self.const_forward_velocity
        else:
            self.forward_velocity = 0
            
        walk.set_velocity(self.forward_velocity, self.circling_velocity, ball_angle()[0])


""" circles towards the middle of the goal """
class AdjustPosition:
    
    def __init__(self,direction,difference=0):
        
        if direction=="left":
            self.circling_velocity=0.02
        else:
            self.circling_velocity=-0.02
            
        self.const_forward_velocity=0.02
        
        self.max_angle=pi/8
        self.min_angle=-0.733
        
        self.max_angle_timer=self.max_angle/2
        self.min_angle_timer=self.min_angle/2
        
        self.alowed_angled_diff=pi/18
        
        self.difference=difference
    
    def entry(self):
        self.forward_velocity=0
        
        #Updating the head position so that DARwIn will look down at the ball
        self.wanted_head_position=[0,pi/8]
        set_head_position(self.wanted_head_position)
        
        #Head timers
        self.timer=time.time()
        self.up_and_down="up"
        
        #Turning timer
        self.start_time = self.timer
        self.lucky_shot_timer = self.start_time + 30
        
        #starting the lost ball timer
        self.lost_ball_timer=time.time()+5
        
    def update(self):
        #Storing the current time for the update
        self.current_time=time.time()
        
        
        
        if like(goal_angle()[0]-self.difference,0,self.alowed_angled_diff):
                robotbody.set_eyes_led(0, 31, 0)
                print("looking at goal")
                return "done"
        
        #Testing if it has lost the ball
        if self.has_lost_ball():
            print ("lost the ball")
            return "lost ball"
        
        self.update_head_position()
        self.update_speed()
        
    def exit(self):
        pass
        
    
    #The test that decides if it has lost the ball
    #and a test that updates the lost ball timer if it has a new observation
    def has_lost_ball(self):
        if self.current_time>=self.lost_ball_timer:
            robotbody.set_eyes_led(31, 0, 0)
            return True
        
        elif vision.has_new_ball_observation():
            self.lost_ball_timer=self.current_time+5
            return False
        
        if distance_to_ball()<0:
            return True

        else:
            return False
        
    def update_head_position(self):
        if self.up_and_down=="down":
            if self.current_time>=self.timer+self.max_angle_timer:
                self.timer=self.current_time+self.max_angle_timer
                self.up_and_down="up"
            else:
                set_head_position([0,2*(self.current_time-self.timer)])
        
        else:
            if self.current_time>=self.timer-self.min_angle_timer:
                self.timer=self.current_time-self.min_angle_timer
                self.up_and_down="down"
            else:
                set_head_position([0,2*(self.timer-self.current_time)])
                
    #A method that updates which forward speed the robot should use
    #depending on the distance to the ball
    def update_speed(self):
        self.distance_to_ball=distance_to_ball()
        if self.distance_to_ball> pi*3:
            self.forward_velocity = self.const_forward_velocity;
        elif self.distance_to_ball< pi and self.distance_to_ball>0:
            self.forward_velocity = -self.const_forward_velocity
        else:
            self.forward_velocity = 0
            
        walk.set_velocity(self.forward_velocity, self.circling_velocity, ball_angle()[0])
        
        
class TurnGyro:
    """The robot turn a certain angle"""

    def __init__(self):
        self.angle = 7.0/4*pi-1.0
        self.number_of_turns = 0
        
    def entry(self):
        print("Entry gyro turn")
        self.start_angle = imu.get_angle()[2]
        self.number_of_turns += 1
        
        if goal_angle()[0]>=0:
            self.first_post=1
            walk.turn_left(0.4)
        else:
            self.first_post=-1
            walk.turn_right(0.4)
            
    def update(self):
        
        if self.first_post==1:
            if imu.get_angle()[2]>self.start_angle +self.angle:
                set_head_position([0,pi/8])
                return "aim for post left"
        else:
            if imu.get_angle()[2]<self.start_angle -self.angle:
                set_head_position([0,pi/8])
                return "aim for post right"
                
        
        if goal_angle()[0]*self.first_post<0:
            if self.first_post==1:
                return "right"
            else:
                return "left"
        
    def exit(self):
        walk.turn_left(0)
        print("Exit gyro turn")
        
class TurnBackToBall:
    
    def __init__(self,direction):
        self.direction=direction
    
    def entry(self):
        set_head_position([0,pi/8])
        
        if self.direction=="left":
            walk.turn_left(0.4)
        else:
            walk.turn_right(0.4)
            
        self.start_angle=imu.get_angle()[2]
        
    def update(self):
        
        if self.direction=="left" and imu.get_angle()[2]>self.start_angle+2*pi-1.6:
            return "lost ball"
        
        elif self.direction=="right" and imu.get_angle()[2]<self.start_angle-2*pi+1.6:
            return "lost ball"
        
        if vision.has_new_ball_observation() and like(ball_angle()[0],0,pi/45):
            return "done"
        
    def exit(self):
        pass

""" A state which checks which team the goal in the last
    goal observation belongs to. """


class CheckTeam:
    
    def __init__(self):
        #Initiates the constant variables
        self.wanted_head_position=[0,0]
        self.team_id=robotid.get_team_number()
    
    def entry(self):
        print ("checking which goal")
        
    def update(self):
        
        #Test if the last vision of a goal was the opponents
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
    
    #Test if the last goal the robot saw belonged to the opponents team or its own
    def opponents_goal(self):
        goal_team_number = vision.get_goal().team
        return not self.team_id==goal_team_number
        
class Done:
    
    def entry(self):
        pass
    
    def update(self):
        pass
    
    def exit(self):
        pass
    
class LostBall:
    
    def entry(self):
        pass
    
    def update(self):
        pass
    
    def exit(self):
        pass