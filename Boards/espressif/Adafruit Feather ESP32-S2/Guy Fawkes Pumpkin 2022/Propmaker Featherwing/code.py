"""Pumpkin Candle Flicker for M4 Express + PropMaker Feathering + 3W RGB LED by DJDevon3"""
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
    red_rand = random.randint(0, 200)
    green_rand = random.randint(200, 255)
    blue_rand = 255  # Brightness 0-255 0=on 255=off
    MAIN_COLOR = (red_rand, green_rand, blue_rand)
    led.color = MAIN_COLOR