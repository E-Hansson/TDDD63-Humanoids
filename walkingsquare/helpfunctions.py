# Some helpfunctions for the robot

from math import fabs,pi
from Robot.Interface import robotbody
from Robot.Interface.Sensors import imu
from Robot.Actions import walk


"""        Written by Erik            """

def has_fallen():
    
    if like(imu.get_angle()[1],-pi/2) or like(imu.get_angle()[1],pi/2):
        return True
    else:
        return False


#Compares two values to evaluate whether they're
#close enough to be counted as the same
def like (a,b,tolerance=0.1):
    
    alike=True
    if isinstance(a, tuple):
        for i in range(len(a)):
            if not fabs(a[i]-b[i])<=tolerance:
                alike = False
                break
    
    elif not fabs(a-b)<=tolerance:
        alike = False
    
    return alike
    
    
#Not needed since get_angles from ball object seems to return relative to imu and not head
def set_head_position(x,y):
    head_position = robotbody.get_head_position()
    new_head_position =(head_position[0] + x, head_position[1] + y)
    robotbody.set_head_position(new_head_position[0], new_head_position[1])
    return new_head_position
    
    
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

