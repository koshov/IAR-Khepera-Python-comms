import pygame, sys
from pygame.locals import *

# set up pygame
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

# draw the white background onto the surface
windowSurface.fill(BLUE)

# draw a green polygon onto the surface
pygame.draw.polygon(windowSurface, GREEN, ((146, 0), (291, 106), (236, 277), (56, 277), (0, 106)))

# draw some blue lines onto the surface
pygame.draw.line(windowSurface, BLUE, (60, 60), (120, 60), 4)
pygame.draw.line(windowSurface, BLUE, (120, 60), (60, 120))
pygame.draw.line(windowSurface, RED, (60, 120), (120, 120), 4)

# draw a blue circle onto the surface
pygame.draw.circle(windowSurface, BLUE, (300, 50), 20, 0)

# draw a red ellipse onto the surface
pygame.draw.ellipse(windowSurface, RED, (300, 250, 40, 80), 1)

# get a pixel array of the surface
pixArray = pygame.PixelArray(windowSurface)
for x in range(100):
    for y in range(100):
        pixArray[x+200][y+300] = ORANGE
del pixArray


# draw the window onto the screen
pygame.display.update()

# run the game loop
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
