import serial
from time import sleep

import state
import event

class Robot():
    """ Robot class - what else didi you expect?! """
    # TODO: sensor valuies to INT!!!!

    def __init__(self):
        self.serial_connection = serial.Serial(0,9600, timeout=0.1)
        self.FULL_SPEED = 10
        self.TIMEOUT = 0.0005
        self.gaussArray = [1.4867195147342977e-06, 6.691511288e-05, 0.00020074533864, 0.0044318484119380075, 0.02699548325659403, 0.03142733166853204, 0.05399096651318806, 0.19947114020071635, 0.24197072451914337, 0.4414418647198597]

        self.IRqueue = [[0]*10,[0]*10,[0]*10,[0]*10,[0]*10,[0]*10,[0]*10,[0]*10]

        shit = self.serial_connection.readline()
        while shit != "":
            print shit
            shit = self.serial_connection.readline()
        
        self.historicIR = [[],[],[],[],[],[],[],[]]
        self.smoothIterations = 100
        for i in range(self.smoothIterations):
            vals = self.readIR()
            for i in range(8):
                self.historicIR[i].append(vals[i])
            sleep(self.TIMEOUT)
            # print self.historicIR 
        self.baseIR = [sum(list)/self.smoothIterations for list in self.historicIR]
        print self.baseIR



    def run(self):
        self.state = state.Initial(self)
        try:
            while True:
                self.thick()
        except KeyboardInterrupt, e:
            self.stop()

    def thick(self):
        for event in self.state.events:
            if event.check():
                event.call()
                self.state = event.transition
                print "Transitioned to " + self.state.name

        sleep(self.TIMEOUT)
        # sleep(1)


    # Actions
    class Action():
        def __init__(self, robot):
            pass            

    class Move_forward(Action):
        def __init__(self, robot):
            self.events = [event.Odometry(robot)]
            robot.go(robot.FULL_SPEED)



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
        return (value - self.baseIR[i])/(1020 - self.baseIR[i])

    """
    This will read the sensors values
    and then scale them down according to the calibration
    """
    def readScaled(self):
        vals = self.readIR()
        for i in range(0,len(vals)):
            vals[i] = self.scaleIR(vals[i],i)
        return vals

    def readIR(self):
        self.serial_connection.write("N\n")
        sensorString = self.serial_connection.readline()
        sensorArray = self.validateSensorValue(sensorString)
        result = [0]*8
        for i, value in enumerate(sensorArray):
            del self.IRqueue[i][0]
            self.IRqueue[i].append(int(value))
            result[i] = sum([a*b for a,b in zip(self.IRqueue[i],self.gaussArray)])
        # print sensorArray
        # print result
        return result

    def readAmbient(self):
        self.serial_connection.write("O\n")
        sensorString = self.serial_connection.readline()
        return self.validateSensorValue(sensorString)

    def setCounts(self, leftCount, rightCount):
        self.serial_connection.write("G,"+str(leftCount)+","+str(rightCount)+"\n")
        self.serial_connection.readline()

    def readCount(self):
        self.serial_connection.write("H\n")
        sensorString = self.serial_connection.readline()
        print self.validateSensorValue(sensorString)

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




