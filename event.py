import state


class Event():
    def __init__(self, robot):
        self.robot = robot
        self.transition = None

    def check(self):
        return False

    def call(self):
        pass

class Obsticle(Event):
    def __init__(self, robot):
        self.robot = robot
        self.transition = state.State(robot)

    def check(self):
        sensor_values = self.robot.readIR()
        if sensor_values is not None:
            for value in sensor_values:
                if int(value) > 320:
                    print sensor_values
                    return True
            return False

    def call(self):
        print "Stopping"
        self.robot.stop()

class Odometry(Event):
    pass
