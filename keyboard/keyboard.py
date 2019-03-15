# Adapted from: https://github.com/wbphelps/VKeyboard

import pygame, time, os, sched
from key import VKey
from textinput import TextInput
from pygame.locals import *
from screeninfo import get_monitors
from string import maketrans

Uppercase = maketrans("abcdefghijklmnopqrstuvwxyz`1234567890-=[]\;\',./",
                      'ABCDEFGHIJKLMNOPQRSTUVWXYZ~!@#$%^&*()_+{}|:"<>?')
# codes of the keys that we use
#Chars = {97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 96, 49, 50, 51, 52, 53, 54, 55, 56, 57, 48, 45, 61, 91, 93, 92, 59, 39, 44, 46, 47}


class VirtualKeyboard():
    def __init__(self, screen):
        self.screen = screen
        self.rect = self.screen.get_rect()
        self.w = self.rect.width
        self.h = self.rect.height
        self.screenCopy = screen.copy()

        # create a background surface
        self.background = pygame.Surface(self.rect.size)
        self.background.fill((0, 0, 0))  # fill with blackthere
        self.background.set_alpha(127)  # 50% transparent
        # blit background to screen
        self.screen.blit(self.background, (0, 0))

        self.keyW = int(self.w / 12 + 0.5)  # key width with border
        self.keyH = int(self.h / 8 + 0.5)  # key height

        self.x = (self.w - self.keyW * 12) / 2  # centered
        self.y = 5  # stay away from the edges (better touch)

        pygame.font.init()  # Just in case
        self.keyFont = pygame.font.Font(None, self.keyW)  # keyboard font

        # set dimensions for text input box
        self.textW = self.keyW * 12
        self.textH = self.keyH * 2 - 6

        self.caps = False
        self.shifted = False
        self.keys = []
        self.addkeys()  # add all the keys
        self.paintkeys()  # paint all the keys
        pygame.display.update()

    def run(self, text=''):
        self.text = text
        # create a text input box with room for 2 lines of text. leave room for the escape key
        self.input = TextInput(self.screen, self.text, self.x, self.y, self.textW, self.textH)

        # main event loop (hog all processes since we're on top, but someone might want
        # to rewrite this to be more event based...

        #editor_focus = True
        while True:
            time.sleep(0.02)  # 10/second is often enough
            events = pygame.event.get()
            if events is not None:
                for e in events:
                    #if e.type == MOUSEBUTTONDOWN:
                    #    mouse_pos = pygame.mouse.get_pos()
                    #    if self.input.editor.rect.collidepoint(mouse_pos):
                    #        editor_focus = True
                    #    else:
                    #        editor_focus = False
                    if (e.type == KEYDOWN and e.key > 0):
                        if e.key == K_RETURN:
                            print "return"
                            # TODO: could add newline here
                        elif e.key == K_LEFT:
                            pygame.display.flip()
                        elif e.key == K_RIGHT:
                            pygame.display.flip()
                        elif e.key == K_BACKSPACE:
                            self.selectkey('<-')
                            self.paintkeys()
                        elif e.key == K_SPACE:
                            self.selectkey('space')
                            self.paintkeys()
                        elif e.key == K_RSHIFT or e.key == K_LSHIFT:
                            self.shifted = True
                            self.togglecaps()
                            self.selectkey("shift")
                            self.paintkeys()
                        elif e.key == K_CAPSLOCK:
                            self.caps = True
                            self.togglecaps()
                            self.paintkeys()
                        #elif(e.key in Chars):
                        # the key is one of the keys that should be written to the screen
                        elif (e.key >= 96 and e.key <= 122) or (e.key >= 44 and e.key <= 57) or (e.key >= 91 and e.key <= 93) or e.key == 39 or e.key == 59 or e.key == 61:
                            charac = chr(e.key)
                            self.selectkey(charac)
                            if self.caps ^ self.shifted:
                                charac = chr(e.key).translate(Uppercase)
                            self.paintkeys()

                    elif (e.type == KEYUP and e.key > 0):
                        if (e.key == K_RSHIFT or e.key == K_LSHIFT):
                            self.shifted = False
                            self.togglecaps()
                        elif e.key == K_CAPSLOCK:
                            self.caps = False
                            self.togglecaps()
                        self.unselectall()
                        self.paintkeys()
                    elif (e.type == pygame.QUIT):
                        return self.text  # Return what we started with

                #self.input.update(editor_focus, events)
                self.input.update(True, events)

    def selectkey(self, caption):
        for key in self.keys:
            if key.caption.lower() == caption:
                key.selected = True
                key.dirty = True
                return True
        return False

    def unselectall(self, force=False): #Force all the keys to be unselected. Marks any that change as dirty to redraw
        for key in self.keys:
            if key.selected:
                key.selected = False
                key.dirty = True

    def togglecaps(self):
        for key in self.keys:
            key.dirty = True

    def addkeys(self):  # Add all the keys for the virtual keyboard
        x = self.x
        y = self.y + self.textH + self.keyH / 4

        row = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=']
        for item in row:
            onekey = VKey(item, x, y, self.keyW, self.keyH, self.keyFont)
            self.keys.append(onekey)
            x += self.keyW

        y += self.keyH  # overlap border
        x = self.x

        row = ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']']
        for item in row:
            onekey = VKey(item, x, y, self.keyW, self.keyH, self.keyFont)
            self.keys.append(onekey)
            x += self.keyW

        y += self.keyH
        x = self.x

        row = ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'']
        for item in row:
            onekey = VKey(item, x, y, self.keyW, self.keyH, self.keyFont)
            self.keys.append(onekey)
            x += self.keyW

        x = self.x + self.keyW / 2
        y += self.keyH

        row = ['z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/']
        for item in row:
            onekey = VKey(item, x, y, self.keyW, self.keyH, self.keyFont)
            self.keys.append(onekey)
            x += self.keyW

        x = self.x + 1
        y += self.keyH + self.keyH / 4

        onekey = VKey('Shift', x, y, int(self.keyW * 2.5), self.keyH, self.keyFont)
        onekey.noTrans = True
        onekey.shiftkey = True
        self.keys.append(onekey)
        x += onekey.w + self.keyW / 6

        onekey = VKey('Space', x, y, self.keyW * 5, self.keyH, self.keyFont)
        onekey.noTrans = True
        onekey.spacekey = True
        self.keys.append(onekey)
        x += onekey.w + self.keyW / 6

        onekey = VKey('Enter', x, y, int(self.keyW * 2.5), self.keyH, self.keyFont)
        onekey.noTrans = True
        onekey.enter = True
        self.keys.append(onekey)
        x += onekey.w + self.keyW / 3

        onekey = VKey('<-', x, y, int(self.keyW * 1.2 + 0.5), self.keyH, self.keyFont)
        onekey.noTrans = True
        onekey.bskey = True
        self.keys.append(onekey)
        x += onekey.w + self.keyW / 3

    def paintkeys(self): # Draw the keyboard (but only if they're dirty)
        for key in self.keys:
            key.draw(self.screen, self.background, self.caps ^ self.shifted)
        pygame.display.update()


WINDOWSIZE = .75
		
def main():
    pygame.init()

    # create window and center it
    screen = get_monitors().pop()
    screen_width = screen.width
    screen_height = screen.height
    window_width = int(round(screen_width * WINDOWSIZE))
    window_height = int(round(screen_height * WINDOWSIZE))
    # pos_x = screen_width / 2 - window_width / 2
    # pos_y = screen_height - window_height
    # os.environ['SDL_VIDEO_WINDOW_POS'] = '%i,%i' % (pos_x, pos_y)
    # os.environ['SDL_VIDEO_CENTERED'] = '0'

    surf = pygame.display.set_mode([window_width, window_height])
    vkeybd = VirtualKeyboard(surf)
    #userinput = vkeybd.run("This is a very long and interesting storyy about how one day long ago there was a")
    userinput = vkeybd.run("hi")
    print "User Entered: " + userinput

if __name__ == "__main__":
    main()
