# SPDX-FileCopyrightText: 2024 DJDevon3
# SPDX-License-Identifier: MIT
# Coded for Circuit Python 9.x
"""Rachio Touch Screen"""

import board
import supervisor
import os
import time

import adafruit_imageload
import adafruit_connection_manager
import displayio
import fourwire
import json
import terminalio
import wifi

import adafruit_requests
from circuitpython_st7796s import ST7796S
from circuitpython_xpt2046 import Touch
from adafruit_lc709203f import LC709203F
from adafruit_display_text import label, outlined_label
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_bitmap_font import bitmap_font
from adafruit_button.sprite_button import SpriteButton
from adafruit_button import Button

# Rachio API Key required (comes with purchase of a device)
# API is rate limited to 1700 calls per day.
# https://support.rachio.com/en_us/public-api-documentation-S1UydL1Fv
# https://rachio.readme.io/reference/getting-started
RACHIO_KEY = os.getenv("RACHIO_APIKEY")

# Get WiFi details, ensure these are setup in settings.toml
ssid = os.getenv("CIRCUITPY_WIFI_SSID")
password = os.getenv("CIRCUITPY_WIFI_PASSWORD")

# API Polling Rate
# 900 = 15 mins, 1800 = 30 mins, 3600 = 1 hour
SLEEP_TIME = 3600

# Set debug to True for full JSON response.
# WARNING: absolutely shows extremely sensitive personal information & credentials
# Including your real name, latitude, longitude, account id, mac address, etc...
DEBUG = False

# Initalize Wifi, Socket Pool, Request Session
pool = adafruit_connection_manager.get_radio_socketpool(wifi.radio)
ssl_context = adafruit_connection_manager.get_radio_ssl_context(wifi.radio)
requests = adafruit_requests.Session(pool, ssl_context)
rssi = wifi.radio.ap_info.rssi

RACHIO_HEADER = {"Authorization": " Bearer " + RACHIO_KEY}
RACHIO_SOURCE = "https://api.rach.io/1/public/person/info/"
RACHIO_PERSON_SOURCE = "https://api.rach.io/1/public/person/"

def obfuscating_asterix(obfuscate_object, direction, characters=2):
    """
    Obfuscates a string with asterisks except for a specified number of characters.
    param object: str The string to obfuscate with asterisks
    param direction: str Option either 'prepend', 'append', or 'all' direction
    param characters: int The number of characters to keep unobfuscated (default is 2)
    """
    object_len = len(obfuscate_object)
    if direction not in {"prepend", "append", "all"}:
        raise ValueError("Invalid direction. Use 'prepend', 'append', or 'all'.")
    if characters >= object_len and direction != "all":
        # If characters greater than or equal to string length,
        # return the original string as it can't be obfuscated.
        return obfuscate_object
    asterix_replace = "*" * object_len
    if direction == "append":
        asterix_final = obfuscate_object[:characters] + "*" * (object_len - characters)
    elif direction == "prepend":
        asterix_final = "*" * (object_len - characters) + obfuscate_object[-characters:]
    elif direction == "all":
        # Replace all characters with asterisks
        asterix_final = asterix_replace

    return asterix_final

def time_calc(input_time):
    """Converts seconds to minutes/hours/days"""
    if input_time < 60:
        return f"{input_time:.0f} seconds"
    if input_time < 3600:
        return f"{input_time / 60:.0f} minutes"
    if input_time < 86400:
        return f"{input_time / 60 / 60:.0f} hours"
    return f"{input_time / 60 / 60 / 24:.1f} days"

def _format_datetime(datetime):
    """ F-String formatted struct time conversion"""
    return (f"{datetime.tm_mon:02}/" +
            f"{datetime.tm_mday:02}/" +
            f"{datetime.tm_year:02} " +
            f"{datetime.tm_hour:02}:" +
            f"{datetime.tm_min:02}:" +
            f"{datetime.tm_sec:02}")

def _rachio_timestamp(rachio_time, rachio_timezone_offset):
    """ Convert Rachio timestamps from milliseconds to human readable time"""
    # Rachio Unix time is in milliseconds, convert to seconds
    rachio_createdate_seconds = rachio_time // 1000
    rachio_timezone_offset_seconds = rachio_timezone_offset // 1000
    # Apply timezone offset in seconds
    local_unix_time = rachio_createdate_seconds + rachio_timezone_offset_seconds
    current_struct_time = time.localtime(local_unix_time)
    rachio_converted_timestamp = "{}".format(_format_datetime(current_struct_time))
    return rachio_converted_timestamp

displayio.release_displays()
# 3.5" ST7796S Display
DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 320
DISPLAY_ROTATION = 180

tft_cs = board.D9
tft_dc = board.D10
tft_rst = board.A3
sd_cs = board.D5
ts_cs = board.D6

spi = board.SPI()
display_bus = fourwire.FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_rst)
display = ST7796S(display_bus, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, rotation=DISPLAY_ROTATION)

# Touch calibration
TOUCH_X_MIN = 150
TOUCH_X_MAX = 2000
TOUCH_Y_MIN = 150
TOUCH_Y_MAX = 2000

touch = Touch(
    spi=spi,
    cs=ts_cs,
    width=DISPLAY_WIDTH,
    height=DISPLAY_HEIGHT,
    rotation=DISPLAY_ROTATION,
    x_min=TOUCH_X_MIN,
    x_max=TOUCH_X_MAX,
    y_min=TOUCH_Y_MIN,
    y_max=TOUCH_Y_MAX,
)

# LC709203F Battery Monitor
i2c = board.I2C()
while not i2c.try_lock():
    pass
