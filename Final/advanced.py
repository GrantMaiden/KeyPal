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

# Global game variables
WINDOWWIDTH = 1024
WINDOWHEIGHT = 768

WHITE = (255, 255, 255) 
GRAY = (120, 120, 120)
BLACK = (0, 0, 0)
LIGHTBLUE = (40, 40, 195)
GREEN = (80, 190, 20)
DARKGREEN = (20, 120, 20)

ks = KeyboardSerial()

# Global resource map
RESOURCES = {}

BGCOLOR = BLACK
TEXTCOLOR = WHITE
TEXTSHADOWCOLOR = GRAY
TEXTHIGHLIGHT = LIGHTBLUE
TEXTGUIDE = GREEN
SHIFTED = False
SHIFT_RIGHT = False
SHIFT_LEFT = False
FIRST = True

STR_UPPER = "abcdefghijklmnopqrstuvwxyz`1234567890-=[]\;\',./"
STR_LOWER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ~!@#$%^&*()_+{}|:\"<>?"
Uppercase = str.maketrans(STR_UPPER, STR_LOWER)
Lowercase = str.maketrans(STR_LOWER, STR_UPPER)


# map from key character to sensor array index
KEY_CAP_MAP = {'a': 5, 's': 1, 'd': 4, 'f': 3, 'j': 0, 'k': 2, 'l': 7, ';': 6}
CAP_THRESHOLD = 15
# Which keys should be pressed by which fingers
KEYS_LEFT = "asdf"
KEYS_RIGHT = "jkl;"
KEY_GROUPS = {'a': ['ESC', '1', 'TAB', 'CAPSLOCK', 'a', 'SHIFT_LEFT', 'z', 'CTRL_LEFT', 'ALT_LEFT'],
              's': ['2', 'w', 's', 'x'],
              'd': ['3', 'e', 'd', 'c'],
              'f': ['4', 'r', 'f', 'v', '5', 't', 'g', 'b'],
              'j': ['6', 'y', 'h', 'n', '7', 'u', 'j', 'm'],
              'k': ['8', 'i', 'k', ','],
              'l': ['9', 'o', 'l', '.'],
              ';': ['0', 'p', ';', '/', '-', '=', 'BACKSPACE', '[', ']', 'ENTER', '\'', 'SHIFT_LEFT', 'ALT_RIGHT', 'CTRL_RIGHT']}
KEY_CORRECT = ''
HOMEROW_INCORRECT = False
# How long each key has been left untouched
KEY_CAP_TIMERS = {'a': 0, 's': 0, 'd': 0, 'f': 0, 'j': 0, 'k': 0, 'l': 0, ';': 0}
MAX_RELEASE_SAME_SIDE = 60
MAX_RELEASE_OTHER_SIDE = 30

# Sentence progress
SENTENCE = ""
SENT_INDEX = 0

WORDS_PER_MIN = 0.0
TITLE = "Advanced Mode"


