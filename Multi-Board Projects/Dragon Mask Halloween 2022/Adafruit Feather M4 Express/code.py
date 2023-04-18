# DJDevon3 Dragon Mask Halloween 2022
# Feather M4 Express + PropMaker Featherwing
# 3W RGB LED Flicker Scepter Code

import time
import board
import adafruit_rgbled
import digitalio
import random

enable = digitalio.DigitalInOut(board.D10)
enable.direction = digitalio.Direction.OUTPUT
enable.value = True

RED_LED = board.D11  # Red LED pin
GREEN_LED = board.D12  # Green LED pin
BLUE_LED = board.D13  # Blue LED pin
led = adafruit_rgbled.RGBLED(RED_LED, GREEN_LED, BLUE_LED)
while True:
    red_rand = random.randint(0, 255)
    green_rand = random.randint(0, 255)
    blue_rand = (255)
    MAIN_COLOR = (red_rand, green_rand, blue_rand)
    led.color = MAIN_COLOR