i2c_address_list = i2c.scan()
i2c.unlock()
if 0x0b in i2c_address_list:
    battery_monitor = LC709203F(board.I2C())
    # Update to match the mAh of your battery for more accurate readings.
    # Can be MAH100, MAH200, MAH400, MAH500, MAH1000, MAH2000, MAH3000.
    # Choose the closest match. Include "PackSize." before it, as shown.
    # battery_monitor.pack_size = PackSize.MAH400
    battery_monitor.thermistor_bconstant = 3950
    battery_monitor.thermistor_enable = True

# Quick Colors for Labels
TEXT_BLACK = 0x000000
TEXT_BLUE = 0x0000FF
TEXT_CYAN = 0x00FFFF
TEXT_DARK_GRAY = 0x5A5A5A
TEXT_GRAY = 0x8B8B8B
TEXT_GREEN = 0x00FF00
TEXT_LIGHTBLUE = 0x90C7FF
TEXT_MAGENTA = 0xFF00FF
TEXT_ORANGE = 0xFFA500
TEXT_PURPLE = 0x800080
TEXT_RACHIOBLUE = 0x00a7e1
TEXT_RACHIO_OUTLINE = 0xa1def4
TEXT_RACHIO_FOOTER = 0x131313
TEXT_RED = 0xFF0000
TEXT_WHITE = 0xFFFFFF
TEXT_YELLOW = 0xFFFF00

Arial12 = bitmap_font.load_font("/fonts/Arial-12.bdf")
Arial16 = bitmap_font.load_font("/fonts/Arial-16.bdf")
ForkAwesome12 = bitmap_font.load_font("/fonts/forkawesome-12.pcf")

def make_my_label(font, anchor_point, anchored_position, scale, color):
    """Minimizes labels to 1 liners. Attribution: Anecdata"""
    func_label = label.Label(font)
    func_label.anchor_point = anchor_point
    func_label.anchored_position = anchored_position
    func_label.scale = scale
    func_label.color = color
    return func_label

# name_label (FONT, (ANCHOR POINT), (ANCHOR POSITION), SCALE, COLOR)
loading_label = make_my_label(
    Arial12, (0.5, 1.0), (DISPLAY_WIDTH / 2, DISPLAY_HEIGHT-10), 1, TEXT_WHITE
)
hello_label = make_my_label(
    Arial12, (0.5, 1.0), (DISPLAY_WIDTH / 2, 50), 1, TEXT_WHITE
)
menu_popout_label = make_my_label(
    terminalio.FONT, (0.5, 0.5), (DISPLAY_WIDTH / 2, 25), 1, TEXT_CYAN
)
zone0_label = make_my_label(
    Arial12, (0.5, 1.0), (DISPLAY_WIDTH / 4, 170), 1, TEXT_LIGHTBLUE
)
zone1_label = make_my_label(
    Arial12, (0.5, 1.0), (DISPLAY_WIDTH / 4+110, 170), 1, TEXT_LIGHTBLUE
)
zone2_label = make_my_label(
    Arial12, (0.5, 1.0), (DISPLAY_WIDTH / 4+220, 170), 1, TEXT_LIGHTBLUE
)
wifi_label = make_my_label(
    ForkAwesome12, (1.0, 0.0), (DISPLAY_WIDTH -5, 5), 1, TEXT_GREEN
)
vbat_label = make_my_label(Arial12, (1.0, 1.0), (DISPLAY_WIDTH - 20, 20), 1, None)
plugbmp_label = make_my_label(terminalio.FONT, (1.0, 1.0), None, 1, None)
greenbmp_label = make_my_label(terminalio.FONT, (1.0, 1.0), None, 1, None)
bluebmp_label = make_my_label(terminalio.FONT, (1.0, 1.0), None, 1, None)
yellowbmp_label = make_my_label(terminalio.FONT, (1.0, 1.0), None, 1, None)
orangebmp_label = make_my_label(terminalio.FONT, (1.0, 1.0), None, 1, None)
redbmp_label = make_my_label(terminalio.FONT, (1.0, 1.0), None, 1, None)

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

text_area = outlined_label.OutlinedLabel(
    Arial12,
    color=TEXT_RACHIOBLUE,
    outline_color=TEXT_BLACK,
    outline_size=1,
    padding_left=2,
    padding_right=2,
    padding_top=2,
    padding_bottom=2,
    scale=1,
    anchor_point = (0.0, 0.0),
    anchored_position = (5, 50)
)

# Load battery voltage icons (from 1 sprite sheet image)
sprite_sheet, palette = adafruit_imageload.load(
    "/icons/vbat_spritesheet.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette
)
sprite = displayio.TileGrid(
    sprite_sheet, pixel_shader=palette, width=1, height=1, tile_width=11, tile_height=20
)
sprite_group = displayio.Group(scale=1)
sprite_group.append(sprite)
sprite_group.x = 465
sprite_group.y = 2

# Load Bitmap to tile grid first (Background layer)
DiskBMP = displayio.OnDiskBitmap("/images/Rachio_Wallpaper_480x320_8bit.bmp")
wallpaper = displayio.TileGrid(
    DiskBMP,
    pixel_shader=DiskBMP.pixel_shader,
    tile_width=480,
    tile_height=320,
)

RachioBMP = displayio.OnDiskBitmap("/images/Rachio_Logo_white_small_8bit.bmp")
rachio_logo = displayio.TileGrid(
    RachioBMP,
    pixel_shader=RachioBMP.pixel_shader,
    tile_width=100,
    tile_height=26,
    x=DISPLAY_WIDTH//2-50,
    y=7
)
logo_palette = RachioBMP.pixel_shader
logo_palette.make_transparent(0)

Events_BMP = displayio.OnDiskBitmap("/icons/events_white.bmp")
icon_events = displayio.TileGrid(
    Events_BMP,
    pixel_shader=Events_BMP.pixel_shader,
    tile_width=30,
    tile_height=30,
    x=int(DISPLAY_WIDTH/3-50),
    y=int(DISPLAY_HEIGHT-44)
)
icon_events_palette = Events_BMP.pixel_shader
icon_events_palette.make_transparent(0)

