from Robot.StateMachines import general_fsm
import states_for_darwin

""" 

    Still needs to be done:
    *Calibration of the goal finding state
    *Calibration of the lining up state
    *Calibration of the find middle of goal states
    
"""

class Program(general_fsm.StateMachine):
    def __init__(self):
        
        """        Create our states        """
        
        """ Pure movement states """
        _walk_straight = states_for_darwin.WalkSpeed(3)
        

        """ ball interaction states"""
        _follow_ball = states_for_darwin.FollowBall()
        _stand_in_front_of_ball = states_for_darwin.FollowBall(2,True)
        
        _finding_the_goal = states_for_darwin.CrudeGoalAdjusting(1)
        
        _kick_ball = states_for_darwin.KickBall()
        _circle_away_from_own_goal = states_for_darwin.CircleBall()
        
        
        """ Tracking states """
        
        _track_ball_left = states_for_darwin.TrackBall("left")
        _track_ball_right = states_for_darwin.TrackBall("right")
        _track_direction = states_for_darwin.TrackDirection()


        """ goal interaction states """
        _check_team_goal = states_for_darwin.CheckTeam()
        _center_goal = states_for_darwin.FindMiddleOfGoal()
        _line_up_shot = states_for_darwin.LineUpShot()
        
        """ system states """
        _get_up = states_for_darwin.GetUp()
        

        super(Program, self).__init__(_get_up)
        
        """        Adding the darwin        """
        
        """ pure motion states """
        self.add_state(_walk_straight)
        
        """ ball interaction states """
        self.add_state(_follow_ball)
        self.add_state(_finding_the_goal)
        self.add_state(_kick_ball)
        self.add_state(_stand_in_front_of_ball)
        self.add_state(_circle_away_from_own_goal)
        
        """ Tracking states """
        self.add_state(_track_ball_left)
        self.add_state(_track_ball_right)
        self.add_state(_track_direction)
        
        """ goal interaction states """
        self.add_state(_center_goal)
        self.add_state(_line_up_shot)
        self.add_state(_check_team_goal)
        
        """ system states """
        self.add_state(_get_up)

        
        """        Adding transitions between darwin        """
        
        """ if everything goes well transitions """
        self.add_transition(_track_ball_left,"done",_follow_ball)
        self.add_transition(_track_ball_right, "done", _follow_ball)
        self.add_transition(_follow_ball, "done", _finding_the_goal)

        self.add_transition(_finding_the_goal, "done", _center_goal)
        self.add_transition(_finding_the_goal, "fail", _stand_in_front_of_ball)
        
        self.add_transition(_center_goal, "fail", _finding_the_goal)
        self.add_transition(_center_goal, "focus middle", _line_up_shot)
        self.add_transition(_center_goal, "focus one",_check_team_goal)
        
        self.add_transition(_line_up_shot, "check again", _center_goal)
        self.add_transition(_line_up_shot, "lined up", _check_team_goal)
        
        self.add_transition(_check_team_goal, "fire", _stand_in_front_of_ball)
        self.add_transition(_stand_in_front_of_ball, "done", _kick_ball)
        self.add_transition(_kick_ball, "done", _track_direction)
        
        self.add_transition(_check_team_goal, "turn", _circle_away_from_own_goal)
        self.add_transition(_circle_away_from_own_goal, "done", _stand_in_front_of_ball)
        
        
        self.add_transition(_walk_straight, "timeout", _track_direction)

        """ Lost ball transitions """
        self.add_transition(_follow_ball, "lost ball", _track_direction)
        self.add_transition(_stand_in_front_of_ball, "lost ball", _track_direction)
        self.add_transition(_line_up_shot, "lost ball", _track_direction)
        self.add_transition(_circle_away_from_own_goal, "lost ball", _track_direction)
        self.add_transition(_finding_the_goal, "lost ball", _track_direction)
        self.add_transition(_track_ball_left, "out of sight", _walk_straight)
        self.add_transition(_track_ball_right, "out of sight", _walk_straight)
        
        self.add_transition(_track_direction, "right", _track_ball_right)
        self.add_transition(_track_direction, "left", _track_ball_left)


        """ Falling transitions """
        self.add_transition(_walk_straight, "fallen", _get_up)
        self.add_transition(_follow_ball, "fallen", _get_up)
        self.add_transition(_stand_in_front_of_ball, "fallen", _get_up)
        self.add_transition(_finding_the_goal, "fallen", _get_up)
        self.add_transition(_kick_ball, "fallen", _get_up)
        self.add_transition(_circle_away_from_own_goal, "fallen", _get_up)
        self.add_transition(_track_ball_left, "fallen", _get_up)
        self.add_transition(_track_ball_right, "fallen", _get_up)
        self.add_transition(_check_team_goal, "fallen", _get_up)
        self.add_transition(_center_goal, "fallen", _get_up)
        self.add_transition(_line_up_shot, "fallen", _get_up)
        self.add_transition(_get_up, "done", _track_ball_left)