import serial
import matplotlib.pyplot as plt
import numpy as np

ser = serial.Serial(0, 9600)

def setup_backend(backend='TkAgg'):
    import sys
    del sys.modules['matplotlib.backends']
    del sys.modules['matplotlib.pyplot']
    import matplotlib as mpl
    mpl.use(backend)  # do this before importing pyplot
    import matplotlib.pyplot as plt
    return plt

#Returns a list with the 8 elements for the sensor values. 
def readIR(ser):
        ser.write("N\n")
        sensorString = ser.readline()
        # Drop "\r\n" at the end of string and "n" at beginning
        return sensorString[:-2].split(",")[1:]  


def animate():
    N = 8
    rects = plt.bar(range(N), range(0,8), align='center')

    while True:
    	
    	for i in range(8):
    		# x = data[i]
    		for rect, h in zip(rects, readIR(ser)):
    			if(h.isdigit()==True):
    				rect.set_height(int(h))
    		fig.canvas.draw()

# plt.yticks(range(1,1000))
plt = setup_backend()
fig = plt.figure()
plt.axis([0, 7, 0, 1100])
win = fig.canvas.manager.window
win.after(10, animate)
plt.show()