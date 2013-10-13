from math import radians, sin, cos

import matplotlib.pyplot as pylab
import numpy


class WorldMap():
    """
    Map legend:
    1 - obstacle
    2 - robot path 
    """
    
    def __init__(self, pipe):
        self.pipe = pipe

        self.world_map = {}
        self.resolution = 100.0
        self.wall_distance = 600 / self.resolution
        self.threshhold = 0.2
        khepera_angles = [305, 325, 350, 10, 35, 55]
        self.sensor_angles = [radians(x) for x in khepera_angles]

        pylab.ion()
        pylab.hold(False)
        pylab.show()
        # self.hl, = plt.plot([], [])
        self.xs = []
        self.ys = []
        print "kur"


    def update(self, (x, y, phi), sensorValues):
        r_x = x/self.resolution
        r_y = y/self.resolution

        temp_angles = [x + phi for x in self.sensor_angles]
        d = self.wall_distance

        obstacle_locations = []
        for i in range(6):
            if sensorValues[i] > self.threshhold:
                a = self.sensor_angles[i]
                a_location = ( round(cos(a)*d + r_x), round(sin(a)*d + r_y) )
                obstacle_locations.append( a_location )


        robot_location = (round(r_x), round(r_y))
        self.world_map[robot_location] = 2
        # print "Robot: x-%d y-%d"%(round(r_x), round(r_y))
        self.update_plot(robot_location)
        for location in obstacle_locations:
            self.world_map[location] = 1
            print "Wall: x- %d y- %d"%(location)

    def update_plot(self,  (x, y)):
        self.xs.append(x)
        self.ys.append(y)
        pylab.plot(self.xs, self.ys)
        # pylab.show()
        # pylab.draw()




