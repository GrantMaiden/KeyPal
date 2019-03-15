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
from pygame.locals import *
from ser.keyboardserial import KeyboardSerial

basepath = os.path.dirname(os.path.abspath(__file__))
connection = sqlite3.connect(basepath + "/words.db")

# Global game variables
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
SHIFTED = False
FIRST = True

STR_UPPER = "abcdefghijklmnopqrstuvwxyz`1234567890-=[]\;\',./"
STR_LOWER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ~!@#$%^&*()_+{}|:\"<>?"
Uppercase = str.maketrans(STR_UPPER, STR_LOWER)
Lowercase = str.maketrans(STR_LOWER, STR_UPPER)

LEVEL = 0
ERRORS = 0
WORDS = 0
CHARS = 0
SENTENCES = 0

# Sentence progress
SENTENCE = ""
SENT_INDEX = 0

WORDS_PER_MIN = 0.0
TITLE = "Beginner Mode"


def main():
    global DISPLAYSURF, LEVEL, CUR, SENTENCES, SENTENCE, SENT_INDEX, SMALLFONT, BIGFONT

    # Connect to the keyboard
    ks.autoconnect()
    if ks.is_connected():
        print("Successfully connected")
    else:
        print("Could not connect")
        return

    # Pygame game initialization
    pygame.init()
    ERROR_SOUND = pygame.mixer.Sound(os.path.join("resources", "error.wav"))

    pygame.event.set_allowed(None)
    pygame.event.set_allowed([KEYUP, KEYDOWN, QUIT])
    clock = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode([WINDOWWIDTH, WINDOWHEIGHT], pygame.FULLSCREEN)
    SMALLFONT = pygame.font.Font('freesansbold.ttf', 25)
    BIGFONT = pygame.font.Font('freesansbold.ttf', 45)
    
    pygame.display.set_caption(TITLE)

    show_title_screen(TITLE)
    pygame.event.clear()
    pygame.event.wait() # need to wait for 2 events: initial KEYDOWN & KEYUP
    pygame.event.wait()
    
    # Start the timer to keep track of seconds elapsed and WPM
    update_timer(time.time())

    # Retrieve sentence array
    sentence_array = get_sentence_list(LEVEL)
    SENTENCE = sentence_array.pop()
    set_char_light(SENTENCE[0], KeyboardSerial.LED_GREEN)

    pressed = pygame.key.get_pressed()
    shift_pressed = pressed[K_RSHIFT] or pressed[K_LSHIFT]

    # Main game loop
    running = True
    while running:
        clock.tick(30)
        # Handle user input
        for event in pygame.event.get():
            if not hasattr(event, 'key'): continue
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                ks.clear_leds()
                running = False
            if event.key == K_RSHIFT or event.key == K_LSHIFT:
                if event.type == KEYDOWN:
                    shift_pressed = True
                else:
                    shift_pressed = False
            if event.key == K_UP:
                LEVEL = min(4, LEVEL + 1)
                sentence_array = get_sentence_list(LEVEL)
            if event.key == K_DOWN:
                LEVEL = max(0, LEVEL - 1)
                sentence_array = get_sentence_list(LEVEL)
            if event.type == KEYDOWN and event.key < 256:
                charac = chr(event.key)
                if shift_pressed:
                    charac = charac.translate(Uppercase)
                letter_typed(charac)
                # Move on to a new sentence
                if SENT_INDEX == len(SENTENCE):
                    SENT_INDEX = 0
                    SENTENCES += 1
                    SENTENCE = sentence_array.pop()
                    set_char_light(SENTENCE[0], KeyboardSerial.LED_GREEN)
        
        # Draw the current state
        DISPLAYSURF.fill(BGCOLOR)
        draw_interface()
        draw_sentence()
        pygame.display.flip()

    # Cleanup on exit
    ks.disconnect()

## Game update
# runs in separate thread and shows the time on the screen
def update_timer(start):
    global WORDS_PER_MIN, WORDS, TIME
    t = threading.Timer(.1, update_timer, (start,))
    t.daemon = True
    t.start()
    #print "TIME: {}".format(time.time() - start)
    TIME = int(time.time() - start)

    if(TIME > 0 and TIME % 5 == 0): # update words per min every 5s
        WORDS_PER_MIN = float(WORDS) / TIME * 60


def get_sentence_list(level):
    global CUR
    CUR = connection.cursor()
    CUR.execute("SELECT * FROM words WHERE language = 'eng' AND level = " + str(LEVEL))
    sentence_array = list(CUR.fetchall())
    sentence_array = list(map(lambda x: x[0], sentence_array))
    random.shuffle(sentence_array)
    return sentence_array


def make_text_objs(text, font, fontcolor):
    surf = font.render(text, True, fontcolor)
    return surf, surf.get_rect()


