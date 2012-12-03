from Robot.Interface.Sensors import imu, vision
from Robot.Interface import robotbody
from Robot.Actions import motion, walk, kick
from Robot.Util import robotid
from help_functions import *
from math import pi, fabs, tan

import time

"""        General motion states        """
    

class CircleBall:
    
    def entry(self):
        self.wanted_rotation=pi
        walk.set_velocity(0, 0, 0)
        self.rotation_progress = 0
        self.const_forward_velocity=0.02
        self.forward_velocity=0
        
        self.wanted_head_position=[0,pi/8]
        set_head_position(self.wanted_head_position)
        
        self.start_time = time.time()
        self.time = 13
        
    def update(self):
        if has_fallen():
            return "fallen"
        
        
        self.set_new_head_position()
        if distance_to_ball() > 1.5:
            self.forward_velocity = self.const_forward_velocity;
        else:
                self.forward_velocity = 0
        
                walk.set_velocity(self.forward_velocity, 0.4, self.wanted_head_position[0]*1.2)
                self.rotation_progress -= self.wanted_head_position[0]/12
        
        if time.time() > self.start_time + self.time:
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
        
class CrudeGoalAdjusting:
    
    def __init__(self,direction):
        self.direction=direction
        self.forward_velocity=0
        self.const_forward_velocity=0.01
        
        #Turning timers
        self.time = 26
        
    def entry(self):
        print("Crude")
        #HeadTimers
        self.max_angle_timer=pi/8
        self.min_angle_timer=-pi/9
        self.timer=time.time()
        self.up_and_down="up"
        
        #Turning timers
        self.start_time = self.timer
        
    def update(self):
        
        if has_fallen():
            return "fallen"
        if vision.has_new_goal_observation():
            if like(goal_angle()[0],0):
                print("found goal")
                return "done"

        
        self.update_head_position()
        
        if distance_to_ball() > pi*3:
            self.forward_velocity = self.const_forward_velocity;
        else:
            self.forward_velocity = 0
        
        walk.set_velocity(self.forward_velocity, 0.4*self.direction, ball_angle()[0]*1.2)
        
        if time.time() > self.start_time + self.time:
            print("aiming away from our goal")
            return "fail"
        
    def exit(self):
        pass
        
    def update_head_position(self):
        self.current_time=time.time()
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


#A Simple state to kick the ball, wait some time for the robot to regain it's football
class KickBall:
    
    def entry(self):
        print ("kicking the ball")
        self.time=6
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
                   # if self.ball_angle>0:
                   #     kick.forward_left()
                   # else:
                    kick.forward_right()
        
        if self.start_time and time.time()>self.time+self.start_time:
            return "done"
        
    
    def exit(self):
        print ("kicked the ball")
    

class FaceBall:
    
    def entry(self):
        print("facing the ball")
        self.last_ball_angle=ball_angle()[0]
        
        if self.last_ball_angle<0:
            walk.set_velocity(0, -0.4, self.last_ball_angle)
        else:
            walk.set_velocity(0, 0.4, self.last_ball_angle)
    
    def update(self):
        if has_fallen():
            return "fallen"
        if like(ball_angle()[0],0):
            return "done"
        
    def exit(self):
        print("standing in front of ball")
        

#A class which follows the ball and stops when the angle of the head is close enough
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
                walk.set_velocity(self.speed, 0, 0)
                robotbody.set_eyes_led(31, 0, 0)
                print("lost ball")
                return "no ball"
    
        self.current_head_position = robotbody.get_head_position()
        
        self.update_head_position()
           
        self.last_observation_of_ball=time.time()
        self.last_distance=distance_to_ball()
            
        if self.last_distance>0 and self.last_distance<self.distance:
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
        if time.time() > self.start_time + self.time:
            return "timeout"
    def exit(self):
        print("Exit still")
        motion.start_walk()
        

#A state to get the robot to stand up after falling
class GetUp:
        
    def entry (self):
        motion.get_up()
    
    def update (self):
        if like(imu.get_angle()[1],0.001):
            return ("done")
    
    def exit (self):
        print("sitting")
        

"""        Walking states        """


class StartWalk:
    
    def __init__(self,speed):
        self.speed=speed
        
    def entry(self):
        print("start walking")
        walk.walk_forward(self.speed)
        
    def update(self):
        if has_fallen():
            return "fallen"
        return "done"
    
    def exit(self):
        print ("walking at speed "+str(self.speed))
        
class WalkStraight:
    """The robot walks forward some time"""

    def __init__(self, time):
        self.time = time
    def entry(self):
        print("Entry walk")
        self.start_time = time.time()

        walk.walk_forward(0.02)

    def update(self):
        if has_fallen():
            return "fallen"
        if time.time() > self.start_time + self.time:
            return "timeout"
    def exit(self):
        print("Exit walk")
        

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


"""        Direction states        """

