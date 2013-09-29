import serial
from time import sleep

import state
import event

class Robot():
    """ Robot class - what else didi you expect?! """
    # TODO: sensor valuies to INT!!!!

    def __init__(self):
        self.serial_connection = serial.Serial(0,9600, timeout=0.1)
        self.FULL_SPEED = 20
        self.TIMEOUT = 0.001  # 1ms

        # self.serial_connection.write("D,0,0\n")
        shit = self.serial_connection.readline()
        while shit != "":
            print shit
            # self.serial_connection.write("D,0,0\n")
            shit = self.serial_connection.readline()

        sleep(1)
        self.state = state.Initial(self)

        while True:
            self.thick()

    def thick(self):
        for event in self.state.events:
            if event.check():
                event.call()
                self.state = event.transition
                print "Transitioned to " + self.state.name

        sleep(self.TIMEOUT)

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

    def readIR(self):
        self.serial_connection.write("N\n")
        sensorString = self.serial_connection.readline()
        return self.validateSensorValue(sensorString)

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




