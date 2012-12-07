from Robot.StateMachines import general_fsm
import states_for_darwin
import goal_finding_machine
import track_ball_states


class Program(general_fsm.StateMachine):
    def __init__(self):
        
        """        Create our states        """

        """ ball interaction states"""
        _follow_ball = states_for_darwin.FollowBall()
        _stand_in_front_of_ball = states_for_darwin.FollowBall(2,True)
        
        _kick_ball = states_for_darwin.KickBall()
        
        
        """ Tracking states """
        
        _track_ball=track_ball_states.Program()


        """ goal interaction states """
        _finding_the_goal = goal_finding_machine.Program()
        
        """ system states """
        _get_up = states_for_darwin.GetUp()
        

        super(Program, self).__init__(_get_up)
        
        """        Adding the darwin        """
        
        """ ball interaction states """
        self.add_state(_follow_ball)
        self.add_state(_kick_ball)
        self.add_state(_stand_in_front_of_ball)
        
        """ Tracking states """
        self.add_state(_track_ball)
        
        """ goal interaction states """
        self.add_state(_finding_the_goal)
        
        """ system states """
        self.add_state(_get_up)

        
        """        Adding transitions between darwin        """
        
        """ if everything goes well transitions """
        self.add_transition(_follow_ball, "done", _finding_the_goal)
        self.add_transition(_finding_the_goal, "done", _stand_in_front_of_ball)
        self.add_transition(_stand_in_front_of_ball, "done", _kick_ball)
        self.add_transition(_kick_ball, "done", _track_ball)
        
        """ Lost ball transitions """
        self.add_transition(_follow_ball, "lost ball",_track_ball)
        self.add_transition(_stand_in_front_of_ball, "lost ball", _track_ball)
        self.add_transition(_finding_the_goal, "lost ball", _track_ball)

        """ Falling transitions """
        self.add_transition(_follow_ball, "fallen", _get_up)
        self.add_transition(_stand_in_front_of_ball, "fallen", _get_up)
        self.add_transition(_finding_the_goal, "fallen", _get_up)
        self.add_transition(_kick_ball, "fallen", _get_up)
        self.add_transition(_track_ball, "fallen", _get_up)
        self.add_transition(_get_up, "done", _track_ball)