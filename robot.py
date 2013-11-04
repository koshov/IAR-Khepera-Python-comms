import serial
from multiprocessing import Process, Pipe
from math import cos, sin, pi, degrees, atan2
import cPickle as pickle
from time import sleep, time, clock

import state
import event
from worldMap import worldMap
import service_functions


class Robot():
    """ Robot class - what else did you expect?! """

    def __init__(self):
        self.serial_connection = serial.Serial(0, 9600, timeout=0.1)
        serial_info = self.serial_connection.readline()
        while serial_info != "":
            print serial_info
            serial_info = self.serial_connection.readline()
        try:
            self.min_IR_readings = pickle.load(open("min_IR_readings.p", "rb"))
        except IOError:
            self.min_IR_readings = service_functions.calibrateIR()

        self.FULL_SPEED = 5
        self.TIMEOUT = 0.0005
        self.gaussArray = [1.4867195147342977e-06, 6.691511288e-05,
                           0.00020074533864,       0.0044318484119380075,
                           0.02699548325659403,    0.03142733166853204,
                           0.05399096651318806,    0.19947114020071635,
                           0.24197072451914337,    0.4414418647198597
                          ]
        self.IRqueue = [[0] * 10, [0] * 10, [0] * 10, [0] * 10, [0] * 10, [0] * 10, [0] * 10, [0] * 10]
        self.wheelDiff = 163.8 # This can also be broken up to the differential plus the calibration factor
        self.gauss_result = [0] * 8  # readIR result TODO: rename
        self.sensor_values = []
        self.target_angle = 0.0
        self.pipe, child_pipe = Pipe()
        self.world_map = Process(target=worldMap, args=(child_pipe, ))
        self.world_map.start()

        self.resetCounts()
        child_signal, signal_object = self.pipe.recv()
        if child_signal == 'END':
            self.stop()
            exit()
        elif child_signal == 'LOCATION':
            self.x = signal_object['x']
            self.y = signal_object['y']
            self.phi = signal_object['phi']


    def run(self):
        self.state = state.State(self)
        # self.__class__.state = self.state.name
        # self.state = state.Moving_To_Target(self, 50, 50)
        self.start_time = time()
        try:
            while True:
                self.thick()
        except KeyboardInterrupt, e:
            self.stop()
            self.world_map.join()

    def thick(self):
        # t = time()

        data = self.readCount()
        if len(data) == 2:
            left_n = int(data[0])
            right_n = int(data[1])
            left_d = left_n - self.left_l
            self.left_l = left_n
            right_d = right_n - self.right_l
            self.right_l = right_n
            # print "L: %f R: %f" % (left_d, right_d)
            self.setOdometry(left_d, right_d)

        self.sensor_values = self.readScaledIR()
        if self.pipe.poll():
            child_signal, signal_object = self.pipe.recv()
            if child_signal == 'END':
                self.stop()
                exit()
            elif child_signal == 'PATH':
                self.state = state.Follow_Path(self, signal_object)
        self.pipe.send(((self.x, self.y, self.phi), self.sensor_values))

        for event in self.state.events:
            if event.check():
                event.call()
                if event.transition() != None:
                    self.state = event.transition()

                # print "FPS: %f"%(1/(time() - t))
                # sleep(self.TIMEOUT)

    def calibrateIR(self):
        historicIR = [[], [], [], [], [], [], [], []]
        smoothIterations = 100
        for i in range(smoothIterations):
            vals = self.readIR()
            for i in range(8):
                historicIR[i].append(vals[i])
            sleep(self.TIMEOUT)
        min_IR_readings = [sum(list) / smoothIterations for list in historicIR]
        pickle.dump(min_IR_readings, open("min_IR_readings.p", "wb"))
        print "Minimum IR levels after calibration:\n%s" % min_IR_readings
        return min_IR_readings


    # ==== Actions ====
    class Action():
        def __init__(self, robot):
            pass

    class Go_to(Action):
        def __init__(self, robot, x, y):
            print "Rotating to face goal"
            robot.target_angle = atan2(y-robot.y, x-robot.x)
            robot.rotateTo(robot.target_angle)
            print "Done Rotating, now moving towards goal"
            temp = robot.phi
            # robot.resetCounts()
            robot.phi = temp

    class Follow_Path(Action):
        def __init__(self, robot, pointsArray):

            print "Going to waypoint %f %f"

    class Move_forward(Action):
        def __init__(self, robot):
            self.events = [event.Odometry(robot)]
            print 'Moving Forward'
            robot.go(robot.FULL_SPEED)

    class Adjust_to_wall(Action):
        def __init__(self, robot, wall_position):
            self.robot = robot
            # self.wall_position = wall_position
            self.events = [event.Distance_changed(robot, wall_position)]
            # print 'Adjusting to the wall'
            # self.robot.stop()

    class Rotate_to_wall(Action):
        def __init__(self, robot):
            #Now get the sensors.
            irs = self.robot.readScaledIR
            left = sum(irs[0:2])
            right = sum(irs[3:5])
            #Check which wall is closer
            if left > right:
                print 'Left wall is closer'
                self.robot.setSpeeds(-5, 5)
                self.events = [event.Parallel_completed(robot, [1, 0])]

            else:
                print 'Right wall is closer'
                self.robot.setSpeeds(5, -5)
                self.events = [event.Parallel_completed(robot, [4, 5])]


    def rotateTo(self, phi):

        robot_phi = self.phi % (2*pi)
        target = phi % (2*pi)

        if (robot_phi - target) < 0:
            if (target - robot_phi) > pi:
                rot = (2*pi) - target - robot_phi
                self.setSpeeds(self.FULL_SPEED, -self.FULL_SPEED)
            else:
                rot = target - robot_phi
                self.setSpeeds(-self.FULL_SPEED, self.FULL_SPEED)
        else:
            if robot_phi - target > pi:
                rot = (2*pi) - target - robot_phi
                self.setSpeeds(-self.FULL_SPEED, self.FULL_SPEED)
            else:
                rot = robot_phi - target
                self.setSpeeds(self.FULL_SPEED, -self.FULL_SPEED)


        # if robot_phi > pi: robot_phi = 2*pi - robot_phi

        print "Target: %f"%target
        print "At %f"%robot_phi
        print "I should rotate by: %f" %rot

        while abs(robot_phi - target) > 0.1:
            data = self.readCount()
            if len(data) == 2:
                left_n = int(data[0])
                right_n = int(data[1])

                left_d = left_n - self.left_l
                self.left_l = left_n
                right_d = right_n - self.right_l
                self.right_l = right_n
                self.setOdometry(left_d, right_d)

                robot_phi = self.phi % (2*pi)

        # self.stop()


    # ==== Khepera Functions ====
    def closeConnection(self):
        try:
            self.serial_connection.close()
        except Exception, e:
            print e

    def setSpeeds(self, leftSpeed, rightSpeed):
        self.serial_connection.write("D," + str(leftSpeed) + "," + str(rightSpeed) + "\n")
        self.serial_connection.readline()

    def go(self, speed):
        self.setSpeeds(speed, speed)

    def stop(self):
        self.go(0)

    def validateSensorValue(self, sensorString):
        # print sensorString
        result = sensorString[:-2].split(",")[1:]  # Drop "\r\n" at the end of string and "n" at beginning
        if len(result) < 8:
            return None
        for value in result:
            try:
                value = int(value)
                if value < 0 or value > 1024:
                    return None
            except ValueError, e:
                return None
        return result

    def scaleIR(self, value, i):
        return (value - self.min_IR_readings[i]) / (1020 - self.min_IR_readings[i])

    def readScaledIR(self):
        vals = self.readIR()
        for i in range(0, len(vals)):
            vals[i] = self.scaleIR(vals[i], i)
        return vals

    def readIR(self):
        self.serial_connection.write("N\n")
        sensorString = self.serial_connection.readline()
        sensorArray = self.validateSensorValue(sensorString)

        if sensorArray != None:
            for i, value in enumerate(sensorArray):
                del self.IRqueue[i][0]
                self.IRqueue[i].append(int(value))
                self.gauss_result[i] = sum([a * b for a, b in zip(self.IRqueue[i], self.gaussArray)])
        return self.gauss_result

    def readAmbient(self):
        self.serial_connection.write("O\n")
        sensorString = self.serial_connection.readline()
        return self.validateSensorValue(sensorString)

    def setCounts(self, leftCount, rightCount):
        self.serial_connection.write("G," + str(leftCount) + "," + str(rightCount) + "\n")
        self.serial_connection.readline()

    def setOdometry(self, left, right):
        self.x = self.x + 0.5 * (left + right) * cos(self.phi)
        self.y = self.y + 0.5 * (left + right) * sin(self.phi)
        self.phi = self.phi - (left - right) / (4 * self.wheelDiff)
        # print "X: %f Y: %f phi: %f"%(self.x, self.y, degrees(self.phi))

    def readCount(self):
        self.serial_connection.write("H\n")
        sensorString = self.serial_connection.readline()
        result = sensorString[:-2].split(",")[1:]  # Drop "\r\n" at the end of string and "n" at beginning
        return result

    def setLED(self, led, value):
        if led == "left":
            led = '0'
        else:
            led = '1'
        self.serial_connection.write("L," + led + "," + value + "\n")

    def monitorIR(self):
        while True:
            print self.readIR()
            sleep(self.TIMEOUT)

    def monitorAmbient(self):
        while True:
            print self.readAmbient()
            sleep(self.TIMEOUT)

    def resetCounts(self):
        self.setCounts(0, 0)
        self.x = 0
        self.y = 0
        self.left_l = 0
        self.right_l = 0
        self.phi = 0



