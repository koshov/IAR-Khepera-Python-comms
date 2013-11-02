def calibrateIR (robot):
    historicIR = [[],[],[],[],[],[],[],[]]
    smoothIterations = 100
    for i in range(smoothIterations):
        vals = robot.readIR()
        for i in range(8):
            historicIR[i].append(vals[i])
        sleep(robot.TIMEOUT)
    min_IR_readings = [sum(list)/smoothIterations for list in historicIR]
    pickle.dump(min_IR_readings, open("min_IR_readings.p", "wb"))
    print "Minimum IR levels after calibration:\n%s"%min_IR_readings
    return min_IR_readings
