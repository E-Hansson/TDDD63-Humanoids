# FSM for the goal keeper

from Robot.StateMachines import general_fsm
import goal_keeper_states
from math import pi

class Program (general_fsm.StateMachine):
    
    def __init__(self):
        _stand_still=goal_keeper_states.StandStill()
        _walk_forward=goal_keeper_states.WalkSpeed(2)
        _face_goal=goal_keeper_states.FaceMiddleOfGoal()
        _walk_to_line_away_from_goal=goal_keeper_states.GoToLine()
        _walk_to_line_to_goal=goal_keeper_states.GoToLine()
        _test_if_standing_in_goal=goal_keeper_states.CheckIfStandingInGoal()
        _guarding=goal_keeper_states.Guarding()
        _ball_tracking=goal_keeper_states.BallTracking()
        _find_the_middle_of_the_goal=goal_keeper_states.FindMiddleOfGoal
        _get_up=goal_keeper_states.GetUp()
        _turn_half_circle_first = goal_keeper_states.TurnGyro(pi-0.4)
        _turn_half_circle_second = goal_keeper_states.TurnGyro(pi-0.4)
        
        super(Program, self).__init__(_stand_still)
        
        self.add_state(_stand_still)
        self.add_state(_walk_forward)
        self.add_state(_face_goal)
        self.add_state(_walk_to_line_away_from_goal)
        self.add_state(_walk_to_line_to_goal)
        self.add_state(_test_if_standing_in_goal)
        self.add_state(_guarding)
        self.add_state(_ball_tracking)
        self.add_state(_find_the_middle_of_the_goal)
        self.add_state(_get_up)
        self.add_state(_turn_half_circle_first)
        self.add_state(_turn_half_circle_second)
        
        self.add_transition(_stand_still, "timeout", _test_if_standing_in_goal)
        self.add_transition(_test_if_standing_in_goal, "done", _ball_tracking)
        self.add_transition(_ball_tracking, "done", _guarding)
        self.add_transition(_guarding, "out of sight", _ball_tracking)
        
        self.add_transition(_test_if_standing_in_goal,"standing in front of the goal", _walk_to_line_to_goal)
        self.add_transition(_walk_to_line_to_goal, "standing on line", _test_if_standing_in_goal)
        
        self.add_transition(_test_if_standing_in_goal, "can't find the goal", _turn_half_circle_first)
        self.add_transition(_turn_half_circle_first, "done", _find_the_middle_of_the_goal)
        self.add_transition(_find_the_middle_of_the_goal, "focus middle", _face_goal)
        self.add_transition(_face_goal, "done", _walk_to_line_to_goal)
    
        self.add_transition(_find_the_middle_of_the_goal, "focus one", _turn_half_circle_second)
        self.add_transition(_turn_half_circle_second, "done", _walk_forward)
        self.add_transition(_walk_forward, "timeout", _turn_half_circle_first)
        
        self.add_transition(_stand_still, "fallen", _get_up)
        self.add_transition(_walk_forward, "fallen", _get_up)
        self.add_transition(_face_goal, "fallen", _get_up)
        self.add_transition(_walk_to_line_away_from_goal, "fallen", _get_up)
        self.add_transition(_walk_to_line_to_goal, "fallen", _get_up)
        self.add_transition(_test_if_standing_in_goal, "fallen", _get_up)
        self.add_transition(_guarding, "fallen", _get_up)
        self.add_transition(_ball_tracking, "fallen", _get_up)
        self.add_transition(_find_the_middle_of_the_goal, "fallen", _get_up)
        self.add_transition(_turn_half_circle_first, "fallen", _get_up)
        self.add_transition(_turn_half_circle_second, "fallen", _get_up)
        self.add_transition(_get_up, "done", _stand_still)