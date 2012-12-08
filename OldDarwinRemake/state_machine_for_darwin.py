from Robot.StateMachines import general_fsm
import states_for_darwin
import track_ball_machine
import erik_test_states

""" 

    Still needs to be done:
    *Calibration of the goal finding state
    *Calibration of the lining up state
    *Calibration of the find middle of goal states
    
"""

class Program(general_fsm.StateMachine):
    def __init__(self):
        
        """        Create our states        """
        

        """ ball interaction states"""
        _follow_ball = states_for_darwin.FollowBall()
        _stand_in_front_of_ball = erik_test_states.WalkSpeed()
        
        _finding_the_goal = states_for_darwin.CrudeGoalAdjusting(1)
        
        _kick_ball = erik_test_states.KickBall()
        _circle_away_from_own_goal = states_for_darwin.CircleBall()
        
        _aim_at_goal = erik_test_states.GoalAdjusting()
        
        """ Tracking states """
        
        _track_ball_machine = track_ball_machine.Program()


        """ goal interaction states """
        _check_team_goal = states_for_darwin.CheckTeam()
        _center_goal = states_for_darwin.FindMiddleOfGoal()
        _line_up_shot = states_for_darwin.LineUpShot()
        
        """ system states """
        _get_up = states_for_darwin.GetUp()
        

        super(Program, self).__init__(_get_up)
        
        """        Adding the darwin        """
        
        
        """ ball interaction states """
        self.add_state(_follow_ball)
        self.add_state(_finding_the_goal)
        self.add_state(_kick_ball)
        self.add_state(_stand_in_front_of_ball)
        self.add_state(_circle_away_from_own_goal)
        
        """ Tracking states """
        self.add_state(_track_ball_machine)
        
        """ goal interaction states """
        self.add_state(_center_goal)
        self.add_state(_line_up_shot)
        self.add_state(_check_team_goal)
        self.add_state(_aim_at_goal)
        
        """ system states """
        self.add_state(_get_up)

        
        """        Adding transitions between darwin        """
        
        """ if everything goes well transitions """
        self.add_transition(_track_ball_machine,"done",_follow_ball)
        self.add_transition(_follow_ball, "done", _aim_at_goal)
        self.add_transition(_aim_at_goal, "done", _check_team_goal)
        
        self.add_transition(_aim_at_goal, "fail", _circle_away_from_own_goal)
        #self.add_transition(_follow_ball, "done", _finding_the_goal)

        #self.add_transition(_finding_the_goal, "done", _center_goal)
        #self.add_transition(_finding_the_goal, "fail", _stand_in_front_of_ball)
        
        #self.add_transition(_center_goal, "fail", _finding_the_goal)
        #self.add_transition(_center_goal, "focus middle", _line_up_shot)
        #self.add_transition(_center_goal, "focus one",_check_team_goal)
        
        #self.add_transition(_line_up_shot, "check again", _center_goal)
        #self.add_transition(_line_up_shot, "lined up", _check_team_goal)
        
        self.add_transition(_check_team_goal, "fire", _stand_in_front_of_ball)
        self.add_transition(_stand_in_front_of_ball, "done", _kick_ball)
        self.add_transition(_kick_ball, "done", _track_ball_machine)
        
        self.add_transition(_check_team_goal, "turn", _circle_away_from_own_goal)
        self.add_transition(_circle_away_from_own_goal, "done", _stand_in_front_of_ball)
        

        """ Lost ball transitions """
        self.add_transition(_follow_ball, "lost ball", _track_ball_machine)
        self.add_transition(_stand_in_front_of_ball, "lost ball", _track_ball_machine)
        self.add_transition(_line_up_shot, "lost ball", _track_ball_machine)
        self.add_transition(_circle_away_from_own_goal, "lost ball", _track_ball_machine)
        self.add_transition(_finding_the_goal, "lost ball", _track_ball_machine)


        """ Falling transitions """
        
        self.add_transition(_aim_at_goal, "fallen", _get_up)
        self.add_transition(_follow_ball, "fallen", _get_up)
        self.add_transition(_stand_in_front_of_ball, "fallen", _get_up)
        self.add_transition(_finding_the_goal, "fallen", _get_up)
        self.add_transition(_kick_ball, "fallen", _get_up)
        self.add_transition(_circle_away_from_own_goal, "fallen", _get_up)
        self.add_transition(_track_ball_machine, "fallen", _get_up)
        self.add_transition(_check_team_goal, "fallen", _get_up)
        self.add_transition(_center_goal, "fallen", _get_up)
        self.add_transition(_line_up_shot, "fallen", _get_up)
        self.add_transition(_get_up, "done", _track_ball_machine)