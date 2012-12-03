from Robot.StateMachines import general_fsm
import states_for_darwin
from math import pi
import states_for_darwin 

""" 

    Still needs to be done:
    *Calibration of the goal finding state
    *Calibration of the lining up state
    *Calibration of the find middle of goal states
    *Test if it is possible to remove the _one_step_forward state
    and replace it by setting it's input to the _stand_in_front_of_ball state
    *Test if it works without the initiate walking state
    *Make the robot check so that it is still in posession of the ball
    *Make the robot turn right if the ball leaves to the right while tracking
    *The same as above but for left.
    
"""

class Program(general_fsm.StateMachine):
    def __init__(self):
        
        """        Create our states_for_darwin        """
        
        """ Pure movement states """
        _stand_still = states_for_darwin.StandStill()
        _walk_straight = states_for_darwin.WalkSpeed(3)
        _after_kick_walk = states_for_darwin.WalkSpeed(15)
        #_initiate_walking = states_for_darwin.WalkSpeed(3,0)
        

        """ ball interaction states"""
        _follow_ball = states_for_darwin.FollowBall()
        _stand_in_front_of_ball = states_for_darwin.FollowBall(2.1)
        _one_step_forward = states_for_darwin.FollowBall(pi,True)
        
        _finding_the_goal = states_for_darwin.CrudeGoalAdjusting(1)
        
        _kick_ball = states_for_darwin.KickBall()
        _circle_away_from_own_goal = states_for_darwin.CircleBall()
        
        
        """ Tracking states """
        
        _track_ball = states_for_darwin.TrackBall()


        """ goal interaction states """
        _check_team_goal = states_for_darwin.CheckTeam()
        _center_goal = states_for_darwin.FindMiddleOfGoal()
        _line_up_shot = states_for_darwin.LineUpShot()
        
        """ system states """
        _terminate = states_for_darwin.Exit()
        _get_up = states_for_darwin.GetUp()
        
        # Initiate the StateMachine, and give it an initial state 
        #super(Program, self).__init__(_stand_still)
        super(Program, self).__init__(_stand_still)
        
        
        """        Adding the states_for_darwin        """
        
        """ pure motion states """
        self.add_state(_stand_still)
        self.add_state(_walk_straight)
        #self.add_state(_initiate_walk)
        self.add_state(_one_step_forward)
        self.add_state(_after_kick_walk)
        
        """ ball interaction states """
        self.add_state(_follow_ball)
        self.add_state(_finding_the_goal)
        self.add_state(_kick_ball)
        self.add_state(_stand_in_front_of_ball)
        self.add_state(_circle_away_from_own_goal)
        
        """ Tracking states """
        self.add_state(_track_ball)
        
        """ goal interaction states """
        self.add_state(_center_goal)
        self.add_state(_line_up_shot)
        self.add_state(_check_team_goal)
        
        """ system states """
        self.add_state(_terminate)
        self.add_state(_get_up)

        
        """        Adding transitions between states_for_darwin        """
        
        """ if everything goes well transitions """
        #self.add_transition(_stand_still,"timeout",_initiate_walking)
        #self.add_transition(_initiate_walking, "timeout", _track_ball)
        self.add_transition(_stand_still, "timeout", _track_ball)
        self.add_transition(_track_ball,"done",_follow_ball)
        self.add_transition(_follow_ball, "done", _finding_the_goal)

        self.add_transition(_finding_the_goal, "done", _center_goal)
        self.add_transition(_finding_the_goal, "fail", _stand_in_front_of_ball)
        
        self.add_transition(_center_goal, "fail", _center_goal)
        self.add_transition(_center_goal, "focus middle", _line_up_shot)
        self.add_transition(_center_goal, "focus one",_check_team_goal)
        
        self.add_transition(_line_up_shot, "check again", _center_goal)
        self.add_transition(_line_up_shot, "lined up", _check_team_goal)
        
        self.add_transition(_check_team_goal, "fire", _stand_in_front_of_ball)
        self.add_transition(_stand_in_front_of_ball, "done", _one_step_forward)
        self.add_transition(_one_step_forward, "done", _kick_ball)
        self.add_transition(_kick_ball, "done", _after_kick_walk)
        self.add_transition(_after_kick_walk, "timeout", _track_ball)
        
        self.add_transition(_check_team_goal, "turn", _circle_away_from_own_goal)
        self.add_transition(_circle_away_from_own_goal, "done", _stand_in_front_of_ball)
        
        
        self.add_transition(_walk_straight, "timeout", _track_ball)

        """ Lost ball transitions """
        self.add_transition(_follow_ball, "no ball", _track_ball)
        self.add_transition(_stand_in_front_of_ball, "no ball", _track_ball)
        self.add_transition(_line_up_shot, "lost ball", _track_ball)
        self.add_transition(_one_step_forward, "no ball", _track_ball)
        self.add_transition(_track_ball, "out of sight", _walk_straight)


        """ Falling transitions """
        self.add_transition(_circle_away_from_own_goal, "fallen", _get_up)
        self.add_transition(_one_step_forward, "fallen", _get_up)
        self.add_transition(_check_team_goal, "fallen", _get_up)
        self.add_transition(_kick_ball, "fallen", _get_up)
        self.add_transition(_line_up_shot, "fallen", _line_up_shot)
        self.add_transition(_finding_the_goal, "fallen", _get_up)
        self.add_transition(_stand_in_front_of_ball, "fallen", _get_up)
        self.add_transition(_track_ball, "fallen", _get_up)
        self.add_transition(_follow_ball, "fallen", _get_up)
        self.add_transition(_stand_still, "fallen", _get_up)
        #self.add_transition(_initiate_walking, "fallen", _get_up)
        self.add_transition(_walk_straight, "fallen", _get_up)
        self.add_transition(_get_up, "done", _stand_still)