Zones_BMP = displayio.OnDiskBitmap("/icons/zones_white.bmp")
icon_zones = displayio.TileGrid(
    Zones_BMP,
    pixel_shader=Zones_BMP.pixel_shader,
    tile_width=30,
    tile_height=30,
    x=int(DISPLAY_WIDTH/2),
    y=int(DISPLAY_HEIGHT-44)
)
icon_zones_palette = Zones_BMP.pixel_shader
icon_zones_palette.make_transparent(0)

Schedules_BMP = displayio.OnDiskBitmap("/icons/schedules_white.bmp")
icon_schedules = displayio.TileGrid(
    Schedules_BMP,
    pixel_shader=Schedules_BMP.pixel_shader,
    tile_width=30,
    tile_height=30,
    x=int(DISPLAY_WIDTH*0.75),
    y=int(DISPLAY_HEIGHT-44)
)
icon_schedules_palette = Schedules_BMP.pixel_shader
icon_schedules_palette.make_transparent(0)

Zone0_BG_BMP = displayio.OnDiskBitmap("/images/Zone_BG_8bit.bmp")
zone0bg = displayio.TileGrid(
    Zone0_BG_BMP,
    pixel_shader=Zone0_BG_BMP.pixel_shader,
    tile_width=100,
    tile_height=100,
    x=int(DISPLAY_WIDTH/4-50),
    y=75
)
zone0bg_palette = Zone0_BG_BMP.pixel_shader
zone0bg_palette.make_transparent(0)

Zone1_BG_BMP = displayio.OnDiskBitmap("/images/Zone_BG_8bit.bmp")
zone1bg = displayio.TileGrid(
    Zone1_BG_BMP,
    pixel_shader=Zone1_BG_BMP.pixel_shader,
    tile_width=100,
    tile_height=100,
    x=int(DISPLAY_WIDTH/4-50+110),
    y=75
)
zone1bg_palette = Zone1_BG_BMP.pixel_shader
zone1bg_palette.make_transparent(0)

Zone2_BG_BMP = displayio.OnDiskBitmap("/images/Zone_BG_8bit.bmp")
zone2bg = displayio.TileGrid(
    Zone2_BG_BMP,
    pixel_shader=Zone2_BG_BMP.pixel_shader,
    tile_width=100,
    tile_height=100,
    x=int(DISPLAY_WIDTH/4-50+220),
    y=75
)
zone2bg_palette = Zone2_BG_BMP.pixel_shader
zone2bg_palette.make_transparent(0)

zone0_rect = RoundRect(
    x=int(DISPLAY_WIDTH/4-50),
    y=75,
    width=100,
    height=100,
    r=10,
    fill=None,
    outline=TEXT_RED,
    stroke=1,
)
zone1_rect = RoundRect(
    x=int(DISPLAY_WIDTH/4-50+110),
    y=75,
    width=100,
    height=100,
    r=10,
    fill=None,
    outline=TEXT_BLUE,
    stroke=1,
)
zone2_rect = RoundRect(
    x=int(DISPLAY_WIDTH/4-50+220),
    y=75,
    width=100,
    height=100,
    r=10,
    fill=None,
    outline=TEXT_GREEN,
    stroke=1,
)

# Popout Menu RoundRect
menu_roundrect = RoundRect(
    int(50),  # start corner x
    int(50),  # start corner y
    DISPLAY_WIDTH - 100,  # width
    DISPLAY_HEIGHT - 100,  # height
    10,  # corner radius
    fill=TEXT_DARK_GRAY,
    outline=0xFFFFFF,
    stroke=1,
)

# Footer Rect
footer_rect = Rect(
    int(0),  # start corner x
    int(DISPLAY_HEIGHT-50),  # start corner y
    DISPLAY_WIDTH,  # width
    50,  # height
    fill=TEXT_RACHIO_FOOTER,
    outline=0xFFFFFF,
    stroke=0,
)

# Footer Rect
loading_rect = Rect(
    int(0),  # start corner x
    int(DISPLAY_HEIGHT-50),  # start corner y
    DISPLAY_WIDTH,  # width
    50,  # height
    fill=TEXT_DARK_GRAY,
    outline=0xFFFFFF,
    stroke=0,
)

# Button width & height must be multiple of 3
# otherwise you'll get a tilegrid_inflator error
menu_button = SpriteButton(
    x=5,
    y=5,
    width=50,
    height=32,
    label="\uf0c9",
    label_font=ForkAwesome12,
    label_color=TEXT_WHITE,
    bmp_path="icons/gradient_button_0.bmp",
    selected_bmp_path="icons/gradient_button_1.bmp",
    transparent_index=0,
)

water_button = Button(
    x=DISPLAY_WIDTH-43,
    y=DISPLAY_HEIGHT-57,
    width=40,
    height=60,
    label="\uf04b",
    label_font=ForkAwesome12,
    label_color=TEXT_WHITE,
    fill_color=None,
    outline_color=None,
)

# Footer Rect
water_circle = Circle(
    int(DISPLAY_WIDTH-26),  # start corner x
    int(DISPLAY_HEIGHT-27),  # start corner y
    r=16,  # height
    fill=TEXT_RACHIOBLUE,
    outline=TEXT_RACHIO_OUTLINE,
    stroke=2,
)

item1_button = SpriteButton(
    x=int(DISPLAY_WIDTH/2-100),
    y=60,
    width=200,
    height=32,
    label="Home",
    label_font=Arial12,
    label_color=TEXT_WHITE,
    bmp_path="icons/gradient_button_0.bmp",
    selected_bmp_path="icons/gradient_button_1.bmp",
    transparent_index=0,
)

