# TODO: could add autoscroll and font size based on the size of the text input box

import pygame, textwrap, os
from glyph import Editor, Glyph, Macros
from pygame import display
from pygame.locals import *

FONT = pygame.font.SysFont('Courier New', 20, bold=True)
DEFAULT = {
    'bkg'       : (11, 11, 11),
    'color'     : (201, 192, 187),
    'font'      : FONT,
    'spacing'   : 0
    }

class TextInput(): # Handles the text input box and manages the cursor
    def __init__(self, screen, text, x, y, w, h):
        self.screen = screen
        self.background = pygame.Surface((w, h))
        self.background.fill((0, 0, 0))  # fill with black
        self.editor = Editor(Rect(x, y, w, h), **DEFAULT)
        self.start_editor()

    def start_editor(self):
        editor = self.editor
        editor_rect = editor.rect
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(editor.image, editor_rect)

    def update(self, focused, events):
        for ev in events:
            if ev.type == KEYDOWN and focused:
                self.editor.input(ev)
        cursor = self.editor.get_cursor()
        self.editor.image.fill((255, 205, 0), cursor)
        self.screen.blit(self.editor.image, self.editor.rect)
        display.update()