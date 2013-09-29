class Action():
    pass


class Move_forward(Action):
    def __init__(self, robot):
        robot.go(robot.FULL_SPEED)
