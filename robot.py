import serial
from multiprocessing import Process, Pipe
from worldMap import worldMap
from time import sleep, time, clock
import state
import event
from math import cos, sin, pi, degrees, atan
import cPickle as pickle


class Robot():
    """ Robot class - what else did you expect?! """

    def __init__(self):
        self.serial_connection = serial.Serial(0,9600, timeout=0.1)
        self.FULL_SPEED = 5
        self.state = "Initial State"
        self.TIMEOUT = 0.0005
        self.gaussArray = [1.4867195147342977e-06, 6.691511288e-05, 0.00020074533864, 0.0044318484119380075, 0.02699548325659403, 0.03142733166853204, 0.05399096651318806, 0.19947114020071635, 0.24197072451914337, 0.4414418647198597]
        self.IRqueue = [[0]*10,[0]*10,[0]*10,[0]*10,[0]*10,[0]*10,[0]*10,[0]*10]
        self.wheelDiff = 163.8 # This can also be broken up to the differential plus the calibration factor
        self.gauss_result = [0]*8  # readIR result TODO: rename
        self.sensor_values = []

        self.pipe, child_pipe = Pipe()
        self.world_map = Process(target=worldMap, args=(child_pipe, ))
        self.world_map.start()

        self.destination_unknown = True

        # Odometry
        self.resetCounts()

        shit = self.serial_connection.readline()
        while shit != "":
            print shit
            shit = self.serial_connection.readline()

        try:
            self.min_IR_readings = pickle.load(open("min_IR_readings.p", "rb"))
        except IOError:
            self.min_IR_readings = self.calibrateIR()



    def run(self):
        self.resetCounts()

        self.state = state.Initial(self)
        self.__class__.state = self.state.name
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
            print "L: %f R: %f"%(left_d, right_d)
            self.setOdometry(left_d, right_d)

        self.sensor_values = self.readScaledIR()
        if self.pipe.poll():
            child_signal = self.pipe.recv()
            if child_signal:
                self.stop()
                exit()
        self.pipe.send(((self.x, self.y, self.phi), self.sensor_values))


        for event in self.state.events:
            if event.check():
                event.call()
                if event.transition() != None:
                    self.state = event.transition()
                # print "Transitioned to " + self.state.name

        if self.destination_unknown:
            if time() - self.start_time > 20:
                self.destination_unknown = False
                self.state = state.Homing(self)


        # print "FPS: %f"%(1/(time() - t))
        # sleep(self.TIMEOUT)

    def calibrateIR (self):
        historicIR = [[],[],[],[],[],[],[],[]]
        smoothIterations = 100
        for i in range(smoothIterations):
            vals = self.readIR()
            for i in range(8):
                historicIR[i].append(vals[i])
            sleep(self.TIMEOUT)
        min_IR_readings = [sum(list)/smoothIterations for list in historicIR]
        pickle.dump(min_IR_readings, open("min_IR_readings.p", "wb"))
        print "Minimum IR levels after calibration:\n%s"%min_IR_readings
        return min_IR_readings


    # Actions
    class Action():
        def __init__(self, robot):
            pass

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
                self.robot.setSpeeds(-5,5)
                self.events = [event.Parallel_completed(robot, [1,0])]
            else:
                print 'Right wall is closer'
                self.robot.setSpeeds(5,-5)
                self.events = [event.Parallel_completed(robot, [4,5])]

    class GoHome(Action):
        def __init__(self, robot):
            self.robot = robot
            robot.stop()
            alpha = atan(robot.y / robot.x)

            if((self.robot.phi - alpha) > pi):
				destination = pi - robot.phi - alpha
            else:
	            destination = robot.phi - alpha - pi


            destination = pi - (robot.phi % (2*pi)) - alpha
            robot.phi = robot.phi % (2*pi)
            robot.rotateTo(destination)
            self.events = []




    # Khepera functions
    def closeConnection(self):
        try:
            self.serial_connection.close()
        except Exception, e:
            print e

    def setSpeeds(self, leftSpeed, rightSpeed):
        self.serial_connection.write("D,"+str(leftSpeed)+","+str(rightSpeed)+"\n")
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
            value = int(value)
            if value < 0 or value > 1024:
                return None
        return result

    def scaleIR(self,value,i):
        return (value - self.min_IR_readings[i])/(1020 - self.min_IR_readings[i])

    """
    This will read the sensors values
    and then scale them down according to the calibration
    """
    def readScaledIR(self):
        vals = self.readIR()
        for i in range(0,len(vals)):
            vals[i] = self.scaleIR(vals[i],i)
        return vals

    def readIR(self):
        self.serial_connection.write("N\n")
        sensorString = self.serial_connection.readline()
        sensorArray = self.validateSensorValue(sensorString)

        if sensorArray != None:
            for i, value in enumerate(sensorArray):
                del self.IRqueue[i][0]
                self.IRqueue[i].append(int(value))
                self.gauss_result[i] = sum([a*b for a,b in zip(self.IRqueue[i],self.gaussArray)])
        # print sensorArray
        # print result
        return self.gauss_result

    def readAmbient(self):
        self.serial_connection.write("O\n")
        sensorString = self.serial_connection.readline()
        return self.validateSensorValue(sensorString)

    def setCounts(self, leftCount, rightCount):
        self.serial_connection.write("G,"+str(leftCount)+","+str(rightCount)+"\n")
        self.serial_connection.readline()

    def setOdometry(self,left,right):
        self.x = self.x + 0.5 * (left + right) * cos(self.phi)
        self.y = self.y + 0.5 * (left + right) * sin(self.phi)
        self.phi = self.phi - (left - right) / (4*self.wheelDiff)
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
        self.serial_connection.write("L,"+led+","+value+"\n")

    def monitorIR(self):
        while True:
            print self.readIR()
            sleep(self.TIMEOUT)

    def monitorAmbient(self):
        while True:
            print self.readAmbient()
            sleep(self.TIMEOUT)


    def hump(self):
        try:
            while True:
                self.go(100)
                sleep(0.3)
                self.go(-100)
                sleep(0.3)
        except KeyboardInterrupt, e:
            self.stop()

    def resetCounts(self):
        self.setCounts(0, 0)
        self.x = 17500
        self.y = -11500
        self.left_l = 0
        self.right_l = 0
        self.phi = pi

    def rot(self):
        self.resetCounts()
        print "x: %s \ny: %s \nphi: %s  "%(self.x, self.y, (self.phi))
        self.setSpeeds(-5, 5)

        while self.phi < 4*pi:
            data = self.readCount()
            if len(data) == 2:
                left_n = int(data[0])
                right_n = int(data[1])
                left_d = left_n - self.left_l
                self.left_l = left_n
                right_d = right_n - self.right_l
                self.right_l = right_n
                print "L: %f R: %f"%(left_d, right_d)
                self.setOdometry(left_d, right_d)

        self.setSpeeds(0,0)

        print "x: %s \ny: %s \nphi: %s  "%(self.x, self.y, (self.phi))

    def goTo(self, x):
        self.resetCounts()

        self.go(self.FULL_SPEED)

        while self.x < x:
            data = self.readCount()
            if len(data) == 2:
                left_n = int(data[0])
                right_n = int(data[1])
                left_d = left_n - self.left_l
                self.left_l = left_n
                right_d = right_n - self.right_l
                self.right_l = right_n
                print "L: %f R: %f"%(left_d, right_d)
                self.setOdometry(left_d, right_d)

        self.stop()

    def rotateTo(self, phi):
        print "Target: %f"%phi
        print "At %f"%self.phi
        if phi > 0:
            self.setSpeeds(-self.FULL_SPEED, self.FULL_SPEED)
        else:
            self.setSpeeds(self.FULL_SPEED, -self.FULL_SPEED)

        start_phi = self.phi

        print "Homing"
        while (phi>0 and self.phi < start_phi + phi) or (phi < 0 and self.phi > start_phi + phi):
            data = self.readCount()
            if len(data) == 2:
                left_n = int(data[0])
                right_n = int(data[1])
                left_d = left_n - self.left_l
                self.left_l = left_n
                right_d = right_n - self.right_l
                self.right_l = right_n
                print "L: %f R: %f"%(left_d, right_d)
                self.setOdometry(left_d, right_d)

        self.stop()

    def razhodka(self):
        self.goTo(4000.0)
        self.rotateTo(pi)
        self.goTo(4000.0)