item2_button = SpriteButton(
    x=int(DISPLAY_WIDTH/2-100),
    y=100,
    width=200,
    height=32,
    label="Device Info",
    label_font=Arial12,
    label_color=TEXT_WHITE,
    bmp_path="icons/gradient_button_0.bmp",
    selected_bmp_path="icons/gradient_button_1.bmp",
    transparent_index=0,
)

item3_button = SpriteButton(
    x=int(DISPLAY_WIDTH/2-100),
    y=140,
    width=200,
    height=32,
    label="WiFi Credentials",
    label_font=Arial12,
    label_color=TEXT_WHITE,
    bmp_path="icons/gradient_button_0.bmp",
    selected_bmp_path="icons/gradient_button_1.bmp",
    transparent_index=0,
)

# Groups & Sub-Groups
main_group = displayio.Group()
deviceinfo_group = displayio.Group()
wifi_credentials_group = displayio.Group()
wallpaper_group = displayio.Group()
menu_button_group = displayio.Group()
water_button_group = displayio.Group()
text_group = displayio.Group()
battery_group = displayio.Group()
loading_group = displayio.Group()
menu_popout_group = displayio.Group()
menu_popout_group_items = displayio.Group()
footer_rect_group = displayio.Group()

wallpaper_group.append(wallpaper)
wallpaper_group.append(rachio_logo)
footer_rect_group.append(footer_rect)
footer_rect_group.append(icon_events)
footer_rect_group.append(icon_zones)
footer_rect_group.append(icon_schedules)
water_button_group.append(water_circle)
water_button_group.append(water_button)
loading_group.append(loading_rect)
loading_group.append(loading_label)

text_group.append(text_area)
battery_group.append(vbat_label)
battery_group.append(plugbmp_label)
battery_group.append(greenbmp_label)
battery_group.append(bluebmp_label)
battery_group.append(yellowbmp_label)
battery_group.append(orangebmp_label)
battery_group.append(redbmp_label)
battery_group.append(sprite_group)

# Main Group
main_group.append(wallpaper_group)
main_group.append(hello_label)
main_group.append(battery_group)
main_group.append(footer_rect_group)
main_group.append(water_button_group)
main_group.append(loading_group)
main_group.append(zone0bg)
main_group.append(zone1bg)
main_group.append(zone2bg)
main_group.append(zone0_rect)
main_group.append(zone1_rect)
main_group.append(zone2_rect)
main_group.append(zone0_label)
main_group.append(zone1_label)
main_group.append(zone2_label)


# Add Menu popup group
main_group.append(menu_button_group)
main_group.append(menu_popout_group)
main_group.append(menu_popout_group_items)
menu_popout_group.append(menu_roundrect)
menu_popout_group.append(menu_popout_label)
menu_popout_group_items.append(item1_button)
menu_popout_group_items.append(item2_button)
menu_popout_group_items.append(item3_button)
menu_button_group.append(menu_button)

display.root_group = main_group

def map_touch_to_display(raw_x, raw_y, x_min=TOUCH_X_MIN, x_max=TOUCH_X_MAX, y_min=TOUCH_Y_MIN, y_max=TOUCH_Y_MAX):
    mapped_x = DISPLAY_WIDTH * (raw_x - x_min) // (x_max - x_min)
    mapped_y = DISPLAY_HEIGHT * (raw_y - y_min) // (y_max - y_min)
    return mapped_x, mapped_y
    
def usb_battery_monitor(usb_sense):
    """ Set battery icon and voltage label """
    try:
        vbat_label.text = f"{battery_monitor.cell_voltage:.2f}v"
    except (ValueError, RuntimeError, OSError) as e:
        print("LC709203F Error: \n", e)

    # print("USB Sense: ", usb_sense)  # Boolean value
    if usb_sense:  # if on USB power show plug sprite icon
        vbat_label.color = TEXT_LIGHTBLUE
        sprite[0] = 5
    else:  # if on battery power only
        # Changes battery voltage color depending on charge level
        if vbat_label.text >= "4.23":
            vbat_label.color = TEXT_LIGHTBLUE
            sprite[0] = 5
        elif "4.10" <= vbat_label.text <= "4.22":
            vbat_label.color = TEXT_GREEN
            sprite[0] = 0
        elif "4.00" <= vbat_label.text <= "4.09":
            vbat_label.color = TEXT_TEAL
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

def show_loading_rect():
    # Function to display popup menu
    loading_label.text = "Loading..."
    loading_group.hidden = False

def hide_loading_rect():
    # Function to hide popup menu
    loading_group.hidden = True

def show_menu():
    # Function to display popup menu
    menu_popout_label.text = "Menu Popout"
    menu_popout_group.hidden = False
    menu_popout_group_items.hidden = False

def hide_menu():
    # Function to hide popup menu
    menu_popout_group.hidden = True
    menu_popout_group_items.hidden = True


