from Robot.StateMachines import general_fsm
import states
import math

class Program(general_fsm.StateMachine):
    def __init__(self):
        # Create our states
        _stand_still = states.StandStill()
        _walk_straight = states.WalkSpeed(5, 1)
        _lift_right_arm=states.LiftRightArm()
        _turn_left_gyro = states.TurnGyro(math.pi/2-0.4) # Adjust for bias in the imu.
        _terminate = states.Exit()

        # Initiate the StateMachine, and give it an initial state 
        super(Program, self).__init__(_stand_still)
        
        # Add a bunch of states
        self.add_state(_stand_still)
        self.add_state(_walk_straight)
        self.add_state(_lift_right_arm)
        self.add_state(_turn_left_gyro)
        self.add_state(_terminate)
        
        # Add some transitions between states
        self.add_transition(_stand_still,"timeout",_walk_straight)

        self.add_transition(_walk_straight,"timeout", _lift_right_arm)
        self.add_transition(_lift_right_arm, "done", _turn_left_gyro)
        self.add_transition(_turn_left_gyro, "done", _walk_straight)
        self.add_transition(_turn_left_gyro, "complete", _terminate)



