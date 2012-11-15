# FSM for the goal keeper

from Robot.StateMachines import general_fsm
from goal_keeper_states import *

class Program (general_fsm.StateMachine):
    
    def __init__(self):
        