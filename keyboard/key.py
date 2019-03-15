# Adapted from: https://github.com/wbphelps/VKeyboard

# TODO: add repeats when holding a key down

import pygame
from pygame.locals import *
from string import maketrans

Uppercase = maketrans("abcdefghijklmnopqrstuvwxyz`1234567890-=[]\;\',./",
                      'ABCDEFGHIJKLMNOPQRSTUVWXYZ~!@#$%^&*()_+{}|:"<>?')

class VKey(object): # A single key for the VirtualKeyboard
    def __init__(self, caption, x, y, w, h, font):
        self.x = x
        self.y = y
        self.caption = caption
        self.w = w + 1  # overlap borders
        self.h = h + 1  # overlap borders
        self.noTrans = False
        self.enter = False
        self.bskey = False
        self.spacekey = False
        self.shiftkey = False
        self.font = font
        self.selected = False
        self.dirty = True
        self.keylayer = pygame.Surface((self.w, self.h)).convert()
        self.keylayer.fill((128, 128, 128))  # 0,0,0
        # Pre draw the border and store in the key layer
        pygame.draw.rect(self.keylayer, (255, 255, 255), (0, 0, self.w, self.h), 1)

    def draw(self, screen, background, shifted=False, forcedraw=False): # Draw this key if it needs redrawing
        if not forcedraw:
            if not self.dirty: return

        keyletter = self.caption
        if shifted:
            if not self.noTrans:
                keyletter = self.caption.translate(Uppercase)

        position = Rect(self.x, self.y, self.w, self.h)

        # put the background back on the screen so we can shade properly
        screen.blit(background, (self.x, self.y), position)

        # Put the shaded key background into key layer
        if self.selected:
            color = (200, 200, 200)
        else:
            color = (0, 0, 0)

        # Copy key layer onto the screen using Alpha so you can see through it
        pygame.draw.rect(self.keylayer, color, (1, 1, self.w - 2, self.h - 2))
        screen.blit(self.keylayer, (self.x, self.y))

        # Create a new temporary layer for the key contents
        # This might be sped up by pre-creating both selected and unselected layers when
        # the key is created, but the speed seems fine unless you're drawing every key at once
        templayer = pygame.Surface((self.w, self.h))
        templayer.set_colorkey((0, 0, 0))

        color = (255, 255, 255)
        text = self.font.render(keyletter, 1, (255, 255, 255))
        textpos = text.get_rect()
        blockoffx = (self.w / 2)
        blockoffy = (self.h / 2)
        offsetx = blockoffx - (textpos.width / 2)
        offsety = blockoffy - (textpos.height / 2)
        templayer.blit(text, (offsetx, offsety))

        screen.blit(templayer, (self.x, self.y))
        self.dirty = False
