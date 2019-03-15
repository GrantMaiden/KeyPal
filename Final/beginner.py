'''
	Adapted from https://github.com/NoOutlet/ToddlerType

	To get started, just run "python typing.py SERIAL_PORT". You can then press any key on the title screen to get to the words.
	Use the up/down arrow keys to change the level and difficulty of the words.
	The program uses a SQLite database which is included. Also included are a json and a csv of the words.
	
	An example of a serial port is: '/dev/ttyS1' or 'COM3' or '/dev/ttyUSB0'
	
	Dependencies
	============
	* Python 2.7
	* Pygame
	* SQLite3
'''

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

# could remove the hard-coded dimensions
WINDOWWIDTH = 1024
WINDOWHEIGHT = 768

WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
BLACK = (0, 0, 0)
LIGHTBLUE = (20, 20, 175)

BGCOLOR = BLACK
TEXTCOLOR = WHITE
TEXTSHADOWCOLOR = GRAY
TEXTHIGHLIGHT = LIGHTBLUE

ks = KeyboardSerial()
    
RUNNING = True
def main():
    global DISPLAYSURF, BIGFONT, TITLEFONT, SMALLFONT, LEVEL, CUR, ERROR_SOUND, ERRORS, WORDS, WORDS_PER_MIN, RUNNING, TIMER_THREAD

    ks.autoconnect()
    if ks.is_connected():
        print("Successfully connected")
    else:
        print("Could not connect")
        terminate()

    pygame.init()
    ERROR_SOUND = pygame.mixer.Sound(os.path.join("resources", "error.wav"))
    

    pygame.event.set_allowed(None)
    pygame.event.set_allowed([KEYUP, QUIT])
    DISPLAYSURF = pygame.display.set_mode([WINDOWWIDTH, WINDOWHEIGHT], pygame.FULLSCREEN)
    SMALLFONT = pygame.font.Font('freesansbold.ttf', 40)
    TITLEFONT = pygame.font.Font('freesansbold.ttf', 60)
    BIGFONT = pygame.font.Font('freesansbold.ttf', 120)
    LEVEL = 0
    ERRORS = 0
    WORDS = 0
    WORDS_PER_MIN = 0.0
    TITLE = "Beginner Mode"

    pygame.display.set_caption(TITLE)

    show_title_screen(TITLE)
    pygame.event.clear()
    pygame.event.wait()
    # update_timer(time.time())
    TIMER_THREAD = threading.Timer(.1, update_timer, (start,))
    TIMER_THREAD.daemon = True
    TIMER_THREAD.start()


    while RUNNING:
        CUR = connection.cursor()
        CUR.execute("SELECT * FROM words WHERE language = 'eng' AND level = " + str(LEVEL))
        current_level = LEVEL
        wordArray = list(CUR.fetchall())
        random.shuffle(wordArray)

        for word in wordArray:
            if current_level != LEVEL:
                break

            show_word(word)
            if not RUNNING:
                break
            WORDS += 1

            pygame.display.update()
            #pygame.time.wait(1000)
    connection.close()
    ks.disconnect()
    TIMER_THREAD.cancel()


def make_text_objs(text, font, fontcolor):
    surf = font.render(text, True, fontcolor)
    return surf, surf.get_rect()


def show_word(word):
    global LEVEL, ERRORS, WORDS, RUNNING
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

    word_surf, word_rect = make_text_objs('Words: ' + str(WORDS), SMALLFONT, TEXTCOLOR)
    word_rect.bottomleft = (10, WINDOWHEIGHT - 10)
    DISPLAYSURF.blit(word_surf, word_rect)

    title_surf, title_rect = make_text_objs(text.upper(), BIGFONT, TEXTSHADOWCOLOR)
    title_rect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
    DISPLAYSURF.blit(title_surf, title_rect)

    title_surf, title_rect = make_text_objs(text.upper(), BIGFONT, TEXTCOLOR)
    title_rect.center = (int(WINDOWWIDTH / 2) - 2, int(WINDOWHEIGHT / 2) - 2)
    DISPLAYSURF.blit(title_surf, title_rect)

    while typed != text:
        next_letter = to_type[0]
        ks.update_leds({next_letter : 2})

        pygame.event.clear()
        while True:
            pygame.display.update()
            event = pygame.event.wait()
            if event.type == QUIT:
                ks.update_leds({next_letter: 0})
                terminate()
                return
            elif event.type == KEYUP:
                if event.key == K_ESCAPE:
                    ks.update_leds({next_letter: 0})
                    terminate()
                    return
                elif pygame.key.name(event.key) == next_letter:
                    break
                elif event.key == K_UP: # up a level
                    LEVEL = min(7, LEVEL + 1)
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
                elif pygame.key.name(event.key) != "unknown key":
                    ERROR_SOUND.play()
                    ERRORS += 1
                    #print "Expected key: {}\tGot key: {}".format(next_lffdddetter, pygame.key.name(event.key))
                    error_surf, error_rect = make_text_objs('ErrorsXX: ' + str(ERRORS), SMALLFONT, TEXTCOLOR)
                    error_surf.fill(BGCOLOR)
                    error_rect.center = (int(WINDOWWIDTH / 2), level_rect.center[1])
                    DISPLAYSURF.blit(error_surf, error_rect)
                    error_surf, error_rect = make_text_objs('Errors: ' + str(ERRORS), SMALLFONT, TEXTCOLOR)
                    error_rect.center = (int(WINDOWWIDTH / 2), level_rect.center[1])
                    DISPLAYSURF.blit(error_surf, error_rect)
                    
                '''
                elif K_0 <= event.key <= K_7:
                    newlevel = int(pygame.key.name(event.key))
                    CUR.execute("UPDATE words SET level = " + str(newlevel) + " WHERE word = '" + word[0] + "'")
                    word_level_surf, word_level_rect = make_text_objs('Word: ' + str(newlevel), SMALLFONT, TEXTCOLOR)
                    word_level_rect.topright = (WINDOWWIDTH - 10, 10)
                    word_level_surf.fill(BGCOLOR)
                    DISPLAYSURF.blit(word_level_surf, word_level_rect)
                    word_level_surf, word_level_rect = make_text_objs('Word: ' + str(newlevel), SMALLFONT, TEXTCOLOR)
                    word_level_rect.topright = (WINDOWWIDTH - 10, 10)
                    DISPLAYSURF.blit(word_level_surf, word_level_rect)
                '''
        ks.update_leds({next_letter: 0})
        to_type = to_type[1:]
        typed = typed + next_letter
        typed_surf, typed_rect = make_text_objs(typed.upper(), BIGFONT, TEXTHIGHLIGHT)
        DISPLAYSURF.blit(typed_surf, title_rect)


def show_title_screen(text):
    title_surf, title_rect = make_text_objs(text, TITLEFONT, TEXTSHADOWCOLOR)
    title_rect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
    DISPLAYSURF.blit(title_surf, title_rect)

    title_surf, title_rect = make_text_objs(text, TITLEFONT, TEXTCOLOR)
    title_rect.center = (int(WINDOWWIDTH / 2) - 2, int(WINDOWHEIGHT / 2) - 2)
    DISPLAYSURF.blit(title_surf, title_rect)

    pygame.display.update()

# runs in separate thread and shows the time on the screen
def update_timer(start):
    global DISPLAYSURF, WORDS, WORDS_PER_MIN
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
    global RUNNING, TIMER_THREAD
    # Kill the silly timer
    RUNNING = False


if __name__ == '__main__':
    main()
