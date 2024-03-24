# SPDX-FileCopyrightText: 2023 DJDevon3
# SPDX-License-Identifier: MIT
# ESP32-S3 Feather Weather MQTT Touchscreen
# Coded for Circuit Python 8.2.x

import os
import supervisor
import time
import board
import displayio
import fourwire
import digitalio
import terminalio
import pwmio
import adafruit_imageload
import adafruit_sdcard
import storage
import adafruit_connection_manager
import wifi
import adafruit_requests
import json
import ulab.numpy as np
import adafruit_minimqtt.adafruit_minimqtt as MQTT
from adafruit_minimqtt.adafruit_minimqtt import MMQTTException
from adafruit_display_text import label
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_bitmap_font import bitmap_font
from adafruit_lc709203f import LC709203F
from adafruit_bme280 import basic as adafruit_bme280
from adafruit_hx8357 import HX8357
import adafruit_stmpe610
from adafruit_button.sprite_button import SpriteButton
from soft_keyboard.soft_keyboard import SoftKeyboard, PRINTABLE_CHARACTERS
from slider import Slider

_now = time.monotonic()

# 3.5" TFT Featherwing is 480x320
displayio.release_displays()
DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 320

# Initalize Wifi, Socket Pool, Request Session
pool = adafruit_connection_manager.get_radio_socketpool(wifi.radio)
SSL_CONTEXT = adafruit_connection_manager.get_radio_ssl_context(wifi.radio)
# adafruit_requests.Session keep outside the main loop
# otherwise you get Out of Socket errors.
requests = adafruit_requests.Session(pool, SSL_CONTEXT)

# Use settings.toml for credentials
ssid = os.getenv("WIFI_SSID")
password = os.getenv("WIFI_PASSWORD")
aio_username = os.getenv("aio_username")
aio_key = os.getenv("aio_key")
# Local time & weather from lat/lon
OWKEY = os.getenv("openweather_token")
OWLAT = os.getenv("openweather_lat")
OWLON = os.getenv("openweather_lon")

# MQTT Topic
# Use this format for a standard MQTT broker
adafruitio_errors = aio_username + "/errors"
adafruitio_throttled = aio_username + "/throttle"
feed_01 = aio_username + "/feeds/BME280-Unbiased"
feed_02 = aio_username + "/feeds/BME280-RealTemp"
feed_03 = aio_username + "/feeds/BME280-Pressure"
feed_04 = aio_username + "/feeds/BME280-Humidity"
feed_05 = aio_username + "/feeds/BME280-Altitude"

# Time in seconds between updates (polling)
# 600 = 10 mins, 900 = 15 mins, 1800 = 30 mins, 3600 = 1 hour
sleep_time = 900

# Initialize TFT Display
spi = board.SPI()
tft_cs = board.D9
tft_dc = board.D10

display_bus = fourwire.FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = HX8357(display_bus, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT)
display.rotation = 0
_touch_flip = (False, True)

# Initialize 3.5" TFT Featherwing Touchscreen
ts_cs_pin = digitalio.DigitalInOut(board.D6)
touchscreen = adafruit_stmpe610.Adafruit_STMPE610_SPI(
    board.SPI(),
    ts_cs_pin,
    calibration=((231, 3703), (287, 3787)),
    size=(display.width, display.height),
    disp_rotation=display.rotation,
    touch_flip=_touch_flip,
)

# Initialize SDCard on TFT Featherwing
try:
    cs = digitalio.DigitalInOut(board.D5)
    sdcard = adafruit_sdcard.SDCard(spi, cs)
    vfs = storage.VfsFat(sdcard)
    virtual_root = "/sd"
    storage.mount(vfs, virtual_root)
except Exception as e:
    print(f"Error Loading SD Card: {e}")
    pass

# TFT Featherwing LITE Bodge Mod
# Use board.D8 for NRF52840 Sense, board.A5 for ESP32-S3
# Controls TFT backlight brightness via PWM signal
display_duty_cycle = 65535  # Values from 0 to 65535
TFT_brightness = pwmio.PWMOut(board.A5, frequency=500, duty_cycle=display_duty_cycle)
TFT_brightness.duty_cycle = 40000

# ---- FEATHER WEATHER SPLASH SCREEN -----
feather_weather = displayio.OnDiskBitmap("/images/feather_weather.bmp")
feather_weather_bg = displayio.TileGrid(
    feather_weather,
    pixel_shader=feather_weather.pixel_shader,
    width=1,
    height=1,
    tile_width=DISPLAY_WIDTH,
    tile_height=DISPLAY_HEIGHT,
)

# ---- SPLASH GROUP -----
splash_label = label.Label(terminalio.FONT)
splash_label.anchor_point = (0.5, 0.5)
splash_label.anchored_position = (DISPLAY_WIDTH / 2, DISPLAY_HEIGHT - 20)
splash_label.scale = 1
splash_label.color = 0xFFFFFF
loading_splash = displayio.Group()
loading_splash.append(feather_weather_bg)
loading_splash.append(splash_label)
display.root_group = loading_splash
splash_label.text = "Initializing BME280 Sensor..."

# Initialize BME280 Sensor
i2c = board.STEMMA_I2C()  # uses board.SCL and board.SDA
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
# sea_level_pressure should be set in the while true loop
# bme280.sea_level_pressure = bme280.pressure
# print("Sea Level Pressure: ", bme280.sea_level_pressure)
# print("Altitude = %0.2f meters" % bme280.altitude)

splash_label.text = "Initializing Battery Voltage Monitor..."
i2c = board.I2C()
battery_monitor = LC709203F(board.I2C())
# LC709203F github repo library
# https://github.com/adafruit/Adafruit_CircuitPython_LC709203F/blob/main/adafruit_lc709203f.py
# only up to 3000 supported, don't use PackSize if battery larger than 3000mah
# battery_monitor.pack_size = PackSize.MAH3000
battery_monitor.thermistor_bconstant = 3950
battery_monitor.thermistor_enable = True


def time_calc(input_time):
    # Attribution: Written by DJDevon3 & refined by Elpekenin
    """Converts seconds to minutes/hours/days"""
    if input_time < 60:
        return f"{input_time:.0f} seconds"
    if input_time < 3600:
        return f"{input_time / 60:.0f} minutes"
    if input_time < 86400:
        return f"{input_time / 60 / 60:.0f} hours"
    return f"{input_time / 60 / 60 / 24:.1f} days"


# OpenWeather 2.5 Free API
DATA_SOURCE = "https://api.openweathermap.org/data/2.5/onecall?"
DATA_SOURCE += "lat=" + OWLAT
DATA_SOURCE += "&lon=" + OWLON
DATA_SOURCE += "&exclude=hourly,daily"
DATA_SOURCE += "&appid=" + OWKEY
DATA_SOURCE += "&units=imperial"


def _format_date(datetime):
    """F-String formatted struct time conversion"""
    return (
        f"{datetime.tm_year:02}/" + f"{datetime.tm_mon:02}/" + f"{datetime.tm_mday:02} "
    )


