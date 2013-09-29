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
        self.events = [event.Obsticle(robot)] + self.action.events

class Follow_wall(State):
    pass

class Correct_position(State):  
    pass

class Evade_obstacle(State):
    pass
