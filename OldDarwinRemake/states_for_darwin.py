from Robot.Interface.Sensors import imu, vision
from Robot.Interface import robotbody
from Robot.Actions import motion, walk, kick
from Robot.Util import robotid
from help_functions import set_head_position, like, goal_angle_and_type, has_fallen, distance_to_ball, ball_angle
from math import pi
import time


""" A state to adjust robot to face the goal with the ball between them.
    There will be four different results of the state
    since there are four different types of goal Darwin can recognize.
    1. Found the whole goal --> facing the whole goal
    2. Found the right post --> facing a bit left of the right post
    3. Found the left post --> facing a bit right of the left post
    4. Found an unknown post while the head was high --> facing the unknown post """
    
class GoalAdjusting:
    
    def __init__(self):
        #How long time it will take to circle roughly one complete turn around the ball
        self.max_circling_time=30
        
        #Forward/backward speed that will be used to avoid walking into the ball while turning around it
        self.forward_speed=0.01
        self.backward_speed=-0.01
        
        #How fast the robot will circle around the ball
        self.circling_speed=0.02
        
        #How fast the robot will turn its head (higher is fasater)
        self.head_turning_speed=2
        
        #The maximum angle the robot will turn its head
        self.max_angle=-0.799
        self.min_angle=pi/8
        
        #The how long time it will take to move the head to the right position
        self.max_angle_timer=self.min_angle/self.head_turning_speed
        self.min_angle_timer=self.max_angle/self.head_turning_speed
        
        #The allowed angle diff for looking at an unknown post
        self.allowed_angle_diff=pi/36
        
        #The allowed angle diff for looking at the middle of the goal
        self.to_big_angle=pi/18
        
    def entry(self):
        #saves the current time
        self.current_time=time.time()
        
        #Starts the turning timer
        self.start_time=self.current_time
        
        #Resets the control variable if it has turned one complete circle
        self.one_turn=False
        
        #Starts the head timer
        self.timer=self.current_time
        
        #Starts the adjustment timer
        self.adjustment_timer=None
        
        #Starts the unknown counter
        self.counter=0
        
        #Starts the counter for how many times it has changed circling speed
        self.changed_speed=False
        
        #Sets current speed
        self.current_forward_speed=0
        self.current_circling_speed=self.circling_speed
        
        #Starts lost ball timer
        self.lost_ball_timer=self.current_time+7
        
        #Resets the up and down variable
        self.up_and_down="down"
        
        #String for print statement, which goal
        self.which_goal_type=""
        
        #Resets the goal angle and goal type
        self.goal_angle=None
        self.goal_type=None
        
        #Adjusting
        self.adjusting=False
        
        print("looking for goal")
        
    def update(self):
        
        #Tests if it has fallen
        if has_fallen():
            return "fallen"
        
        #Stores current time
        self.current_time=time.time()
        
        #Stores whether it has found a new ball observation
        self.has_new_ball_observation=vision.has_new_ball_observation()
        
        #Stores whether it has found a new goal observation
        self.has_new_goal_observation=vision.has_new_goal_observation()
        
        #Stores the distance to the ball
        self.distance_to_ball=distance_to_ball()
        
        #Stores the new angle and type if it has new observation of the goal
        if self.has_new_goal_observation:
            self.goal_angle,self.goal_type=goal_angle_and_type()
        
        #Tests if it has lost the ball
        if self.has_lost_ball() or self.to_long_distance():
            print ("lost the ball")
            return "lost ball"
        
        #Tests the adjustment timer
        if self.adjustment_timer and self.current_time>=self.adjustment_timer:
            robotbody.set_eyes_led(0, 31, 0)
            print("probably looking at goal")
            return "done"
        
        #Test if it has found a goal post
        if (self.has_new_goal_observation and self.looking_at_goal())\
            or self.changed_speed and self.current_time>self.start_time:
            robotbody.set_eyes_led(0, 31, 0)
            print("found goal, " + self.which_goal_type)
            return "done"
        
        #Tests if it is time to abandon the search for a goal
        if self.current_time > self.start_time + self.max_circling_time:
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
        
    #Tests for looking at the goal
    def looking_at_goal(self):
        
        print (str(self.goal_type)+"         :        "+str(self.goal_angle))
        
        if self.goal_type==3:
            
            if like(self.goal_angle,0,self.to_big_angle):
                self.which_goal_type="middle"
                return True
            
            elif not self.adjusting and self.goal_angle>0:
                self.adjustment_timer=self.goal_angle*15/pi
                self.current_circling_speed=self.circling_speed
                self.adjusting=True
                return False
            
            elif self.goal_angle<0:
                self.adjustment_timer=-self.goal_angle*15/pi
                self.current_circling_speed=-self.circling_speed
                self.adjusting=True
                return False
                

        elif self.goal_type==2:
            if self.goal_angle<-self.allowed_angle_diff and self.goal_angle>-pi/6:
                self.which_goal_type="right"
                return True
            
            elif not self.adjusting and self.goal_angle>-self.allowed_angle_diff:
                self.adjustment_timer=self.current_time+abs(self.allowed_angle_diff+self.goal_angle)*15/pi
                self.current_circling_speed=self.circling_speed
                self.adjusting=True
                return False
            
            elif not self.adjusting and self.goal_angle<-pi/6:
                self.adjustment_timer=self.current_time+(-self.goal_angle-self.allowed_angle_diff)*15/pi
                self.current_circling_speed=-self.circling_speed
                self.adjusting=True
                return False
        
        elif self.goal_type==1:
            if self.goal_angle>self.allowed_angle_diff and self.goal_angle<pi/6:
                self.which_goal_type="left"
                return True
            
            elif not self.adjusting and self.goal_angle<self.allowed_angle_diff:
                self.adjustment_timer=self.current_time+(self.allowed_angle_diff-self.goal_angle)*15/pi
                self.current_circling_speed=-self.circling_speed
                self.adjusting=True
                return False
            
            elif not self.adjusting and self.goal_angle>pi/6:
                self.adjustment_timer=self.current_time+(self.goal_angle-self.allowed_angle_diff)*15/pi
                self.current_circling_speed=self.circling_speed
                self.adjusting=True
                return False
        
        elif self.goal_type==0:
            if like(self.goal_angle,0,pi/36):
                self.counter+=1
                
            if not self.adjusting and self.counter>=10:
                if like(self.goal_angle,0,self.allowed_angle_diff):
                    self.which_goal_type="unknown"
                    return True
            
                elif not self.adjusting and self.goal_angle>0:
                    self.adjustment_timer=self.goal_angle*15/pi
                    self.current_circling_speed=self.circling_speed
                    self.adjusting=True
                    return False
                
                elif self.goal_angle<0:
                    self.adjustment_timer=-self.goal_angle*15/pi
                    self.current_circling_speed=-self.circling_speed
                    self.adjusting=True
                    return False
            else:
                return False
        
        else:
            return False
    
    #Updates the head with the current time as a parameter
    def update_head_position(self):
        if self.up_and_down=="down":
            if self.current_time>=self.timer+self.max_angle_timer:
                self.timer=self.current_time+self.max_angle_timer
                self.up_and_down="up"
            
            else: 
                set_head_position([0,self.head_turning_speed*(self.current_time-self.timer)])
        
        else:
            if self.current_time>=self.timer-self.min_angle_timer:
                self.timer=self.current_time-self.min_angle_timer
                self.up_and_down="down"
            else:    
                set_head_position([0,self.head_turning_speed*(self.timer-self.current_time)])
    
    #A simple calculation of the angle the robot has,
    #needed since we are calculating everything with the time.
    def head_height(self):
        if self.up_and_down=="down":
            return self.head_turning_speed*(self.current_time-self.timer)
        else:
            return self.head_turning_speed*(self.timer-self.current_time)
                
    #A method that updates which forward speed the robot should use
    #depending on the distance to the ball
    def update_speed(self):
        if self.distance_to_ball> pi*3:
            self.current_forward_speed = self.forward_speed
        elif self.distance_to_ball< pi and self.distance_to_ball>0:
            self.current_forward_speed = self.backward_speed
        else:
            self.current_forward_speed = 0
        
        #Updates the circling direction if it finds that it's looking to the right of the right post
        #or if it looks to the left of the left post
        if self.has_new_goal_observation:
            
            if self.goal_type==1 and self.goal_angle<0 and\
                self.current_circling_speed==-self.circling_speed:
                
                self.current_circling_speed=self.circling_speed
                self.changed_speed=True
                self.start_time=self.current_time+2
            
            elif self.goal_type==2 and self.goal_angle>0 and\
                self.current_circling_speed==self.circling_speed:
                
                self.current_circling_speed=-self.circling_speed
                self.changed_speed=True
                self.start_time=self.current_time+2
                
        #Sets the new walk instructions
        walk.set_velocity(self.current_forward_speed, self.current_circling_speed, ball_angle()[0])
        
        
    #The test that decides if it has lost the ball
    #and a test that updates the lost ball timer if it has a new observation
    def has_lost_ball(self):
        if self.current_time>=self.lost_ball_timer:
            robotbody.set_eyes_led(31, 0, 0)
            return True
        
        if self.has_new_ball_observation:
            self.lost_ball_timer=self.current_time+7
        return False
    
    #A test if the ball is to far away.
    #Note that if self.distance_to_ball has a value lower than 0 it is really far away
    #since the distance is calculated with the use of the heads tilt angle and tan.
    def to_long_distance(self):
        return self.distance_to_ball<0 or self.distance_to_ball>20
    

