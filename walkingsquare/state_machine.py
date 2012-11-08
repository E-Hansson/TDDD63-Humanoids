from Robot.StateMachines import general_fsm
import states
import math

class Program(general_fsm.StateMachine):
    def __init__(self):
        
        """        Create our states        """
        
        """ movement states """
        _stand_still = states.StandStill()
        _walk_straight = states.WalkSpeed(5, 1)
        _turn_left_gyro = states.TurnGyro(math.pi/2-0.4) # Adjust for bias in the imu.
        _initiate_walking = states.WalkSpeed(3,0)
        _walk_on_spot = states.WalkSpeed(0.2,0)
        _start_walking = states.StartWalk(1)
                
        """ arm states """
        _lift_right_arm = states.MoveArm("right", relation="ground")
        _lower_right_arm = states.MoveArm("right",angle=(math.pi/2,0,0),relation="ground")
        
        """ ball interaction states"""
        _track_ball = states.TrackBall()
        _circle_ball = states.CircleBall()
        
        """ misc states """
        _set_eye_color_blue = states.SetEyeColor(0,0,31)
        _set_eye_color_red = states.SetEyeColor(31,0,0)
        
        """ system states """
        _terminate = states.Exit()
        _get_up = states.GetUp()

        # Initiate the StateMachine, and give it an initial state 
        #super(Program, self).__init__(_stand_still)
        super(Program, self).__init__(_stand_still)
        
        
        """        Adding the states        """
        
        """ motion states """
        self.add_state(_stand_still)
        self.add_state(_walk_straight)
        self.add_state(_turn_left_gyro)
        self.add_state(_initiate_walking)
        self.add_state(_walk_on_spot)
        self.add_state(_start_walking)
        
        """ arm states """
        self.add_state(_lift_right_arm)
        self.add_state(_lower_right_arm)
        
        
        """ball interaction states"""
        self.add_state(_track_ball)
        self.add_state(_circle_ball)
        
        """ misc stats """
        self.add_state(_set_eye_color_blue)
        self.add_state(_set_eye_color_red)
        
        """ system states """
        self.add_state(_terminate)
        self.add_state(_get_up)
        
        
        """        Adding transitions between states        """
        
        """ motion transitions """
        
        self.add_transition(_stand_still,"timeout",_initiate_walking)
        self.add_transition(_turn_left_gyro, "done", _initiate_walking)
        self.add_transition(_initiate_walking, "timeout", _start_walking)
        self.add_transition(_start_walking, "done", _track_ball)
        self.add_transition(_track_ball, "done", _circle_ball)
        self.add_transition(_circle_ball, "done", _walk_straight)

        """ track transitions """
        
        self.add_transition(_track_ball, "done", _stand_still)
        
        """ arm transitions """
        self.add_transition(_lift_right_arm, "done", _turn_left_gyro)
        self.add_transition(_lower_right_arm, "done", _walk_straight)

        """ misc transitions """
        self.add_transition(_set_eye_color_blue, "done", _lower_right_arm)
        self.add_transition(_set_eye_color_red, "done", _lift_right_arm)

        """ error transitions """
        self.add_transition(_track_ball, "fallen", _get_up)
        self.add_transition(_stand_still, "fallen", _get_up)
        self.add_transition(_initiate_walking, "fallen", _get_up)
        self.add_transition(_turn_left_gyro, "fallen", _get_up)
        self.add_transition(_walk_on_spot, "fallen", _get_up)
        self.add_transition(_lift_right_arm, "fallen", _get_up)
        self.add_transition(_lower_right_arm, "fallen", _get_up)
        self.add_transition(_set_eye_color_blue, "fallen", _get_up)
        self.add_transition(_set_eye_color_red, "fallen", _get_up)
        self.add_transition(_walk_straight, "fallen", _get_up)
        self.add_transition(_get_up, "initiat_walking", _initiate_walking)
        self.add_transition(_get_up, "done", _stand_still)