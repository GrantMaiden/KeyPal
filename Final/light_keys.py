import sys, time
import pygame, pygame_textinput
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

STR_UPPER = "abcdefghijklmnopqrstuvwxyz`1234567890-=[]\;\',./"
STR_LOWER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ~!@#$%^&*()_+{}|:\"<>?"
Uppercase = str.maketrans(STR_UPPER, STR_LOWER)
Lowercase = str.maketrans(STR_LOWER, STR_UPPER)

def main():

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

    textinput = pygame_textinput.TextInput('freesansbold.ttf', 25, True, TEXTCOLOR)
    
    running = True
    while running:
        clock.tick(30)
        DISPLAYSURF.fill(BGCOLOR)
        # Detect exit events
        events = pygame.event.get()
        for event in events:
            if not hasattr(event, 'key'): continue
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                ks.clear_leds()
                running = False
            if event.type == KEYDOWN and event.key == K_RETURN:
                last = ' '
                text = textinput.get_text()
                for c in text:
                    light(last, KeyboardSerial.LED_OFF)
                    light(c, KeyboardSerial.LED_GREEN)
                    last = c
                    time.sleep(0.5)
                ks.clear_leds()


        textinput.update(events)
        DISPLAYSURF.blit(textinput.get_surface(), (10, 10))
        pygame.display.flip()
            
    ks.disconnect()


def show_title_screen(text):
    title_surf, title_rect = make_text_objs(text, pygame.font.Font('freesansbold.ttf', 90), TEXTSHADOWCOLOR)
    title_rect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
    DISPLAYSURF.blit(title_surf, title_rect)

    title_surf, title_rect = make_text_objs(text, pygame.font.Font('freesansbold.ttf', 90), TEXTCOLOR)
    title_rect.center = (int(WINDOWWIDTH / 2) - 2, int(WINDOWHEIGHT / 2) - 2)
    DISPLAYSURF.blit(title_surf, title_rect)

    pygame.display.update()


def light(char, state):
    if (char == ' '):
        ks.update_leds({'SPACE_LEFT': state})
        ks.update_leds({'SPACE_RIGHT': state})
    else:
        key = KeyboardSerial.KEYS[KeyboardSerial.CHAR_MAP[char.translate(Lowercase)]]
        ks.update_leds({key: state})


if __name__ == "__main__": main()
