import sys, time
import pygame
from pygame.locals import *
from ser.keyboardserial import KeyboardSerial

WINDOWWIDTH = 1024
WINDOWHEIGHT = 768

WHITE = (255, 255, 255) 
GRAY = (180, 180, 180)
BLACK = (0, 0, 0)
LIGHTBLUE = (20, 20, 175)
GREEN = (80, 190, 20)

ks = KeyboardSerial()

BGCOLOR = BLACK
TEXTCOLOR = WHITE
TEXTSHADOWCOLOR = GRAY
TEXTHIGHLIGHT = LIGHTBLUE
TEXTGUIDE = GREEN

def main():
    global DISPLAYSURF, SMALLFONT, BIGFONT
    ks = KeyboardSerial()

    ks.autoconnect()
    if ks.is_connected():
        print("Successfully connected")
                    
    pygame.init()
    pygame.event.set_allowed(None)
    pygame.event.set_allowed([KEYUP, KEYDOWN, QUIT])
    clock = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode([WINDOWWIDTH, WINDOWHEIGHT], pygame.FULLSCREEN)
    SMALLFONT = pygame.font.Font('freesansbold.ttf', 25)
    BIGFONT = pygame.font.Font('freesansbold.ttf', 33)

    show_title_screen("Capacitive Touch Demo")

    def threshhold(x):
        if x > 12:
            return 2
        return 1

    oldData = {}
    running = True
    while running:
        clock.tick(30)
        data = ks.get_sensor_data()
        # DO DATA PROCESSING
        data = list(map(threshhold, data))
        ks.update_leds({'a': data[5], 's': data[1], 'd': data[4], 'f': data[3], 'j': data[0], 'k': data[2], 'l': data[7], ';': data[6]})
        # Detect exit events
        for event in pygame.event.get():
            if not hasattr(event, 'key'): continue
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                ks.clear_leds()
                running = False
            
    ks.disconnect()


def make_text_objs(text, font, fontcolor):
    surf = font.render(text, True, fontcolor)
    return surf, surf.get_rect()


def show_title_screen(text):
    global DISPLAYSURF, SMALLFONT, BIGFONT
    title_surf, title_rect = make_text_objs(text, pygame.font.Font('freesansbold.ttf', 60), TEXTSHADOWCOLOR)
    title_rect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
    DISPLAYSURF.blit(title_surf, title_rect)

    title_surf, title_rect = make_text_objs(text, pygame.font.Font('freesansbold.ttf', 60), TEXTCOLOR)
    title_rect.center = (int(WINDOWWIDTH / 2) - 2, int(WINDOWHEIGHT / 2) - 2)
    DISPLAYSURF.blit(title_surf, title_rect)

    pygame.display.update()

