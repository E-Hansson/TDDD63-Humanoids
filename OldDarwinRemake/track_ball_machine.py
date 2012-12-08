from Robot.StateMachines import general_fsm
import track_ball_states
from help_functions import has_fallen

class Program(general_fsm.StateMachine):
    def __init__(self):
        
        """        Create our states        """
        
        _track_ball_left = track_ball_states.TrackBall("left")
        _track_ball_right = track_ball_states.TrackBall("right")
        _track_direction = track_ball_states.TrackDirection()
        
        _walk_straight = track_ball_states.WalkSpeed(3)
        
        self._done=track_ball_states.Done()
        
        super(Program, self).__init__(_track_direction)
        
        """        Adding the states        """
        self.add_state(self._done)
        self.add_state(_walk_straight)
        self.add_state(_track_ball_left)
        self.add_state(_track_ball_right)
        self.add_state(_track_direction)
        
        """        Adding the transitions    """
        self.add_transition(_track_ball_left, "out of sight", _walk_straight)
        self.add_transition(_track_ball_right, "out of sight", _walk_straight)
        self.add_transition(_track_direction, "right", _track_ball_right)
        self.add_transition(_track_direction, "left", _track_ball_left)
        self.add_transition(_walk_straight, "timeout", _track_direction)
        
        self.add_transition(_track_ball_right, "done", self._done)
        self.add_transition(_track_ball_left, "done", self._done)
        
    def update(self):
        #Test if the robot has fallen
        if has_fallen():
            return "fallen"
        
        #Tests if the track ball machine is in the done state
        if self.get_state()==self._done:
            return "done"
        
        #Updates the track ball machine
        super(Program,self).update()