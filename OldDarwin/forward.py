# Code for controlling the forward(s)


from Robot.StateMachines import general_fsm
from math import pi
import states


class Program (general_fsm.StateMachine):
    
    def __init__(self):
        
        """     Create the states       """
        
        
        """ vision states """
        
        
        """ movement states """
        _stand_still = states.StandStill()
        
        """ misc states """
        
        
        """ error states """
        _get_up = states.GetUp
        
        #Initiation of the statemachine
        super(Program, self).__init__(_stand_still)
        
        
        """     Adding the states       """
        
        
        """ vision states """
        
        
        """ movement states """
        self.add_state(_stand_still)
                
        """ misc states """
        
        
        """ error states """
        self.add_state(_get_up)
        
        """     Transitions     """
        
        """ vision transition """
        
        
        """ movement transition """
        
        
        """ misc transition """
        
        
        """ error transition """
        # Transitions when the robot has fallen
        self.add_transition(_get_up, "sitting", _stand_still)
        self.add_transition(_stand_still, "fallen", _get_up)