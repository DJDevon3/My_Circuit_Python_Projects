# SPDX-FileCopyrightText: 2020 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: MIT
#
"""DJDevon3 Simple Offline Weatherstation"""
import time
import board
import adafruit_bmp280
import adafruit_sht31d
import displayio
import adafruit_imageload
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
from adafruit_hx8357 import HX8357
from analogio import AnalogIn

# This sketch should also work for the 2.5" TFT, just change the size.
DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 320

# Initialize TFT Display
displayio.release_displays()
i2c = board.I2C()
spi = board.SPI()
tft_cs = board.D9
tft_dc = board.D10
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = HX8357(display_bus, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT)

vbat_voltage = AnalogIn(board.VOLTAGE_MONITOR)
def get_voltage(pin):
    return (pin.value * 3.3) / 65536 * 2
vbat = get_voltage(vbat_voltage)

bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)
sht31d = adafruit_sht31d.SHT31D(i2c)

# BMP280 altitude sensor changes with barometric pressure!
# I set sea level pressure to sensor pressure because I'm always at sea level.
# Set manually if it doesn't work well for your elevation.
# bmp280.sea_level_pressure = 1010.80
bmp280.sea_level_pressure = bmp280.pressure

# Some quick colors. Must be HEX values. You can add custom colors.
text_black = (0x000000)
text_blue = (0x0000FF)
text_cyan = (0x00FFFF)
text_green = (0x00FF00)
text_magenta = (0xFF00FF)
text_orange = (0xFFA500)
text_red = (0xFF0000)
text_white = (0xFFFFFF)
text_yellow = (0xFFFF00)

# Fonts are optional
small_font = bitmap_font.load_font("/fonts/Arial-12.bdf")
medium_font = bitmap_font.load_font("/fonts/Arial-16.bdf")
huge_font = bitmap_font.load_font("/fonts/GoodTimesRg-Regular-121.bdf")

# Individual customizable position labels
# https://learn.adafruit.com/circuitpython-display-support-using-displayio/text
hello_label = label.Label(small_font)
# Anchor point bottom center of text
hello_label.anchor_point = (0.5, 1.0)
# Display width divided in half for center of display (x,y)
hello_label.anchored_position = (DISPLAY_WIDTH/2, 15)
hello_label.scale = (1)
hello_label.color = text_white

temp_label = label.Label(medium_font)
temp_label.anchor_point = (1.0, 0.0)
temp_label.anchored_position = (475, 115)
temp_label.scale = (2)
temp_label.color = text_orange

temp_data_label = label.Label(huge_font)
temp_data_label.anchor_point = (0.5, 1.0)
temp_data_label.anchored_position = (DISPLAY_WIDTH/2, 200)
temp_data_label.scale = (1)
temp_data_label.color = text_orange

humidity_label = label.Label(small_font)
# Anchor point bottom left of text
humidity_label.anchor_point = (0.0, 1.0)
humidity_label.anchored_position = (5, DISPLAY_HEIGHT)
humidity_label.scale = (1)
humidity_label.color = text_white

humidity_data_label = label.Label(medium_font)
humidity_data_label.anchor_point = (0.0, 1.0)
humidity_data_label.anchored_position = (5, DISPLAY_HEIGHT-25)
humidity_data_label.scale = (1)
humidity_data_label.color = text_white

barometric_label = label.Label(small_font)
# Anchor point bottom center of text
barometric_label.anchor_point = (0.5, 1.0)
barometric_label.anchored_position = (DISPLAY_WIDTH/2, DISPLAY_HEIGHT)
barometric_label.scale = (1)
barometric_label.color = text_white

barometric_data_label = label.Label(medium_font)
barometric_data_label.anchor_point = (0.5, 1.0)
barometric_data_label.anchored_position = (DISPLAY_WIDTH/2, DISPLAY_HEIGHT-25)
barometric_data_label.scale = (1)
barometric_data_label.color = text_white

altitude_label = label.Label(small_font)
# Anchor point bottom right of text
altitude_label.anchor_point = (1.0, 1.0)
altitude_label.anchored_position = (470, DISPLAY_HEIGHT)
altitude_label.scale = (1)
altitude_label.color = text_white

altitude_data_label = label.Label(medium_font)
altitude_data_label.anchor_point = (1.0, 1.0)
altitude_data_label.anchored_position = (470, DISPLAY_HEIGHT-25)
altitude_data_label.scale = (1)
altitude_data_label.color = text_white

vbat_label = label.Label(small_font)
vbat_label.anchor_point = (1.0, 1.0)
vbat_label.anchored_position = (DISPLAY_WIDTH-15, 15)
vbat_label.scale = (1)

