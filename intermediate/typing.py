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
connection = sqlite3.connect(basepath + "/sentences.db")

# could remove the hard-coded dimensions
WINDOWWIDTH = 1024
WINDOWHEIGHT = 768

WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
BLACK = (0, 0, 0)
LIGHTBLUE = (20, 20, 175)

ks = KeyboardSerial()

BGCOLOR = BLACK
TEXTCOLOR = WHITE
TEXTSHADOWCOLOR = GRAY
TEXTHIGHLIGHT = LIGHTBLUE
SHIFTED = False
FIRST = True

STR_UPPER = "abcdefghijklmnopqrstuvwxyz`1234567890-=[]\;\',./"
STR_LOWER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ~!@#$%^&*()_+{}|:\"<>?"
Uppercase = str.maketrans(STR_UPPER, STR_LOWER)
Lowercase = str.maketrans(STR_LOWER, STR_UPPER)

def main():
    global DISPLAYSURF, BIGFONT, BIGFONT, SMALLFONT, LEVEL, CUR, ERROR_SOUND, ERRORS, WORDS, CHARS, SENTENCES, WORDS_PER_MIN

    # print("Connecting to serial port on " + sys.argv[1])
    # ks.connect(sys.argv[1])
    # if ks.is_connected():
        # print("Successfully connected")
    # else:
        # print("Could not connect")
        # terminate()

    pygame.init()
    ERROR_SOUND = pygame.mixer.Sound("error.wav")

    pygame.event.set_allowed(None)
    pygame.event.set_allowed([KEYUP, KEYDOWN, QUIT])
    DISPLAYSURF = pygame.display.set_mode([WINDOWWIDTH, WINDOWHEIGHT], pygame.FULLSCREEN)
    SMALLFONT = pygame.font.Font('freesansbold.ttf', 25)
    BIGFONT = pygame.font.Font('freesansbold.ttf', 33)
    LEVEL = 0
    ERRORS = 0
    WORDS = 0
    CHARS = 0
    SENTENCES = 0
    WORDS_PER_MIN = 0.0
    TITLE = "Intermediate Mode"

    pygame.display.set_caption(TITLE)

    show_title_screen(TITLE)
    pygame.event.clear()
    pygame.event.wait() # need to wait for 2 events: initial KEYDOWN & KEYUP
    pygame.event.wait()
    update_timer(time.time())

    while True:
        CUR = connection.cursor()
        CUR.execute("SELECT * FROM sentences WHERE level = " + str(LEVEL))
        current_level = LEVEL
        sentence_array = list(CUR.fetchall())
        random.shuffle(sentence_array)

        for sentence in sentence_array:
            if current_level != LEVEL:
                break

            show_sentence(sentence)
            SENTENCES += 1

            pygame.display.update()
    connection.close()
    ks.disconnect()


def make_text_objs(text, font, fontcolor):
    surf = font.render(text, True, fontcolor)
    return surf, surf.get_rect()


