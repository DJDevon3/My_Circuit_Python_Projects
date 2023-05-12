# SPDX-FileCopyrightText: 2023 DJDevon3
# SPDX-License-Identifier: MIT
""" Adafruit Feather RP2040 DVI & OBS Weatherstation"""
import time
import board
import displayio
import terminalio
import adafruit_ahtx0
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
aht20 = adafruit_ahtx0.AHTx0(i2c)

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

# Blend Mode inverts colors for OBS Overlays
# These are actual color outputs & easier to work with.
ADDITIVE_CLEAR = 0x000000
ADDITIVE_HIGHLIGHTER_YELLOW = 0x0000FF
ADDITIVE_MAROON = 0x00FFFF
ADDITIVE_LIGHT_GRAY = 0x8B8B8B
ADDITIVE_MAGENTA = 0x00FF00
ADDITIVE_LIGHT_RED = 0x90C7FF
ADDITIVE_BRIGHT_GREEN = 0xFF00FF
ADDITIVE_BLUE = 0xFFA500
ADDITIVE_LIGHT_GREEN = 0x800080
ADDITIVE_AQUA = 0xFF0000
ADDITIVE_DARK_PURPLE = 0xFFFFFF
ADDITIVE_DARK_BLUE = 0xFFFF00
ADDITIVE_BROWN = 0x2AB5FF
ADDITIVE_ORANGE = 0x0099FF
ADDITIVE = 0x0099FF

# Fonts
medium_font = bitmap_font.load_font("/fonts/Arial-16.bdf")
huge_font = bitmap_font.load_font("/fonts/GoodTimesRg-Regular-16.bdf")

# Individual customizable position labels
# https://learn.adafruit.com/circuitpython-display-support-using-displayio/text
hello_label = label.Label(terminalio.FONT)
hello_label.anchor_point = (0.5, 1.0)
hello_label.anchored_position = (DISPLAY_WIDTH / 2 + 10 , 15)
hello_label.scale = (1)
hello_label.color = TEXT_WHITE

warning_label = label.Label(terminalio.FONT)
warning_label.anchor_point = (0.5, 1.0)
warning_label.anchored_position = (72, DISPLAY_HEIGHT - 54)
warning_label.scale = (2)
warning_label.color = ADDITIVE_HIGHLIGHTER_YELLOW

warning_text_label = label.Label(terminalio.FONT)
warning_text_label.anchor_point = (0.5, 1.0)
warning_text_label.anchored_position = (72, DISPLAY_HEIGHT - 45)
warning_text_label.scale = (1)
warning_text_label.color = ADDITIVE_HIGHLIGHTER_YELLOW

date_label = label.Label(medium_font)
# Anchor point bottom center of text
date_label.anchor_point = (0.0, 0.0)
# Display width divided in half for center of display (x,y)
date_label.anchored_position = (5, 5)
date_label.scale = 1
date_label.color = TEXT_LIGHTBLUE

temp_data_label = label.Label(terminalio.FONT)
temp_data_label.anchor_point = (1.0, 1.0)
temp_data_label.anchored_position = (280, 25)
temp_data_label.scale = 1
temp_data_label.color = ADDITIVE_ORANGE

aht_temp_data_label = label.Label(terminalio.FONT)
aht_temp_data_label.anchor_point = (1.0, 1.0)
aht_temp_data_label.anchored_position = (280 + 1, 35 + 1)
aht_temp_data_label.scale = 1
aht_temp_data_label.color = ADDITIVE_ORANGE

barometric_data_label = label.Label(terminalio.FONT)
barometric_data_label.anchor_point = (1.0, 1.0)
barometric_data_label.anchored_position = (295, 123)
barometric_data_label.scale = 1
barometric_data_label.color = ADDITIVE_ORANGE

aht_relative_humidity_label = label.Label(terminalio.FONT)
aht_relative_humidity_label.anchor_point = (0.0, 0.0)
aht_relative_humidity_label.anchored_position = (5, DISPLAY_HEIGHT - 110)
aht_relative_humidity_label.scale = 1
aht_relative_humidity_label.color = ADDITIVE_ORANGE

aht_relative_humidity_data_label = label.Label(huge_font)
aht_relative_humidity_data_label.anchor_point = (0.0, 0.0)
aht_relative_humidity_data_label.anchored_position = (5, DISPLAY_HEIGHT - 95)
aht_relative_humidity_data_label.scale = 1
aht_relative_humidity_data_label.color = ADDITIVE_ORANGE

# Warning label RoundRect
roundrect = RoundRect(int(5), int(DISPLAY_HEIGHT-78), 130, 35, 10, fill=ADDITIVE_MAROON, outline=ADDITIVE_ORANGE, stroke=1)

# Create subgroups
text_group = displayio.Group()
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
temp_group.append(temp_data_label)
text_group.append(barometric_data_label)
text_group.append(aht_temp_data_label)
text_group.append(aht_relative_humidity_data_label)
text_group.append(aht_relative_humidity_label)
display.show(main_group)

def show_warning(title, text):
    warning_label.text = title
    warning_text_label.text = text
    warning_group.hidden = False
def hide_warning():
    warning_group.hidden = True

while True:
    hello_label.text = "Feather RP2040 DVI"

    # Account for PCB heating bias, gets slightly hotter as ambient increases
    temperature = dps310.temperature * 1.8 + 32
    aht_temperature = aht20.temperature * 1.8 + 32
    temperature = round(temperature, 1)
    pressure = dps310.pressure
    humidity = aht20.relative_humidity
    # Set pressure manually to test warning system
    # pressure = 1000

    # print("Temp: ", temperature) # biased reading
    # Attempt to fix bias board heating
    display_temperature = temperature - 9.3
    # print(f"Actual Temp: {display_temperature:.1f}")

    temp_data_label.text = f"{display_temperature:.1f}"
    barometric_data_label.text = f"{pressure:.1f}"
    aht_temp_data_label.text = f"{aht_temperature:.1f}"
    aht_relative_humidity_label.text = "Humidity"
    aht_relative_humidity_data_label.text = f"{humidity:.1f}"

    # Warnings based on local sensors
    if pressure <= 1010:
        show_warning("WARNING", "Low Pressure System")
    elif pressure >= 1024:
        show_warning("WARNING", "High Pressure System")
    else:
        hide_warning()

    # time.sleep(10)


