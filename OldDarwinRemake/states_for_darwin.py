from Robot.Interface.Sensors import imu, vision
from Robot.Interface import robotbody
from Robot.Actions import motion, walk, kick
from Robot.Util import robotid
from help_functions import *
from math import pi, fabs

import time
    

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
            

""" Searches for a goal while walking in a circle around the ball
    If no goal has been found during, approximately, 360 degrees
    it kicks the ball anyhow wishing for the best outcome """

class CrudeGoalAdjusting:
    
    def __init__(self,direction):
        #Initiates the constant variables
        self.direction=direction
        self.forward_velocity=0
        self.const_forward_velocity=0.01
        self.constant_circling_speed=0.1
        self.slow_circling_speed=0.02
        self.max_angle_timer=pi/8
        self.min_angle_timer=-0.733
        self.alowed_angled_diff=pi/90
        self.slow_down_time=pi/45
        
        #Turning timers
        self.time = 40
        
    def entry(self):
        #Reseting the variables from the last use of the state:
        
        #Head timers
        self.timer=time.time()
        self.up_and_down="up"
        
        #Turning timer
        self.start_time = self.timer
        
        #Circling speed
        self.circling_velocity=self.constant_circling_speed
        
        #Lost ball timer
        self.lost_ball_timer=self.timer+7
        
        print("Looking for a goal")
        
    def update(self):
        
        #Test if the robot has fallen
        if has_fallen():
            return "fallen"
        
        #Stores the current time for further tests
        self.current_time=time.time()
        
        #Stores whether it have found a new ball observation
        self.has_new_ball_observation=vision.has_new_ball_observation()
        
        self.has_new_goal_observation=vision.has_new_goal_observation()
        
        #Stores the current distance to the ball for further tests
        self.distance_to_ball=distance_to_ball()
        
        #Tests if it has lost the ball
        if self.has_lost_ball() or self.to_long_distance():
            print ("lost the ball")
            return "lost ball"
        
        #Test if it has found a goal post
        if self.has_new_goal_observation:
            if like(goal_angle()[0],0,self.alowed_angled_diff):
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
    
    #Updates the head position by the use of the current time, the max and min angles.
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
    
    #The test that decides if it has lost the ball
    #and a test that updates the lost ball timer if it has a new observation
    def has_lost_ball(self):
        if self.current_time>=self.lost_ball_timer:
            robotbody.set_eyes_led(31, 0, 0)
            return True
        
        if self.has_new_ball_observation:
            self.lost_ball_timer=self.current_time+7
        
        return False
    
    #A method that updates which forward speed the robot should use
    #depending on the distance to the ball
    def update_speed(self):
        if self.distance_to_ball> pi*3:
            self.forward_velocity = self.const_forward_velocity;
        elif self.distance_to_ball< pi and self.distance_to_ball>0:
            self.forward_velocity = -self.const_forward_velocity
        else:
            self.forward_velocity = 0
        
        if like(goal_angle()[0],0,self.slow_down_time):
            self.circling_velocity=self.slow_circling_speed
            self.timer=self.current_time+20
            
        walk.set_velocity(self.forward_velocity, self.circling_velocity, ball_angle()[0])
        
    def to_long_distance(self):
        
        return self.distance_to_ball>20


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
        if like(self.ball_angle,0):
            walk.set_velocity(0, 0.4, 0)
            
        #Else it will stop, look up, start the timer since the last kick
        #and kick with the foot that has the ball in front of it.
        else:
            walk.set_velocity(0, 0, 0)
            set_head_position([0,0])
            self.time_since_kick = time.time()
            if self.ball_angle>0:
                kick.forward_left()
            else:
                kick.forward_right()
    

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
        
        #Tests if the robot has fallen
        if has_fallen():
            return "fallen"
        #Tests if it is time to stop walking
        
        if time.time() > self.start_time + self.time:
            return "timeout"
        
    def exit(self):
        print("Exit walk")


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
    

""" The robot adjust it's position around the ball so that the ball is between the robot
    and the middle of the goal """
            
