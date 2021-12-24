#!/usr/bin/env python3

import pygame, sys

# Get state of joysticks and print events

pygame.init()

if not pygame.joystick.get_init():
    print("Joystick module not initialised")
    sys.exit(0)

jscount = pygame.joystick.get_count()

print(f"Joystick module initialised, {jscount} joystick(s) found")

for js_n in range(jscount):
    js = pygame.joystick.Joystick(js_n)

    print(f"Joystick {js_n}:", js.get_name())
    print(" Instance ID:    ", js.get_instance_id())
    print(" GUID:           ", js.get_guid())
    print(" Power:          ", js.get_power_level())
    print(" Axes:           ", js.get_numaxes())
    print(" Balls:          ", js.get_numballs())
    print(" Hats:           ", js.get_numhats())
    print(" Buttons:        ", js.get_numbuttons())
    print(" Rumble:         ", js.rumble(1,1,100))

while True:
    event = pygame.event.wait()
    print(event)

