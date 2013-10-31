from math import radians, sin, cos
import pygame, sys
from pygame.locals import *


def worldMap(pipe):

    # == Pygame setup ==
    pygame.init()

    # set up the window
    windowSurface = pygame.display.set_mode((900, 900), 0, 32)
    pygame.display.set_caption('Goshko & Nasko rule!')

    # set up the colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (228, 120, 118)
    ORANGE = (237, 151, 81)
    GREEN = (195, 237, 81)
    BLUE = (32, 118, 186)

    windowSurface.fill(BLUE)
    world_map = pygame.PixelArray(windowSurface)
    # == End Pygame setup ==

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

    while True:
        (x, y, phi), sensorValues = pipe.recv()
        phi = -phi
        y = -y

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

        # if r_x > max_a:
        #     max_a = r_x
        #     rescale = True
        # elif r_x < min_a:
        #     min_a = r_x
        #     rescale = True
        # elif r_y > max_a:
        #     max_a = r_y
        #     rescale = True
        # elif r_y < min_a:
        #     min_a = r_y
        #     rescale = True

        # if rescale:
        #     plt.axis([min_a, max_a, min_a, max_a])
        #     rescale = False

        # robot_location = (r_x, r_y)
        # world_map[robot_location] = 2
        # # print "Robot: x-%d y-%d"%(round(r_x), round(r_y))
        # for location in obstacle_locations:
        #     world_map[location] = 1
        #     print "Wall: x- %d y- %d"%(location)

        # world_map[int(r_x)+200][int(r_y)+200] = GREEN
        lft = 200
        rght = 200

        r_pos = ( int(r_x)+lft, int(r_y)+rght )
        r_dir_pos = ( int(cos(phi)*10 + r_x + lft), int(sin(phi)*10 + r_y + lft) )

        windowSurface.fill(BLUE)
        robot = pygame.draw.circle(windowSurface, RED, r_pos, 6)
        direction = pygame.draw.line(windowSurface, RED, r_pos, r_dir_pos ,2)

        for x, y in obstacle_locations:
            world_map[int(x)+lft][int(y)+rght] = ORANGE

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()



