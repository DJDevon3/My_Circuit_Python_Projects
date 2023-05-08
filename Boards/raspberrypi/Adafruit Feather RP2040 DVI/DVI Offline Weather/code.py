# SPDX-FileCopyrightText: 2023 DJDevon3
# SPDX-License-Identifier: MIT
""" Adafruit Feather RP2040 DVI Offline Weatherstation"""
import time
import board
import displayio
import terminalio
from adafruit_display_text import label
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_bitmap_font import bitmap_font
from adafruit_dps310.basic import DPS310

display = board.DISPLAY

# displayio.release_displays()
DISPLAY_WIDTH = 320
DISPLAY_HEIGHT = 240

i2c = board.I2C()  # uses board.SCL and board.SDA
dps310 = DPS310(i2c)

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

# Fonts
medium_font = bitmap_font.load_font("/fonts/Arial-16.bdf")
huge_font = bitmap_font.load_font("/fonts/GoodTimesRg-Regular-80.bdf")

# Individual customizable position labels
# https://learn.adafruit.com/circuitpython-display-support-using-displayio/text
hello_label = label.Label(terminalio.FONT)
hello_label.anchor_point = (0.5, 1.0)
hello_label.anchored_position = (DISPLAY_WIDTH/2, 15)
hello_label.scale = (1)
hello_label.color = TEXT_WHITE

warning_label = label.Label(terminalio.FONT)
warning_label.anchor_point = (0.5, 1.0)
warning_label.anchored_position = (DISPLAY_WIDTH / 2, DISPLAY_HEIGHT - 20)
warning_label.scale = (2)
warning_label.color = TEXT_RED

warning_text_label = label.Label(terminalio.FONT)
warning_text_label.anchor_point = (0.5, 1.0)
warning_text_label.anchored_position = (DISPLAY_WIDTH / 2, DISPLAY_HEIGHT - 5)
warning_text_label.scale = (1)
warning_text_label.color = TEXT_RED

date_label = label.Label(medium_font)
# Anchor point bottom center of text
date_label.anchor_point = (0.0, 0.0)
# Display width divided in half for center of display (x,y)
date_label.anchored_position = (5, 5)
date_label.scale = 1
date_label.color = TEXT_LIGHTBLUE

temp_label = label.Label(medium_font)
temp_label.anchor_point = (1.0, 1.0)
temp_label.anchored_position = (DISPLAY_WIDTH - 2, DISPLAY_HEIGHT / 2 - 10)
temp_label.scale = 1
temp_label.color = TEXT_ORANGE

temp_data_label = label.Label(huge_font)
temp_data_label.anchor_point = (0.5, 1.0)
temp_data_label.anchored_position = (DISPLAY_WIDTH / 2, DISPLAY_HEIGHT / 2 + 30)
temp_data_label.scale = 1
temp_data_label.color = TEXT_ORANGE

temp_data_shadow = label.Label(huge_font)
temp_data_shadow.anchor_point = (0.5, 1.0)
temp_data_shadow.anchored_position = (DISPLAY_WIDTH / 2 + 2, DISPLAY_HEIGHT / 2 + 30 + 2)
temp_data_shadow.scale = 1
temp_data_shadow.color = TEXT_BLACK

barometric_label = label.Label(medium_font)
barometric_label.anchor_point = (1.0, 1.0)
barometric_label.anchored_position = (DISPLAY_WIDTH - 5, DISPLAY_HEIGHT - 27)
barometric_label.scale = 1
barometric_label.color = TEXT_GRAY

barometric_data_label = label.Label(medium_font)
barometric_data_label.anchor_point = (1.0, 1.0)
barometric_data_label.anchored_position = (DISPLAY_WIDTH - 5, DISPLAY_HEIGHT - 5)
barometric_data_label.scale = 1
barometric_data_label.color = TEXT_ORANGE

# Load Bitmap to tile grid first (Background layer)
DiskBMP = displayio.OnDiskBitmap("/images/Astral_Fruit_320x240.bmp")
tile_grid = displayio.TileGrid(
    DiskBMP,
    pixel_shader=DiskBMP.pixel_shader,
    width=1,
    height=1,
    tile_width=DISPLAY_WIDTH,
    tile_height=DISPLAY_HEIGHT)

# Warning label RoundRect
roundrect = RoundRect(int(DISPLAY_WIDTH/2-65), int(DISPLAY_HEIGHT-50), 130, 50, 10, fill=0x0, outline=0xFFFFFF, stroke=1)

# Create subgroups
text_group = displayio.Group()
text_group.append(tile_grid)
temp_group = displayio.Group()
warning_group = displayio.Group()
main_group = displayio.Group()

# Add subgroups to main display group
main_group.append(text_group)
main_group.append(warning_group)
main_group.append(temp_group)

# Add warning popup group
warning_group.append(roundrect)
warning_group.append(warning_label)
warning_group.append(warning_text_label)

# Label Display Group (foreground layer)
text_group.append(hello_label)
text_group.append(date_label)
temp_group.append(temp_label)
temp_group.append(temp_data_shadow)
temp_group.append(temp_data_label)
text_group.append(barometric_label)
text_group.append(barometric_data_label)
display.show(main_group)

def show_warning(title, text):
    warning_label.text = title
    warning_text_label.text = text
    warning_group.hidden = False
def hide_warning():
    warning_group.hidden = True

while True:
    hello_label.text = "Adafruit Feather RP2040 DVI Offline Weather"
    
    # Account for PCB heating bias, gets slightly hotter as ambient increases
    temperature = dps310.temperature * 1.8 + 32
    temperature = round(temperature, 1)
    pressure = dps310.pressure
    
    # print("Temp: ", temperature) # biased reading
    # Attempt to fix bias board heating
    display_temperature = temperature - 9.3
    # print(f"Actual Temp: {display_temperature:.1f}")
    
    temp_label.text = "°F"
    temp_data_shadow.text = f"{display_temperature:.1f}"
    temp_data_label.text = f"{display_temperature:.1f}"
    barometric_label.text = "Pressure"
    barometric_data_label.text = f"{dps310.pressure:.1f}"

    # Warnings based on local sensors
    if pressure <= 1010:
        show_warning("WARNING", "Low Pressure System")
    elif pressure >= 1024:
        show_warning("WARNING", "High Pressure System")
    else:
        hide_warning()


