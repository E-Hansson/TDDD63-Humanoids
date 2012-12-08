from Robot.Interface.Sensors import imu, vision
from Robot.Interface import robotbody
from Robot.Actions import motion, walk, kick
from Robot.Util import robotid
from help_functions import *
from math import pi, fabs

import time

class WalkSpeed:
    """The robot walks forward some time"""

    def __init__(self):
        #initiates the constant variables
        self.speed = 0.01
        
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
        
        if distance_to_ball()<=2.1:
            return "done"
        
    def exit(self):
        print("Exit walk")

""" The robot kicks the ball and waits for some time after kicking it
    to avoid getting in a loop in which it believes it's still in front of the ball """

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
    

""" The robot follows the ball until it's close enough.
    Standard value for how close it will go is two times pi.
    However, the distance is an optional input as well as
    the option to force the robot to look at the ground """

class FollowBall:
    
    def __init__(self,distance=2*pi+0.3,look_down=False):
        #Sets the constant variables for the state
        self.distance=distance
        self.look_down=look_down
        
        if self.look_down:
            self.speed=0.02
        else:
            self.speed=0.03
        
    #FSM methods
    def entry(self):
        #Starts the timer from when the ball was last seen
        self.lost_ball_timer=time.time()+5
        
        #Sets the wanted head position, either to the current or
        #to one looking down at the ball
        if self.look_down:
            self.wanted_head_position=[0,pi/8]
        else:
            self.wanted_head_position=robotbody.get_head_position()
        
        #Makes sure that the head hardness is correct and updates the head position
        robotbody.set_head_hardness(0.95)
        set_head_position(self.wanted_head_position)
        
        print("following the ball")
        
    def update(self):
        
        #Tests if the robot has fallen
        if has_fallen():
            return "fallen"
        
        #Stores the current time for tests and updates
        self.current_time=time.time()
        
        #Tests if the robot has lost the ball
        if self.has_lost_ball():
                print("lost ball")
                return "lost ball"
        
        #Test if the robot is standing in front of the ball
        self.distance_to_ball=distance_to_ball()
        
        if self.distance_to_ball>0 and self.distance_to_ball<self.distance:
            robotbody.set_eyes_led(0, 31, 0)
            print ("standing in front of ball")
            return "done"
        
        #Updates the position of the head
        self.update_head_position()
        
        #Updates the walking direction
        self.update_walk_direction()
        
    def exit(self):
        walk.set_velocity(-0.001, 0, 0)
    
    #Methods used by the FSM
    
    #The test that decides if it has lost the ball
    #and a test that updates the lost ball timer if it has a new observation
    def has_lost_ball(self):
        if self.current_time>=self.lost_ball_timer:
            robotbody.set_eyes_led(31, 0, 0)
            return True
        
        elif vision.has_new_ball_observation():
            self.lost_ball_timer=self.current_time+5
            return False
        
        else:
            return False
    
    #Updates the position of the head to look at the ball
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
    
    #Updates the walking direction if it isn't close to the direction of the ball
    def update_walk_direction(self):
        
        current_head_position = robotbody.get_head_position()
        
        if not like(current_head_position[0],0,pi/18):
            walk.set_velocity(self.speed,0.025,current_head_position[0])
                
        else:
            walk.set_velocity(self.speed, 0, 0)


""" A state that makes the robot stand after it has fallen """

class GetUp:
        
    def entry (self):
        #Reset the variables since the last use of the state and
        #sets the eyes to a fancy red colour
        robotbody.set_eyes_led(31, 0, 0)
        self.sitting=False
        self.start_time=None
        
        #Starts the get up motion
        motion.get_up()
    
    def update (self):
        #If the robot is sitting and the timer hasn't started
        #it's time for the robot to stand up and start the timer
        if self.sitting and not self.start_time:
            self.start_time=time.time()
            motion.stand_still()
            
        #Tests if the robot is sitting or standing by checking the
        #angle of the IMU. In not it starts the motion to enter a sitting position
        if like(imu.get_angle()[1],0.01):
            self.sitting=True
        
        #Test if the robot is finished with the motions
        if self.start_time and time.time()>self.start_time+1:
            return "done"
    
    def exit (self):
        print ("sitting")
        motion.start_walk()
        robotbody.set_eyes_led(0, 0, 31)
        


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