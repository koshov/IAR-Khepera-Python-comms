from math import pi
from time import sleep
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
        sensor_values = self.robot.sensor_values
        if sensor_values is not None:
            for value in sensor_values:
                if value > 0.1:
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
        sensor_values = self.robot.sensor_values
        if sensor_values is not None:
            if max(sensor_values) < 0.025:
                return True
            return False

    def call(self):
        print "Initial State"
        # self.robot.go(self.robot.FULL_SPEED)

    def transition(self):
        return state.Initial(self.robot)

class AtHome(Event):
    def __init__(self, robot):
        self.robot = robot

    def check(self):
        if abs(self.robot.x) < 50 and abs(self.robot.y) < 50:
            return True
        return False

    def call(self):
        self.robot.setLED("left", '1')
        sleep(1)
        self.robot.setLED("left", '0')
        self.robot.setLED("right", '1')
        sleep(1)
        self.robot.setLED("right", '0')


    def transition(self):
        return state.State(self.robot)


class Reached_Positon(Event):
    def __init__(self, robot, x, y):
        self.robot = robot
        self.x = x
        self.y = y

        self.bounding_r = (abs(self.x) - abs(self.robot.x))**2 + (abs(self.y) - abs(self.robot.y))**2
        self.bounding_x = self.robot.x
        self.bounding_y = self.robot.y

    def check(self):
        robot_phi = self.robot.phi % (2*pi)
        target_phi = self.robot.target_angle % (2*pi)
        # print 'Phi: %f, Target: %f'%(robot_phi, target_phi)
        print 'G: %f, %f\nR: %f, %f'%(self.x, self.y, self.robot.x, self.robot.y)
        if robot_phi > target_phi + target_phi * 0.1:
            self.robot.setSpeeds(5, 4)
        elif robot_phi < target_phi - target_phi * 0.1:
            self.robot.setSpeeds(4, 5)
        else:
            self.robot.setSpeeds(5, 5)


        return (abs(self.robot.x) - abs(self.bounding_x))**2 + (abs(self.robot.y) - abs(self.bounding_y))**2 > self.bounding_r

    def call(self):
        # self.robot.stop()
        self.robot.state.nextWaypoint()
        print "Reached position %f %f" %(self.robot.x, self.robot.y)

    def transition(self):
        return None

class SpottedFood(Event):
    def __init__(self, robot):
        self.robot = robot

    def check(self):
        sensor_values = self.robot.readScaledIR()
        return any(sensor > 0.7 for sensor in sensor_values)

    def call(self):
        self.robot.setLED("left", '1')
        sleep(1)
        self.robot.setLED("left", '0')
        self.robot.setLED("right", '1')
        sleep(1)
        self.robot.setLED("right", '0')

class Distance_changed(Event):
    def __init__(self, robot, wall_position):
        self.robot = robot
        self.wall_position = wall_position
        self.THRESHOLD = 0.15

    def check(self):
        sensor_values = self.robot.sensor_values
        if self.wall_position == "left":
            first_sensors = max([sensor_values[1], sensor_values[2]])
            second_sensors = max([sensor_values[3], sensor_values[4]])
        else:
            first_sensors = max([sensor_values[3], sensor_values[4]])
            second_sensors = max([sensor_values[1], sensor_values[2]])

        if first_sensors > self.THRESHOLD or second_sensors > self.THRESHOLD * 2:
            front = self.robot.FULL_SPEED
        else:
            front = 0

        if sensor_values is not None:
            if self.wall_position == "left":
                gain_dir = ["left", "right"]
                target_wall = sensor_values[0]
                other_wall = sensor_values[5]
            else:
                gain_dir = ["right", "left"]
                target_wall = sensor_values[5]
                other_wall = sensor_values[0]

            # Escape from nearby wall
            if max([sensor_values[0], sensor_values[5]]) > self.THRESHOLD:
                if target_wall > other_wall:
                    gain_direction = gain_dir[0]
                    sensor_val = target_wall
                else:
                    gain_direction = gain_dir[1]
                    sensor_val = other_wall

                self.gain = (gain_direction, sensor_val * 0.5  - self.THRESHOLD + front/self.robot.FULL_SPEED, front)
                return True
            # Move towards wall when loosing it
            else:
                self.gain = (gain_dir[1], (1-self.THRESHOLD) - target_wall * (1-self.THRESHOLD)/self.THRESHOLD + front/self.robot.FULL_SPEED, front)
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
        sensor_values = self.robot.sensor_values
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
