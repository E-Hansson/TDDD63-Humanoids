# Some help functions for the robot

from math import fabs,pi,tan
from Robot.Interface import robotbody
from Robot.Interface.Sensors import imu,vision
from Robot.Util import robotid

""" Written by Gustaf """

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
def goal_angle_and_type():
    
    #Goal types
    #0 unknown post
    #1 left post
    #2 right post
    #3 whole goal
    
    last_goal = vision.get_goal()
    goal = vision.Goal(last_goal.x,last_goal.y,last_goal.z,last_goal.t,robotid.get_team_number(),last_goal.goal_type)
    angles=goal.get_angle()[0]
    return angles,last_goal.goal_type


# Returns the angles to the ball in relation to imu
def ball_angle():
    
    last_ball = vision.get_ball()
    ball = vision.Ball(last_ball.x,last_ball.y,last_ball.t)
    angles=ball.get_angle()
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