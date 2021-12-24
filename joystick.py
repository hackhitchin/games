
# Python module to simplify the joystick interface
#
# This module leaves out a lot of stuff in the name of simplicity - it will
# use the first joystick it finds. It can only do repeat presses in one axis
# (unlike the keyboard), and doesn't repeat button presses

import pygame

class Joystick:
    BUTTONDOWN = pygame.event.custom_type()
    BUTTONUP = pygame.event.custom_type()
    LEFT = 256
    RIGHT = 257
    UP = 258
    DOWN = 259

    def __init__(self):
        pygame.joystick.init()
        
        self.__js__ = None

        self.joystick = pygame.joystick.get_count() > 0

        self.p_left = False
        self.p_right = False
        self.p_up = False
        self.p_down = False

        self.repeat = None


    def start(self):
        if pygame.joystick.get_count():
            self.__js__ = pygame.joystick.Joystick(0)
            self.name = self.__js__.get_name()

    def set_repeat(self, millis):
        self.repeat = millis

    def get_pressed(self):
        # Fetch state of buttons
        if self.__js__:
            buttoncount = self.__js__.get_numbuttons()
            return [self.__js__.get_button(b) for b in range(buttoncount)]
        else:
            return [ False ]

    def event(self, event):
        THRESHOLD = 0.25    # Threshold which determines whether an analogue
                            # stick is pushed or not

        # Repeat button events as Joystick.BUTTON* events
        # This only does anything if JOYBUTTON events are sent to this
        # function
        if event.type == pygame.JOYBUTTONDOWN:
            pygame.event.post(pygame.event.Event(self.BUTTONDOWN, button=event.button))
            return
        if event.type == pygame.JOYBUTTONUP:
            pygame.event.post(pygame.event.Event(self.BUTTONUP, button=event.button))
            return

        up = down = left = right = None

        if event.type == pygame.JOYAXISMOTION:
            if event.axis == 0:
                if event.value < -THRESHOLD:
                    left = True
                    right = False
                elif event.value > THRESHOLD:
                    right = True
                    left = False
                else:
                    left = False
                    right = False
            
            if event.axis == 1:
                if event.value < -THRESHOLD:
                    up = True
                    down = False
                elif event.value > THRESHOLD:
                    down = True
                    up = False
                else:
                    up = False
                    down = False
        
        elif event.type == pygame.JOYHATMOTION:
            (x,y) = event.value

            left = x<0
            right = x>0
            up = y<0
            down = y>0

        else:
            # Some other event type we don't understand
            return

        e = None

        if left is not None and left != self.p_left:
            e = pygame.event.Event(
                self.BUTTONDOWN if left else self.BUTTONUP, button=self.LEFT)
            pygame.event.post(e)
        if right is not None and right != self.p_right:
            e = pygame.event.Event(
                self.BUTTONDOWN if right else self.BUTTONUP, button=self.RIGHT)
            pygame.event.post(e)
        if up is not None and up != self.p_up:
            e = pygame.event.Event(
                self.BUTTONDOWN if up else self.BUTTONUP, button=self.UP)
            pygame.event.post(e)
        if down is not None and down != self.p_down:
            e = pygame.event.Event(
                self.BUTTONDOWN if down else self.BUTTONUP, button=self.DOWN)
            pygame.event.post(e)

        if self.repeat and e is not None:
            if e.type == self.BUTTONDOWN:
                pygame.time.set_timer(e, self.repeat)
            else:
                pygame.time.set_timer(self.BUTTONDOWN, 0)

        if left is not None:
            self.p_left = left
        if right is not None:
            self.p_right = right
        if up is not None:
            self.p_up = up
        if down is not None:
            self.p_down = down