plugbmp_label = label.Label(small_font)
plugbmp_label.anchor_point = (1.0, 1.0)
plugbmp_label.scale = (1)

greenbmp_label = label.Label(small_font)
greenbmp_label.anchor_point = (1.0, 1.0)
greenbmp_label.scale = (1)

bluebmp_label = label.Label(small_font)
bluebmp_label.anchor_point = (1.0, 1.0)
bluebmp_label.scale = (1)

yellowbmp_label = label.Label(small_font)
yellowbmp_label.anchor_point = (1.0, 1.0)
yellowbmp_label.scale = (1)

orangebmp_label = label.Label(small_font)
orangebmp_label.anchor_point = (1.0, 1.0)
orangebmp_label.scale = (1)

redbmp_label = label.Label(small_font)
redbmp_label.anchor_point = (1.0, 1.0)
redbmp_label.scale = (1)

# Load Bitmap to tile grid first (background layer)
bitmap = displayio.OnDiskBitmap("/images/Wallpaper_Spritesheet_8bit.bmp")
tile_grid = displayio.TileGrid(
    bitmap,
    pixel_shader=bitmap.pixel_shader,
    width=1,
    height=1,
    tile_width=DISPLAY_WIDTH,
    tile_height=DISPLAY_HEIGHT)

# Load battery voltage icons (from 1 sprite sheet image)
sprite_sheet, palette = adafruit_imageload.load("/icons/vbat_spritesheet.bmp",
                                                bitmap=displayio.Bitmap,
                                                palette=displayio.Palette)
sprite = displayio.TileGrid(sprite_sheet, pixel_shader=palette,
                            width=1,
                            height=1,
                            tile_width=11,
                            tile_height=20)
sprite_group = displayio.Group(scale=1)
sprite_group.append(sprite)
sprite_group.x = 470
sprite_group.y = 0

text_group = displayio.Group()
text_group.append(tile_grid)

main_group = displayio.Group()

# Add the sprite and castle to the group
main_group.append(text_group)
main_group.append(sprite_group)

# Label Display Group (foreground layer)
text_group.append(hello_label)
text_group.append(vbat_label)
text_group.append(temp_label)
text_group.append(temp_data_label)
text_group.append(humidity_label)
text_group.append(humidity_data_label)
text_group.append(barometric_label)
text_group.append(barometric_data_label)
text_group.append(altitude_label)
text_group.append(altitude_data_label)
text_group.append(plugbmp_label)
text_group.append(greenbmp_label)
text_group.append(bluebmp_label)
text_group.append(yellowbmp_label)
text_group.append(orangebmp_label)
text_group.append(redbmp_label)
display.show(main_group)

vbat_label.text = "{:.2f}".format(vbat)
source_index = 0
while True:
    # Label.text in the loop for sensor data updates
    hello_label.text = "Simple Offline Weatherstation"

    # Changes battery voltage color depending on charge level
    if vbat_label.text >= "4.23":
        vbat_label.color = text_white
        sprite[0] = 3
    elif vbat_label.text >= "4.10" and vbat_label.text <= "4.22":
        vbat_label.color = text_green
        sprite[0] = 1
    elif vbat_label.text >= "4.00" and vbat_label.text <= "4.09":
        vbat_label.color = text_blue
        sprite[0]
    elif vbat_label.text >= "3.90" and vbat_label.text <= "3.99":
        vbat_label.color = text_yellow
        sprite[0] = 5
    elif vbat_label.text >= "3.80" and vbat_label.text <= "3.89":
        vbat_label.color = text_orange
        sprite[0] = 2
    elif vbat_label.text <= "3.79":
        vbat_label.color = text_red
        sprite[0] = 4
    else:
        vbat_label.color = text_white
        
    tile_grid[0] = source_index % 4
    source_index += 1

    vbat_label.text
    temp_label.text = "°F"
    temp_data_label.text = "{:.1f}".format(bmp280.temperature*1.8+32)
    humidity_label.text = "Humidity"
    humidity_data_label.text = "{:.1f} %".format(sht31d.relative_humidity)
    altitude_label.text = "Altitude"
    altitude_data_label.text = "{:.1f} f".format(bmp280.altitude*3.28)
    barometric_label.text = "Pressure"
    barometric_data_label.text = f"{bmp280.pressure:.1f}"

    # Serial printout for debugging
    # print("Temperature: {:.1f} F".format(bmp280.temperature*1.8+32))
    # print("Humidity: {:.1f} %".format(sht31d.relative_humidity))
    # print("Barometric pressure:", bmp280.pressure)
    # print("Altitude: {:.1f} m".format(bmp280.altitude))
    # print("VBat voltage: {:.2f}".format(vbat))
    # print("Background Index Count: {:.2f}".format(source_index))

    time.sleep(60.0)
    pass