def show_sentence(word):
    global LEVEL, ERRORS, WORDS, SHIFTED, CHARS, WORDS_PER_MIN, SENTENCES, FIRST
    text = word[0]
    DISPLAYSURF.fill(BGCOLOR)
    typed = ''
    to_type = text

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

    title_surf, title_rect = make_text_objs(text, BIGFONT, TEXTCOLOR)
    title_rect.center = (int(WINDOWWIDTH / 2) , int(WINDOWHEIGHT / 2) )
    DISPLAYSURF.blit(title_surf, title_rect)

    while typed != text:
        next_letter = to_type[0]
        if (next_letter == ' '):
            ks.update_leds({'SPACE_LEFT': 2})
            ks.update_leds({'SPACE_RIGHT': 2})
        else:
            key = KeyboardSerial.KEYS[KeyboardSerial.CHAR_MAP[next_letter.translate(Lowercase)]]#error on '!'
            ks.update_leds({key : 2})
            # ks.update_leds({next_letter.lower(): 2})
        print("light up letter: '{}'".format(next_letter))

        pygame.event.clear()
        while True:
            pygame.display.update()
            event = pygame.event.wait()
            if event.type == QUIT:
                if (next_letter == ' '):
                    ks.update_leds({'SPACE_LEFT': 0})
                    ks.update_leds({'SPACE_RIGHT': 0})
                else:
                    key = KeyboardSerial.KEYS[KeyboardSerial.CHAR_MAP[next_letter.translate(Lowercase)]]
                    ks.update_leds({key: 0})
                terminate()
            elif event.type == KEYDOWN and (event.key == K_RSHIFT or event.key == K_LSHIFT):
                SHIFTED = True
            elif event.type == KEYUP and (event.key == K_RSHIFT or event.key == K_LSHIFT):
                SHIFTED = False
            elif event.type == KEYDOWN and event.key > 0:
                if event.key == K_ESCAPE:
                    if (next_letter == ' '):
                        ks.update_leds({'SPACE_LEFT': 0})
                        ks.update_leds({'SPACE_RIGHT': 0})
                    else:
                        key = KeyboardSerial.KEYS[KeyboardSerial.CHAR_MAP[next_letter.translate(Lowercase)]]
                        ks.update_leds({key: 0})
                    terminate()
                elif event.key == K_UP: # up a level
                    LEVEL = min(4, LEVEL + 1)
                    level_surf, level_rect = make_text_objs('LevelXX: ' + str(LEVEL), SMALLFONT, TEXTCOLOR)
                    level_surf.fill(BGCOLOR)
                    level_rect.topleft = (10, 10)
                    DISPLAYSURF.blit(level_surf, level_rect)
                    level_surf, level_rect = make_text_objs('Level: ' + str(LEVEL), SMALLFONT, TEXTCOLOR)
                    level_rect.topleft = (10, 10)
                    DISPLAYSURF.blit(level_surf, level_rect)
                elif event.key == K_DOWN: # down a level
                    LEVEL = max(0, LEVEL - 1)
                    level_surf, level_rect = make_text_objs('LevelXX: ' + str(LEVEL), SMALLFONT, TEXTCOLOR)
                    level_surf.fill(BGCOLOR)
                    level_rect.topleft = (10, 10)
                    DISPLAYSURF.blit(level_surf, level_rect)
                    level_surf, level_rect = make_text_objs('Level: ' + str(LEVEL), SMALLFONT, TEXTCOLOR)
                    level_rect.topleft = (10, 10)
                    DISPLAYSURF.blit(level_surf, level_rect)
                elif event.key < 256:
                    charac = chr(event.key)
                    if SHIFTED:
                        charac = chr(event.key).translate(Uppercase)
                    #print "Pygame Name: {}".format(pygame.key.name(event.key))
                    #print "Charac: {}".format(charac)
                    if(charac == next_letter):
                        break

                    print("Expected: {} Typed: {}".format(next_letter, charac))

                    ERROR_SOUND.play()
                    ERRORS += 1
                    error_surf, error_rect = make_text_objs('ErrorsXX: ' + str(ERRORS), SMALLFONT, TEXTCOLOR)
                    error_surf.fill(BGCOLOR)
                    error_rect.center = (int(WINDOWWIDTH / 2), level_rect.center[1])
                    DISPLAYSURF.blit(error_surf, error_rect)
                    error_surf, error_rect = make_text_objs('Errors: ' + str(ERRORS), SMALLFONT, TEXTCOLOR)
                    error_rect.center = (int(WINDOWWIDTH / 2), level_rect.center[1])
                    DISPLAYSURF.blit(error_surf, error_rect)

        CHARS += 1
        if (next_letter == ' '):
            ks.update_leds({'SPACE_LEFT': 0})
            ks.update_leds({'SPACE_RIGHT': 0})
        else:
            key = KeyboardSerial.KEYS[KeyboardSerial.CHAR_MAP[next_letter.translate(Lowercase)]]
            ks.update_leds({key: 0})
        to_type = to_type[1:]
        typed = typed + next_letter
        typed_surf, typed_rect = make_text_objs(typed, BIGFONT, TEXTHIGHLIGHT)
        DISPLAYSURF.blit(typed_surf, title_rect)
        if (next_letter == ' ' or typed == text):
            WORDS += 1

        # these lines will draw a rectangle behind where the user is typing
        #rect_surf = pygame.Surface((typed_surf.get_width(), typed_surf.get_height()))
        #rect_surf.set_alpha(75)
        #rect_surf.fill(TEXTHIGHLIGHT)
        #DISPLAYSURF.blit(rect_surf, title_rect)
        sent_surf, sent_rect = make_text_objs('SentencesXX: ' + str(SENTENCES), SMALLFONT, TEXTCOLOR)
        sent_rect.bottomleft = (10, WINDOWHEIGHT - 10)
        sent_surf.fill(BGCOLOR)
        DISPLAYSURF.blit(sent_surf, sent_rect)
        sent_surf, sent_rect = make_text_objs('Sentences: ' + str(SENTENCES), SMALLFONT, TEXTCOLOR)
        sent_rect.bottomleft = (10, WINDOWHEIGHT - 10)
        DISPLAYSURF.blit(sent_surf, sent_rect)
        word_surf, word_rect = make_text_objs('WordsXX: ' + str(WORDS), SMALLFONT, TEXTCOLOR)
        word_rect.bottomleft = (10, WINDOWHEIGHT - 20 - sent_surf.get_height())
        word_surf.fill(BGCOLOR)
        DISPLAYSURF.blit(word_surf, word_rect)
        word_surf, word_rect = make_text_objs('Words: ' + str(WORDS), SMALLFONT, TEXTCOLOR)
        word_rect.bottomleft = (10, WINDOWHEIGHT - 20 - sent_surf.get_height())
        DISPLAYSURF.blit(word_surf, word_rect)
        char_surf, char_rect = make_text_objs('CharactersXX: ' + str(CHARS), SMALLFONT, TEXTCOLOR)
        char_rect.bottomleft = (10, WINDOWHEIGHT - 30 - sent_surf.get_height() - word_surf.get_height())
        char_surf.fill(BGCOLOR)
        DISPLAYSURF.blit(char_surf, char_rect)
        char_surf, char_rect = make_text_objs('Characters: ' + str(CHARS), SMALLFONT, TEXTCOLOR)
        char_rect.bottomleft = (10, WINDOWHEIGHT - 30 - sent_surf.get_height() - word_surf.get_height())
        DISPLAYSURF.blit(char_surf, char_rect)


