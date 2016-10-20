import pygame
import PIL.Image as Image
from pygame.locals import *
import sys
import cv2
import numpy

cap = cv2.VideoCapture(0)
i=0
def get_image():
    ret, im = cap.read()
    #convert numpy array to PIL image
    im = numpy.array(im)
    return Image.fromarray(im)

fps = 25.0
pygame.init()
window = pygame.display.set_mode((1280,720))
pygame.display.set_caption("WebCAM Demo")
screen = pygame.display.get_surface()

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT or event.type == KEYDOWN:
            sys.exit(0)
    im = get_image()
    pg_img = pygame.image.frombuffer(im.tostring(), im.size, im.mode)

    screen.blit(pg_img, (0,0))
    pygame.display.flip()
    pygame.time.delay(int(1000 * 1.0/fps))