def main():
    global DISPLAYSURF, LEVEL, ERRORS, WORDS, CHARS, CUR, SENTENCES, SENTENCE, SENT_INDEX, RESOURCES

    # Connect to the keyboard
    ks.autoconnect()
    if ks.is_connected():
        print("Successfully connected")
    else:
        print("Could not connect")
        return

    # Pygame game initialization
    pygame.init()

    pygame.event.set_allowed(None)
    pygame.event.set_allowed([KEYUP, KEYDOWN, QUIT])
    clock = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode([WINDOWWIDTH, WINDOWHEIGHT], pygame.FULLSCREEN)
    #DISPLAYSURF = pygame.display.set_mode([WINDOWWIDTH, WINDOWHEIGHT])
    LEVEL = 0
    ERRORS = 0
    WORDS = 0
    CHARS = 0
    SENTENCES = 0

    # Load resources
    RESOURCES['font_small'] = pygame.font.Font('freesansbold.ttf', 25)
    RESOURCES['font_big'] = pygame.font.Font('freesansbold.ttf', 33)
    RESOURCES['sound_error'] = pygame.mixer.Sound(os.path.join('resources', "error.wav"))
    RESOURCES['img_hand_left'] = pygame.image.load(os.path.join('resources', 'hand_outline.png'))
    RESOURCES['img_hand_right'] = pygame.transform.flip(RESOURCES['img_hand_left'], True, False)
    RESOURCES['img_fingers_left'] = [pygame.image.load(os.path.join('resources', 'finger_' + str(i) + '.png')) for i in range(0, 4)]
    RESOURCES['img_fingers_right'] = [pygame.transform.flip(finger, True, False) for finger in RESOURCES['img_fingers_left']]
    RESOURCES['img_thumb_left'] = pygame.image.load(os.path.join('resources', 'finger_4.png'))
    RESOURCES['img_thumb_left'].fill((0, 255, 0, 255), None, pygame.BLEND_RGBA_MULT)
    RESOURCES['img_thumb_right'] = pygame.transform.flip(RESOURCES['img_thumb_left'], True, False)
    
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
    correct_letter_typed(' ')

    pressed = pygame.key.get_pressed()
    SHIFTED = pressed[K_RSHIFT] or pressed[K_LSHIFT]

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
                    SHIFTED = True
                else:
                    SHIFTED = False
            if event.key == K_UP:
                LEVEL = min(4, LEVEL + 1)
                sentence_array = get_sentence_list(LEVEL)
            if event.key == K_DOWN:
                LEVEL = max(0, LEVEL - 1)
                sentence_array = get_sentence_list(LEVEL)
            if event.type == KEYDOWN and event.key < 256 and not HOMEROW_INCORRECT:
                charac = chr(event.key)
                if SHIFTED:
                    charac = charac.translate(Uppercase)
                letter_typed(charac)
                # Move on to a new sentence
                if SENT_INDEX == len(SENTENCE):
                    SENT_INDEX = 0
                    SENTENCES += 1
                    SENTENCE = sentence_array.pop()
                    correct_letter_typed(' ')

        # Read homerow sensors
        update_homerow(ks.get_sensor_data())
        
        # Draw the current state
        DISPLAYSURF.fill(BGCOLOR)
        draw_interface()
        draw_sentence()
        draw_fingers()
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
    CUR.execute("SELECT * FROM sentences WHERE level = " + str(LEVEL))
    sentence_array = list(CUR.fetchall())
    sentence_array = list(map(lambda x: x[0], sentence_array))
    random.shuffle(sentence_array)
    return sentence_array


def make_text_objs(text, font, fontcolor):
    surf = font.render(text, True, fontcolor)
    return surf, surf.get_rect()


def correct_letter_typed(typed):
    global SENTENCE, SENT_INDEX, KEY_CORRECT, KEY_CAP_TIMERS, SHIFT_LEFT, SHIFT_RIGHT
    # Turn off old leds
    set_char_light(typed, KeyboardSerial.LED_OFF)
    # We don't care about the timer if we just pressed a key
    KEY_CAP_TIMERS[KEY_CORRECT] = 0
    if SHIFT_LEFT:
        KEY_CAP_TIMERS['a'] = 0
    elif SHIFT_RIGHT:
        KEY_CAP_TIMERS[';'] = 0
    # Turn on new leds
    if SENT_INDEX < len(SENTENCE):
        next_letter = SENTENCE[SENT_INDEX]
        # Update the correct key to use for the touch typing
        if next_letter == ' ':
            KEY_CORRECT = ' '
        else:
            lower_next = KeyboardSerial.KEYS[KeyboardSerial.CHAR_MAP[next_letter.translate(Lowercase)]]
            for key, letters in KEY_GROUPS.items():
                if lower_next in letters:
                    KEY_CORRECT = key
                    break
        # If we need to press shift for this puppy
        SHIFT_LEFT = False
        SHIFT_RIGHT = False
        if next_letter in STR_LOWER:
            if KEY_CORRECT in KEYS_LEFT:
                SHIFT_RIGHT = True
            else:
                SHIFT_LEFT = True
        set_char_light(next_letter, KeyboardSerial.LED_GREEN)


def letter_typed(typed):
    global SENTENCE, SENT_INDEX, WORDS, CHARS, ERRORS
    target_letter = SENTENCE[SENT_INDEX]
    if typed == target_letter:
        # Update global counter variables
        SENT_INDEX += 1
        CHARS += 1
        if (target_letter == ' ' or SENT_INDEX == len(SENTENCE)):
            WORDS += 1
        correct_letter_typed(target_letter)
    else:
        ERRORS += 1
        

