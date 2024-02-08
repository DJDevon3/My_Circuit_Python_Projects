# SPDX-FileCopyrightText: 2024 DJDevon3
# SPDX-License-Identifier: MIT
# Coded for Circuit Python 8.x ST7796S TFT Featherwing

import time
import board
import displayio
import terminalio
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label, wrap_text_to_pixels
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

intro1 = "Far out in the uncharted backwaters of the unfashionable end of the western spiral arm of the Galaxy lies a small unregarded yellow sun."
intro2 = "Orbiting this at a distance of roughly ninety-two million miles is an utterly insignificant little blue-green planet whose ape-descended life forms are so amazingly primitive that they still think digital watches are a pretty neat idea."
intro3 = "This planet has or rather had a problem, which was this: most of the people living on it were unhappy for pretty much all of the time."
intro4 = "Many solutions were suggested for this problem, but most of these were largely concerned with the movement of small green pieces of paper, which was odd because on the whole it wasn't the small green pieces of paper that were unhappy."
intro5 = "Many were increasingly of the opinion that they'd all made a big mistake in coming down from the trees in the first place."
intro6 = "And some said that even the trees had been a bad move, and that no one should ever have left the oceans."
intro7 = "In many of the more relaxed civilizations on the Outer Eastern Rim of the Galaxy, the Hitchhiker's Guide has already supplanted the great Encyclopaedia Galactica as the standard repository of all knowledge and wisdom."
intro8 = "For though it has many omissions and contains much that is apocryphal, or at least wildly inaccurate, it scores over the older, more pedestrian work in two important respects."
intro9 = "First, it is slightly cheaper; and secondly it has the words DON'T PANIC inscribed in large friendly letters on its cover."
intro10 = "Hitchhikers Guide to the Galaxy \n ~ Douglas Adams"

while True:
    hello_label.text = "\n".join(wrap_text_to_pixels(intro1, DISPLAY_WIDTH-5, Arial16_font))
    time.sleep(10)
    hello_label.text = "\n".join(wrap_text_to_pixels(intro2, DISPLAY_WIDTH-5, Arial16_font))
    time.sleep(10)
    hello_label.text = "\n".join(wrap_text_to_pixels(intro3, DISPLAY_WIDTH-5, Arial16_font))
    time.sleep(10)
    hello_label.text = "\n".join(wrap_text_to_pixels(intro4, DISPLAY_WIDTH-5, Arial16_font))
    time.sleep(10)
    hello_label.text = "\n".join(wrap_text_to_pixels(intro5, DISPLAY_WIDTH-5, Arial16_font))
    time.sleep(10)
    hello_label.text = "\n".join(wrap_text_to_pixels(intro6, DISPLAY_WIDTH-5, Arial16_font))
    time.sleep(10)
    hello_label.text = "\n".join(wrap_text_to_pixels(intro7, DISPLAY_WIDTH-5, Arial16_font))
    time.sleep(10)
    hello_label.text = "\n".join(wrap_text_to_pixels(intro8, DISPLAY_WIDTH-5, Arial16_font))
    time.sleep(10)
    hello_label.text = "\n".join(wrap_text_to_pixels(intro9, DISPLAY_WIDTH-5, Arial16_font))
    time.sleep(10)
    hello_label.text = "\n".join(wrap_text_to_pixels(intro10, DISPLAY_WIDTH-5, Arial16_font))
    time.sleep(10)
