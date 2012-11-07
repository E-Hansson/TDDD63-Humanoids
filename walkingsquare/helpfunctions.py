'''
Created on Nov 1, 2012

@author: grupp 2
'''

from math import fabs,pi
from Robot.Interface import robotbody
from Robot.Interface.Sensors import imu


"""        Written by Erik            """

def has_fallen():
    
    if like(imu.get_angle()[1],-pi/2) or like(imu.get_angle()[1],pi/2):
        return True
    else:
        return False


#Compares two values to evaluate whether they're
#close enough to be counted as the same
def like (a,b,tolerance=0.1):
    
    if fabs(a-b)<=tolerance:
        return True
    
    else:
        return False
    
    
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