def update_homerow(sensor_data):
    global KEY_CAP_TIMERS, HOMEROW_INCORRECT
    HOMEROW_INCORRECT = False
    # Update the sensor timers
    for key, value in KEY_CAP_MAP.items():
        if sensor_data[value] < CAP_THRESHOLD:
            KEY_CAP_TIMERS[key] += 1
        else:
            KEY_CAP_TIMERS[key] = 0
        # Don't invalidate the homework for space and shift cases
        if (key == 'a' and SHIFT_LEFT) or (key == ';' and SHIFT_RIGHT):
            continue
        if KEY_CORRECT in KEYS_LEFT:
            if key in KEYS_LEFT:
                release_max = MAX_RELEASE_SAME_SIDE
            else:
                release_max = MAX_RELEASE_OTHER_SIDE
        else:
            if key in KEYS_RIGHT:
                release_max = MAX_RELEASE_SAME_SIDE
            else:
                release_max = MAX_RELEASE_OTHER_SIDE
        if KEY_CAP_TIMERS[key] > release_max:
            HOMEROW_INCORRECT = True
        

def set_char_light(c, led_state):
    global SHIFT_LEFT, SHIFT_RIGHT
    if (c == ' '):
        ks.update_leds({'SPACE_LEFT': led_state})
        ks.update_leds({'SPACE_RIGHT': led_state})
    else:
        if SHIFT_RIGHT:
            ks.update_leds({'SHIFT_RIGHT': led_state})
        elif SHIFT_LEFT:
            ks.update_leds({'SHIFT_LEFT': led_state})
        key = KeyboardSerial.KEYS[KeyboardSerial.CHAR_MAP[c.translate(Lowercase)]]
        ks.update_leds({key: led_state})
        

## Game graphics
def draw_interface():
    global SENTENCES, ERRORS, WORDS, CHARS, WORDS_PER_MIN, TIME, RESOURCES

    level_surf, level_rect = make_text_objs('Level: ' + str(LEVEL), RESOURCES['font_small'], TEXTCOLOR)
    level_rect.topleft = (10, 10)
    DISPLAYSURF.blit(level_surf, level_rect)

    error_surf, error_rect = make_text_objs('Errors: ' + str(ERRORS), RESOURCES['font_small'], TEXTCOLOR)
    error_rect.center = (int(WINDOWWIDTH / 2), level_rect.center[1])
    DISPLAYSURF.blit(error_surf, error_rect)

    word_level_surf, word_level_rect = make_text_objs('Words/Min: %.1f' % WORDS_PER_MIN, RESOURCES['font_small'], TEXTCOLOR)
    word_level_rect.topright = (WINDOWWIDTH - 10, 10)
    DISPLAYSURF.blit(word_level_surf, word_level_rect)

    sent_surf, sent_rect = make_text_objs('Sentences: ' + str(SENTENCES), RESOURCES['font_small'], TEXTCOLOR)
    sent_rect.bottomleft = (10, WINDOWHEIGHT - 10)
    DISPLAYSURF.blit(sent_surf, sent_rect)

    word_surf, word_rect = make_text_objs('Words: ' + str(WORDS), RESOURCES['font_small'], TEXTCOLOR)
    word_rect.bottomleft = (10, WINDOWHEIGHT - 20 - sent_surf.get_height())
    DISPLAYSURF.blit(word_surf, word_rect)

    char_surf, char_rect = make_text_objs('Characters: ' + str(CHARS), RESOURCES['font_small'], TEXTCOLOR)
    char_rect.bottomleft = (10, WINDOWHEIGHT - 30 - sent_surf.get_height() - word_surf.get_height())
    DISPLAYSURF.blit(char_surf, char_rect)

    time_surf, time_rect = make_text_objs('Time: ' + str(TIME), RESOURCES['font_small'], TEXTCOLOR)
    time_rect.bottomright = (WINDOWWIDTH - 10, WINDOWHEIGHT - 10)
    DISPLAYSURF.blit(time_surf, time_rect)

    
def draw_sentence():
    global SENTENCE, SENT_INDEX, RESOURCES

    text_col = TEXTCOLOR
    if HOMEROW_INCORRECT:
        text_col = TEXTSHADOWCOLOR
    title_surf, title_rect = make_text_objs(SENTENCE, RESOURCES['font_big'], text_col)
    title_rect.center = (int(WINDOWWIDTH / 2) , int(WINDOWHEIGHT / 2) )
    DISPLAYSURF.blit(title_surf, title_rect)

    typed_text = SENTENCE[:SENT_INDEX]
    typed_surf, typed_rect = make_text_objs(typed_text, RESOURCES['font_big'], TEXTHIGHLIGHT)
    typed_back_rect = typed_rect.copy()
    typed_back_rect.x = title_rect.x
    typed_back_rect.y = title_rect.y
    pygame.draw.rect(DISPLAYSURF, BGCOLOR, typed_back_rect)
    DISPLAYSURF.blit(typed_surf, title_rect)
    
    if not HOMEROW_INCORRECT:
        next_surf, next_rect = make_text_objs(SENTENCE[:SENT_INDEX + 1], RESOURCES['font_big'], TEXTHIGHLIGHT)
        current_pos = (title_rect.x + int((typed_rect.width + next_rect.width) / 2), title_rect.y + typed_rect.height + 8)
        pygame.draw.circle(DISPLAYSURF, TEXTGUIDE, current_pos, 5)

    
