# SPDX-FileCopyrightText: 2023 DJDevon3
#
# SPDX-License-Identifier: MIT
# Used with Adafruit MatrixPortal S3
# Coded for Circuit Python 9.0 alpha

import time
import board
import displayio
import rgbmatrix
import framebufferio
import adafruit_imageload
import ulab.numpy as np
import terminalio
from adafruit_display_text import label
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_bitmap_font import bitmap_font
from cedargrove_palettefader.palettefader_ulab import PaletteFader
import adafruit_bme680

displayio.release_displays()
DISPLAY_WIDTH = 128
DISPLAY_HEIGHT = 64

matrix = rgbmatrix.RGBMatrix(
    width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, bit_depth=4,
    rgb_pins=[
        board.MTX_R1,
        board.MTX_G1,
        board.MTX_B1,
        board.MTX_R2,
        board.MTX_G2,
        board.MTX_B2],
    addr_pins=[board.MTX_ADDRA, board.MTX_ADDRB, board.MTX_ADDRC, board.MTX_ADDRD],
    clock_pin=board.MTX_CLK,
    latch_pin=board.MTX_LAT,
    output_enable_pin=board.MTX_OE,
    tile=2,
    serpentine=True,
    doublebuffer=True)

# Associate the RGB matrix with a Display so we can use displayio
display = framebufferio.FramebufferDisplay(matrix, auto_refresh=True)

i2c = board.I2C()
sensor = adafruit_bme680.Adafruit_BME680_I2C(i2c)

# Time in seconds between updates (polling)
# 600 = 10 mins, 900 = 15 mins, 1800 = 30 mins, 3600 = 1 hour
sleep_time = 30

# Converts seconds in minutes/hours/days
def time_calc(input_time):
    if input_time < 60:
        sleep_int = input_time
        time_output = f"{sleep_int:.0f} seconds"
    elif 60 <= input_time < 3600:
        sleep_int = input_time / 60
        time_output = f"{sleep_int:.0f} minutes"
    elif 3600 <= input_time < 86400:
        sleep_int = input_time / 60 / 60
        time_output = f"{sleep_int:.0f} hours"
    else:
        sleep_int = input_time / 60 / 60 / 24
        time_output = f"{sleep_int:.1f} days"
    return time_output

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

# Fonts are optional
tinyfont = bitmap_font.load_font("/fonts/tiny3x5.bdf")
medium_font = bitmap_font.load_font("/fonts/Arial-16.bdf")
huge_font = bitmap_font.load_font("/fonts/GoodTimesRg-Regular-16.bdf")

# Individual customizable position labels
# https://learn.adafruit.com/circuitpython-display-support-using-displayio/text
hello_label = label.Label(tinyfont)
hello_label.anchor_point = (0.5, 0.0)
hello_label.anchored_position = (DISPLAY_WIDTH/2, 2)
hello_label.scale = (1)
hello_label.color = TEXT_WHITE

hello_label_outline1 = label.Label(tinyfont)
hello_label_outline1.anchor_point = (0.5, 0.0)
hello_label_outline1.anchored_position = (DISPLAY_WIDTH/2, 2+1)
hello_label_outline1.scale = (1)
hello_label_outline1.color = TEXT_BLACK

hello_label_outline2 = label.Label(tinyfont)
hello_label_outline2.anchor_point = (0.5, 0.0)
hello_label_outline2.anchored_position = (DISPLAY_WIDTH/2, 2-1)
hello_label_outline2.scale = (1)
hello_label_outline2.color = TEXT_BLACK

hello_label_outline3 = label.Label(tinyfont)
hello_label_outline3.anchor_point = (0.5, 0.0)
hello_label_outline3.anchored_position = (DISPLAY_WIDTH/2+1, 2)
hello_label_outline3.scale = (1)
hello_label_outline3.color = TEXT_BLACK

hello_label_outline4 = label.Label(tinyfont)
hello_label_outline4.anchor_point = (0.5, 0.0)
hello_label_outline4.anchored_position = (DISPLAY_WIDTH/2-1, 2)
hello_label_outline4.scale = (1)
hello_label_outline4.color = TEXT_BLACK

warning_label = label.Label(tinyfont)
warning_label.anchor_point = (0.0, 0.0)
warning_label.anchored_position = (4, 11)
warning_label.scale = (1)
warning_label.color = TEXT_RED

warning_text_label = label.Label(tinyfont)
warning_text_label.anchor_point = (1.0, 0.0)
warning_text_label.anchored_position = (DISPLAY_WIDTH-4, 11)
warning_text_label.scale = (1)
warning_text_label.color = TEXT_RED

temp_label = label.Label(medium_font)
temp_label.anchor_point = (1.0, 1.0)
temp_label.anchored_position = (DISPLAY_WIDTH-5, 40)
temp_label.scale = 1
temp_label.color = TEXT_ORANGE

temp_data_label = label.Label(huge_font)
temp_data_label.anchor_point = (0.5, 1.0)
temp_data_label.anchored_position = (DISPLAY_WIDTH / 2, 36)
temp_data_label.scale = 1
temp_data_label.color = TEXT_ORANGE