class CheckTeam:
    
    def entry(self):
        print ("checking which goal")
        self.wanted_head_position=[0,0]
        set_head_position(self.wanted_head_position)
        self.team_id=robotid.get_team_number()
        self.first_turn=True
        
    def update(self):
        self.current_head_position=robotbody.get_head_position()[0]
        if has_fallen():
            return "fallen"
        
        
        if vision.has_new_goal_observation():
            if self.opponents_goal():
                print("fire at opponents goal")
                return "fire"
            else:
                print ("turning towards opponents goal")
                return "turn"
        
            self.update_head_position()
        
        if like(self.current_head_position,pi/3):
            return "fire"
        
    def exit(self):
        pass
    
    def opponents_goal(self):
        goal_team_number = vision.get_goal().team
        return not self.team_id==goal_team_number
    
    def update_head_position(self):
        if like(self.wanted_head_position[0],self.current_head_position):
            if like(self.current_head_position,-pi/3):
                self.wanted_head_position[0]=pi/18
                self.first_turn=False
            elif self.first_turn:
                self.wanted_head_position[0]-=pi/18
            else:
                self.wanted_head_position[0]+=pi/18
            
            set_head_position(self.wanted_head_position)
        
            
class LineUpShot:
    
    def entry(self):
        print("lining up...")
        robotbody.set_head_hardness(0.95)
        self.goal_angle=robotbody.get_head_position()[0]
        
        self.wanted_head_position=[self.goal_angle,pi/8]
        set_head_position(self.wanted_head_position)
        
        self.timer=None
        self.lost_ball_timer=time.time()+10
        
        self.first_ball_angle=None
        self.last_ball_angle=None
        
    def update(self):
        
        self.current_time=time.time()
        
        if has_fallen():
            return "fallen"
        
        if self.current_time>=self.lost_ball_timer:
            print ("lost ball")
            return "lost ball"
        
        if self.timer and self.current_time>self.timer:
            return "check again"
        
        if not self.timer:
            if vision.has_new_ball_observation():
                self.first_ball_angle=ball_angle()[0]
                self.last_ball_angle=self.first_ball_angle
                self.timer=time.time()+fabs(self.first_ball_angle)*100
                self.lost_ball_timer=self.current_time+10
        
        else:
            if like(self.first_ball_angle,self.goal_angle,pi/9):
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
"""

Sets the head position to face the middle of the goal if it can find two pillars within 180 degrees.
Sets the head position to one of the pillar if it can only find one.
Otherwise calls it a fail.
"""

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
                return "focus one"
            
            elif len(self.angles)==0:
                if vision.has_new_goal_observation():
                    self.get_goal_observation()
                    self.searching_for_next()
                    print("got first observation")
                    
                elif like(self.current_head_position[0],pi/2):
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

#A State to find the goal
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
                self.wanted_head_position[1]=pi/8
                self.left_or_right="left"
            else:
                self.wanted_head_position[0]=-(self.current_time-self.timer)
            
        set_head_position(self.wanted_head_position)

class Turn:
    """The robot turns for some timyawyawe"""
    
    def __init__(self,time):
        self.time = time
        self.number_of_turns = 0
    def entry(self):
        print("Entry turn")
        self.start_time = time.time()
        self.number_of_turns += 1
        walk.turn_left(0.4)
    def update(self):
        if has_fallen():
            return "fallen"
        if self.number_of_turns == 4:
            return "complete"
        if time.time() > self.start_time + self.time:
            return "done"
        
    def exit(self):
        print("Exit turn")


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


"""        Arm states        """

class MoveArm:
    """ a state to make the robot lift the right arm """
    
    def __init__ (self,arm,angle=(0,0,0),relation="body"):
        self.relation=relation
        self.angle=angle
        self.arm=arm
        self.init_angle=angle
        
    def entry (self):
        print("moving "+self.arm+" arm")
        if self.arm=="right":
            self.angle=set_right_arm_position(self.init_angle[0],self.init_angle[1],self.init_angle[2],self.relation)
        
        elif self.arm=="left":
            self.angle=set_left_arm_position(self.init_angle[0],self.init_angle[1],self.init_angle[2],self.relation)
    
    def update (self):
        if has_fallen():
            return "fallen"
        if self.arm=="right" and like(get_right_arm_position()[0],self.angle[0]):
            return "done"
        
        elif self.arm=="left" and like(get_left_arm_position()[0],self.angle[0]):
            return "done"
        
    def exit (self):
        print ("done")
        

"""        Eye states        """

class SetEyeColor:
    """ Sets the Eye color of the robot"""
    
    def __init__(self,red,green,blue):
        self.color=(red,green,blue)
        print ("Changing eye color")
        
    def entry(self):
        robotbody.set_eyes_led(self.color[0],self.color[1],self.color[2])

    def update(self):
        if has_fallen():
            return "fallen"
        else:
            return "done"
        
    def exit(self):
        print("terminating")
        
        
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