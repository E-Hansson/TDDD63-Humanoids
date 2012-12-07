from Robot.StateMachines import general_fsm
import goal_finding_states
from help_functions import has_fallen

class Program(general_fsm.StateMachine):
    def __init__(self):
        
        """        Create our states        """
        
        _looking_for_goal=goal_finding_states.LookingForFirstObservation()
        _turn_a_quarter_around_ball=goal_finding_states.CircleBall()
        _turn_ever_so_little_to_the_left=goal_finding_states.CircleBall(10/8,"left")
        _turn_ever_so_little_to_the_right=goal_finding_states.CircleBall(10/8,"right")
        _adjust_right=goal_finding_states.AdjustPosition("right")
        _adjust_left=goal_finding_states.AdjustPosition("left")
        _look_for_next_post=goal_finding_states.TurnGyro()
        _turn_back_to_ball_left=goal_finding_states.TurnBackToBall("left")
        _turn_back_to_ball_right=goal_finding_states.TurnBackToBall("right")
        
        _check_team_goal = goal_finding_states.CheckTeam()
        _circle_away = goal_finding_states.CircleBall(20,"right")
        
        _done=goal_finding_states.Done()
        _lost_ball=goal_finding_states.LostBall()
        
        super(Program, self).__init__(_looking_for_goal)
        
        self.add_state(_looking_for_goal)
        self.add_state(_turn_a_quarter_around_ball)
        self.add_state(_turn_ever_so_little_to_the_left)
        self.add_state(_turn_ever_so_little_to_the_right)
        self.add_state(_adjust_right)
        self.add_state(_adjust_left)
        self.add_state(_look_for_next_post)
        self.add_state(_turn_back_to_ball_left)
        self.add_state(_turn_back_to_ball_right)
        
        self.add_state(_check_team_goal)
        self.add_state(_circle_away)
        
        self.add_state(_done)
        self.add_state(_lost_ball)
        
        self.add_transition(_looking_for_goal, "whole right", _adjust_right)
        self.add_transition(_looking_for_goal, "whole left", _adjust_left)
        
        self.add_transition(_looking_for_goal, "nothing",_turn_a_quarter_around_ball)
        self.add_transition(_turn_a_quarter_around_ball, "done", _looking_for_goal)
        
        self.add_transition(_looking_for_goal, "post", _look_for_next_post)
        self.add_transition(_look_for_next_post, "right", _turn_back_to_ball_right)
        self.add_transition(_look_for_next_post, "left", _turn_back_to_ball_left)
        
        self.add_transition(_turn_back_to_ball_right, "done", _turn_ever_so_little_to_the_left)
        self.add_transition(_turn_back_to_ball_left, "done", _turn_ever_so_little_to_the_right)
        
        self.add_transition(_turn_ever_so_little_to_the_left,"done" , _check_team_goal)
        self.add_transition(_turn_ever_so_little_to_the_right, "done", _check_team_goal)
        self.add_transition(_adjust_right, "done", _check_team_goal)
        self.add_transition(_adjust_left, "done", _check_team_goal)
        
        self.add_transition(_check_team_goal, "fire", _done)
        self.add_transition(_check_team_goal, "turn", _circle_away)
        self.add_transition(_circle_away, "done", _done)
        
        self.add_transition(_adjust_right, "lost ball", _lost_ball)
        self.add_transition(_adjust_left, "lost ball", _lost_ball)
        self.add_transition(_turn_a_quarter_around_ball, "lost ball", _lost_ball)
        self.add_transition(_turn_ever_so_little_to_the_left, "lost ball", _lost_ball)
        self.add_transition(_turn_ever_so_little_to_the_right, "lost ball", _lost_ball)
        
    def update(self):
        
        if has_fallen():
            return "fallen"
        
        if self.get_state()==self._done:
            print ("looking at goal")
            return "done"
        
        if self.get_state()==self._lost_ball:
            print("lost ball")
            return "done"
        
        super(Program,self).update()