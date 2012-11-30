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
        
        self.wanted_head_position=[0,pi/4.5]
        set_head_position(self.wanted_head_position)
        
        self.start_time = time.time()
        self.time = 8
        
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
            if current_ball_angle[1]>pi/4.5:
                self.wanted_head_position[1]=pi/4.5
            else:
                self.wanted_head_position[1]=current_ball_angle[1]
        
            self.wanted_head_position[0]=current_ball_angle[0]
            set_head_position(self.wanted_head_position)
        
class CrudeGoalAdjusting:
    
    def __init__(self,intervall,head_start,head_end,circle_direction,start_with_turn=False):
        self.rotation_intervall = intervall
        self.head_start = head_start
        self.head_end = head_end
        self.circle_direction = circle_direction
        self.start_with_turn=start_with_turn
    
    def entry(self):
        print("Circle this little bitch!")
        robotbody.set_head_hardness(0.95)
        
        walk.set_velocity(0, 0, 0)
        self.forward_velocity = 0
        self.const_forward_velocity = 0.02
        self.wanted_rotation = pi/2
        self.rotation_progress = 0
        self.start_time = time.time()
        self.time = 2
          
        self.head_ball = [0, pi/4.5]
        self.wanted_head_position = list(self.head_start)
        self.looking_for_goal = not self.start_with_turn
        set_head_position(self.head_start)
        
    def update(self):
        self.head_position = robotbody.get_head_position()
        if has_fallen():
            return "fallen"
        
        if(self.looking_for_goal):
            if vision.has_new_goal_observation():
                
                self.set_new_adjusting()
                self.set_new_head_position()
                print("Adjust " + self.adjust_direction)
                return "adjust " + self.adjust_direction

            self.update_head_position()
        else:
            self.set_new_head_position()
            
            if distance_to_ball() > pi/3.8:
                self.forward_velocity = self.const_forward_velocity;
            else:
                    self.forward_velocity = 0
        
            walk.set_velocity(self.forward_velocity, 0.4*self.circle_direction, self.wanted_head_position[0]*1.2)
            self.rotation_progress -= self.wanted_head_position[0]/7.3
        
            if time.time() > self.start_time + self.time:
                self.init_goal_check()
        
    def exit(self):
        print("Rotation done")
        
    def set_new_adjusting(self):
        temp_goal_angles=goal_angle()
        if not like(temp_goal_angles[0],0,pi/36):
            if temp_goal_angles[0] < 0:
                self.adjust_direction = "left"
            else:
                self.adjust_direction = "right"
                        
        elif self.circle_direction==1:
            self.adjust_direction = "right"
                    
        else:
            self.adjust_direction = "left"

    def set_wanted_rotation(self, rotation_intervall):
        self.rotation_intervall = rotation_intervall
        
    def init_goal_check(self):
        self.looking_for_goal = True
        self.rotation_progress = 0
        walk.set_velocity(0, 0, 0)
        set_head_position(self.head_start)
        self.wanted_head_position = [self.head_start[0],self.head_start[1]]
                    
    def update_head_position(self):
        if like(self.head_position,self.head_end):
            self.looking_for_goal = False
            self.wanted_head_position = self.head_ball
        else:
            if like(self.wanted_head_position,self.head_position):
                self.wanted_head_position[0] -= pi/16

        set_head_position(self.wanted_head_position)
        
    def set_new_head_position(self):
        current_ball_angle=ball_angle()
        if current_ball_angle[1]>pi/4.5:
            self.wanted_head_position[1]=pi/4.5
        else:
            self.wanted_head_position[1]=current_ball_angle[1]
        
        self.wanted_head_position[0]=current_ball_angle[0]
        set_head_position(self.wanted_head_position)