def root_group_switch(PAGE_FROM, PAGE_TO):
    # Removal order is less important than append order
    hide_menu()
    PAGE_FROM.remove(wallpaper_group)
    PAGE_FROM.remove(hello_label)
    PAGE_FROM.remove(menu_button_group)
    PAGE_FROM.remove(menu_popout_group)
    PAGE_FROM.remove(menu_popout_group_items)
    PAGE_FROM.remove(water_button_group)
    PAGE_FROM.remove(battery_group)
    PAGE_FROM.remove(footer_rect_group)
    if PAGE_FROM == main_group:
        PAGE_FROM.remove(loading_group)
        PAGE_FROM.remove(zone0bg)
        PAGE_FROM.remove(zone1bg)
        PAGE_FROM.remove(zone2bg)
        PAGE_FROM.remove(zone0_rect)
        PAGE_FROM.remove(zone1_rect)
        PAGE_FROM.remove(zone2_rect)
        PAGE_FROM.remove(zone0_label)
        PAGE_FROM.remove(zone1_label)
        PAGE_FROM.remove(zone2_label)
    if PAGE_FROM == deviceinfo_group:
        PAGE_FROM.remove(text_group)
    if PAGE_FROM == wifi_credentials_group:
        PAGE_FROM.remove(rssi_data_label)
        PAGE_FROM.remove(rssi_data_label0)
        PAGE_FROM.remove(rssi_data_label1)
        PAGE_FROM.remove(rssi_data_label2)
        PAGE_FROM.remove(rssi_data_label3)
        PAGE_FROM.remove(rssi_data_label4)
        PAGE_FROM.remove(rssi_data_label5)
        PAGE_FROM.remove(rssi_data_label6)
        PAGE_FROM.remove(rssi_data_label7)
        PAGE_FROM.remove(rssi_data_label8)
        PAGE_FROM.remove(rssi_data_label9)

    # Append order is layer order top to bottom for each page.
    PAGE_TO.append(wallpaper_group)  # load wallpaper 1st regardless of page
    if PAGE_TO == main_group:
        PAGE_TO.append(loading_group)
        PAGE_TO.append(zone0bg)
        PAGE_TO.append(zone1bg)
        PAGE_TO.append(zone2bg)
        PAGE_TO.append(zone0_rect)
        PAGE_TO.append(zone1_rect)
        PAGE_TO.append(zone2_rect)
        PAGE_TO.append(zone0_label)
        PAGE_TO.append(zone1_label)
        PAGE_TO.append(zone2_label)
    if PAGE_TO == deviceinfo_group:
        PAGE_TO.append(text_group)
    if PAGE_TO == wifi_credentials_group:
        PAGE_TO.append(rssi_data_label)
        PAGE_TO.append(rssi_data_label0)
        PAGE_TO.append(rssi_data_label1)
        PAGE_TO.append(rssi_data_label2)
        PAGE_TO.append(rssi_data_label3)
        PAGE_TO.append(rssi_data_label4)
        PAGE_TO.append(rssi_data_label5)
        PAGE_TO.append(rssi_data_label6)
        PAGE_TO.append(rssi_data_label7)
        PAGE_TO.append(rssi_data_label8)
        PAGE_TO.append(rssi_data_label9)
    
    # Global layers applied to every page
    PAGE_TO.append(hello_label)
    PAGE_TO.append(battery_group)
    PAGE_TO.append(footer_rect_group)
    PAGE_TO.append(water_button_group)
    PAGE_TO.append(menu_button_group)
    PAGE_TO.append(menu_popout_group)
    PAGE_TO.append(menu_popout_group_items)
    display.root_group = PAGE_TO

def group_cleanup():
    # When touch moves outside of button
    item1_button.selected = False
    item2_button.selected = False
    item3_button.selected = False
    menu_button.selected = False


def menu_switching(current_group, item1_target, item2_target, item3_target,):
    """ Touchscreen Popout Menu for root_group_switch """
    touch_point = touch.raw_touch()
    if touch_point is not None:
        mapped_x, mapped_y = map_touch_to_display(touch_point[0], touch_point[1])
        mapped_touch_point = (mapped_x, mapped_y)
        
        if menu_button.contains(mapped_touch_point):
            if not menu_button.selected:
                menu_button.selected = True
                time.sleep(0.25)
                print("Menu Pressed")
                show_menu()
                group_cleanup()
        elif not menu_popout_group.hidden:
            if item1_button.contains(mapped_touch_point):
                if not item1_button.selected:
                    item1_button.selected = True
                    time.sleep(0.25)
                    print("Item 1 Pressed")
                    root_group_switch(current_group, item1_target)
            elif item2_button.contains(mapped_touch_point):
                if not item2_button.selected:
                    item2_button.selected = True
                    time.sleep(0.25)
                    print("Item 2 Pressed")
                    root_group_switch(current_group, item2_target)
            elif item3_button.contains(mapped_touch_point):
                if not item3_button.selected:
                    item3_button.selected = True
                    time.sleep(0.25)
                    print("Item 3 Pressed")
                    root_group_switch(current_group, item3_target)
            else:
                group_cleanup()
                hide_menu()
        else:
            group_cleanup()
            hide_menu()
hide_menu()  # sets default menu popout to hidden

