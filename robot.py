import serial
from multiprocessing import Process
from worldMap import WorldMap
from time import sleep
import state
import event
from math import cos, sin, pi, degrees
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
        self.wheelDiff = 163.45212655537651 # This can also be broken up to the differential plus the calibration factor
        self.gauss_result = [0]*8  # readIR result TODO: rename
        self.sensor_values = []
        self.world_map = WorldMap()

        #Odometry#####
        self.x = 0   #
        self.y = 0   #
        self.phi = 0.0 #
        self.setCounts(0, 0)

        shit = self.serial_connection.readline()
        while shit != "":
            print shit
            shit = self.serial_connection.readline()
        
        try:
            self.min_IR_readings = pickle.load(open("min_IR_readings.p", "rb"))
        except IOError:
            self.min_IR_readings = self.calibrateIR()



    def run(self):
        self.state = state.Initial(self)
        self.__class__.state = self.state.name
        try:
            while True:
                self.thick()
        except KeyboardInterrupt, e:
            self.stop()

    def thick(self):
        # print self.state.name
        self.sensor_values = self.readScaledIR()
        data = self.readCount()
        self.setCounts(0, 0)
        if len(data) > 1:
            # print "Counts are:" + str(data)
            # testVar = self.readCount()
            # print 'The counts are now ' + str(testVar)
            self.setOdometry(int(data[0]),int(data[1]))
        # print "x: %s \ny: %s \nphi: %s  "%(self.x, self.y, (self.phi))
        self.world_map.update((self.x, self.y, self.phi), self.sensor_values)
        for event in self.state.events:
            if event.check():
                event.call()
                if event.transition() != None:
                    self.state = event.transition()
                # print "Transitioned to " + self.state.name

        sleep(self.TIMEOUT)
        # sleep(1)

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
            if (left>right):
                print 'Left wall is closer'
                self.robot.setSpeeds(-5,5)
                self.events = [event.Parallel_completed(robot, [1,0])]
            else: 
                print 'Right wall is closer'
                self.robot.setSpeeds(5,-5)
                self.events = [event.Parallel_completed(robot, [4,5])]




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
        # print 'FROM ODOMETRY METHOD:'
        # print 'LEFT:'+ str(left)
        # print 'RIGHT:' + str(right)
        # print 'PHI0:' + str(self.phi)
        # print '-(left - right)' + str(self.phi - (left-right))
        # print 'DENOMINATOR:' + str(4*self.wheelDiff)
        self.phi = self.phi - (left - right) / (4.0 * self.wheelDiff)
        # print 'FIRST:' + str(self.phi)
        # self.phi = abs(self.phi) % pi
        # print 'RESULT:' + str(self.phi)
        # print 'DEGREES:' + str(degrees(self.phi % 2*pi))
        self.x = self.x + 0.5 * (left + right) * cos(self.phi)
        self.y = self.y + 0.5 * (left + right) * sin(self.phi)
        
        
        #Ensure that phi is between -3.14 and 3.14
        # if self.phi > pi: #Bigger than 180 deg
        #     self.phi = (self.phi % pi) + (-pi)
        # elif self.phi < (-pi): # Less than -180 deg
        #     self.phi = (self.phi % pi)


    def readCount(self):
        self.serial_connection.write("H\n")
        sensorString = self.serial_connection.readline()
        result = sensorString[:-2].split(",")[1:]  # Drop "\r\n" at the end of string and "n" at beginning
        return result

    def setLED(self, led, value):
        if led == "left":
            led = 0
        else:
            led = 1
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

    def rot(self):
        self.setCounts(0, 0)
        data = self.readCount()
        print "Initial Counts:" + str(data)
        #Start Rotation
        self.setSpeeds(-10,10)
        sleep(2.0800000000000001)
        self.setSpeeds(0,0)
        #Stop rotation and measure wheels
        data = self.readCount()
        if len(data) > 1:
            print "Final counts are:" + str(data[0])+ ' and ' + str(data[1])
            self.setOdometry(int(data[0]),int(data[1]))
        print "x: %s \ny: %s \nphi: %s  "%(self.x, self.y, (self.phi))


    def measureMapping(self):
        self.setCounts(0, 0)
        data = self.readCount()
        # print "Initial Counts:" + str(data)
        #Start Moving Forward
        self.setSpeeds(1,1)
        sleep(1.25)
        self.setSpeeds(0,0)
        #Stop moving forward and measure wheels
        data = self.readCount()
        if len(data) > 1:
            # print "Final counts are:" + str(data[0])+ ' and ' + str(data[1])
            self.setOdometry(int(data[0]),int(data[1]))
        # print "x: %s \ny: %s \nphi: %s  "%(self.x, self.y, (self.phi))
        print 'For 1cm, x= %s'%(self.x)