def _format_time(datetime):
    """F-String formatted struct time conversion"""
    return f"{datetime.tm_hour:02}:" + f"{datetime.tm_min:02}"


splash_label.text = "Loading Fonts..."
# Fonts are optional
forkawesome_font = bitmap_font.load_font("/fonts/forkawesome-12.pcf")
arial_font = bitmap_font.load_font("/fonts/Arial-16.bdf")
small_font = bitmap_font.load_font("/fonts/GoodTimesRg-Regular-16.bdf")
medium_font = bitmap_font.load_font("/fonts/GoodTimesRg-Regular-40.bdf")
huge_font = bitmap_font.load_font("/fonts/GoodTimesRg-Regular-121.bdf")

splash_label.text = "Loading Font Colors..."
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

splash_label.text = "Loading Labels..."


def make_my_label(font, anchor_point, anchored_position, scale, color):
    """Minimizes labels to 1 liners. Attribution: Anecdata"""
    func_label = label.Label(font)
    func_label.anchor_point = anchor_point
    func_label.anchored_position = anchored_position
    func_label.scale = scale
    func_label.color = color
    return func_label


# name_label (FONT, (ANCHOR POINT), (ANCHOR POSITION), SCALE, COLOR)
# loading screen label
loading_label = make_my_label(
    terminalio.FONT, (0.5, 0.5), (DISPLAY_WIDTH / 2, DISPLAY_HEIGHT - 20), 1, TEXT_WHITE
)
hello_label = make_my_label(
    terminalio.FONT, (0.5, 1.0), (DISPLAY_WIDTH / 2, 15), 1, TEXT_WHITE
)
preferences_value = make_my_label(
    terminalio.FONT, (0.5, 0.5), (DISPLAY_WIDTH / 2, 5), 1, TEXT_WHITE
)
label_preferences_current_brightness = make_my_label(
    terminalio.FONT, (1.0, 1.0), (DISPLAY_WIDTH - 10, 80), 1, TEXT_CYAN
)
wifi_settings_ssid = make_my_label(
    terminalio.FONT, (0.0, 0.0), (DISPLAY_WIDTH / 3, 50), 2, TEXT_WHITE
)
wifi_settings_pw = make_my_label(
    terminalio.FONT, (0.0, 0.0), (DISPLAY_WIDTH / 3, 150), 2, TEXT_WHITE
)
wifi_settings_instructions = make_my_label(
    terminalio.FONT, (0.0, 0.0), (DISPLAY_WIDTH / 4, 250), 1, TEXT_WHITE
)

sys_info_data_label1 = make_my_label(
    terminalio.FONT, (0.0, 0.0), (5, 50), 2, TEXT_WHITE
)
sys_info_data_label2 = make_my_label(
    terminalio.FONT, (0.0, 0.0), (5, 150), 1, TEXT_WHITE
)
sys_info_data_label3 = make_my_label(
    terminalio.FONT, (0.0, 0.0), (5, 150 + 32), 1, TEXT_WHITE
)
sys_info_data_label4 = make_my_label(
    terminalio.FONT, (0.0, 0.0), (5, 150 + 48), 1, TEXT_WHITE
)
sys_info_data_label5 = make_my_label(
    terminalio.FONT, (0.0, 0.0), (5, 150 + 64), 1, TEXT_WHITE
)
sys_info_data_label6 = make_my_label(
    terminalio.FONT, (0.0, 0.0), (5, 150 + 80), 1, TEXT_WHITE
)
sys_info_data_label7 = make_my_label(
    terminalio.FONT, (0.0, 0.0), (5, 150 + 96), 1, TEXT_WHITE
)
rssi_data_label = make_my_label(terminalio.FONT, (0.0, 0.0), (5, 60), 1, TEXT_MAGENTA)
rssi_data_label0 = make_my_label(
    terminalio.FONT, (0.0, 0.0), (5, 60 + 20), 1, TEXT_WHITE
)
rssi_data_label1 = make_my_label(
    terminalio.FONT, (0.0, 0.0), (5, 60 + 40), 1, TEXT_WHITE
)
rssi_data_label2 = make_my_label(
    terminalio.FONT, (0.0, 0.0), (5, 60 + 60), 1, TEXT_WHITE
)
rssi_data_label3 = make_my_label(
    terminalio.FONT, (0.0, 0.0), (5, 60 + 80), 1, TEXT_WHITE
)
rssi_data_label4 = make_my_label(
    terminalio.FONT, (0.0, 0.0), (5, 60 + 100), 1, TEXT_WHITE
)
rssi_data_label5 = make_my_label(
    terminalio.FONT, (0.0, 0.0), (5, 60 + 120), 1, TEXT_WHITE
)
rssi_data_label6 = make_my_label(
    terminalio.FONT, (0.0, 0.0), (5, 60 + 140), 1, TEXT_WHITE
)
rssi_data_label7 = make_my_label(
    terminalio.FONT, (0.0, 0.0), (5, 60 + 160), 1, TEXT_WHITE
)
rssi_data_label8 = make_my_label(
    terminalio.FONT, (0.0, 0.0), (5, 60 + 180), 1, TEXT_WHITE
)
rssi_data_label9 = make_my_label(
    terminalio.FONT, (0.0, 0.0), (5, 60 + 200), 1, TEXT_WHITE
)

