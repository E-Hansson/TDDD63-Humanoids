# Some help functions for the robot

from math import fabs,pi,tan
from Robot.Interface import robotbody
from Robot.Interface.Sensors import imu,vision
from Robot.Util import robotid


#sets head position, protects from twist
def set_head_position(head_position):
    if head_position[0] > pi/3:
        head_position[0] = pi/3
    elif head_position[0] < -pi/3:
        head_position[0] = -pi/3
        
    if head_position[1] > pi/8:
        head_position[1] = pi/8
    elif head_position[1] < -0.8:
        head_position[1] = -0.8
        
    robotbody.set_head_position_list(head_position)

"""        Written by Erik            """

#Returns the distance to the ball
#Uses a walking robot as 1 unit length
def distance_to_ball():
    
    return tan(pi/2-ball_angle()[1])

# Returns the angles to the goal in relation to imu
def goal_angle():
    
    last_goal = vision.get_goal()
    goal = vision.Goal(last_goal.x,last_goal.y,last_goal.z,last_goal.t,robotid.get_team_number())
    angles=goal.get_angle()
    return angles


# Returns the angles to the ball in relation to imu
def ball_angle():
    
    last_ball = vision.get_ball()
    ball = vision.Ball(last_ball.x,last_ball.y,last_ball.t)
    angles=list(ball.get_angle())
    return angles

# Checks if the robot has fallen
def has_fallen():
    
    if like(imu.get_angle()[1],-pi/2,pi/4) or like(imu.get_angle()[1],pi/2,pi/4)\
        or like(imu.get_angle()[0],-pi/2,pi/4) or like(imu.get_angle()[0],pi/2,pi/4):
        return True
    else:
        return False


#Compares two values to evaluate whether they're
#close enough to be counted as the same
def like (a,b,tolerance=0.1):
    
    alike=True
    if isinstance(a, tuple) or isinstance(a,list):
        for i in range(len(a)):
            if not fabs(a[i]-b[i])<=tolerance:
                alike = False
                break
    
    elif not fabs(a-b)<=tolerance:
        alike = False
    
    return alike
    

#A function to set the left arms position
#in relation to the body or the ground
def set_left_arm_position (x,y,z,relative="body"):
    if relative=="body":
        robotbody.set_left_arm_position(x,y,z)
        return (x,y,z)
        
    elif relative=="ground":
        x-=imu.get_angle()[1]
        robotbody.set_left_arm_position(x,y,z)
        return (x,y,z)
        

#A function to set the right arms position
#in relation to the body or the ground
def set_right_arm_position (x,y,z,relative="body"):
    if relative=="body":
        robotbody.set_right_arm_position(x,y,z)
        return (x,y,z)
        
    elif relative=="ground":
        x-=imu.get_angle()[1]
        print(x)
        robotbody.set_right_arm_position(x,y,z)
        return (x,y,z)
        

#A function to get the left arms position
#in relation to the body or the ground
def get_left_arm_position (relative="body"):
    if relative=="body":
        return robotbody.get_left_arm_position()
    
    elif relative=="ground":
        return (robotbody.get_left_arm_position()[0]+imu.get_angle()[1],robotbody.get_left_arm_position()[1],robotbody.get_left_arm_position()[2])
   
   
#A function to get the right arms position
#in relation to the body or the ground 
def get_right_arm_position (relative="body"):
    if relative=="body":
        return robotbody.get_right_arm_position()
    
    elif relative=="ground":
        return (robotbody.get_right_arm_position()[0]+imu.get_angle()[1],robotbody.get_right_arm_position()[1],robotbody.get_right_arm_position()[2])