class LineUpShot:
    
    def entry(self):
        #Resets all the variables for the last use of the state
        #The movement timer
        self.timer=None
        
        #The last and first angle to the ball
        self.first_ball_angle=None
        self.last_ball_angle=None
        
        #The lost ball timer
        self.lost_ball_timer=time.time()+7
        
        #Makes sure that the head hardness is right and sets the
        #wanted head position to the same as last by looking down at the ball
        robotbody.set_head_hardness(0.95)
        self.goal_angle=robotbody.get_head_position()[0]
        self.wanted_head_position=[self.goal_angle,pi/8]
        set_head_position(self.wanted_head_position)
        
        #Makes the robot stand still since it shouldn't move during while looking
        walk.set_velocity(0,0,0)
        
        print("lining up...")
        
    def update(self):
        
        #Tests if the robot has fallen
        if has_fallen():
            return "fallen"
        
        #Stores the value if the robot has a new ball observation for further use
        self.has_new_ball_observation=vision.has_new_ball_observation()
        
        #Stores the current time for further tests
        self.current_time=time.time()
        
        #Tests if the robot has lost the ball
        if self.has_lost_ball():
                print("lost ball")
                return "lost ball"
        
        #Tests if it has finished moving,
        #if the robot already has decided that it had to move
        if self.timer and self.current_time>self.timer:
            robotbody.set_eyes_led(0, 0, 31)
            return "check again"
        
        #If the timer has not started yet.
        #The robot looks for the first ball observation.
        #If it finds one it starts the timer and stores the angles.
        if not self.timer:
            if self.has_new_ball_observation:
                self.start_timer()
        
        else:
            #If the difference between the goal angle and the first ball angle is less
            #then 20 degrees it will tell that it has lined up
            #Otherwise it will start to turn around the ball for some time,
            #depending on the difference
            if like(self.first_ball_angle,self.goal_angle,pi/9):
                robotbody.set_eyes_led(0, 31, 0)
                print("lined up")
                return "lined up"
            
            self.start_turning()
        
            
    def exit(self):
        pass
        
    #Starts the timer and stores the first ball angles
    #Also updates the lost ball timer
    def start_timer(self):
        self.first_ball_angle=ball_angle()[0]
        self.timer=self.current_time+20*fabs(self.first_ball_angle)/(2*pi)
        self.lost_ball_timer=self.current_time+7
    
    #Starts the turning or updates the turning depending on if it has
    #already been started
    def start_turning(self):
        
        #Updates the head position
        self.last_ball_angle=ball_angle()
        set_head_position(self.last_ball_angle)
        
        #Updates the walking
        if self.first_ball_angle<0:
            walk.set_velocity(0, -0.2, self.last_ball_angle[0])
        else:
            walk.set_velocity(0, 0.2, self.last_ball_angle[0])
        
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


""" Sets the head position to face the middle of the goal,
    if it can find two pillars within 180 degrees.
    Sets the head position to one of the pillar if it only can find one.
    Otherwise calls it a fail. 
    Note that this state would be a lot better if it was implemented as
    a state machine. """

