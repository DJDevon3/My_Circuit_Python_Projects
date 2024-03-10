# SPDX-FileCopyrightText: 2024 DJDevon3
# SPDX-License-Identifier: MIT
# Coded for Circuit Python 8.x ST7796S TFT Featherwing
# ATECC Crypto Module display example
# https://www.adafruit.com/product/4314

import board
import busio
import displayio
from adafruit_atecc.adafruit_atecc import ATECC
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label
from circuitpython_st7796s import ST7796S

spi = board.SPI()
tft_cs = board.D9
tft_dc = board.D10
tft_rst = board.D17

# 4.0" ST7796S Display
DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 320

displayio.release_displays()
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_rst)
display = ST7796S(display_bus, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, rotation=180)

i2c = busio.I2C(board.SCL, board.SDA, frequency=75000)
atecc = ATECC(i2c)
# Initialize the SHA256 calculation engine
atecc.sha_start()

# Quick Colors for Labels
TEXT_BLACK = 0x000000
TEXT_BLUE = 0x0000FF
TEXT_CYAN = 0x00FFFF
TEXT_GRAY = 0x8B8B8B
TEXT_GREEN = 0x00FF00
TEXT_LIGHTBLUE = 0x90C7FF
TEXT_MAGENTA = 0xFF00FF
TEXT_ORANGE = 0xFFA500
TEXT_PURPLE = 0x800080
TEXT_RED = 0xFF0000
TEXT_WHITE = 0xFFFFFF
TEXT_YELLOW = 0xFFFF00

Arial16_font = bitmap_font.load_font("/fonts/Arial-16.bdf")

# Label Customizations
hello_label = label.Label(Arial16_font)
hello_label.anchor_point = (0.0, 0.0)
hello_label.anchored_position = (5, 20)
hello_label.scale = (1)
hello_label.color = TEXT_WHITE

# Create Display Groups
text_group = displayio.Group()
text_group.append(hello_label)
display.root_group = text_group

atecc_serialnum = atecc.serial_number
atecc_random_value = atecc.random(rnd_max=1024)
atecc_counter = atecc.counter(1, increment_counter=True)

print("ATECC Serial: ", atecc.serial_number)
# Generate a random number with a maximum value of 1024
print("Random Value: ", atecc.random(rnd_max=1024))
# Print out the value from one of the ATECC's counters
# You should see this counter increase on every time the code.py runs.
print("ATECC Counter #1 Value: ", atecc.counter(1, increment_counter=True))

while True:
    hello_label.text = f"SN: {atecc_serialnum}\nRand: {atecc_random_value}\nCount: {atecc_counter}"


