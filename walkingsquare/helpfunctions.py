'''
Created on Nov 1, 2012

@author: grupp2
'''

from math import fabs
from Robot.Interface import robotbody
from Robot.Interface.Sensors import imu

def like (a,b,tolerance=0.0001):
    
    if fabs(a-b)<=tolerance:
        return True
    
    else:
        return False
    
def set_left_arm_position (x,y,z,relative="body"):
    if relative=="body":
        robotbody.set_left_arm_position(x,y,z)
    
    elif relative=="ground":
        robotbody.set_left_arm_position(x-imu.get_angle()[1],y,z)

def set_right_arm_position (x,y,z,relative="body"):
    if relative=="body":
        robotbody.set_right_arm_position(x,y,z)
    
    elif relative=="ground":
        robotbody.set_right_arm_position(x-imu.get_angle()[1],y,z)

def get_left_arm_position (relative="body"):
    if relative=="body":
        return robotbody.get_left_arm_position()
    
    elif relative=="ground":
        return (robotbody.get_left_arm_position()[0]-imu.get_angle()[1],robotbody.get_left_arm_position()[1],robotbody.get_left_arm_position()[2])
    
def get_right_arm_position (relative="body"):
    if relative=="body":
        return robotbody.get_right_arm_position()
    
    elif relative=="ground":
        return (robotbody.get_right_arm_position()[0]-imu.get_angle()[0],robotbody.get_right_arm_position(),robotbody.get_right_arm_position())

 