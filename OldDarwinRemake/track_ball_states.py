import time
from Robot.Interface import robotbody
from Robot.Actions import walk
from help_functions import ball_angle, set_head_position
from math import pi
from Robot.Interface.Sensors import imu, vision

""" The robot walks forward for some the given time.
    Optional input is the walking speed which is set to 0.02 by default """

class WalkSpeed:
    """The robot walks forward some time"""

    def __init__(self, time, speed = 0.04):
        #initiates the constant variables
        self.time = time
        self.speed = speed
        
    def entry(self):
        #Starts the timer
        self.start_time = time.time()
        
        #Sets the eyes to a fancy blue
        robotbody.set_eyes_led(0, 0, 31)

        #Starts walking forward with the given speed
        walk.walk_forward(self.speed)
        
        print("See the robot walk")

    def update(self):
        
        #Tests if it is time to stop walking
        
        if time.time() > self.start_time + self.time:
            return "timeout"
        
    def exit(self):
        print("Exit walk")

    
""" A state which decide it should turn towards depending
    on which side its last observation of the ball was. """

class TrackDirection:
    
    def entry(self):
        #Gets the last vision of the ball
        self.last_ball_angles=ball_angle()[0]
        
    def update(self):
        
        #Tests which side it lost it on
        if self.last_ball_angles>=0:
            return "left"
        else:
            return "right"
        
    def exit (self):
        pass
    
    
""" A state in which the robot tracks the ball over the field.
    If it can't find the goal while having turned in a, approximately, complete circle
    it calls out that it can't find the ball and goes to the next state """
    
class TrackBall:
    
    def __init__(self,direction):
    
        #Initiates the constant variables for:
        #Turning head and body
        self.max_time_difference=pi/3
        self.angle=2*pi
        self.time_between=1
        self.direction=direction
        self.highest_head_position=-0.733
        self.lowest_head_position=pi/8
        
    def entry(self):
        
        #Resets the variables since the last use of the state:
        
        #starting angle
        self.start_angle = imu.get_angle()[2]
        
        #Timers
        self.start_time=time.time()
        self.timer=self.start_time+self.time_between
        
        #Which direction it should start turning its head
        self.left_or_right=self.direction
        
        #Makes sure that the head hardness is correct and
        #stores the current head position
        robotbody.set_head_hardness(0.95)
        self.wanted_head_position=robotbody.get_head_position()
        
        #Initiates the turn in the right direction
        if self.direction=="left":
            walk.turn_left(0.2)
        else:
            walk.turn_right(0.2)
            
        #Sets a fancy blue eye colour
        robotbody.set_eyes_led(0, 0, 31)
            
        print("Tracking ball")
        
    def update(self):
        
        #Tests if it has found a ball observation
        if vision.has_new_ball_observation():
            walk.turn_left(0)
            robotbody.set_eyes_led(0, 31, 0)
            print("found ball")
            return "done"
        
        #Tests if it's time to stop turning and accept a failure
        if imu.get_angle()[2] > self.start_angle + self.angle:
            walk.turn_left(0)
            robotbody.set_eyes_led(31,0,0)
            print ("can't find the ball")
            return "out of sight"
        
        #Updates the head position
        self.update_head_position()
        
    def exit(self):
        pass
        
    #Updates the head position with time as the variable.
    def update_head_position(self):
        self.current_time=time.time()
        if self.left_or_right=="left":
            if self.current_time>=self.timer+self.max_time_difference:
                self.timer=self.current_time+self.max_time_difference
                self.wanted_head_position[1]=self.highest_head_position
                self.left_or_right="right"
            else:
                self.wanted_head_position[0]=self.current_time-self.timer
        
        else:
            if self.current_time>=self.timer+self.max_time_difference:
                self.timer=self.current_time+self.max_time_difference
                self.wanted_head_position[1]=self.lowest_head_position
                self.left_or_right="left"
            else:
                self.wanted_head_position[0]=-(self.current_time-self.timer)
            
        set_head_position(self.wanted_head_position)


""" A state with the only purpose to tell the Track Ball Machine
    that it s done. """
    
class Done:
    
    def entry(self):
        pass
    
    def update(self):
        pass
    
    def exit(self):
        pass