""" A State that will make the robot move sideways until the ball is in front of its left foot.
    After that it will kick the ball.
    Note that it only uses the left fot since the config for the kick with the right foot
    isn't working. """

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
        
        #If the ball is to the right of the left foot
        if self.ball_angle<0.1:
            walk.set_velocity(0, -0.01, 0)
        
        #If the ball is to the left of the left foot 
        elif self.ball_angle>0.47:
            walk.set_velocity(0, 0.01, 0)
            
        #Else it will stop, look up, start the timer since the last kick
        #and kick with the foot that has the ball in front of it.
        else:
            walk.set_velocity(0, 0, 0)
            set_head_position([0,0])
            self.time_since_kick = time.time()
            kick.forward_left()
         
         
""" This state will make the robot walk forward until it's close to the ball,
    or if it has lost it. """
    
class WalkSpeed:

    def __init__(self):
        #initiates the constant variables
        self.speed = 0.01
        
        #How close will it walk to the ball
        self.distance_to_ball=2.05
        
    def entry(self):
        #Sets the eyes to a fancy blue
        robotbody.set_eyes_led(0, 0, 31)

        #Starts walking forward with the given speed
        walk.walk_forward(self.speed)
        
        #Sets the head position down to the ground
        set_head_position([0,pi/8])
        
        #How long it will wait until it has concluded that it has lost the ball
        self.lost_ball_timer=time.time()+2
        
        print("See the robot walk")

    def update(self):
        
        #Tests if it has fallen
        if has_fallen():
            return "fallen"
        
        #Stores the current time for further tests
        self.current_time=time.time()
        
        #Updates the lost ball timer if it has a new ball observation
        if vision.has_new_ball_observation():
            self.lost_ball_timer=self.current_time+2
        
        #Test if it has lost the ball
        elif self.current_time>self.lost_ball_timer:
            return "lost ball"
        
        #Test if it is close enought to the ball
        if distance_to_ball()<=self.distance_to_ball:
            return "done"
        
    def exit(self):
        print("Exit walk")
        
        
