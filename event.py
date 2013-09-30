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
        # self.robot.stop()

    def transition(self):
        return state.Follow_wall(self.robot)

class Distance_changed(Event):
    def __init__(self, robot, wall_position):
        self.robot = robot
        self.wall_position = wall_position

    def check(self):
        sensor_values = self.robot.readScaled()
        if sensor_values is not None:
            if self.wall_position == "left":
                if sensor_values[0] > 0.1:
                    self.gain = ("left", sensor_values[0])
                    return True
                else:
                    self.gain = ("right", sensor_values[0])
                    return True                    
            else:
                if sensor_values[5] > 0.1:
                    self.gain = ("right", sensor_values[5])
                    return True
                else:
                    self.gain = ("left", sensor_values[5])
                    return True   

        return False

    def call(self):
        speed  = self.robot.FULL_SPEED
        print self.gain
        speed_gain = speed + int(self.gain[1]*speed/4)
        if self.gain[0] == "left":
            print "L LEFT " + str(speed + speed_gain/2)
            print "L RIGH " + str(speed - speed_gain*2)
            self.robot.setSpeeds(speed + speed_gain, speed - speed_gain)
        else:
            print "R LEFT " + str(speed + speed_gain/2)
            print "R RIGH " + str(speed - speed_gain*2)
            self.robot.setSpeeds(speed - speed_gain, speed + speed_gain)


    def transition(self):
        return None

class Odometry(Event):
    pass

class Parallel_completed(Event):
    def __init__(self, robot, sensors):
        self.robot = robot
        #The sensors that we are following
        self.sensors = sensors
        # self.transition = state.State(robot)

    def check(self):
        sensor_values = self.robot.readScaled()
        if sensor_values is not None:
            sensorOne = robot.readScaled[self.sensors[0]]
            sensorTwo = robot.readScaled[self.sensors[1]]
            #DRAGONS BE HERE.
            threshold = 0.039215686
            if (sensorOne - sensorTwo)> threshold:
                return False
            return True

    def call(self):
        print "Parallelness Completed"
        # self.robot.stop()

    def transition(self):
        return state.State(self.robot)
