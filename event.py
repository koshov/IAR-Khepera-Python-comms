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
        sensor_values = self.robot.readScaledIR()
        if sensor_values is not None:
            for value in sensor_values:
                if value > 0.32:
                    # print sensor_values
                    return True
            return False

    def call(self):
        print "Stopping"
        # self.robot.stop()

    def transition(self):
        return state.Follow_wall(self.robot)

class Lost_obsticle(Event):
    def __init__(self, robot):
        self.robot = robot

    def check(self):
        sensor_values = self.robot.readScaledIR()
        if sensor_values is not None:
            if max(sensor_values) < 0.025:
                return True
            return False

    def call(self):
        print "Initial State"
        # self.robot.go(self.robot.FULL_SPEED)

    def transition(self):
        return state.Initial(self.robot)

class Distance_changed(Event):
    def __init__(self, robot, wall_position):
        self.robot = robot
        self.wall_position = wall_position

    def check(self):
        THRESHOLD = 0.2
        sensor_values = self.robot.readScaledIR()
        if max([sensor_values[1], sensor_values[2], sensor_values[3], sensor_values[4]]) > THRESHOLD:
            front = self.robot.FULL_SPEED
        else:
            front = 0

        # TODO: 
        if sensor_values is not None:
            if max([sensor_values[0], sensor_values[5]]) > THRESHOLD:
                if self.wall_position == "left": 
                    gain_dir = "left"
                    sensor_vals = sensor_values[0]
                else: 
                    gain_dir = "right"
                    sensor_vals = sensor_values[5]
                self.gain = (gain_dir, sensor_vals * 0.5 - THRESHOLD + front/self.robot.FULL_SPEED, front)
                return True
            else:
                if self.wall_position == "left": 
                    gain_dir = "right"
                    sensor_vals = sensor_values[0]
                else: 
                    gain_dir = "left"
                    sensor_vals = sensor_values[5]
                self.gain = (gain_dir, (1-THRESHOLD) - sensor_vals * (1-THRESHOLD)/THRESHOLD + front/self.robot.FULL_SPEED, front)
                return True                    
 
        return False

    def call(self):
        speed  = self.robot.FULL_SPEED
        # print self.gain
        in_place = int(self.gain[2])
        # print "Place %d"%in_place
        speed_gain = int(self.gain[1]*speed*2)
        if self.gain[0] == "left":
            left = speed - in_place + speed_gain
            right = speed - in_place - speed_gain
            # print "Left - L: %d, R: %d"%(left,right)
            self.robot.setSpeeds(left, right)
        else:
            left = speed - in_place - speed_gain
            right = speed - in_place + speed_gain
            # print "Left - L: %d, R: %d"%(left,right)
            self.robot.setSpeeds(left, right)


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
        sensor_values = self.robot.readScaledIR()
        if sensor_values is not None:
            sensorOne = robot.readScaledIR[self.sensors[0]]
            sensorTwo = robot.readScaledIR[self.sensors[1]]
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
