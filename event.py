import state


class Event():
    def __init__(self, robot):
        self.robot = robot
        self.transition = None

    def check(self):
        return False

    def call(self):
        pass

    def transition(self):
        return None

class Obsticle(Event):
    def __init__(self, robot):
        self.robot = robot
        # self.transition = state.Follow_wall(robot)

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

    def transition(self):
        return state.Follow_wall(self.robot)

class Distance_changed(Event):
    def __init__(self, robot):
        self.robot = robot
        # self.transition = state.State(robot)

    def check(self):
        sensor_values = self.robot.readScaled()
        if sensor_values is not None:
            return all(x<0.5 for x in sensor_values)

    def call(self):
        print "Distance Changed"
        # self.robot.stop()

    def transition(self):
        return state.State(self.robot)

class Odometry(Event):
    pass
