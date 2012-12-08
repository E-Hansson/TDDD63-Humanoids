from Robot.StateMachines import general_fsm
import states_for_darwin
import track_ball_machine

class Program(general_fsm.StateMachine):
    def __init__(self):
        
        """        Create our states        """
        

        """ ball interaction states"""
        _follow_ball = states_for_darwin.FollowBall()
        _stand_in_front_of_ball = states_for_darwin.WalkSpeed()
        _kick_ball = states_for_darwin.KickBall()
        
        """ Tracking states """
        _track_ball_machine = track_ball_machine.Program()

        """ goal interaction states """
        _check_team_goal = states_for_darwin.CheckTeam()
        _aim_at_goal = states_for_darwin.GoalAdjusting()
        _circle_away_from_own_goal = states_for_darwin.CircleBall()
        
        """ system states """
        _get_up = states_for_darwin.GetUp()
        
        super(Program, self).__init__(_get_up)
        
        """        Adding the darwin        """
        
        
        """ ball interaction states """
        self.add_state(_follow_ball)
        self.add_state(_kick_ball)
        self.add_state(_stand_in_front_of_ball)
        self.add_state(_circle_away_from_own_goal)
        
        """ Tracking states """
        self.add_state(_track_ball_machine)
        
        """ goal interaction states """
        self.add_state(_check_team_goal)
        self.add_state(_aim_at_goal)
        
        """ system states """
        self.add_state(_get_up)

        
        """        Adding transitions between darwin        """
        
        """ if everything goes well transitions """
        self.add_transition(_track_ball_machine,"done",_follow_ball)
        self.add_transition(_follow_ball, "done", _aim_at_goal)
        self.add_transition(_aim_at_goal, "done", _check_team_goal)
        
        self.add_transition(_aim_at_goal, "fail", _stand_in_front_of_ball)
        
        self.add_transition(_check_team_goal, "fire", _stand_in_front_of_ball)
        self.add_transition(_stand_in_front_of_ball, "done", _kick_ball)
        self.add_transition(_kick_ball, "done", _track_ball_machine)
        
        self.add_transition(_check_team_goal, "turn", _circle_away_from_own_goal)
        self.add_transition(_circle_away_from_own_goal, "done", _stand_in_front_of_ball)
        

        """ Lost ball transitions """
        self.add_transition(_aim_at_goal, "lost ball", _track_ball_machine)
        self.add_transition(_follow_ball, "lost ball", _track_ball_machine)
        self.add_transition(_stand_in_front_of_ball, "lost ball", _track_ball_machine)
        self.add_transition(_circle_away_from_own_goal, "lost ball", _track_ball_machine)


        """ Falling transitions """
        
        self.add_transition(_aim_at_goal, "fallen", _get_up)
        self.add_transition(_follow_ball, "fallen", _get_up)
        self.add_transition(_stand_in_front_of_ball, "fallen", _get_up)
        self.add_transition(_kick_ball, "fallen", _get_up)
        self.add_transition(_circle_away_from_own_goal, "fallen", _get_up)
        self.add_transition(_track_ball_machine, "fallen", _get_up)
        self.add_transition(_check_team_goal, "fallen", _get_up)
        self.add_transition(_get_up, "done", _track_ball_machine)