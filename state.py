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

class Moving_To_Target(State):
    def __init__(self, robot, x, y):
        self.name = "Going To Set Coordinates"
        self.action = robot.Go_to(robot, x, y)
        self.events = [event.Reached_Positon(robot, x, y)]

class Homing(State):
    def __init__(self, robot):
        self.name = "Homing State"
        self.action = robot.GoHome(robot)
        self.events = self.action.events + [event.AtHome(robot)]

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
        self.events = self.action.events + [event.Lost_obsticle(robot)]#, event.In_corner(robot)]

# class Escape_corner(State):
#     def __init__(self, robot):
#         self.name = "Escape Corner"

#         self.action = robot.Leave_wall_behind(robot, )
#         self.events = self.action.events + [event.Lost_obsticle(robot), event.Tight_corner(robot)]

class Parallel_to_wall(State):
    def __init(self,robot):
        self.name = "Parallel to wall"
        self.action = robot.Rotate_to_wall(robot)
        self.events = robot.Rotate_to_wall.events

class Correct_position(State):
    pass

class Evade_obstacle(State):
    pass