#A Simple state to kick the ball, wait some time for the robot to regain it's football
class KickBall:
    
    def entry(self):
        print ("kicking the ball")
        self.time=6
        self.wanted_head_position=[0,pi/4.5]
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
    
    def __init__(self,distance=pi/4,look_down=False):
        self.distance=distance
        self.speed=0.02
        self.last_distance=1000
        self.look_down=look_down
        
    #FSM methods
    def entry(self):
        print("following the ball")
        robotbody.set_head_hardness(0.95)
        self.last_observation_of_ball=-1
        if self.look_down:
            self.wanted_head_position=[0,pi/4.5]
        else:
            self.wanted_head_position=robotbody.get_head_position()
        
        set_head_position(self.wanted_head_position)
        
    def update(self):
        if has_fallen():
            return "fallen"
        
        if not vision.has_new_ball_observation():
            if self.last_observation_of_ball+5<time.time() or self.last_distance>=tan(5*pi/12):
                walk.set_velocity(self.speed, 0, 0)
                robotbody.set_eyes_led(31, 0, 0)
                print("lost ball")
                return "no ball"
        else:
            self.current_head_position = robotbody.get_head_position()
            if like(self.current_head_position,self.wanted_head_position):
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
        
        if angles[1]>pi/4.5:
            self.wanted_head_position[1]=pi/4.5
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
        robotbody.set_body_hardness(0.95)
        self.goal_angle=robotbody.get_head_position()[0]
        self.wanted_head_position=[self.goal_angle,pi/4.5]
        set_head_position(self.wanted_head_position)
        self.timer=0
        self.lost_ball_timer=None
        self.first_ball_angle=None
        self.last_ball_angle=None
        
    def update(self):
        self.current_head_position=robotbody.get_head_position()
        if has_fallen():
            return "fallen"
        
        if like(self.current_head_position,self.wanted_head_position):
            
            if self.timer and time.time()>self.timer:
                return "check again"
            else:
                if vision.has_new_ball_observation():
                    self.lost_ball_timer=time.time()+5
            
                elif self.lost_ball_timer and self.lost_ball_timer<time.time():
                    return "lost ball"
                
                if not self.first_ball_angle:
                    self.first_ball_angle=ball_angle()[0]
                    self.last_ball_angle=self.first_ball_angle
                    self.timer=time.time()+fabs(self.first_ball_angle)*10
                    
                else:
                    self.update_head_position()
                    
                if like(self.last_ball_angle,self.goal_angle,pi/9):
                    walk.set_velocity(0, 0, 0)
                    print ("lined up")
                    return "lined up"
            
                if self.first_ball_angle<0:
                    walk.set_velocity(0, -0.4, self.last_ball_angle)
                else:
                    walk.set_velocity(0, 0.4, self.last_ball_angle)
        
    def exit(self):
        pass

    def update_head_position(self):
        temp_ball_angles=ball_angle()
        
        if temp_ball_angles[1]>pi/4.5:
            #Tuples are immutable
            #temp_ball_angles[1]=pi/4.5
            temp_ball_angles = (temp_ball_angles[0],pi/4.5)
            
        
        if temp_ball_angles[0]>pi/3:
            temp_ball_angles[0]=pi/3
            temp_ball_angles = (pi/3,temp_ball_angles[1])
        elif temp_ball_angles[0]<-pi/3:
            temp_ball_angles = (-pi/3,temp_ball_angles[1])
        
        self.last_ball_angle=temp_ball_angles[0]
        set_head_position(temp_ball_angles)


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
class TrackGoal:
    
    def __init__(self, circle_ball):
        self.circle_ball = circle_ball
    
    def entry(self):
        print ("Tracking goal")
        robotbody.set_head_hardness(0.95)
        set_head_position([pi/2,-pi/8])
        self.wanted_head_position = [pi/2,-pi/8]
        self.start_angle = imu.get_angle()[2]
        self.angle=2*pi
        self.rotated=0 
    
    def update(self):
        head_position=robotbody.get_head_position()
        if has_fallen():
            return "fallen"
        
        self.wanted_head_position[0] -= pi/16
        set_head_position(self.wanted_head_position)
        
        if head_position[0] <= pi/2:
            self.wanted_head_position = [0,pi/3]
            set_head_position(self.wanted_head_position)  
        
        
        if vision.has_new_goal_observation():
            angles=goal_angle()
            set_head_position(list(angles))     
            head_position = robotbody.get_head_position()
            
            walk.turn_left(0)
            print(head_position[0])
            self.circle_ball.set_wanted_rotation(self.rotated+head_position[0])
            return "done"
        
        if imu.get_angle()[2] > self.start_angle + self.angle:
            return "no goal found"
    
    def exit(self):
        set_head_position([0,0])
        print ("exit goal tracking")


#A State to find the ball on the field
class TrackBall:
    
        
    def entry(self):
        print ("Tracking ball")
        robotbody.set_head_hardness(0.95)
        self.wanted_head_position=robotbody.get_head_position()
        self.start_angle = imu.get_angle()[2]
        self.angle=2*pi
        
        walk.turn_left(0.2)
        set_head_position(self.wanted_head_position)
        
    def update(self):     
        head_position=robotbody.get_head_position()
        if has_fallen():
            return "fallen"
        if like(head_position,self.wanted_head_position,0.2):
            if like(head_position,[pi/3,0]):
                self.wanted_head_position=[-pi/3,pi/4.5]
        
            elif like(head_position[0],pi/3):
                self.wanted_head_position=[-pi/3,0]
        
            else:
                self.wanted_head_position[0]=head_position[0]+pi/15
            
            set_head_position(self.wanted_head_position)
            
        
        if vision.has_new_ball_observation():
            walk.turn_left(0)
            robotbody.set_eyes_led(0, 31, 0)
            return "done"
        
        if imu.get_angle()[2] > self.start_angle + self.angle:
            robotbody.set_eyes_led(31,0,0)
            return "out of sight"
        
    def exit (self):
        set_head_position([0,0])
        print ("exit ball tracking")
    

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