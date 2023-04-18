# Dragon Mask Project by DJDevon3
# Controller for 5 adafruit noods
# 4 green noods and 1 red nood all on pin A0 & A1
# all noods sharing perfboard common ground to Qt Py GND pin
# Only using built-in library modules (nothing in lib needed)
import math
import time
import board
import pwmio
import random

# This uses the 3 adjacent SPI pins on QtPy RP2040, but any pins will do.
PINS = (board.A0, board.A1, board.MOSI) # List of pins, one per nOOd
GAMMA = 1.0  # For perceptually-linear brightness

# Convert pin number list to PWMOut object list
pin_list = [pwmio.PWMOut(pin, frequency=1000, duty_cycle=0) for pin in PINS]

while True:                            # Repeat forever...
    for i, pin in enumerate(pin_list): # For each pin...
        # Calc sine wave, phase offset for each pin, with gamma correction.
        # If using red, green, blue nOOds, you'll get a cycle of hues.
        red_rand = random.randint(0, 65535)
        phase = (time.monotonic() - 2 * i / len(PINS)) * math.pi
        brightness = int((math.sin(phase) + 1.0) * 0.5 ** GAMMA * 65535 + 0.5)
        pin.duty_cycle = brightness

