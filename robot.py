import serial

class Robot():
	""" Robot class - what else didi you expect?! """

	def __init__(self):
		self.serial_connection = serial.Serial(0,9600)

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

	def readIR(self):
		self.serial_connection.write("N\n")
		sensorString = self.serial_connection.readline()
		return sensorString[:-2].split(",")[1:]  # Drop "\r\n" at the end of string and "n" at beginning

	def readAmbient(self):
		self.serial_connection.write("O\n")
		sensorString = self.serial_connection.readline()
		return sensorString[:-2].split(",")[1:]  # Drop "\r\n" at the end of string and "o" at beginning

	def setCounts(self, leftCount, rightCount):
		self.serial_connection.write("G,"+str(leftCount)+","+str(rightCount)+"\n")
		self.serial_connection.readline()

	def readCount(self):
		self.serial_connection.write("H\n")
		sensorString = self.serial_connection.readline()
		print sensorString[:-2].split(",")[1:]  # Drop "\r\n" at the end of string and "h" at beginning