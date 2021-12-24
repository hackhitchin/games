#!/usr/bin/env python3

# Test the Joystick module

import pygame, sys
import joystick

pygame.init()

js = joystick.Joystick()

if not js.joystick:
    print("No joystick")
    sys.exit(0)

js.set_repeat(200)
js.start()

while True:
    event = pygame.event.wait()
    if event.type == js.BUTTONDOWN:
        name = "BUTTONDOWN"
    elif event.type == js.BUTTONUP:
        name = "BUTTONUP  "
    else:
        name = "        - "
    print(name, event)
    if event.type == pygame.JOYAXISMOTION or event.type == pygame.JOYHATMOTION:
        js.event(event)

