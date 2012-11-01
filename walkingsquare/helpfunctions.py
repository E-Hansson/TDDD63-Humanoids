'''
Created on Nov 1, 2012

@author: grupp2
'''

from math import fabs

def like (a,b,tolerance=0.0001):
    
    if fabs(a-b)<=tolerance:
        return True
    
    else:
        return False