input_change_wifi = make_my_label(terminalio.FONT, (0.0, 0.0), (5, 50), 1, TEXT_WHITE)
input_new_cred = make_my_label(terminalio.FONT, (0.0, 0.0), (100, 50), 1, TEXT_WHITE)
input_lbl = label.Label(
    terminalio.FONT, scale=2, text="", color=0xFFFFFF, background_color=0x00000
)
input_lbl.x = 100
input_lbl.y = 50
warning_label = make_my_label(
    arial_font, (0.5, 0.5), (DISPLAY_WIDTH / 2, DISPLAY_HEIGHT - 103), 1, TEXT_RED
)
menu_popout_label = make_my_label(
    terminalio.FONT, (0.5, 0.5), (DISPLAY_WIDTH / 2, 25), 1, TEXT_CYAN
)
date_label = make_my_label(small_font, (0.0, 0.0), (5, 45), 1, TEXT_LIGHTBLUE)
time_label = make_my_label(small_font, (0.0, 0.0), (5, 65), 2, TEXT_LIGHTBLUE)
temp_label = make_my_label(small_font, (1.0, 1.0), (475, 123), 2, TEXT_ORANGE)
temp_data_label = make_my_label(
    huge_font, (0.5, 0.0), (DISPLAY_WIDTH / 2, 100), 1, TEXT_ORANGE
)
temp_data_shadow = make_my_label(
    huge_font, (0.5, 0.0), (DISPLAY_WIDTH / 2 + 2, 100 + 2), 1, TEXT_BLACK
)
owm_temp_data_label = make_my_label(
    medium_font, (0.5, 0.0), (DISPLAY_WIDTH / 2, 65), 1, TEXT_LIGHTBLUE
)
owm_temp_data_shadow = make_my_label(
    medium_font, (0.5, 0.0), (DISPLAY_WIDTH / 2 + 2, 65 + 2), 1, TEXT_BLACK
)
humidity_label = make_my_label(
    small_font, (0.0, 1.0), (5, DISPLAY_HEIGHT - 40), 1, TEXT_GRAY
)
humidity_data_label = make_my_label(
    medium_font, (0.0, 1.0), (5, DISPLAY_HEIGHT), 1, TEXT_ORANGE
)
owm_humidity_data_label = make_my_label(
    arial_font, (0.0, 1.0), (5, DISPLAY_HEIGHT - 60), 1, TEXT_LIGHTBLUE
)
barometric_label = make_my_label(
    small_font, (1.0, 1.0), (471, DISPLAY_HEIGHT - 40), 1, TEXT_GRAY
)
barometric_data_label = make_my_label(
    medium_font, (1.0, 1.0), (470, DISPLAY_HEIGHT), 1, TEXT_ORANGE
)
owm_barometric_data_label = make_my_label(
    arial_font, (1.0, 1.0), (470, DISPLAY_HEIGHT - 60), 1, TEXT_LIGHTBLUE
)
owm_windspeed_label = make_my_label(
    arial_font, (1.0, 1.0), (DISPLAY_WIDTH - 5, 90), 1, TEXT_LIGHTBLUE
)
vbat_label = make_my_label(arial_font, (1.0, 1.0), (DISPLAY_WIDTH - 15, 60), 1, None)
plugbmp_label = make_my_label(terminalio.FONT, (1.0, 1.0), None, 1, None)
greenbmp_label = make_my_label(terminalio.FONT, (1.0, 1.0), None, 1, None)
bluebmp_label = make_my_label(terminalio.FONT, (1.0, 1.0), None, 1, None)
yellowbmp_label = make_my_label(terminalio.FONT, (1.0, 1.0), None, 1, None)
orangebmp_label = make_my_label(terminalio.FONT, (1.0, 1.0), None, 1, None)
redbmp_label = make_my_label(terminalio.FONT, (1.0, 1.0), None, 1, None)

splash_label.text = "Loading Background Images..."
# Load Bitmap to tile grid first (Background layer)
DiskBMP = displayio.OnDiskBitmap("/images/Wallpaper_Spritesheet_8bit.bmp")
wallpaper = displayio.TileGrid(
    DiskBMP,
    pixel_shader=DiskBMP.pixel_shader,
    tile_width=480,
    tile_height=320,
)

splash_label.text = "Loading Icons..."
# Load battery voltage icons (from 1 sprite sheet image)
sprite_sheet, palette = adafruit_imageload.load(
    "/icons/vbat_spritesheet.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette
)
sprite = displayio.TileGrid(
    sprite_sheet, pixel_shader=palette, width=1, height=1, tile_width=11, tile_height=20
)
sprite_group = displayio.Group(scale=1)
sprite_group.append(sprite)
sprite_group.x = 470
sprite_group.y = 45

# Warning label RoundRect
roundrect = RoundRect(
    int(10),
    int(DISPLAY_HEIGHT - 125),
    DISPLAY_WIDTH - 10,
    40,
    10,
    fill=0x0,
    outline=0xFFFFFF,
    stroke=1,
)

# Menu RoundRect
menu_roundrect = RoundRect(
    int(130),  # start corner x
    int(5),  # start corner y
    DISPLAY_WIDTH - 200,  # width
    200,  # height
    10,  # corner radius
    fill=None,
    outline=0xFFFFFF,
    stroke=0,
)

splash_label.text = "Loading Touch Buttons..."
# Button width & height must be multiple of 3
# otherwise you'll get a tilegrid_inflator error
BUTTON_WIDTH = 12 * 16
BUTTON_HEIGHT = 3 * 16
BUTTON_MARGIN = 5

# Defiine the button
menu_button = SpriteButton(
    x=BUTTON_MARGIN,
    y=BUTTON_MARGIN,
    width=7 * 16,
    height=2 * 16,
    label="MENU",
    label_font=small_font,
    label_color=TEXT_WHITE,
    bmp_path="icons/gradient_button_0.bmp",
    selected_bmp_path="icons/gradient_button_1.bmp",
    transparent_index=0,
)

next_button = SpriteButton(
    x=DISPLAY_WIDTH - 3 * 16,
    y=BUTTON_MARGIN,
    width=3 * 16,
    height=2 * 16,
    label=">",
    label_font=arial_font,
    label_color=TEXT_WHITE,
    bmp_path="icons/gradient_button_0.bmp",
    selected_bmp_path="icons/gradient_button_1.bmp",
    transparent_index=0,
)

prev_button = SpriteButton(
    x=DISPLAY_WIDTH - 6 * 16 - 5,
    y=BUTTON_MARGIN,
    width=3 * 16,
    height=2 * 16,
    label="<",
    label_font=arial_font,
    label_color=TEXT_WHITE,
    bmp_path="icons/gradient_button_0.bmp",
    selected_bmp_path="icons/gradient_button_1.bmp",
    transparent_index=0,
)

item1_button = SpriteButton(
    x=135,
    y=50,
    width=BUTTON_WIDTH,
    height=BUTTON_HEIGHT,
    label="Preferences",
    label_font=arial_font,
    label_color=TEXT_WHITE,
    bmp_path="icons/gradient_button_0.bmp",
    selected_bmp_path="icons/gradient_button_1.bmp",
    transparent_index=0,
)

item2_button = SpriteButton(
    x=135,
    y=105,
    width=BUTTON_WIDTH,
    height=BUTTON_HEIGHT,
    label="WiFi Credentials",
    label_font=arial_font,
    label_color=TEXT_WHITE,
    bmp_path="icons/gradient_button_0.bmp",
    selected_bmp_path="icons/gradient_button_1.bmp",
    transparent_index=0,
)

item3_button = SpriteButton(
    x=135,
    y=160,
    width=BUTTON_WIDTH,
    height=BUTTON_HEIGHT,
    label="RSSI Scan",
    label_font=arial_font,
    label_color=TEXT_WHITE,
    bmp_path="icons/gradient_button_0.bmp",
    selected_bmp_path="icons/gradient_button_1.bmp",
    transparent_index=0,
)

item4_button = SpriteButton(
    x=135,
    y=215,
    width=BUTTON_WIDTH,
    height=BUTTON_HEIGHT,
    label="System Info",
    label_font=arial_font,
    label_color=TEXT_WHITE,
    bmp_path="icons/gradient_button_0.bmp",
    selected_bmp_path="icons/gradient_button_1.bmp",
    transparent_index=0,
)

item5_button = SpriteButton(
    x=135,
    y=270,
    width=BUTTON_WIDTH,
    height=BUTTON_HEIGHT,
    label="Change Credentials",
    label_font=arial_font,
    label_color=TEXT_WHITE,
    bmp_path="icons/gradient_button_0.bmp",
    selected_bmp_path="icons/gradient_button_1.bmp",
    transparent_index=0,
)