temp_data_shadow = label.Label(huge_font)
temp_data_shadow.anchor_point = (0.5, 1.0)
temp_data_shadow.anchored_position = (DISPLAY_WIDTH / 2 + 1, 36 + 1)
temp_data_shadow.scale = 1
temp_data_shadow.color = TEXT_BLACK

humidity_label = label.Label(terminalio.FONT)
humidity_label.anchor_point = (0.0, 1.0)
humidity_label.anchored_position = (2, DISPLAY_HEIGHT - 14)
humidity_label.scale = 1
humidity_label.color = TEXT_GRAY

humidity_outline1 = label.Label(terminalio.FONT)
humidity_outline1.anchor_point = (0.0, 1.0)
humidity_outline1.anchored_position = (2, DISPLAY_HEIGHT - 14+1)
humidity_outline1.scale = 1
humidity_outline1.color = TEXT_BLACK

humidity_outline2 = label.Label(terminalio.FONT)
humidity_outline2.anchor_point = (0.0, 1.0)
humidity_outline2.anchored_position = (2, DISPLAY_HEIGHT - 14-1)
humidity_outline2.scale = 1
humidity_outline2.color = TEXT_BLACK

humidity_outline3 = label.Label(terminalio.FONT)
humidity_outline3.anchor_point = (0.0, 1.0)
humidity_outline3.anchored_position = (2+1, DISPLAY_HEIGHT - 14)
humidity_outline3.scale = 1
humidity_outline3.color = TEXT_BLACK

humidity_outline4 = label.Label(terminalio.FONT)
humidity_outline4.anchor_point = (0.0, 1.0)
humidity_outline4.anchored_position = (2-1, DISPLAY_HEIGHT - 14)
humidity_outline4.scale = 1
humidity_outline4.color = TEXT_BLACK

humidity_data_label = label.Label(huge_font)
humidity_data_label.anchor_point = (0.0, 1.0)
humidity_data_label.anchored_position = (1, DISPLAY_HEIGHT-2)
humidity_data_label.scale = 1
humidity_data_label.color = TEXT_ORANGE

humidity_shadow = label.Label(huge_font)
humidity_shadow.anchor_point = (0.0, 1.0)
humidity_shadow.anchored_position = (2, DISPLAY_HEIGHT-1)
humidity_shadow.scale = 1
humidity_shadow.color = TEXT_BLACK

barometric_label = label.Label(terminalio.FONT)
barometric_label.anchor_point = (1.0, 1.0)
barometric_label.anchored_position = (DISPLAY_WIDTH-2, DISPLAY_HEIGHT - 13)
barometric_label.scale = 1
barometric_label.color = TEXT_GRAY

barometric_label_shadow = label.Label(terminalio.FONT)
barometric_label_shadow.anchor_point = (1.0, 1.0)
barometric_label_shadow.anchored_position = (DISPLAY_WIDTH-1, DISPLAY_HEIGHT - 12)
barometric_label_shadow.scale = 1
barometric_label_shadow.color = TEXT_BLACK

barometric_data_label = label.Label(huge_font)
barometric_data_label.anchor_point = (1.0, 1.0)
barometric_data_label.anchored_position = (DISPLAY_WIDTH-2, DISPLAY_HEIGHT-2)
barometric_data_label.scale = 1
barometric_data_label.color = TEXT_ORANGE

barometric_shadow = label.Label(huge_font)
barometric_shadow.anchor_point = (1.0, 1.0)
barometric_shadow.anchored_position = (DISPLAY_WIDTH-1, DISPLAY_HEIGHT-1)
barometric_shadow.scale = 1
barometric_shadow.color = TEXT_BLACK

# Define background graphic object parameters
BKG_BRIGHTNESS = 0.5   # Initial brightness level
BKG_GAMMA = 0.8  # Works nicely for brightness = 0.2
BKG_IMAGE_FILE = "images/Astral_Fruit_128x64.bmp"

# Load the background image and source color palette
bkg_bitmap, bkg_palette_source = adafruit_imageload.load(
    BKG_IMAGE_FILE, bitmap=displayio.Bitmap, palette=displayio.Palette
)
# Instantiate background PaletteFader object and display on-screen
faded_object = PaletteFader(bkg_palette_source,
                            brightness=BKG_BRIGHTNESS,
                            gamma=BKG_GAMMA, 
                            normalize=True)
bkg_tile = displayio.TileGrid(bkg_bitmap, pixel_shader=faded_object.palette)

# Warning label RoundRect
roundrect = RoundRect(int(0),  # x-position of the top left corner
                      int(8),  # y-position of the top left corner
                      128,  # width of the rounded-corner rectangle
                      11,  # height of the rounded-corner rectangle
                      5,  # corner radius
                      fill=0x0,  # fill color
                      outline=0xFFFFFF,  # outline color
                      stroke=1)  # stroke width

# Create subgroups
primary_group = displayio.Group()
primary_group.append(bkg_tile)
text_group = displayio.Group()
hello_group = displayio.Group()
temp_group = displayio.Group()
warning_group = displayio.Group()
main_group = displayio.Group()

