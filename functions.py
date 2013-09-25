import serial


def openConnection():
	return serial.Serial(0,9600)

def closeConnection(serial_connection):
	try:
		serial_connection.close()
	except Exception, e:
		print e

def setSpeeds(serial_connection, leftSpeed, rightSpeed):
	serial_connection.write("D,"+str(leftSpeed)+","+str(rightSpeed)+"\n")
	serial_connection.readline()

def go(serial_connection, speed):
	setSpeeds(serial_connection, speed, speed)

def stop(serial_connection):
	go(s,0)

def readIR(serial_connection):
	serial_connection.write("N\n")
	sensorString = serial_connection.readline()
	return sensorString[:-2].split(",")[1:]  # Drop "\r\n" at the end of string and "n" at beginning

def readAmbient(serial_connection):
	serial_connection.write("O\n")
	sensorString = serial_connection.readline()
	return sensorString[:-2].split(",")[1:]  # Drop "\r\n" at the end of string and "o" at beginning

def setCounts(serial_connection, leftCount, rightCount):
	serial_connection.write("G,"+str(leftCount)+","+str(rightCount)+"\n")
	serial_connection.readline()

def readCount(serial_connection):
	serial_connection.write("H\n")
	sensorString = serial_connection.readline()
	print sensorString[:-2].split(",")[1:]  # Drop "\r\n" at the end of string and "h" at beginning