my_slider = Slider(x=5, y=50, width=300, value=40000)

splash_label.text = "Loading Soft Keyboard..."
soft_kbd = SoftKeyboard(
    2,
    100,
    DISPLAY_WIDTH - 2,
    DISPLAY_HEIGHT - 100,
    terminalio.FONT,
    forkawesome_font,
    layout_config="mobile_layout.json",
)
"""
soft_kbd2 = SoftKeyboard(
    2,
    100,
    DISPLAY_WIDTH - 2,
    DISPLAY_HEIGHT - 100,
    terminalio.FONT,
    forkawesome_font,
    layout_config="mobile_layout_special.json",
)
"""
splash_label.text = "Loading Display Groups..."
# Create subgroups
wallpaper_group = displayio.Group()
wallpaper_group.append(wallpaper)
splash = displayio.Group()
text_group = displayio.Group()
temp_group = displayio.Group()
warning_group = displayio.Group()
loading_group = displayio.Group()
menu_button_group = displayio.Group()
menu_popout_group = displayio.Group()
menu_popout_group_items = displayio.Group()
main_group = displayio.Group()

# Page 2 Groups
main_group2 = displayio.Group()

# Page 3 Groups
main_group3 = displayio.Group()

# Preferences Group
preferences_group = displayio.Group()

# Wifi Settings Group
wifi_settings_group = displayio.Group()

# RSSI Scan Group
rssi_group = displayio.Group()

# System Info Group
sys_info_group = displayio.Group()

# Wifi Change Credentials Group
wifi_change_group = displayio.Group()

# Add subgroups to main display group
main_group.append(splash)
main_group.append(wallpaper_group)
main_group.append(hello_label)
main_group.append(text_group)
main_group.append(warning_group)
main_group.append(loading_group)
main_group.append(temp_group)
main_group.append(sprite_group)
main_group.append(menu_button_group)
main_group.append(menu_popout_group)
main_group.append(menu_popout_group_items)

# Add warning popup group
warning_group.append(roundrect)
warning_group.append(warning_label)

# Label Display Group (foreground layer)
text_group.append(date_label)
text_group.append(time_label)
temp_group.append(temp_label)
temp_group.append(temp_data_shadow)
temp_group.append(temp_data_label)
temp_group.append(owm_temp_data_shadow)
temp_group.append(owm_temp_data_label)
text_group.append(humidity_label)
text_group.append(humidity_data_label)
text_group.append(owm_humidity_data_label)
text_group.append(barometric_label)
text_group.append(barometric_data_label)
text_group.append(owm_barometric_data_label)
text_group.append(owm_windspeed_label)
text_group.append(vbat_label)
text_group.append(plugbmp_label)
text_group.append(greenbmp_label)
text_group.append(bluebmp_label)
text_group.append(yellowbmp_label)
text_group.append(orangebmp_label)
text_group.append(redbmp_label)

# Add Menu popup group
menu_popout_group.append(menu_roundrect)
menu_popout_group.append(menu_popout_label)
menu_popout_group_items.append(item1_button)
menu_popout_group_items.append(item2_button)
menu_popout_group_items.append(item3_button)
menu_popout_group_items.append(item4_button)
menu_popout_group_items.append(item5_button)
menu_button_group.append(menu_button)
menu_button_group.append(next_button)
menu_button_group.append(prev_button)
# display.root_group = main_group

splash_label.text = "Loading Menu Functions..."


def show_warning(text):
    # Function to display weather popup warning
    warning_label.text = text
    warning_group.hidden = False


def hide_warning():
    # Function to hide weather popup warning
    warning_group.hidden = True


def show_menu():
    # Function to display popup menu
    menu_popout_label.text = "Menu Popout"
    menu_popout_group.hidden = False
    menu_popout_group_items.hidden = False


def hide_menu():
    # Function to hide popup menu
    menu_popout_group.hidden = True
    menu_popout_group_items.hidden = True


# Page Switching Function (FROM, TO)
def root_group_switch(SHOUTY_REMOVE, SHOUTY_APPEND):
    # Removal order is less important than append order
    hide_menu()
    SHOUTY_REMOVE.remove(wallpaper_group)
    SHOUTY_REMOVE.remove(hello_label)
    SHOUTY_REMOVE.remove(menu_button_group)
    SHOUTY_REMOVE.remove(menu_popout_group)
    SHOUTY_REMOVE.remove(menu_popout_group_items)
    if SHOUTY_REMOVE == main_group:
        SHOUTY_REMOVE.remove(text_group)
        SHOUTY_REMOVE.remove(warning_group)
        SHOUTY_REMOVE.remove(loading_group)
        SHOUTY_REMOVE.remove(temp_group)
        SHOUTY_REMOVE.remove(sprite_group)
    if SHOUTY_REMOVE == preferences_group:
        SHOUTY_REMOVE.remove(label_preferences_current_brightness)
        SHOUTY_REMOVE.remove(my_slider)
    if SHOUTY_REMOVE == wifi_settings_group:
        SHOUTY_REMOVE.remove(wifi_settings_ssid)
        SHOUTY_REMOVE.remove(wifi_settings_pw)
        SHOUTY_REMOVE.remove(wifi_settings_instructions)
    if SHOUTY_REMOVE == rssi_group:
        SHOUTY_REMOVE.remove(rssi_data_label)
        SHOUTY_REMOVE.remove(rssi_data_label0)
        SHOUTY_REMOVE.remove(rssi_data_label1)
        SHOUTY_REMOVE.remove(rssi_data_label2)
        SHOUTY_REMOVE.remove(rssi_data_label3)
        SHOUTY_REMOVE.remove(rssi_data_label4)
        SHOUTY_REMOVE.remove(rssi_data_label5)
        SHOUTY_REMOVE.remove(rssi_data_label6)
        SHOUTY_REMOVE.remove(rssi_data_label7)
        SHOUTY_REMOVE.remove(rssi_data_label8)
        SHOUTY_REMOVE.remove(rssi_data_label9)
    if SHOUTY_REMOVE == sys_info_group:
        SHOUTY_REMOVE.remove(sys_info_data_label1)
        SHOUTY_REMOVE.remove(sys_info_data_label2)
        SHOUTY_REMOVE.remove(sys_info_data_label3)
        SHOUTY_REMOVE.remove(sys_info_data_label4)
        SHOUTY_REMOVE.remove(sys_info_data_label5)
        SHOUTY_REMOVE.remove(sys_info_data_label6)
        SHOUTY_REMOVE.remove(sys_info_data_label7)
    if SHOUTY_REMOVE == wifi_change_group:
        SHOUTY_REMOVE.remove(input_change_wifi)
        SHOUTY_REMOVE.remove(input_new_cred)
        SHOUTY_REMOVE.remove(soft_kbd)
        SHOUTY_REMOVE.remove(input_lbl)

    # Append order is layer order top to bottom for each page.
    SHOUTY_APPEND.append(wallpaper_group)  # load wallpaper 1st regardless of page
    if SHOUTY_APPEND == main_group:
        SHOUTY_APPEND.append(text_group)
        SHOUTY_APPEND.append(warning_group)
        SHOUTY_APPEND.append(loading_group)
        SHOUTY_APPEND.append(temp_group)
        SHOUTY_APPEND.append(sprite_group)
    if SHOUTY_APPEND == preferences_group:
        SHOUTY_APPEND.append(label_preferences_current_brightness)
        SHOUTY_APPEND.append(my_slider)
    if SHOUTY_APPEND == wifi_settings_group:
        SHOUTY_APPEND.append(wifi_settings_ssid)
        SHOUTY_APPEND.append(wifi_settings_pw)
        SHOUTY_APPEND.append(wifi_settings_instructions)
    if SHOUTY_APPEND == rssi_group:
        SHOUTY_APPEND.append(rssi_data_label)
        SHOUTY_APPEND.append(rssi_data_label0)
        SHOUTY_APPEND.append(rssi_data_label1)
        SHOUTY_APPEND.append(rssi_data_label2)
        SHOUTY_APPEND.append(rssi_data_label3)
        SHOUTY_APPEND.append(rssi_data_label4)
        SHOUTY_APPEND.append(rssi_data_label5)
        SHOUTY_APPEND.append(rssi_data_label6)
        SHOUTY_APPEND.append(rssi_data_label7)
        SHOUTY_APPEND.append(rssi_data_label8)
        SHOUTY_APPEND.append(rssi_data_label9)
    if SHOUTY_APPEND == sys_info_group:
        SHOUTY_APPEND.append(sys_info_data_label1)
        SHOUTY_APPEND.append(sys_info_data_label2)
        SHOUTY_APPEND.append(sys_info_data_label3)
        SHOUTY_APPEND.append(sys_info_data_label4)
        SHOUTY_APPEND.append(sys_info_data_label5)
        SHOUTY_APPEND.append(sys_info_data_label6)
        SHOUTY_APPEND.append(sys_info_data_label7)
    if SHOUTY_APPEND == wifi_change_group:
        SHOUTY_APPEND.append(input_change_wifi)
        SHOUTY_APPEND.append(input_new_cred)
        SHOUTY_APPEND.append(soft_kbd)
        SHOUTY_APPEND.append(input_lbl)

    SHOUTY_APPEND.append(hello_label)
    SHOUTY_APPEND.append(menu_button_group)
    SHOUTY_APPEND.append(menu_popout_group)
    SHOUTY_APPEND.append(menu_popout_group_items)
    display.root_group = SHOUTY_APPEND