# Add subgroups to main display group
main_group.append(primary_group)
main_group.append(text_group)
main_group.append(hello_group)
main_group.append(warning_group)
main_group.append(temp_group)

# Add warning popup group
warning_group.append(roundrect)
warning_group.append(warning_label)
warning_group.append(warning_text_label)

# Label Display Group (foreground layer)
hello_group.append(hello_label_outline1)
hello_group.append(hello_label_outline2)
hello_group.append(hello_label_outline3)
hello_group.append(hello_label_outline4)
hello_group.append(hello_label)
temp_group.append(temp_label)
temp_group.append(temp_data_shadow)
temp_group.append(temp_data_label)
text_group.append(humidity_outline1)
text_group.append(humidity_outline2)
text_group.append(humidity_outline3)
text_group.append(humidity_outline4)
text_group.append(humidity_label)
text_group.append(humidity_shadow)
text_group.append(humidity_data_label)
text_group.append(barometric_label_shadow)
text_group.append(barometric_label)
text_group.append(barometric_shadow)
text_group.append(barometric_data_label)
display.show(main_group)

def show_warning(title, text):
    warning_label.text = title
    warning_text_label.text = text
    warning_group.hidden = False
def hide_warning():
    warning_group.hidden = True

display_temperature = 0
# Temperature offset adjustments
# For correcting incorrect temp sensor readings
input_range = [50, 70, 80, 88, 90, 95, 120]
output_range = [50-0.1, 70-2.0, 80-2.0, 88-4.5, 90-7.0, 95-10.0, 120-15]

hello_text = "MATRIX PORTAL S3"
humidity_text = "HUMIDITY"
pressure_text = "PRESSURE"
while True:
    sensor.sea_level_pressure = sensor.pressure
    hello_label_outline1.text = f"{hello_text}"
    hello_label_outline2.text = f"{hello_text}"
    hello_label_outline3.text = f"{hello_text}"
    hello_label_outline4.text = f"{hello_text}"
    hello_label.text = f"{hello_text}"
    print("===============================")
    debug_OWM = False  # Set to True for Serial Print Debugging

    # Local sensor data display
    temp_label.text = "°F"

    # Board Uptime
    print("Board Uptime: ", time_calc(time.monotonic()))

    # Account for PCB heating bias, gets slightly hotter as ambient increases
    temperature = sensor.temperature * 1.8 + 32
    temp_round = round(temperature, 2)
    print("Sensor Temp: ", temperature)  # biased reading
    display_temperature = np.interp(temperature, input_range, output_range)
    display_temperature = round(display_temperature[0], 2)
    print(f"Adjusted Temp: {display_temperature:.1f}")
    # mqtt_pressure = 1009  # Manually set to debug warning message
    mqtt_humidity = round(sensor.relative_humidity, 1)
    mqtt_pressure = round(sensor.pressure, 1)
    mqtt_altitude = round(sensor.altitude, 2)

    temp_data_shadow.text = f"{display_temperature:.1f}"
    temp_data_label.text = f"{display_temperature:.1f}"
    humidity_outline1.text = f"{humidity_text}"
    humidity_outline2.text = f"{humidity_text}"
    humidity_outline3.text = f"{humidity_text}"
    humidity_outline4.text = f"{humidity_text}"
    humidity_label.text = f"{humidity_text}"
    humidity_shadow.text = f"{mqtt_humidity:.1f} %"
    humidity_data_label.text = f"{mqtt_humidity:.1f} %"
    barometric_label_shadow.text = f"{pressure_text}"
    barometric_label.text = f"{pressure_text}"
    barometric_shadow.text = f"{mqtt_pressure:.1f}"
    barometric_data_label.text = f"{mqtt_pressure:.1f}"

    # Warnings based on local sensors
    if mqtt_pressure <= 919:  # pray you never see this message
        show_warning("HOLY SHIT:", "SEEK SHELTER!")
    elif 920 <= mqtt_pressure <= 979:
        show_warning("DANGER:", "MAJOR HURRICANE!")
    elif 980 <= mqtt_pressure <= 989:
        show_warning("DANGER:", "MINOR HURRICANE")
    elif 990 <= mqtt_pressure <= 1001:
        show_warning("WARNING:", "TROPICAL STORM")
    elif 1002 <= mqtt_pressure <= 1009:  # sudden gusty downpours
        show_warning("CAUTION:", "LOW PRESSURE SYSTEM")
    elif 1019 <= mqtt_pressure <= 1025:  # sudden light cold rain
        show_warning("CAUTION:", "HIGH PRESSURE SYSTEM")
    elif mqtt_pressure >= 1026:
        show_warning("WARNING:", "HAIL & TORNADO WATCH")
    else:
        hide_warning()  # Normal pressures: 1110-1018 (no message)

    print("Next Update: ", time_calc(sleep_time))
    print("===============================")
    # display.refresh(target_frames_per_second=3, minimum_frames_per_second=0)
    time.sleep(sleep_time)
