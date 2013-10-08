import event


class State():
    def __init__(self, robot):
        self.name = "Empty State"
        self.action = None  # Empty Action
        self.events = []  # Empty Event

class Initial(State):
    def __init__(self, robot):
        self.name = "Initial State"
        self.action = robot.Move_forward(robot)
        self.events = [event.Obsticle(robot)]
        # + self.action.events

class Follow_wall(State):
    def __init__(self, robot):
        self.name = "Following Wall"
        # Determine on which side of robot the wall is
        sensor_values = robot.readScaledIR()
        if sum(sensor_values[0:2]) > sum(sensor_values[3:5]):
            print "WALL ON LEFT"
            self.wall_position = "left"
        else:
            print "WALL ON RIGTH"
            self.wall_position = "right"

        self.action = robot.Adjust_to_wall(robot, self.wall_position)
        self.events = self.action.events


#This wil make the robot parallel to a wall
class Parallel_to_wall(State):
    def __init(self,robot):
        self.name = "Parallel to wall"
        self.action = robot.Rotate_to_wall(robot)
        self.events = robot.Rotate_to_wall.events

class Correct_position(State):  
    pass

class Evade_obstacle(State):
    pass
