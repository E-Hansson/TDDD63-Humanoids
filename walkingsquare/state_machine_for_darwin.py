from Robot.StateMachines import general_fsm
import states_for_darwin
from math import pi
import states_for_darwin 

class Program(general_fsm.StateMachine):
    def __init__(self):
        #self.robocom = "http://192.168.0.5:5000/"
        """        Create our states_for_darwin        """
        
        """ movement states_for_darwin """
        _stand_still = states_for_darwin.StandStill()
        _walk_straight = states_for_darwin.WalkSpeed(3)
        _initiate_walking = states_for_darwin.WalkSpeed(3,0)
        _one_step_forward = states_for_darwin.FollowBall(pi,True)

        """ ball interaction states_for_darwin"""
        _follow_ball = states_for_darwin.FollowBall()
        _circle_ball_left = states_for_darwin.CrudeGoalAdjusting(1)
        _track_ball = states_for_darwin.TrackBall()
        _stand_in_front_of_ball = states_for_darwin.FollowBall(2.1)
        _kick_ball = states_for_darwin.KickBall()
        _circle_away_from_own_goal = states_for_darwin.CircleBall()
        
        """ goal interaction states_for_darwin"""
        _center_goal = states_for_darwin.FindMiddleOfGoal()
        _line_up_shot = states_for_darwin.LineUpShot()
        _check_team_goal = states_for_darwin.CheckTeam()
        
        """ system states_for_darwin """
        _terminate = states_for_darwin.Exit()
        _get_up = states_for_darwin.GetUp()
        
        # Initiate the StateMachine, and give it an initial state 
        #super(Program, self).__init__(_stand_still)
        super(Program, self).__init__(_stand_still)
        
        
        """        Adding the states_for_darwin        """
        
        """ motion states_for_darwin """
        self.add_state(_stand_still)
        self.add_state(_walk_straight)
        self.add_state(_initiate_walking)
        self.add_state(_one_step_forward)
        
        """ball interaction states_for_darwin"""
        self.add_state(_follow_ball)
        self.add_state(_circle_ball_left)
        self.add_state(_kick_ball)
        self.add_state(_stand_in_front_of_ball)
        self.add_state(_circle_away_from_own_goal)
        
        """goal interaction states_for_darwin"""
        self.add_state(_center_goal)
        self.add_state(_line_up_shot)
        
        """ system states_for_darwin """
        self.add_state(_terminate)
        self.add_state(_get_up)
        
        self.add_state(_track_ball)
        
        """        Adding transitions between states_for_darwin        """
        
        """ motion transitions """
        
        self.add_transition(_stand_still,"timeout",_initiate_walking)
        self.add_transition(_initiate_walking, "timeout", _track_ball)
        self.add_transition(_track_ball,"done",_follow_ball)
        self.add_transition(_follow_ball, "done", _circle_ball_left)

        self.add_transition(_circle_ball_left, "done", _center_goal)
        self.add_transition(_circle_ball_left, "fail", _stand_in_front_of_ball)
        
        self.add_transition(_center_goal, "fail", _center_goal)
        self.add_transition(_center_goal, "focus middle", _line_up_shot)
        self.add_transition(_center_goal, "focus one",_check_team_goal)
        
        self.add_transition(_line_up_shot, "check again", _center_goal)
        self.add_transition(_line_up_shot, "lined up", _check_team_goal)
        
        self.add_transition(_check_team_goal, "fire", _stand_in_front_of_ball)
        self.add_transition(_stand_in_front_of_ball, "done", _one_step_forward)
        self.add_transition(_one_step_forward, "done", _kick_ball)
        self.add_transition(_kick_ball, "done", _track_ball)
        
        self.add_transition(_check_team_goal, "turn", _circle_away_from_own_goal)
        self.add_transition(_circle_away_from_own_goal, "done", _stand_in_front_of_ball)
        
        
        self.add_transition(_walk_straight, "timeout", _track_ball)

        """ track transitions """
        self.add_transition(_follow_ball, "no ball", _track_ball)
        self.add_transition(_stand_in_front_of_ball, "no ball", _track_ball)
        self.add_transition(_line_up_shot, "lost ball", _track_ball)
        self.add_transition(_one_step_forward, "no ball", _track_ball)
        
        self.add_transition(_track_ball, "out of sight", _walk_straight)


        """ error transitions """
        self.add_transition(_circle_away_from_own_goal, "fallen", _get_up)
        self.add_transition(_one_step_forward, "fallen", _get_up)
        self.add_transition(_check_team_goal, "fallen", _get_up)
        self.add_transition(_kick_ball, "fallen", _get_up)
        self.add_transition(_line_up_shot, "fallen", _line_up_shot)
        self.add_transition(_circle_ball_left, "fallen", _get_up)
        self.add_transition(_stand_in_front_of_ball, "fallen", _get_up)
        self.add_transition(_track_ball, "fallen", _get_up)
        self.add_transition(_follow_ball, "fallen", _get_up)
        self.add_transition(_stand_still, "fallen", _get_up)
        self.add_transition(_initiate_walking, "fallen", _get_up)
        self.add_transition(_walk_straight, "fallen", _get_up)
        self.add_transition(_get_up, "done", _stand_still)