def group_cleanup():
    # When touch moves outside of button
    item1_button.selected = False
    item2_button.selected = False
    item3_button.selected = False
    item4_button.selected = False
    item5_button.selected = False
    menu_button.selected = False
    prev_button.selected = False
    next_button.selected = False


def menu_switching(
    current_group,
    prev_target,
    next_target,
    item1_target,
    item2_target,
    item3_target,
    item4_target,
    item5_target,
):
    if menu_button.contains(p):
        if not menu_button.selected:
            menu_button.selected = True
            time.sleep(0.25)
            print("Menu Pressed")
            show_menu()
    elif prev_button.contains(p):
        if not prev_button.selected:
            prev_button.selected = True
            time.sleep(0.1)
            print("Previous Pressed")
            root_group_switch(current_group, prev_target)
    elif next_button.contains(p):
        if not next_button.selected:
            next_button.selected = True
            time.sleep(0.5)
            print("Next Pressed")
            root_group_switch(current_group, next_target)
    elif not menu_popout_group.hidden:
        if item1_button.contains(p):
            if not item1_button.selected:
                item1_button.selected = True
                time.sleep(0.25)
                print("Item 1 Pressed")
                root_group_switch(current_group, item1_target)
        elif item2_button.contains(p):
            if not item2_button.selected:
                item2_button.selected = True
                time.sleep(0.25)
                print("Item 2 Pressed")
                root_group_switch(current_group, item2_target)
        elif item3_button.contains(p):
            if not item3_button.selected:
                item3_button.selected = True
                time.sleep(0.25)
                print("Item 3 Pressed")
                root_group_switch(current_group, item3_target)
        elif item4_button.contains(p):
            if not item4_button.selected:
                item4_button.selected = True
                time.sleep(0.25)
                print("Item 4 Pressed")
                root_group_switch(current_group, item4_target)
        elif item5_button.contains(p):
            if not item5_button.selected:
                item5_button.selected = True
                time.sleep(0.25)
                print("Item 5 Pressed")
                root_group_switch(current_group, item5_target)
        else:
            group_cleanup()
            hide_menu()
    else:
        group_cleanup()
        hide_menu()


hide_warning()
hide_menu()

splash_label.text = "Loading AdafruitIO Functions..."
# Define callback methods when events occur
def connect(mqtt_client, userdata, flags, rc):
    # Method when mqtt_client connected to the broker.
    print("| | ✅ Connected to MQTT Broker!")


def disconnect(mqtt_client, userdata, rc):
    # Method when the mqtt_client disconnects from broker.
    print("| | ✂️ Disconnected from MQTT Broker")


def subscribe(mqtt_client, userdata, topic, granted_qos):
    # Method when the mqtt_client subscribes to a new feed.
    print("Subscribed to {0} with QOS level {1}".format(topic, granted_qos))


def unsubscribe(mqtt_client, userdata, topic, pid):
    # Method when the mqtt_client unsubscribes from a feed.
    print("Unsubscribed from {0} with PID {1}".format(topic, pid))


def publish(mqtt_client, userdata, topic, pid):
    # Method when the mqtt_client publishes data to a feed.
    print(f"| | | Published {topic}")


def message(mqtt_client, topic, message):
    # Method client's subscribed feed has a new value.
    print("New message on topic {0}: {1}".format(topic, message))


def ioerrors(mqtt_client, topic, message):
    # Method for callback errors.
    print("New message on topic {0}: {1}".format(topic, message))


def throttle(mqtt_client, topic, message):
    # Method for callback errors.
    print("New message on topic {0}: {1}".format(topic, message))


# Initialize MQTT Client object
mqtt_client = MQTT.MQTT(
    broker="io.adafruit.com",
    username=aio_username,
    password=aio_key,
    socket_pool=pool,
    ssl_context=SSL_CONTEXT,
)

# Connect callback handlers to mqtt_client
mqtt_client.on_connect = connect
mqtt_client.on_disconnect = disconnect
mqtt_client.on_subscribe = subscribe
mqtt_client.on_unsubscribe = unsubscribe
mqtt_client.on_publish = publish
mqtt_client.on_message = message
mqtt_client.subscribe_to_errors = ioerrors
mqtt_client.subscribe_to_throttling = throttle