class FindMiddleOfGoal:
    
    """FSM methods"""
    
    def entry(self):
        #Resets all the variables:
        
        #The wanted head position
        self.wanted_head_position=[-pi/3,-0.733]
        
        #The angles it has found to the goal
        self.angles=[]
        
        #The fail timer
        self.fail_timer=time.time()+7
        
        #A couple of boolean variables to help the robot
        #through the different states of finding the two goal post
        self.ending=False
        self.failing=False
        
        #Makes sure that the head hardness is right and
        #updates the position of the head
        robotbody.set_head_hardness(0.95)  
        set_head_position(self.wanted_head_position)
        
        #Sets the walk speed to the actually zero
        walk.set_velocity(0, 0, 0)

        print ("searching for goal")
        
    def update(self): 
             
        #Tests if the robot has fallen
        if has_fallen():
            return "fallen"
        
        #Stores the if it has a new goal observation for further tests
        self.has_new_goal_observation=vision.has_new_goal_observation()
        
        #Stores the current head position for further tests
        self.current_head_position=robotbody.get_head_position()[0]
        
        self.current_time=time.time()
        
        #If the timer has run out or if the robot has failed to find a goal post
        #it leaves the state depending with a few commands.
        if self.fail_timer<=self.current_time or self.failing:
            
            #If it's not failing it knows that it have found at least one goal post
            #Then it will update the fail timer so that it has time enough to move
            #its head towards that direction
            if not self.failing:
                self.failing=True
                self.fail_timer=self.current_time+1
            
            #If the timer has run out it's time to leave the state
            if self.fail_timer<=self.current_time:
                if len(self.angles)==0:
                    robotbody.set_eyes_led(31, 0, 0)
                    print("fail")
                    return "fail"
                elif len(self.angles)==1:
                    robotbody.set_eyes_led(0, 31, 0)
                    return "focus one"
                else:
                    self.focus_middle()
                    robotbody.set_eyes_led(0, 31, 0)
                    print("focus middle")
                    return "focus middle"
                
            #If the timer hasn't run out it should focus on whatever it has found
            else:
                self.focus_on_results()
        else:
            
            #Tests if it is time to end with only one goal post found
            if self.ending and like(self.current_head_position,self.angles[0][0]):
                robotbody.set_eyes_led(0, 31, 0)
                return "focus one"
        
            #Tests if it has found two goal posts
            if len(self.angles)==2 and \
                like(self.current_head_position,(self.angles[0][0]+self.angles[1][0])/2):
                robotbody.set_eyes_led(0, 31, 0)
                print("focus middle")
                return "focus middle"
        
            #Updates the head position, variables, depending on how many goal post it has found
            if not self.ending and like(self.current_head_position,self.wanted_head_position[0],pi/45):
                self.update_values()
    
    def exit(self):
        pass
    
    
    """ Other methods """
    
    #Gets the latest goal observation if
    #they aren't the same as the previous observation.
    def get_goal_observation(self):
        
        temp_angles=list(goal_angle())
        
        if len(self.angles)==0 or not like(temp_angles,self.angles[0]):
            self.angles.append(temp_angles)
        
        else:
            self.focus_one()
            self.failing=True
            self.fail_timer=self.current_time+1
            
    #Sets the head to search for the next goal post
    #by moving the head from left to right instead of right to left.
    def searching_for_next(self):
        self.wanted_head_position=[pi/3,-0.733]
        set_head_position(self.wanted_head_position)
    
    #Sets the head position to the middle of the two goal post it has found
    def focus_middle(self):
        self.wanted_head_position=[(self.angles[0][0]+self.angles[1][0])/2,0]
        set_head_position(self.wanted_head_position)
    
    #Sets the head position to the goal post it has found   
    def focus_one(self):
        self.wanted_head_position=list(self.angles[0])
        set_head_position(self.wanted_head_position)
        
    #Sets the next head position for the robot while it searches for a goal post
    def set_next_head_position(self):
        if len(self.angles)==0:
            if like(self.current_head_position,pi/3,pi/45):
                self.ending=True
            else:
                self.wanted_head_position[0]+=pi/30
        else:
            if like(self.current_head_position,pi/3,pi/45):
                self.ending=True
            else:
                self.wanted_head_position[0]-=pi/30
        set_head_position(self.wanted_head_position)
    
    #Sets the focus on the results depending on how many goal post
    #the robot has found
    def focus_on_results(self):
        if len(self.angles)==1:
            self.focus_one()
        elif len(self.angles)==2:
            self.focus_middle()
    
    #Updates all the values depending on how many goal post the robot has found
    def update_values(self):
        
        #If it haven't found the first goal post
        if len(self.angles)==0:
            if self.has_new_goal_observation:
                self.get_goal_observation()
                self.searching_for_next()
                self.fail_timer=time.time()+2
                print("got first observation")

            else:
                self.set_next_head_position()
        
        #If it already has found one goal post
        elif len(self.angles)==1:
            if self.has_new_goal_observation:
                print ("hej")
                self.get_goal_observation()
                if len(self.angles)==2:
                    self.focus_middle()
                    print("got second observation")
                #If it has made two different observation of goal post and they are the same
                #it will conclude that it was unable to find the second.
                else:
                    self.ending=True
                    
            else:
                self.set_next_head_position()


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
        
        #Tests if the robot has fallen
        if has_fallen():
            return "fallen"
        
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