from Robot.StateMachines import general_fsm
import states
from math import pi

class Program (general_fsm.StateMachine):
    
    def __init__(self):
        _circle_ball=states.DemoCircleBall(pi/2,[0,0],[0,0])
        _stand_still=states.StandStill()
        _initiate_walking = states.WalkSpeed(3,0)
        _follow_ball = states.FollowBall()
        _track_ball = states.TrackBall()
        _stand_in_front_of_ball = states.FollowBall(pi/3.1)
        _kick_ball = states.KickBall()
        _follow_ball = states.FollowBall()
        _terminate = states.Exit()
        _get_up = states.GetUp()
        _set_eye_color_blue = states.SetEyeColor(0,0,31)
        _set_eye_color_red = states.SetEyeColor(31,0,0)
        
        self.add_state(_circle_ball)
        self.add_state(_stand_still)
        self.add_state(_initiate_walking)
        self.add_state(_follow_ball)
        self.add_state(_track_ball)
        self.add_state(_stand_in_front_of_ball)
        self.add_state(_kick_ball)
        self.add_state(_follow_ball)
        self.add_state(_terminate)
        self.add_state(_get_up)
        self.add_state(_set_eye_color_blue)
        self.add_state(_set_eye_color_red)
        
        
        super(Program, self).__init__(_stand_still)
        
        self.add_transition(_stand_still,"timeout",_initiate_walking)
        self.add_transition(_initiate_walking, "timeout", _set_eye_color_blue)
        self.add_transition(_set_eye_color_blue, "done", _track_ball)
        self.add_transition(_track_ball,"done",_follow_ball)
        self.add_transition(_follow_ball, "done", _circle_ball)
        self.add_transition(_circle_ball, "done", _stand_in_front_of_ball)
        self.add_transition(_stand_in_front_of_ball, "done", _set_eye_color_red)
        self.add_transition(_set_eye_color_red, "done", _kick_ball)
        self.add_transition(_kick_ball, "done", _set_eye_color_blue)
        
        self.add_transition(_follow_ball, "no ball", _track_ball)
        self.add_transition(_stand_in_front_of_ball, "no ball", _track_ball)
        
        
        self.add_transition(_circle_ball, "fallen", _get_up)
        self.add_transition(_follow_ball, "fallen", _get_up)
        self.add_transition(_stand_still, "fallen", _get_up)
        self.add_transition(_initiate_walking, "fallen", _get_up)
        self.add_transition(_set_eye_color_blue, "fallen", _get_up)
        self.add_transition(_set_eye_color_red, "fallen", _get_up)
        self.add_transition(_kick_ball, "fallen", _get_up)
        self.add_transition(_get_up, "done", _stand_still)