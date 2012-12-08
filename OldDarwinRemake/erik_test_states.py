import time
from math import pi
from help_functions import has_fallen,ball_angle, goal_angle_and_type,like,set_head_position,distance_to_ball
from Robot.Interface.Sensors import vision
from Robot.Interface import robotbody
from Robot.Actions import walk,kick

class GoalAdjusting:
    
    def __init__(self):
        self.max_circling_time=20
        self.forward_speed=0.01
        self.backward_speed=-0.01
        self.circling_speed=0.02
        
        self.max_angle=-0.733
        self.min_angle=pi/8
        self.max_angle_timer=self.max_angle/3
        self.min_angle_timer=self.min_angle/3
        
        self.allowed_angle_diff=pi/36
        
        self.to_big_angle=pi/18
        
    def entry(self):
        self.current_time=time.time()
        
        #Starts the turning timer
        self.timer=self.current_time+ self.max_circling_time
        
        #Starts the counter for how many times it has changed circling speed
        self.changed_speed_counter=0
        
        #Sets current speed
        self.current_forward_speed=0
        self.current_circling_speed=self.circling_speed
        
        #Starts lost ball timer
        self.lost_ball_timer=self.current_time+5
        
        #Resets the up and down variable
        self.up_and_down="down"
        
        #Resets the goal angle and goal type
        self.goal_angle=None
        self.goal_type=None
        
    def update(self):
        
        #Tests if it has fallen
        if has_fallen():
            return "fallen"
        
        #Stores current time
        self.current_time=time.time()
        
        #Stores the distance to the ball
        self.distance_to_ball=distance_to_ball()
        
        #Stores whether it has found a new ball observation
        self.has_new_ball_observation=vision.has_new_ball_observation()
        
        #Stores whether it has found a new goal observation
        
        self.has_new_goal_observation=vision.has_new_goal_observation()
        
        #Stores the new angle and type if it has new overservation of the goal
        
        if self.has_new_goal_observation:
            self.goal_angle,self.goal_type=goal_angle_and_type()
        
        #Tests if it has lost the ball
        if self.has_lost_ball() or self.to_long_distance():
            print ("lost the ball")
            return "lost ball"
        
        #Test if it has found a goal post
        if (self.has_new_goal_observation and self.looking_at_goal())\
            or self.changed_speed_counter>5:
            robotbody.set_eyes_led(0, 31, 0)
            print("found goal")
            return "done"
        
        #Tests if it is time to abandon the search for a goal
        if self.current_time > self.start_time + self.time:
            robotbody.set_eyes_led(0, 0, 31)
            print("lucky shot")
            return "fail"
        
        #Updates the head position
        self.update_head_position()
        
        #Updates the walking speed for the robot
        self.update_speed()
        
        
    def exit(self):
        #Reset the walking speed for the robot
        walk.set_velocity(0, 0, 0)
        
    def looking_at_goal(self):
        
        if (self.goal_type==0 or self.goal_type==3) and like(self.goal_angle,0,self.allowed_angle_diff):
            return True
        
        elif self.goal_type==1 and self.goal_angle-self.allowed_angle_diff>0:
            return True
        
        elif self.goal_type==2 and self.goal_angle+self.allowed_angle_diff<0:
            return True
        
        else:
            return False
        
    def update_head_position(self):
        if self.up_and_down=="down":
            if self.current_time>=self.timer+self.max_angle_timer:
                self.timer=self.current_time+self.max_angle_timer
                self.up_and_down="up"
            else:
                set_head_position([0,3*(self.current_time-self.timer)])
        
        else:
            if self.current_time>=self.timer-self.min_angle_timer:
                self.timer=self.current_time-self.min_angle_timer
                self.up_and_down="down"
            else:
                set_head_position([0,3*(self.timer-self.current_time)])
                
    #A method that updates which forward speed the robot should use
    #depending on the distance to the ball
    def update_speed(self):
        if self.distance_to_ball> pi*3:
            self.current_forward_speed = self.forward_speed
        elif self.distance_to_ball< pi and self.distance_to_ball>0:
            self.current_forward_speed = self.backward_speed
        else:
            self.current_forward_speed = 0
        
        if self.has_new_goal_observation:
            
            if self.goal_type==1 and self.goal_angle<0 and\
                self.current_circling_speed==-self.circling_speed:
                
                self.current_circling_speed=self.circling_speed
                self.changed_speed_counter+=1
                self.timer=self.current_time+self.max_circling_time
            
            elif self.goal_type==2 and self.goal_angle>0 and\
                self.current_circling_speed==self.circling_speed:
                
                self.current_circling_speed=-self.circling_speed
                self.changed_speed_counter-=1
                self.timer=self.current_time+self.max_circling_time
                
            
        walk.set_velocity(self.current_forward_speed, self.circling_speed, ball_angle()[0])
        
        
    #The test that decides if it has lost the ball
    #and a test that updates the lost ball timer if it has a new observation
    def has_lost_ball(self):
        if self.current_time>=self.lost_ball_timer:
            robotbody.set_eyes_led(31, 0, 0)
            return True
        
        if self.has_new_ball_observation:
            self.lost_ball_timer=self.current_time+7
        
        return False
    
    def to_long_distance(self):
        
        return self.distance_to_ball>20 or self.distance_to_ball<0
    