""" Circles approximately, due to the unsteady walking, 180 degrees around the ball """

class CircleBall:
    
    def __init__(self):
        #setting a few standard variables that will be the same all the time
        self.circling_velocity=0.2
        self.const_forward_velocity=0.01
    
    def entry(self):
        #Reseting the forward velocity from the last time the state was used
        self.forward_velocity=0
        
        #Updating the head position so that DARwIn will look down at the ball
        self.wanted_head_position=[0,pi/8]
        set_head_position(self.wanted_head_position)
        
        #Starting the sideways walk
        walk.set_velocity(self.forward_velocity, self.circling_velocity, ball_angle()[0])
        
        #Starting the turning timer
        self.start_time = time.time()
        self.time = 10
        
        #starting the lost ball timer
        self.lost_ball_timer=time.time()+4

        
        print ("Turning away from our goal")
        
    def update(self):
        #Testing if it has fallen
        if has_fallen():
            return "fallen"
        
        #Storing the current time for the update
        self.current_time=time.time()
        
        #Testing if it has lost the ball
        if self.has_lost_ball():
            print ("lost the ball")
            return "lost ball"
        
        #Test if it has finished it's turn
        if self.current_time > self.start_time + self.time:
            print("aiming away from our goal")
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
            self.lost_ball_timer=self.current_time+7
            return False
        
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
    

""" The robot follows the ball until it's close enough.
    Standard value for how close it will go is two times pi.
    However, the distance is an optional input as well as
    the option to force the robot to look at the ground """

class FollowBall:
    
    def __init__(self,distance=3,look_down=False):
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
        pass
    
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
        
        self.wanted_head_position[0]=angles[0]
        
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
        #Tests if the robot has fallen
        if has_fallen():
            return "fallen"
        
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