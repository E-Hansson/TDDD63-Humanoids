from Robot.StateMachines import general_fsm
import states
import math
import erik_test_states 

class Program(general_fsm.StateMachine):
    def __init__(self):
        #self.robocom = "http://192.168.0.5:5000/"
        """        Create our states        """
        
        """ movement states """
        _stand_still = states.StandStill()
        _walk_straight = states.WalkSpeed(5, 0.02)
        _turn_left_gyro = states.TurnGyro(math.pi/2-0.4) # Adjust for bias in the imu.
        _initiate_walking = states.WalkSpeed(3,0)
        _walk_on_spot = states.WalkSpeed(0.02,0)
        _start_walking = states.StartWalk(0.02)
        _one_step_forward_force_kick = states.FollowBall(math.pi/4.5,True)
        _one_step_forward = states.FollowBall(math.pi/4.5,True)
        
                
        """ arm states """
        _lift_right_arm = states.MoveArm("right", relation="ground")
        _lift_left_arm = states.MoveArm("left", relation="ground")
        _lower_right_arm = states.MoveArm("right",angle=(math.pi/2,0,0),relation="ground")
        
        """ ball interaction states"""
        _follow_ball = states.FollowBall()
        _circle_ball_left = erik_test_states.CrudeGoalAdjusting(1)
        _circle_ball_right = erik_test_states.CrudeGoalAdjusting(-1)
        #_circle_ball_left = states.CrudeGoalAdjusting(math.pi/3,[math.pi/18,-math.pi/8],[-math.pi/18,-math.pi/8],1)
        #_circle_ball_right = states.CrudeGoalAdjusting(math.pi/3,[math.pi/18,-math.pi/8],[-math.pi/18,-math.pi/8],-1)
        #_adjust_aim_left = states.CrudeGoalAdjusting(math.pi/12,[0,-math.pi/8],[0,-math.pi/8],1,True)
        #_adjust_aim_right = states.CrudeGoalAdjusting(math.pi/12,[0,-math.pi/8],[0,-math.pi/8],-1,True)
        _track_ball = erik_test_states.TrackBall()
        _re_find_ball = erik_test_states.TrackBall()
        _stand_in_front_of_ball = states.FaceBall()
        _kick_ball = states.KickBall()
        _circle_away_from_own_goal = erik_test_states.CircleBall()
        _stand_in_front_of_ball_force_kick = states.FaceBall()
        
        """ goal interaction states"""
        _track_goal = states.TrackGoal(_circle_ball_left)
        _center_goal = states.FindMiddleOfGoal()
        _line_up_shot = erik_test_states.LineUpShot()
        _check_team_goal = states.CheckTeam()
        
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
        self.add_state(_one_step_forward)
        self.add_state(_one_step_forward_force_kick)
        
        """ arm states """
        self.add_state(_lift_right_arm)
        self.add_state(_lift_left_arm)
        self.add_state(_lower_right_arm)
        
        
        """ball interaction states"""
        self.add_state(_follow_ball)
        self.add_state(_circle_ball_left)
        self.add_state(_circle_ball_right)
        #self.add_state(_adjust_aim_left)
        #self.add_state(_adjust_aim_right)
        self.add_state(_kick_ball)
        self.add_state(_stand_in_front_of_ball)
        self.add_state(_re_find_ball)
        self.add_state(_circle_away_from_own_goal)
        self.add_state(_stand_in_front_of_ball_force_kick)
        
        """goal interaction states"""
        self.add_state(_track_goal)
        self.add_state(_center_goal)
        self.add_state(_line_up_shot)
        self.add_state(_check_team_goal)
        
        
        """ misc stats """
        self.add_state(_set_eye_color_blue)
        self.add_state(_set_eye_color_red)
        
        """ system states """
        self.add_state(_terminate)
        self.add_state(_get_up)
        
        self.add_state(_track_ball)
        
        """        Adding transitions between states        """
        
        """ motion transitions """
        
        self.add_transition(_stand_still,"timeout",_initiate_walking)
        self.add_transition(_initiate_walking, "timeout", _track_ball)
        self.add_transition(_follow_ball, "done", _circle_ball_left)
        """
        self.add_transition(_circle_ball_left, "adjust left", _adjust_aim_left)
        self.add_transition(_circle_ball_left, "adjust right", _adjust_aim_right)
        self.add_transition(_adjust_aim_left, "adjust left", _adjust_aim_left)
        self.add_transition(_adjust_aim_right, "adjust right", _adjust_aim_right)
        self.add_transition(_adjust_aim_left, "adjust right", _center_goal)
        self.add_transition(_adjust_aim_right, "adjust left", _center_goal)
        """
        self.add_transition(_circle_ball_left, "done", _center_goal)
        self.add_transition(_circle_ball_right, "done", _center_goal)
        self.add_transition(_circle_ball_left, "fail", _walk_straight)
        
        self.add_transition(_center_goal, "fail", _center_goal)
        self.add_transition(_center_goal, "focus middle", _line_up_shot)
        self.add_transition(_center_goal, "focus one",_check_team_goal)
        
        self.add_transition(_line_up_shot, "check again", _center_goal)
        self.add_transition(_line_up_shot, "lined up", _check_team_goal)
        
        self.add_transition(_stand_in_front_of_ball, "done", _check_team_goal)
        self.add_transition(_check_team_goal, "fire", _one_step_forward)
        self.add_transition(_one_step_forward, "done", _kick_ball)
        self.add_transition(_check_team_goal, "turn", _circle_away_from_own_goal)
        self.add_transition(_circle_away_from_own_goal, "done", _stand_in_front_of_ball_force_kick)
        self.add_transition(_stand_in_front_of_ball_force_kick, "done", _one_step_forward_force_kick)
        self.add_transition(_one_step_forward_force_kick, "done", _kick_ball)
        self.add_transition(_one_step_forward, "done", _kick_ball)
        self.add_transition(_kick_ball, "done", _track_ball)
        self.add_transition(_walk_straight, "timeout", _track_ball)

        """ track transitions """
        
        #self.add_transition(_track_goal, "done", _re_find_ball)
        #self.add_transition(_re_find_ball, "done", _circle_ball)
        self.add_transition(_track_ball,"done",_follow_ball)
        self.add_transition(_follow_ball, "no ball", _track_ball)
        self.add_transition(_stand_in_front_of_ball, "no ball", _track_ball)
        self.add_transition(_track_ball, "out of sight", _walk_straight)
        
        self.add_transition(_line_up_shot, "lost ball", _track_ball)
        self.add_transition(_one_step_forward, "no ball", _track_ball)


        """ error transitions """
        self.add_transition(_circle_away_from_own_goal, "fallen", _get_up)
        self.add_transition(_one_step_forward, "fallen", _get_up)
        self.add_transition(_one_step_forward_force_kick, "fallen", _get_up)
        self.add_transition(_check_team_goal, "fallen", _get_up)
        self.add_transition(_kick_ball, "fallen", _get_up)
        self.add_transition(_line_up_shot, "fallen", _line_up_shot)
        self.add_transition(_track_goal, "fallen", _get_up)
        self.add_transition(_circle_ball_left, "fallen", _get_up)
        self.add_transition(_circle_ball_right, "fallen", _get_up)
        self.add_transition(_stand_in_front_of_ball, "fallen", _get_up)
        self.add_transition(_track_ball, "fallen", _get_up)
        self.add_transition(_follow_ball, "fallen", _get_up)
        self.add_transition(_stand_still, "fallen", _get_up)
        self.add_transition(_initiate_walking, "fallen", _get_up)
        self.add_transition(_turn_left_gyro, "fallen", _get_up)
        self.add_transition(_walk_on_spot, "fallen", _get_up)
        self.add_transition(_lift_right_arm, "fallen", _get_up)
        self.add_transition(_lower_right_arm, "fallen", _get_up)
        self.add_transition(_set_eye_color_blue, "fallen", _get_up)
        self.add_transition(_set_eye_color_red, "fallen", _get_up)
        self.add_transition(_walk_straight, "fallen", _get_up)
        self.add_transition(_get_up, "done", _stand_still)