class KickBall:
    
    def __init__(self):
        #Initiates the constant variable for the program
        self.time=4
        
    def entry(self):
        #Reset the variables from the last use of the state
        self.time_since_kick=False
        
        #Sets the head to the wanted position and stores the value
        self.wanted_head_position=[0,pi/8]
        set_head_position(self.wanted_head_position)
        
        print ("kicking the ball")
        
    def update(self):
        
        #Tests if the robot has fallen
        if has_fallen():
            return "fallen"
        
        #Tests if the robot hasn't kicked yet.
        #If it hasn't it will move sideways or kick the ball
        if not self.time_since_kick:
            self.move_or_kick()
        
        #Test if the time since the last kick is enough for it to
        #have returned to standing position
        if self.time_since_kick and time.time()>self.time+self.time_since_kick:
            return "done"
        
    
    def exit(self):
        print ("kicked the ball")

    #Decides if the robot should kick the ball or move sideways
    def move_or_kick(self):
        #Gets the angles for to the ball
        self.ball_angle=ball_angle()[0]
        
        #If they are close to the middle it will move sideways
        if not like(self.ball_angle,0.2,0.1):
            walk.set_velocity(0, -0.01, 0)
        
        elif self.ball_angle>0.47:
            walk.set_velocity(0, 0.01, 0)
            
        #Else it will stop, look up, start the timer since the last kick
        #and kick with the foot that has the ball in front of it.
        else:
            walk.set_velocity(0, 0, 0)
            set_head_position([0,0])
            self.time_since_kick = time.time()
            kick.forward_left()
            
class WalkSpeed:
    """The robot walks forward to the ball """

    def __init__(self):
        #initiates the constant variables
        self.speed = 0.01
        
        self.distance_to_ball=2.1
        
    def entry(self):
        #Sets the eyes to a fancy blue
        robotbody.set_eyes_led(0, 0, 31)

        #Starts walking forward with the given speed
        walk.walk_forward(self.speed)
        
        self.lost_ball_timer=time.time()+5
        
        print("See the robot walk")

    def update(self):
        
        if has_fallen():
            return "fallen"
        
        self.current_time=time.time()
        
        if vision.has_new_ball_observation():
            self.lost_ball_timer=self.current_time+2
        
        elif self.current_time>self.lost_ball_timer:
            return "lost ball"
        
        if distance_to_ball()<=self.distance_to_ball:
            return "done"
        
    def exit(self):
        print("Exit walk")