def draw_fingers():
    global RESOURCES, KEY_CAP_TIMERS, KEY_CORRECT

    left_rect = RESOURCES['img_hand_left'].get_rect()
    left_rect.bottomright = (int(WINDOWWIDTH / 2), WINDOWHEIGHT)
    DISPLAYSURF.blit(RESOURCES['img_hand_left'], left_rect)

    right_rect = RESOURCES['img_hand_right'].get_rect()
    right_rect.bottomleft = (int(WINDOWWIDTH / 2), WINDOWHEIGHT)
    DISPLAYSURF.blit(RESOURCES['img_hand_right'], right_rect)

    if KEY_CORRECT == ' ':
        DISPLAYSURF.blit(RESOURCES['img_thumb_left'], left_rect)
        DISPLAYSURF.blit(RESOURCES['img_thumb_right'], right_rect)

    if KEY_CORRECT == ' ':
        release_left = MAX_RELEASE_OTHER_SIDE
        release_right = MAX_RELEASE_OTHER_SIDE
    elif KEY_CORRECT in KEYS_LEFT:
        release_left = MAX_RELEASE_SAME_SIDE
        release_right = MAX_RELEASE_OTHER_SIDE
    else:
        release_left = MAX_RELEASE_OTHER_SIDE
        release_right = MAX_RELEASE_SAME_SIDE

    for i, key in enumerate(KEYS_LEFT):
        time_off = KEY_CAP_TIMERS[key]
        finger_surf = RESOURCES['img_fingers_left'][i]
        finger_alpha = min(255, int((time_off / release_left) * 255))
        if finger_alpha == 255 or key == KEY_CORRECT or (key == 'a' and SHIFT_LEFT):
            finger_surf = finger_surf.copy()
            finger_alpha = 255
            if key == KEY_CORRECT or (key == 'a' and SHIFT_LEFT):
                finger_surf.fill((0, 255, 0, 255), None, pygame.BLEND_RGBA_MULT)
            else:
                finger_surf.fill((255, 0, 0, 255), None, pygame.BLEND_RGBA_MULT)
        finger_surf.set_alpha(finger_alpha)
        blit_alpha(DISPLAYSURF, finger_surf, left_rect, finger_alpha)
        
    for i, key in enumerate(reversed(KEYS_RIGHT)):
        time_off = KEY_CAP_TIMERS[key]
        finger_surf = RESOURCES['img_fingers_right'][i]
        finger_alpha = min(255, int((time_off / release_right) * 255))
        if finger_alpha == 255 or key == KEY_CORRECT or (key == ';' and SHIFT_RIGHT):
            finger_surf = finger_surf.copy()
            finger_alpha = 255
            if key == KEY_CORRECT or (key == ';' and SHIFT_RIGHT):
                finger_surf.fill((0, 255, 0, 255), None, pygame.BLEND_RGBA_MULT)
            else:
                finger_surf.fill((255, 0, 0, 255), None, pygame.BLEND_RGBA_MULT)
        finger_surf.set_alpha(finger_alpha)
        blit_alpha(DISPLAYSURF, finger_surf, right_rect, finger_alpha)



def blit_alpha(target, source, location, opacity):
    x = location[0]
    y = location[1]
    temp = pygame.Surface((source.get_width(), source.get_height())).convert()
    temp.blit(target, (-x, -y))
    temp.blit(source, (0, 0))
    temp.set_alpha(opacity)        
    temp.set_colorkey(GREEN)
    target.blit(temp, location)


def show_title_screen(text):
    title_surf, title_rect = make_text_objs(text, pygame.font.Font('freesansbold.ttf', 90), TEXTSHADOWCOLOR)
    title_rect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
    DISPLAYSURF.blit(title_surf, title_rect)

    title_surf, title_rect = make_text_objs(text, pygame.font.Font('freesansbold.ttf', 90), TEXTCOLOR)
    title_rect.center = (int(WINDOWWIDTH / 2) - 2, int(WINDOWHEIGHT / 2) - 2)
    DISPLAYSURF.blit(title_surf, title_rect)

    pygame.display.update()


def terminate():
    pygame.quit()


if __name__ == '__main__':
    main()
