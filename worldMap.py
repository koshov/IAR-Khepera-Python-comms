from math import radians, sin, cos
import pygame, sys
from pygame.locals import *


def worldMap(pipe):

    # == Pygame setup ==
    pygame.init()

    # set up the window
    windowSurface = pygame.display.set_mode((880, 580))
    pygame.display.set_caption('Goshko & Nasko rule!')

    # set up the colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (228, 60, 80)
    ORANGE = (237, 151, 81)
    GREEN = (195, 237, 81)
    BLUE = (32, 118, 186)

    # windowSurface.fill(BLUE)
    # world_map = pygame.PixelArray(windowSurface)

    world_map = pygame.image.load('map.bmp').convert() # Speedup image drawing
    world_map = pygame.transform.scale(world_map, (880, 580))
    windowSurface.blit(world_map, (0,0))
    pygame.display.update()
    # == End Pygame setup ==

    resolution = 20.0
    wall_distance = 615 / resolution
    threshhold = 0.1
    khepera_angles = [305, 325, 350, 10, 35, 55] #[55, 35, 10, 350, 325, 305]
    sensor_angles = [radians(x) for x in khepera_angles]


    # == Robot placement ==
    mx = 0
    my = 0
    placing = True
    while placing:
        for event in pygame.event.get():
            if event.type == QUIT:
                pipe.send(True)
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                mx = event.pos[0]
                my = event.pos[1]
                windowSurface.blit(world_map, (0,0))
                # pygame.draw.line(windowSurface, GREEN, r_pos, r_dir_pos ,2)
                pygame.draw.circle(windowSurface, BLUE, (mx,my), 20)

                pygame.display.update()
            elif event.type == MOUSEBUTTONUP:
                # placing = False
                mx_l = event.pos[0]
                my_l = event.pos[1]
                windowSurface.blit(world_map, (0,0))
                pygame.draw.line(windowSurface, GREEN, (mx,my), (mx_l,my_l) ,2)
                pygame.draw.circle(windowSurface, BLUE, (mx,my), 20)

                pygame.display.update()

    # == End Robot placement ==


    while True:
        (x, y, phi), sensorValues = pipe.recv()
        phi = -phi  # Revert Y and Phi do the differences in origin
        y = -y

        r_x = x/resolution
        r_y = y/resolution

        temp_angles = [a + phi for a in sensor_angles]

        obstacle_locations = []
        for i in range(6):
            if sensorValues[i] > threshhold:
                a = temp_angles[i]
                a_location = ( round(cos(a)*wall_distance + r_x), round(sin(a)*wall_distance + r_y) )
                obstacle_locations.append( a_location )

        left_offset = 0
        right_offset = 0

        r_x = int(round(r_x)) + left_offset
        r_y = int(round(r_y)) + right_offset


        r_pos = ( r_x, r_y )
        r_dir_pos = ( int(cos(phi)*30 + r_x), int(sin(phi)*30 + r_y) )

        # windowSurface.fill(BLUE)
        windowSurface.blit(world_map, (0,0))
        pygame.draw.line(windowSurface, GREEN, r_pos, r_dir_pos ,2)
        pygame.draw.circle(windowSurface, BLUE, r_pos, 20)

        pygame.display.update()
        # for x, y in obstacle_locations:
        #     if (r_x > 0 and r_x < world_map.get_width() and r_y > 0 and r_y < world_map.get_height()):
        #         world_map[r_x][r_y] = ORANGE



        for event in pygame.event.get():
            if event.type == QUIT:
                pipe.send(True)
                pygame.quit()
                sys.exit()