def show_title_screen(text):
    title_surf, title_rect = make_text_objs(text, pygame.font.Font('freesansbold.ttf', 90), TEXTSHADOWCOLOR)
    title_rect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
    DISPLAYSURF.blit(title_surf, title_rect)

    title_surf, title_rect = make_text_objs(text, pygame.font.Font('freesansbold.ttf', 90), TEXTCOLOR)
    title_rect.center = (int(WINDOWWIDTH / 2) - 2, int(WINDOWHEIGHT / 2) - 2)
    DISPLAYSURF.blit(title_surf, title_rect)

    pygame.display.update()

# runs in separate thread and shows the time on the screen
def update_timer(start):
    global DISPLAYSURF, WORDS_PER_MIN, WORDS
    t = threading.Timer(.1, update_timer, (start,))
    t.daemon = True
    t.start()
    #print "TIME: {}".format(time.time() - start)
    difference = int(time.time() - start)
    time_surf, time_rect = make_text_objs('TimeXX: ' + str(difference), SMALLFONT, TEXTCOLOR)
    time_surf.fill(BGCOLOR)
    time_rect.bottomright = (WINDOWWIDTH - 10, WINDOWHEIGHT - 10)
    DISPLAYSURF.blit(time_surf, time_rect)
    time_surf, time_rect = make_text_objs('Time: ' + str(difference), SMALLFONT, TEXTCOLOR)
    time_rect.bottomright = (WINDOWWIDTH - 10, WINDOWHEIGHT - 10)
    DISPLAYSURF.blit(time_surf, time_rect)

    if(difference > 0 and difference % 5 == 0): # update words per min every 5s
        WORDS_PER_MIN = float(WORDS) / difference * 60
        word_level_surf, word_level_rect = make_text_objs('Words/MinXX: %.1f' % WORDS_PER_MIN, SMALLFONT, TEXTCOLOR)
        word_level_surf.fill(BGCOLOR)
        word_level_rect.topright = (WINDOWWIDTH - 10, 10)
        DISPLAYSURF.blit(word_level_surf, word_level_rect)
        word_level_surf, word_level_rect = make_text_objs('Words/Min: %.1f' % WORDS_PER_MIN, SMALLFONT, TEXTCOLOR)
        word_level_rect.topright = (WINDOWWIDTH - 10, 10)
        DISPLAYSURF.blit(word_level_surf, word_level_rect)

    pygame.display.update()


def terminate():
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
