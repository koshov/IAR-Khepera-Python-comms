from math import radians, sin, cos

import matplotlib.pyplot as pl
import numpy


def worldMap(pipe):
    """
    Map legend:
    1 - obstacle
    2 - robot path 
    """
    import matplotlib.pyplot as plt
    import numpy as np

    def setup_backend(backend='TkAgg'):
        import sys
        del sys.modules['matplotlib.backends']
        del sys.modules['matplotlib.pyplot']
        import matplotlib as mpl
        mpl.use(backend)  # do this before importing pyplot
        import matplotlib.pyplot as plt
        return plt

    def loop():

        # world_map = {}
        resolution = 10.0
        wall_distance = 200 / resolution
        threshhold = 0.1
        khepera_angles = [55, 35, 10, 350, 325, 305]
        sensor_angles = [radians(x) for x in khepera_angles]

        xs = [0]
        ys = [0]
        max_a = 200
        min_a = -200
        rescale = False

        plt.axis([min_a, max_a, min_a, max_a])

        wall_xs = []
        wall_ys = []

        while True:
            (x, y, phi), sensorValues = pipe.recv()

            r_x = x/resolution
            r_y = y/resolution

            temp_angles = [a + phi for a in sensor_angles]

            obstacle_locations = []
            for i in range(6):
                if sensorValues[i] > threshhold:
                    a = sensor_angles[i]
                    a_location = ( round(cos(a)*wall_distance + r_x), round(sin(a)*wall_distance + r_y) )
                    obstacle_locations.append( a_location )

            r_x = round(r_x)
            r_y = round(r_y)

            if r_x > max_a:
                max_a = r_x
                rescale = True
            elif r_x < min_a:
                min_a = r_x
                rescale = True
            elif r_y > max_a:
                max_a = r_y
                rescale = True
            elif r_y < min_a:
                min_a = r_y
                rescale = True

            if rescale:
                plt.axis([min_a, max_a, min_a, max_a])
                rescale = False

            # robot_location = (r_x, r_y)
            # world_map[robot_location] = 2
            # # print "Robot: x-%d y-%d"%(round(r_x), round(r_y))
            # for location in obstacle_locations:
            #     world_map[location] = 1
            #     print "Wall: x- %d y- %d"%(location)

            xs.append(r_x)
            ys.append(r_y)

            wall_xs += [x for (x,y) in obstacle_locations]
            wall_ys += [y for (x,y) in obstacle_locations]

            plt.plot(xs, ys, 'b+')
            plt.plot(wall_xs, wall_ys, 'ro')
            fig.canvas.draw()
        


    plt = setup_backend()
    fig = plt.figure()
    # plt.autoscale(enable=True, axis='both', tight=None)
    win = fig.canvas.manager.window
    win.after(1, loop)
    plt.show()