def letter_typed(typed):
    global SENTENCE, SENT_INDEX, WORDS, CHARS, ERRORS
    target_letter = SENTENCE[SENT_INDEX]
    if typed == target_letter:
        # Update global counter variables
        SENT_INDEX += 1
        CHARS += 1
        if (target_letter == ' ' or SENT_INDEX == len(SENTENCE)):
            WORDS += 1
        # Turn off old leds
        set_char_light(target_letter, KeyboardSerial.LED_OFF)
        # Turn on new leds
        if SENT_INDEX < len(SENTENCE):
            set_char_light(SENTENCE[SENT_INDEX], KeyboardSerial.LED_GREEN)
    else:
        ERRORS += 1
        

def set_char_light(c, led_state):
    if (c == ' '):
        ks.update_leds({'SPACE_LEFT': led_state})
        ks.update_leds({'SPACE_RIGHT': led_state})
    else:
        if c in STR_LOWER:
            ks.update_leds({'SHIFT_LEFT': led_state})
            ks.update_leds({'SHIFT_RIGHT': led_state})

        key = KeyboardSerial.KEYS[KeyboardSerial.CHAR_MAP[c.translate(Lowercase)]]
        ks.update_leds({key: led_state})
        

## Game graphics
def draw_interface():
    global SENTENCES, ERRORS, WORDS, CHARS, WORDS_PER_MIN, TIME

    level_surf, level_rect = make_text_objs('Level: ' + str(LEVEL), SMALLFONT, TEXTCOLOR)
    level_rect.topleft = (10, 10)
    DISPLAYSURF.blit(level_surf, level_rect)

    error_surf, error_rect = make_text_objs('Errors: ' + str(ERRORS), SMALLFONT, TEXTCOLOR)
    error_rect.center = (int(WINDOWWIDTH / 2), level_rect.center[1])
    DISPLAYSURF.blit(error_surf, error_rect)

    word_level_surf, word_level_rect = make_text_objs('Words/Min: %.1f' % WORDS_PER_MIN, SMALLFONT, TEXTCOLOR)
    word_level_rect.topright = (WINDOWWIDTH - 10, 10)
    DISPLAYSURF.blit(word_level_surf, word_level_rect)

    sent_surf, sent_rect = make_text_objs('Sentences: ' + str(SENTENCES), SMALLFONT, TEXTCOLOR)
    sent_rect.bottomleft = (10, WINDOWHEIGHT - 10)
    DISPLAYSURF.blit(sent_surf, sent_rect)

    word_surf, word_rect = make_text_objs('Words: ' + str(WORDS), SMALLFONT, TEXTCOLOR)
    word_rect.bottomleft = (10, WINDOWHEIGHT - 20 - sent_surf.get_height())
    DISPLAYSURF.blit(word_surf, word_rect)

    char_surf, char_rect = make_text_objs('Characters: ' + str(CHARS), SMALLFONT, TEXTCOLOR)
    char_rect.bottomleft = (10, WINDOWHEIGHT - 30 - sent_surf.get_height() - word_surf.get_height())
    DISPLAYSURF.blit(char_surf, char_rect)

    time_surf, time_rect = make_text_objs('Time: ' + str(TIME), SMALLFONT, TEXTCOLOR)
    time_rect.bottomright = (WINDOWWIDTH - 10, WINDOWHEIGHT - 10)
    DISPLAYSURF.blit(time_surf, time_rect)

    
def draw_sentence():
    global SENTENCE, SENT_INDEX, BIGFONT


    title_surf, title_rect = make_text_objs(SENTENCE.upper(), BIGFONT, TEXTCOLOR)
    title_rect.center = (int(WINDOWWIDTH / 2) , int(WINDOWHEIGHT / 2) )
    DISPLAYSURF.blit(title_surf, title_rect)

    typed_text = SENTENCE[:SENT_INDEX]
    typed_surf, typed_rect = make_text_objs(typed_text.upper(), BIGFONT, TEXTHIGHLIGHT)
    typed_back_rect = typed_rect.copy()
    typed_back_rect.x = title_rect.x
    typed_back_rect.y = title_rect.y
    pygame.draw.rect(DISPLAYSURF, BGCOLOR, typed_back_rect)
    DISPLAYSURF.blit(typed_surf, title_rect)
    
    next_surf, next_rect = make_text_objs(SENTENCE[:SENT_INDEX + 1].upper(), BIGFONT, TEXTHIGHLIGHT)
    current_pos = (title_rect.x + int((typed_rect.width + next_rect.width) / 2), title_rect.y + typed_rect.height + 8)
    pygame.draw.circle(DISPLAYSURF, TEXTGUIDE, current_pos, 5)

    
def show_title_screen(text):
    title_surf, title_rect = make_text_objs(text, pygame.font.Font('freesansbold.ttf', 90), TEXTSHADOWCOLOR)
    title_rect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
    DISPLAYSURF.blit(title_surf, title_rect)

    title_surf, title_rect = make_text_objs(text, pygame.font.Font('freesansbold.ttf', 90), TEXTCOLOR)
    title_rect.center = (int(WINDOWWIDTH / 2) - 2, int(WINDOWHEIGHT / 2) - 2)
    DISPLAYSURF.blit(title_surf, title_rect)

    pygame.display.update()


if __name__ == '__main__':
    main()
