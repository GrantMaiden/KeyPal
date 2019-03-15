'''
	Adapted from https://github.com/NoOutlet/ToddlerType

	To get started, just run "python typing.py". You can then press any key on the title screen to get to the words.
	Use the up/down arrow keys to change the level and difficulty of the words.
	The program uses a SQLite database which is included. Also included are a json and a csv of the words.
	
	Dependencies
	============
	* Python 2.7
	* Pygame
	* SQLite3
'''

# TODO: word wrap long words, edit some of the sentences

import random
import sqlite3
import pygame
import sys
import os
import threading
import time
import beginner_2, intermediate, advanced, light_keys, capacitive
from pygame.locals import *
from ser.keyboardserial import KeyboardSerial

basepath = os.path.dirname(os.path.abspath(__file__))
connection = sqlite3.connect(basepath + "/sentences.db")

# Global game variables
WINDOWWIDTH = 1024
WINDOWHEIGHT = 768

WHITE = (255, 255, 255) 
GRAY = (180, 180, 180)
BLACK = (0, 0, 0)
LIGHTBLUE = (20, 20, 175)
DARKBLUE = (0, 0, 125)
GREEN = (80, 190, 20)

ks = KeyboardSerial()

BGCOLOR = BLACK
TEXTCOLOR = WHITE
TEXTSHADOWCOLOR = GRAY
TEXTHIGHLIGHT = LIGHTBLUE
TEXTGUIDE = GREEN
SHIFTED = False
FIRST = True
TITLE = "KeyPal Demo"
TITLES = ["Mother of all demos: Sensors", "Mother of all demos: Lights",
        "KeyPal Client: Beginner", "KeyPal Client: Intermediate", "KeyPal Client: Advanced"]
PROGRAMS = [capacitive, light_keys, beginner_2, intermediate, advanced]

SELECT = 0

def main():
    global DISPLAYSURF, SMALLFONT, BIGFONT, SELECT

    # Connect to the keyboard
    ks.autoconnect()
    if ks.is_connected():
        print("Successfully connected")
    else:
        print("Could not connect")
        terminate()

    # Pygame game initialization
    pygame.init()
    ERROR_SOUND = pygame.mixer.Sound(os.path.join("resources", "error.wav"))

    pygame.event.set_allowed(None)
    pygame.event.set_allowed([KEYUP, KEYDOWN, QUIT])
    clock = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode([WINDOWWIDTH, WINDOWHEIGHT], pygame.FULLSCREEN)
    SMALLFONT = pygame.font.Font('freesansbold.ttf', 25)
    BIGFONT = pygame.font.Font('freesansbold.ttf', 33)
    
    pygame.display.set_caption(TITLE)
    show_title_screen(TITLE)
    pygame.display.flip()

    pygame.event.clear()
    pygame.event.wait() # need to wait for 2 events: initial KEYDOWN & KEYUP
    pygame.event.wait()

    # Main game loop
    while True:
        clock.tick(30)
        # Handle user input
        for event in pygame.event.get():
            if not hasattr(event, 'key'): continue
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                ks.clear_leds()
                terminate()
            if event.type == KEYDOWN:
                if event.key == K_UP:
                    SELECT -= 1
                    if SELECT < 0:
                        SELECT = len(PROGRAMS) - 1
                if event.key == K_DOWN:
                    SELECT += 1
                    if SELECT >= len(PROGRAMS):
                        SELECT = 0
                if event.key == pygame.K_RETURN:
                    ks.disconnect()
                    PROGRAMS[SELECT].main()
                    
        # Draw the current state
        DISPLAYSURF.fill(BGCOLOR)
        draw_interface()
        pygame.display.flip()

    # Cleanup on exit
    connection.close()
    ks.disconnect()
    

def draw_interface():
    global BIGFONT
    y = int(WINDOWHEIGHT / 2.5)
    i = 0
    for title in TITLES: 
        text_col = TEXTCOLOR
        text_back = TEXTSHADOWCOLOR
        if SELECT == i:
            text_col = TEXTHIGHLIGHT
            text_back = DARKBLUE
        title_surf, title_rect = make_text_objs(title, BIGFONT, text_back)
        title_rect.center = (int(WINDOWWIDTH / 2), y)
        DISPLAYSURF.blit(title_surf, title_rect)
        
        title_surf, title_rect = make_text_objs(title, BIGFONT, text_col)
        title_rect.center = (int(WINDOWWIDTH / 2) - 2, y - 2)
        DISPLAYSURF.blit(title_surf, title_rect)
        y += 42
        i += 1


def show_title_screen(text):
    title_surf, title_rect = make_text_objs(text, pygame.font.Font('freesansbold.ttf', 90), TEXTSHADOWCOLOR)
    title_rect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
    DISPLAYSURF.blit(title_surf, title_rect)

    title_surf, title_rect = make_text_objs(text, pygame.font.Font('freesansbold.ttf', 90), TEXTCOLOR)
    title_rect.center = (int(WINDOWWIDTH / 2) - 2, int(WINDOWHEIGHT / 2) - 2)
    DISPLAYSURF.blit(title_surf, title_rect)


def make_text_objs(text, font, fontcolor):
    surf = font.render(text, True, fontcolor)
    return surf, surf.get_rect()

def terminate():
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