splash_label.text = "Loading Sensor Algorithms..."
display_temperature = 0
# Temperature Interpolation Algorithm
# pressure and humidity can affect temperature
# especially in sub-tropical climate!
humid_input_range = [0.0, 100]  # interpolated increase
humid_output_range = [0.0, 2.0]  # with humidity
input_range = [50.0, 69, 72, 73, 75, 76, 80, 88.0, 120.0]
output_range = [
    50.0 - 0.1,
    69,
    72.0 - 1.1,
    73.0 - 1.2,
    75.0 - 1.4,
    76 - 1.5,
    80 - 1.0,
    88.0 - 0.0,
    120.0 - 2.2,
]

last = time.monotonic()
First_Run = True
newline = "\n"
splash_label.text = "Loading GUI..."
while True:
    while display.root_group is main_group or loading_splash:
        wallpaper[0] = 0
        if not First_Run and display.root_group is main_group:
            loading_group.append(loading_label)
            loading_label.text = "Loading..."
        debug_OWM = False  # Set True for Serial Print Debugging
        bme280.sea_level_pressure = bme280.pressure
        hello_label.text = "Feather Weather ESP32-S3 MQTT Touch"
        print("===============================")

        # USB Power Sensing
        try:
            vbat_label.text = f"{battery_monitor.cell_voltage:.2f}v"
        except (ValueError, RuntimeError, OSError) as e:
            print("LC709203F Error: \n", e)

        # Set USB plug icon and voltage label to white
        usb_sense = supervisor.runtime.usb_connected
        if debug_OWM:
            print("USB Sense: ", usb_sense)  # Boolean value
        if usb_sense:  # if on USB power show plug sprite icon
            vbat_label.color = TEXT_WHITE
            sprite[0] = 5
        if not usb_sense:  # if on battery power only
            # Changes battery voltage color depending on charge level
            if vbat_label.text >= "4.23":
                vbat_label.color = TEXT_WHITE
                sprite[0] = 5
            elif "4.10" <= vbat_label.text <= "4.22":
                vbat_label.color = TEXT_GREEN
                sprite[0] = 0
            elif "4.00" <= vbat_label.text <= "4.09":
                vbat_label.color = TEXT_LIGHTBLUE
                sprite[0] = 1
            elif "3.90" <= vbat_label.text <= "3.99":
                vbat_label.color = TEXT_YELLOW
                sprite[0] = 2
            elif "3.80" <= vbat_label.text <= "3.89":
                vbat_label.color = TEXT_ORANGE
                sprite[0] = 3
            # TFT cutoff voltage is 3.70
            elif vbat_label.text <= "3.79":
                vbat_label.color = TEXT_RED
                sprite[0] = 4
            else:
                vbat_label.color = TEXT_WHITE

        # Local sensor data display
        temp_label.text = "°F"

        # Board Uptime
        print("Board Uptime: ", time_calc(time.monotonic()))

        # Account for PCB heating bias, gets slightly hotter as ambient increases
        BME280_humidity = round(bme280.relative_humidity, 1)
        relative_humidity = np.interp(
            BME280_humidity, humid_input_range, humid_output_range
        )
        humidity_adjust = round(relative_humidity[0], 2)
        print(f"Humidity Adjust: {humidity_adjust}")
        temperature = bme280.temperature * 1.8 + 32
        temp_round = round(temperature, 2)
        print("Temp: ", temperature)  # biased reading
        display_temperature = np.interp(temperature, input_range, output_range)
        BME280_temperature = round(display_temperature[0] + humidity_adjust, 2)
        print(f"Actual Temp: {BME280_temperature:.1f}")
        if debug_OWM:
            BME280_pressure = 1005  # Manually set debug warning message
            print(f"BME280 Pressure: {BME280_pressure}")
        else:
            BME280_pressure = round(bme280.pressure, 1)
        BME280_altitude = round(bme280.altitude, 2)

        temp_data_shadow.text = f"{BME280_temperature:.1f}"
        temp_data_label.text = f"{BME280_temperature:.1f}"
        humidity_label.text = "Humidity"
        humidity_data_label.text = f"{BME280_humidity:.1f} %"
        barometric_label.text = "Pressure"
        barometric_data_label.text = f"{BME280_pressure:.1f}"

        # Warnings based on local sensors
        if BME280_pressure <= 919:  # pray you never see this message
            show_warning("HOLY COW: Seek Shelter!")
        elif 920 <= BME280_pressure <= 979:
            show_warning("DANGER: Major Hurricane")
        elif 980 <= BME280_pressure <= 989:
            show_warning("DANGER: Minor Hurricane")
        elif 990 <= BME280_pressure <= 1001:
            show_warning("WARNING: Tropical Storm")
        elif 1002 <= BME280_pressure <= 1009:  # sudden gusty downpours
            show_warning("Low Pressure System")
        elif 1019 <= BME280_pressure <= 1025:  # sudden light cold rain
            show_warning("High Pressure System")
        elif BME280_pressure >= 1026:
            show_warning("WARNING: Hail & Tornados?")
        else:
            hide_warning()  # Normal pressures: 1110-1018 (no message)

        if First_Run and display.root_group is loading_splash:
            splash_label.text = "Initializing WiFi 4..."
        if not First_Run and display.root_group is main_group:
            loading_label.text = "Checking Wifi..."

        # Connect to Wi-Fi
        print("\nConnecting to WiFi...")
        while not wifi.radio.ipv4_address:
            try:
                wifi.radio.connect(ssid, password)
            except ConnectionError as e:
                print("❌ Connection Error:", e)
                print("Retrying in 10 seconds")
        print("✅ Wifi!")

        while wifi.radio.ipv4_address:
            try:
                print("| | Attempting to GET Weather...")
                if debug_OWM:
                    print("Full API GET URL: ", DATA_SOURCE)
                    print("\n===============================")
                with requests.get(DATA_SOURCE) as owm_request:

                    # uncomment the 2 lines below to see full json response
                    # warning: returns ALL JSON data, could crash your board
                    # dump_object = json.dumps(owm_request)
                    # print("JSON Dump: ", dump_object)
                    try:
                        owm_response = owm_request.json()
                        if owm_response["message"]:
                            print(
                                f"| | ❌ OpenWeatherMap Error:  {owm_response['message']}"
                            )
                            owm_request.close()
                    except (KeyError) as e:
                        if First_Run and display.root_group is loading_splash:
                            splash_label.text = "Getting Weather..."
                        if not First_Run and display.root_group is main_group:
                            loading_label.text = "Getting Weather..."
                        owm_response = owm_request.json()
                        print("| | Account within Request Limit", e)
                        print("| | ✅ Connected to OpenWeatherMap")

                        # Timezone & offset automatically returned based on lat/lon
                        get_timezone_offset = int(owm_response["timezone_offset"])  # 1
                        tz_offset_seconds = get_timezone_offset
                        if debug_OWM:
                            print(
                                f"Timezone Offset (in seconds): {get_timezone_offset}"
                            )
                        get_timestamp = int(
                            owm_response["current"]["dt"] + int(tz_offset_seconds)
                        )  # 2
                        current_unix_time = time.localtime(get_timestamp)
                        current_struct_time = time.struct_time(current_unix_time)
                        current_date = "{}".format(_format_date(current_struct_time))
                        current_time = "{}".format(_format_time(current_struct_time))

                        sunrise = int(
                            owm_response["current"]["sunrise"] + int(tz_offset_seconds)
                        )  # 3
                        sunrise_unix_time = time.localtime(sunrise)
                        sunrise_struct_time = time.struct_time(sunrise_unix_time)
                        sunrise_time = "{}".format(_format_time(sunrise_struct_time))

                        sunset = int(
                            owm_response["current"]["sunset"] + int(tz_offset_seconds)
                        )  # 4
                        sunset_unix_time = time.localtime(sunset)
                        sunset_struct_time = time.struct_time(sunset_unix_time)
                        sunset_time = "{}".format(_format_time(sunset_struct_time))

                        owm_temp = owm_response["current"]["temp"]  # 5
                        owm_pressure = owm_response["current"]["pressure"]  # 6
                        owm_humidity = owm_response["current"]["humidity"]  # 7
                        weather_type = owm_response["current"]["weather"][0][
                            "main"
                        ]  # 8
                        owm_windspeed = float(
                            owm_response["current"]["wind_speed"]
                        )  # 9

                        if "wind_gust" in owm_response["current"]:
                            owm_windgust = float(owm_response["current"]["wind_gust"])
                            print(f"| | | Gust: {owm_windgust}")
                        else:
                            print("| | | Gust: No Data")

                        print("| | | Sunrise:", sunrise_time)
                        print("| | | Sunset:", sunset_time)
                        print("| | | Temp:", owm_temp)
                        print("| | | Pressure:", owm_pressure)
                        print("| | | Humidity:", owm_humidity)
                        print("| | | Weather Type:", weather_type)
                        print("| | | Wind Speed:", owm_windspeed)
                        print("| | | Timestamp:", current_date + " " + current_time)

                        date_label.text = current_date
                        time_label.text = current_time
                        owm_windspeed_label.text = f"{owm_windspeed:.1f} mph"
                        owm_temp_data_shadow.text = f"{owm_temp:.1f}"
                        owm_temp_data_label.text = f"{owm_temp:.1f}"
                        owm_humidity_data_label.text = f"{owm_humidity:.1f} %"
                        owm_barometric_data_label.text = f"{owm_pressure:.1f}"
                        pass

            except (ValueError, RuntimeError) as e:
                print("ValueError: Failed to get OWM data, retrying\n", e)
                supervisor.reload()
                break
            except OSError as g:
                if g.errno == -2:
                    print("gaierror, breaking out of loop\n", g)
                    time.sleep(240)
                    break
            print("| | ✂️ Disconnected from OpenWeatherMap")

            # Connect to Adafruit IO
            try:
                print("| | Attempting MQTT Broker...")
                mqtt_client.connect()
                if First_Run and display.root_group is loading_splash:
                    splash_label.text = "Publishing to AdafruitIO..."
                if not First_Run and display.root_group is main_group:
                    loading_label.text = "Publishing..."
                mqtt_client.publish(feed_01, temp_round)
                # slight delay required between publishes!
                # otherwise only the 1st publish will succeed
                time.sleep(0.001)
                mqtt_client.publish(feed_02, BME280_temperature)
                time.sleep(1)
                mqtt_client.publish(feed_03, BME280_pressure)
                time.sleep(1)
                mqtt_client.publish(feed_04, BME280_humidity)
                time.sleep(1)
                mqtt_client.publish(feed_05, BME280_altitude)
                time.sleep(1)

            except (
                ValueError,
                RuntimeError,
                ConnectionError,
                OSError,
                MMQTTException,
            ) as ex:
                print("| | ❌ Failed to connect, retrying\n", ex)
                # traceback.print_exception(ex, ex, ex.__traceback__)
                # supervisor.reload()
                time.sleep(10)
                continue
            mqtt_client.disconnect()

            print("| ✂️ Disconnected from Wifi")
            print(f"Loading Time: {time.monotonic() - _now}")
            print("Next Update: ", time_calc(sleep_time))

            if not First_Run and display.root_group is main_group:
                loading_label.text = f"Next Update{newline}{time_calc(sleep_time)}"
                time.sleep(5)
                loading_group.remove(loading_label)

            if First_Run:
                First_Run = False
                display.root_group = main_group
                # Switch from splash to main_group
                loading_splash.remove(splash_label)
                loading_splash.remove(feather_weather_bg)

            print("Entering Touch Loop")
            while (
                time.monotonic() - last
            ) <= sleep_time and display.root_group is main_group:
                p = touchscreen.touch_point
                if p:
                    menu_switching(
                        main_group,
                        main_group3,
                        main_group2,
                        preferences_group,
                        wifi_settings_group,
                        rssi_group,
                        sys_info_group,
                        wifi_change_group,
                    )
                else:
                    # Default state always running
                    group_cleanup()
            last = time.monotonic()
            print("Exited Sleep Loop")
            break
            # time.sleep(sleep_time)

    while display.root_group is main_group2:
        wallpaper[0] = 1
        hello_label.text = "Feather Weather Page 2"
        while (
            time.monotonic() - last
        ) <= sleep_time and display.root_group is main_group2:
            p = touchscreen.touch_point
            if p:
                menu_switching(
                    main_group2,
                    main_group,
                    main_group3,
                    preferences_group,
                    wifi_settings_group,
                    rssi_group,
                    sys_info_group,
                    wifi_change_group,
                )
            else:
                # Default state always running
                group_cleanup()
        last = time.monotonic()

    while display.root_group is main_group3:
        wallpaper[0] = 2
        hello_label.text = "Feather Weather Page 3"
        while (
            time.monotonic() - last
        ) <= sleep_time and display.root_group is main_group3:
            p = touchscreen.touch_point
            if p:
                menu_switching(
                    main_group3,
                    main_group2,
                    main_group,
                    preferences_group,
                    wifi_settings_group,
                    rssi_group,
                    sys_info_group,
                    wifi_change_group,
                )
            else:
                # Default state always running
                group_cleanup()
        last = time.monotonic()

    while display.root_group is preferences_group:
        wallpaper[0] = 3
        hello_label.text = "Feather Weather Preferences"
        while (
            time.monotonic() - last
        ) <= sleep_time and display.root_group is preferences_group:
            p = touchscreen.touch_point
            if (
                p
            ):  # Check each slider if the touch point is within the slider touch area
                if my_slider.when_inside(p):
                    try:
                        my_slider.when_selected(p)
                        print(f"Slider Value: {p[0]}")
                        print(f"Slider Adjusted: {int(p[0] / 300 * 65000)}")
                        _Slider_New_Value = int(p[0] / 300 * 65000)
                        print(f"TFT_brightness.duty_cycle : {_Slider_New_Value}")
                        TFT_brightness.duty_cycle = _Slider_New_Value
                        label_preferences_current_brightness.text = "Display Brightness"
                    except Exception as e:
                        print(e)
                        continue
                menu_switching(
                    preferences_group,
                    main_group,
                    main_group,
                    preferences_group,
                    wifi_settings_group,
                    rssi_group,
                    sys_info_group,
                    wifi_change_group,
                )
            else:
                # Default state always running
                group_cleanup()
        last = time.monotonic()

    while display.root_group is wifi_settings_group:
        wallpaper[0] = 3
        hello_label.text = "Wifi Settings"
        ssid_len = len(ssid)
        ssid_dash_replace = "*" * (ssid_len - 2)
        ssid_ast = ssid.replace(ssid[2:ssid_len], ssid_dash_replace)
        wifi_settings_ssid.text = f"SSID: \n{ssid_ast}"

        appw_len = len(password)
        appw_dash_replace = "*" * (appw_len - 2)
        appw_ast = appw.replace(appw[2:appw_len], appw_dash_replace)
        wifi_settings_pw.text = f"Password: \n{appw_ast}"
        wifi_settings_instructions.text = "To change SSID & PW connect USB cable to PC\nOpen CIRCUITPY USB drive\nEdit settings.toml file"

        while (
            time.monotonic() - last
        ) <= sleep_time and display.root_group is wifi_settings_group:
            p = touchscreen.touch_point
            if p:
                menu_switching(
                    wifi_settings_group,
                    main_group,
                    main_group,
                    preferences_group,
                    wifi_settings_group,
                    rssi_group,
                    sys_info_group,
                    wifi_change_group,
                )
            else:
                # Default state always running
                group_cleanup()
        last = time.monotonic()

    while display.root_group is rssi_group:
        wallpaper[0] = 3
        hello_label.text = "WiFi Signal Strength"
        # Displays available networks sorted by RSSI
        networks = []
        NetworkList = []
        for network in wifi.radio.start_scanning_networks():
            networks.append(network)
        wifi.radio.stop_scanning_networks()
        networks = sorted(networks, key=lambda net: net.rssi, reverse=True)
        for network in networks:
            sorted_networks = {
                "ssid": network.ssid,
                "rssi": network.rssi,
                "channel": network.channel,
            }
            NetworkList.append([sorted_networks])
            # print("ssid:",network.ssid, "rssi:",network.rssi, "channel:",network.channel)
        jsonNetworkList = json.dumps(NetworkList)
        json_list = json.loads(jsonNetworkList)
        # print(f"Items in RSSI List: {len(json_list)}")
        rssi_data_label.text = "SSID\t\t\t\t\t\t\t  RSSI\t\t\t\t    CHANNEL\n"
        try:
            for i in range(min(10, len(json_list))):
                label_text = f"{json_list[i][0]['ssid']:<30}\t{json_list[i][0]['rssi']:<20}\t{json_list[i][0]['channel']:<20}\n"
                globals()[f"rssi_data_label{i}"].text = label_text
        except Exception as e:
            print(f"RSSI List Error: {e}")
            pass

        while (
            time.monotonic() - last
        ) <= sleep_time and display.root_group is rssi_group:
            p = touchscreen.touch_point
            if p:
                menu_switching(
                    rssi_group,
                    main_group,
                    main_group,
                    preferences_group,
                    wifi_settings_group,
                    rssi_group,
                    sys_info_group,
                    wifi_change_group,
                )
            else:
                # Default state always running
                group_cleanup()
        last = time.monotonic()

    while display.root_group is sys_info_group:
        wallpaper[0] = 3
        hello_label.text = "System Information"
        # System Stats
        u_name = os.uname()
        sys_info_data_label1.text = f"Circuit Python Version:\n{u_name[3]}"
        sys_info_data_label2.text = f"Board: \n{u_name[4]}"
        sys_info_data_label3.text = f"Logic Chip: {u_name[0]}"
        fs_stat = os.statvfs("/")
        NORdisk_size = fs_stat[0] * fs_stat[2] / 1024 / 1024
        NORfree_space = fs_stat[0] * fs_stat[3] / 1024 / 1024
        sys_info_data_label4.text = f"Flash Chip Size: {NORdisk_size:.2f} MB"
        NORdisk_used = NORdisk_size - NORfree_space
        if (NORdisk_used) >= 1.0:
            sys_info_data_label5.text = f"Flash Chip Used: {NORdisk_used:.2f} MB"
        if (NORdisk_used) <= 1.0:
            sys_info_data_label5.text = f"Flash Chip Used: {NORdisk_used*1024:.2f} KB"
        sys_info_data_label6.text = f"Flash Chip Free: {NORfree_space:.2f} MB"

        # Volume Information Stats
        try:
            SD_Card_Size = os.statvfs(virtual_root)
            SD_Card_FREE_TOTAL = SD_Card_Size[0] * SD_Card_Size[3] / 1024 / 1024 / 1024
            if (SD_Card_FREE_TOTAL) >= 1.0:
                sys_info_data_label7.text = f"SD Card Free: {SD_Card_FREE_TOTAL:.2f} GB"
            if (SD_Card_FREE_TOTAL) <= 1.0:
                SD_Card_FREE_TOTAL_MB = SD_Card_Size[0] * SD_Card_Size[3] / 1024 / 1024
                sys_info_data_label7.text = (
                    f"SD Card Free: {SD_Card_FREE_TOTAL_MB:.2f} MB"
                )
            # storage.umount(vfs)
        except Exception as e:
            print(e)
            pass

        while (
            time.monotonic() - last
        ) <= sleep_time and display.root_group is sys_info_group:
            p = touchscreen.touch_point
            if p:
                menu_switching(
                    sys_info_group,
                    main_group,
                    main_group,
                    preferences_group,
                    wifi_settings_group,
                    rssi_group,
                    sys_info_group,
                    wifi_change_group,
                )
            else:
                # Default state always running
                group_cleanup()
        last = time.monotonic()

    while display.root_group is wifi_change_group:
        wallpaper[0] = 3
        hello_label.text = "Wifi Edit Credentials"
        input_change_wifi.text = "New Password: "

        while (
            time.monotonic() - last
        ) <= sleep_time and display.root_group is wifi_change_group:
            p = touchscreen.touch_point
            key_value = soft_kbd.check_touches(p)
            if p:
                if key_value in PRINTABLE_CHARACTERS:
                    input_lbl.text += key_value
                elif key_value == 42:  # 0x2a backspace key
                    input_lbl.text = input_lbl.text[:-1]
                elif key_value == 224:  # special character switch key
                    input_lbl.text = input_lbl.text[:-1]
                menu_switching(
                    wifi_change_group,
                    main_group2,
                    main_group,
                    preferences_group,
                    wifi_settings_group,
                    rssi_group,
                    sys_info_group,
                    wifi_change_group,
                )
            else:
                # Default state always running
                group_cleanup()
        last = time.monotonic()