last = time.monotonic()
while True:

    hello_label.text = "Circuit Python 9.0.5"
    # Connect to Wi-Fi
    print("\nConnecting to WiFi...")
    show_loading_rect()
    loading_label.text = "WiFi 4 Connecting..."
    while not wifi.radio.ipv4_address:
        try:
            wifi.radio.connect(ssid, password)
        except ConnectionError as e:
            print("❌ Connection Error:", e)
            print("Retrying in 10 seconds")
    print("✅ Wifi!")
    if rssi <= -100:
        wifi_label.color = TEXT_RED
    elif -99 <= rssi <= -75:
        wifi_label.color = TEXT_MAGENTA
    elif -74 <= rssi <= -55:
        wifi_label.color = TEXT_ORANGE
    elif -54 <= rssi <= -1:
        wifi_label.color = TEXT_GREEN
    else:
        wifi_label.color = TEXT_BLACK
    wifi_label.text = "\uf1eb"

    # First request for authorization
    while wifi.radio.ipv4_address:
        try:
            print(" | Attempting to GET Rachio Authorization")
            try:
                with requests.get(
                    url=RACHIO_SOURCE, headers=RACHIO_HEADER
                ) as rachio_response:
                    rachio_json = rachio_response.json()
            except ConnectionError as e:
                print("Connection Error:", e)
                print("Retrying in 10 seconds")
            print(" | ✅ Authorized")

            rachio_id = rachio_json["id"]
            if DEBUG:
                print(" |  | Person ID: ", rachio_id)
                print(" |  | This ID will be used for subsequent calls")
                print("\nFull API GET URL: ", RACHIO_SOURCE)
                print(rachio_json)

        except (ValueError, RuntimeError) as e:
            print(f"Failed to get data, retrying\n {e}")
            time.sleep(60)
            break

        # Second request to GET data
        try:
            print(" | Attempting to GET Rachio JSON")
            try:
                with requests.get(
                    url=RACHIO_PERSON_SOURCE+rachio_id, headers=RACHIO_HEADER
                ) as rachio_response:
                    rachio_json = rachio_response.json()
            except ConnectionError as e:
                print("Connection Error:", e)
                print("Retrying in 10 seconds")
            loading_label.text = "Polling API..."
            print(" | ✅ Rachio JSON")
            response_headers = rachio_response.headers
            if DEBUG:
                print(f"Response Headers: {response_headers}")
            call_limit = int(response_headers['x-ratelimit-limit'])
            calls_remaining = int(response_headers['x-ratelimit-remaining'])
            calls_made_today = call_limit - calls_remaining

            # This script makes 2 requests every iteration.
            print(f" |  | Headers:")
            print(f" |  |  | Date: {response_headers['date']}")
            print(f" |  |  | Maximum Daily Requests: {call_limit}")
            print(f" |  |  | Today's Requests: {calls_made_today}")
            print(f" |  |  | Remaining Requests: {calls_remaining}")
            print(f" |  |  | Limit Reset: {response_headers['x-ratelimit-reset']}")
            print(f" |  |  | Content Type: {response_headers['content-type']}")

            rachio_id = rachio_json["id"]
            rachio_id_ast = obfuscating_asterix(rachio_id, "append", 3)
            print(" |  | UserID: ", rachio_id_ast)

            rachio_username = rachio_json["username"]
            rachio_username_ast = obfuscating_asterix(rachio_username, "append", 3)
            print(" |  | Username: ", rachio_username_ast)

            rachio_name = rachio_json["fullName"]
            rachio_name_ast = obfuscating_asterix(rachio_name, "append", 3)
            print(" |  | Full Name: ", rachio_name_ast)

            rachio_deleted = rachio_json["deleted"]
            if not rachio_deleted:
                print(" |  | Account Status: Active")
            else:
                print(" |  | Account Status?: Deleted!")

            rachio_createdate = rachio_json["createDate"]
            rachio_timezone_offset = rachio_json["devices"][0]["utcOffset"]
            registration_date = _rachio_timestamp(rachio_createdate, rachio_timezone_offset)
            print(f" |  | Account Registered: {registration_date}")

            rachio_devices = rachio_json["devices"][0]["name"]
            print(" |  | Device: ", rachio_devices)

            rachio_model = rachio_json["devices"][0]["model"]
            print(" |  |  | Model: ", rachio_model)

            rachio_device_id = rachio_json["devices"][0]["id"]
            rachio_device_id_ast = obfuscating_asterix(rachio_device_id, "append")
            print(" |  |  | Device ID: ", rachio_device_id_ast)

            rachio_device_date = rachio_json["devices"][0]["createDate"]
            device_date = _rachio_timestamp(rachio_device_date, rachio_timezone_offset)
            print(f" |  |  | Activation Date: {device_date}")

            rachio_serial = rachio_json["devices"][0]["serialNumber"]
            rachio_serial_ast = obfuscating_asterix(rachio_serial, "append")
            print(" |  |  | Serial Number: ", rachio_serial_ast)

            rachio_mac = rachio_json["devices"][0]["macAddress"]
            rachio_mac_ast = obfuscating_asterix(rachio_mac, "append")
            print(" |  |  | MAC Address: ", rachio_mac_ast)

            rachio_status = rachio_json["devices"][0]["status"]
            print(" |  |  | Device Status: ", rachio_status)

            rachio_timezone = rachio_json["devices"][0]["timeZone"]
            print(" |  |  | Time Zone: ", rachio_timezone)

            # Latitude & Longtitude are used for smart watering & rain delays
            rachio_latitude = str(rachio_json["devices"][0]["latitude"])
            rachio_lat_ast = obfuscating_asterix(rachio_latitude, "all")
            print(" |  |  | Latitude: ", rachio_lat_ast)

            rachio_longitude = str(rachio_json["devices"][0]["longitude"])
            rachio_long_ast = obfuscating_asterix(rachio_longitude, "all")
            print(" |  |  | Longitude: ", rachio_long_ast)

            rachio_rainsensor = rachio_json["devices"][0]["rainSensorTripped"]
            print(" |  |  | Rain Sensor: ", rachio_rainsensor)

            rachio_zone0_enabled = rachio_json["devices"][0]["zones"][0]["enabled"]
            rachio_zone1_enabled = rachio_json["devices"][0]["zones"][1]["enabled"]
            rachio_zone2_enabled = rachio_json["devices"][0]["zones"][2]["enabled"]
            rachio_zone3_enabled = rachio_json["devices"][0]["zones"][3]["enabled"]

            if rachio_zone0_enabled:
                rachio_zone0 = rachio_json["devices"][0]["zones"][0]["name"]
                zone0 = (f" {rachio_zone0} |")
            else:
                zone0 = ""
            if rachio_zone1_enabled:
                rachio_zone1 = rachio_json["devices"][0]["zones"][1]["name"]
                zone1 = (f" {rachio_zone1} |")
            else:
                zone1 = ""
            if rachio_zone2_enabled:
                rachio_zone2 = rachio_json["devices"][0]["zones"][2]["name"]
                zone2 = (f" {rachio_zone2} |")
            else:
                zone2 = ""
            if rachio_zone3_enabled:
                rachio_zone3 = rachio_json["devices"][0]["zones"][3]["name"]
                zone3 = (f" {rachio_zone3} |")
            else:
                zone3 = ""

            zones = f"{zone0}{zone1}{zone2}{zone3}"
            print(f" |  |  | Zones: {zones}")

            if DEBUG:
                print(f"\nFull API GET URL: {RACHIO_PERSON_SOURCE+rachio_id}")
                print(rachio_json)

            print("\nFinished!")
            print(f"Board Uptime: {time_calc(time.monotonic())}")
            print(f"Next Update: {time_calc(SLEEP_TIME)}")
            print("===============================")
            loading_label.text = f"Next Update: {time_calc(SLEEP_TIME)}"
            time.sleep(0.5)
            loading_label.text = ""
            hide_loading_rect()

        except (ValueError, RuntimeError) as e:
            print(f"Failed to get data, retrying\n {e}")
            time.sleep(60)
            break

        # --------------------------------------------------------------------------
        if display.root_group is main_group:
            hello_label.text = "Circuit Python 9.0.5"
            zone0_label.text = "Zone 1"
            zone1_label.text = "Zone 2"
            zone2_label.text = "Zone 3"
            
            print("Entering Touch Loop")
            while (time.monotonic() - last) <= SLEEP_TIME and display.root_group is main_group:
                # Battery voltage label and icon
                usb_sense = supervisor.runtime.usb_connected
                usb_battery_monitor(usb_sense)

                touch_point = touch.raw_touch()
                if touch_point is not None:
                    raw_x, raw_y = touch_point
                    mapped_x, mapped_y = map_touch_to_display(raw_x, raw_y)
                    mapped_touch_point = (mapped_x, mapped_y)
                    if mapped_touch_point:
                        show_menu()
                        menu_switching(main_group, main_group, deviceinfo_group, wifi_credentials_group)
                        water_button.label_color = TEXT_BLACK
                        print("Group 0 Button Pressed")
                        print(f"P={mapped_x},{mapped_y}")
                        time.sleep(0.5)
                        water_button.label_color = TEXT_WHITE
                        group_cleanup()
                    else:
                        # Default state always running
                        group_cleanup()

            last = time.monotonic()
            print("Exited Sleep Loop")
            break

        # --------------------------------------------------------------------------
        if display.root_group is deviceinfo_group:
            hello_label.text = "Device Info"
            text_area.text = "Getting Device Data..."
            rachio_id = rachio_json["id"]
            rachio_id_ast = obfuscating_asterix(rachio_id, "append", 3)
            print(" |  | UserID: ", rachio_id_ast)

            rachio_username = rachio_json["username"]
            rachio_username_ast = obfuscating_asterix(rachio_username, "append", 3)
            print(" |  | Username: ", rachio_username_ast)

            rachio_name = rachio_json["fullName"]
            rachio_name_ast = obfuscating_asterix(rachio_name, "append", 3)
            print(" |  | Full Name: ", rachio_name_ast)

            rachio_deleted = rachio_json["deleted"]
            if not rachio_deleted:
                print(" |  | Account Status: Active")
            else:
                print(" |  | Account Status?: Deleted!")

            rachio_createdate = rachio_json["createDate"]
            rachio_timezone_offset = rachio_json["devices"][0]["utcOffset"]
            registration_date = _rachio_timestamp(rachio_createdate, rachio_timezone_offset)
            print(f" |  | Account Registered: {registration_date}")

            rachio_devices = rachio_json["devices"][0]["name"]
            print(" |  | Device: ", rachio_devices)

            rachio_model = rachio_json["devices"][0]["model"]
            print(" |  |  | Model: ", rachio_model)

            rachio_device_id = rachio_json["devices"][0]["id"]
            rachio_device_id_ast = obfuscating_asterix(rachio_device_id, "append")
            print(" |  |  | Device ID: ", rachio_device_id_ast)

            rachio_device_date = rachio_json["devices"][0]["createDate"]
            device_date = _rachio_timestamp(rachio_device_date, rachio_timezone_offset)
            print(f" |  |  | Activation Date: {device_date}")

            rachio_serial = rachio_json["devices"][0]["serialNumber"]
            rachio_serial_ast = obfuscating_asterix(rachio_serial, "append")
            print(" |  |  | Serial Number: ", rachio_serial_ast)

            rachio_mac = rachio_json["devices"][0]["macAddress"]
            rachio_mac_ast = obfuscating_asterix(rachio_mac, "append")
            print(" |  |  | MAC Address: ", rachio_mac_ast)

            rachio_status = rachio_json["devices"][0]["status"]
            print(" |  |  | Device Status: ", rachio_status)

            rachio_timezone = rachio_json["devices"][0]["timeZone"]
            print(" |  |  | Time Zone: ", rachio_timezone)

            # Latitude & Longtitude are used for smart watering & rain delays
            rachio_latitude = str(rachio_json["devices"][0]["latitude"])
            rachio_lat_ast = obfuscating_asterix(rachio_latitude, "all")
            print(" |  |  | Latitude: ", rachio_lat_ast)

            rachio_longitude = str(rachio_json["devices"][0]["longitude"])
            rachio_long_ast = obfuscating_asterix(rachio_longitude, "all")
            print(" |  |  | Longitude: ", rachio_long_ast)

            rachio_rainsensor = rachio_json["devices"][0]["rainSensorTripped"]
            print(" |  |  | Rain Sensor: ", rachio_rainsensor)

            rachio_zone0_enabled = rachio_json["devices"][0]["zones"][0]["enabled"]
            rachio_zone1_enabled = rachio_json["devices"][0]["zones"][1]["enabled"]
            rachio_zone2_enabled = rachio_json["devices"][0]["zones"][2]["enabled"]
            rachio_zone3_enabled = rachio_json["devices"][0]["zones"][3]["enabled"]

            if rachio_zone0_enabled:
                rachio_zone0 = rachio_json["devices"][0]["zones"][0]["name"]
                zone0 = (f" {rachio_zone0} |")
            else:
                zone0 = ""
            if rachio_zone1_enabled:
                rachio_zone1 = rachio_json["devices"][0]["zones"][1]["name"]
                zone1 = (f" {rachio_zone1} |")
            else:
                zone1 = ""
            if rachio_zone2_enabled:
                rachio_zone2 = rachio_json["devices"][0]["zones"][2]["name"]
                zone2 = (f" {rachio_zone2} |")
            else:
                zone2 = ""
            if rachio_zone3_enabled:
                rachio_zone3 = rachio_json["devices"][0]["zones"][3]["name"]
                zone3 = (f" {rachio_zone3} |")
            else:
                zone3 = ""

            zones = f"{zone0}{zone1}{zone2}{zone3}"
            print(f" |  |  | Zones: {zones}")

            text_area.text = (f"UserID: {rachio_id_ast}\n"
                              +f"Activation Date: {device_date}\n"
                              +f"Device: {rachio_devices}\n"
                              +f"  Model: {rachio_model}\n"
                              +f"  Serial #: {rachio_serial_ast}\n"
                              +f"  MAC: {rachio_mac_ast}\n"
                              +f"  Status: {rachio_status}\n"
                              +f"  Zones: {zones}\n"
                              )
                              
            print("Entering Touch Loop")
            while (time.monotonic() - last) <= SLEEP_TIME and display.root_group is deviceinfo_group:
                touch_point = touch.raw_touch()
                if touch_point is not None:
                    raw_x, raw_y = touch_point
                    mapped_x, mapped_y = map_touch_to_display(raw_x, raw_y)
                    mapped_touch_point = (mapped_x, mapped_y)
                    if mapped_touch_point:
                        menu_switching(deviceinfo_group, main_group, deviceinfo_group, wifi_credentials_group)
                        water_button.label_color = TEXT_BLACK
                        print("Group 1 Button Pressed")
                        print(f"P={mapped_x},{mapped_y}")
                        time.sleep(0.5)
                        water_button.label_color = TEXT_WHITE
                        group_cleanup()
                    else:
                        group_cleanup()
            last = time.monotonic()
            print("Exited Sleep Loop")
        # --------------------------------------------------------------------------
        if display.root_group is wifi_credentials_group:
            hello_label.text = "WiFi Credentials"
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
                print(f"ssid: {network.ssid} | rssi: {network.rssi} | "
                      + f"channel: {network.channel}")
            jsonNetworkList = json.dumps(NetworkList)
            json_list = json.loads(jsonNetworkList)
            # print(f"Items in RSSI List: {len(json_list)}")
            rssi_data_label.text = "SSID\t\t\t\t\t\t\t  RSSI\t\t\t\t    CHANNEL\n"

            if json_list[0][0]['ssid'] == ssid:
                rssi_data_label0.color = TEXT_GREEN
                rssi_data_label0.text = f"{json_list[0][0]['ssid']:<30}\t{json_list[0][0]['rssi']:<20}\t{json_list[0][0]['channel']:<20}\n"
            else:
                rssi_data_label0.color = TEXT_WHITE
                rssi_data_label0.text = f"{json_list[0][0]['ssid']:<30}\t{json_list[0][0]['rssi']:<20}\t{json_list[0][0]['channel']:<20}\n"
                
            if json_list[1][0]['ssid'] == ssid:
                rssi_data_label1.color = TEXT_GREEN
                rssi_data_label1.text = f"{json_list[1][0]['ssid']:<30}\t{json_list[1][0]['rssi']:<20}\t{json_list[1][0]['channel']:<20}\n"
            else:
                rssi_data_label1.color = TEXT_WHITE
                rssi_data_label1.text = f"{json_list[1][0]['ssid']:<30}\t{json_list[1][0]['rssi']:<20}\t{json_list[1][0]['channel']:<20}\n"
            
            if json_list[2][0]['ssid'] == ssid:
                rssi_data_label2.color = TEXT_GREEN
                rssi_data_label2.text = f"{json_list[2][0]['ssid']:<30}\t{json_list[2][0]['rssi']:<20}\t{json_list[2][0]['channel']:<20}\n"
            else:
                print(f"{json_list[2][0]['ssid']} and {ssid}")
                rssi_data_label2.color = TEXT_WHITE
                rssi_data_label2.text = f"{json_list[2][0]['ssid']:<30}\t{json_list[2][0]['rssi']:<20}\t{json_list[2][0]['channel']:<20}\n"
            
            try:
                for i in range(min(10, len(json_list))):
                    label_text = (f"{json_list[i][0]['ssid']:<30}\t"
                                  + f"{json_list[i][0]['rssi']:<20}\t"
                                  + f"{json_list[i][0]['channel']:<20}\n")
                    globals()[f"rssi_data_label{i}"].text = label_text
            except Exception as e:
                print(f"RSSI List Error: {e}")
                pass
                
            print("Entering Touch Loop")
            while (time.monotonic() - last) <= SLEEP_TIME and display.root_group is wifi_credentials_group:
                touch_point = touch.raw_touch()
                if touch_point is not None:
                    raw_x, raw_y = touch_point
                    mapped_x, mapped_y = map_touch_to_display(raw_x, raw_y)
                    mapped_touch_point = (mapped_x, mapped_y)
                    if mapped_touch_point:
                        menu_switching(wifi_credentials_group, main_group, deviceinfo_group, wifi_credentials_group)
                        water_button.label_color = TEXT_BLACK
                        print("Group 2 Button Pressed")
                        print(f"P={mapped_x},{mapped_y}")
                        time.sleep(0.5)
                        water_button.label_color = TEXT_WHITE
                        group_cleanup()
                    else:
                        group_cleanup()
            last = time.monotonic()
            print("Exited Sleep Loop")
            #time.sleep(SLEEP_TIME)
