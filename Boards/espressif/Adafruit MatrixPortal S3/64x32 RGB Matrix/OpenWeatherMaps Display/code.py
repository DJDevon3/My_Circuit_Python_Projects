# SPDX-FileCopyrightText: 2023 John Park & DJDevon3
#
# SPDX-License-Identifier: MIT
# Weather Matrix Display (updated for Matrix Portal S3)
# https://learn.adafruit.com/weather-display-matrix/code-the-weather-display-matrix 
# Circuit Python 8.2.9

import os
import time
import board
import displayio
import rgbmatrix
import framebufferio
import ssl
import wifi
import socketpool
import adafruit_requests
from adafruit_display_text.label import Label
from adafruit_bitmap_font import bitmap_font

# Initialize Web Sockets (This should always be near the top of a script!)
# There can be only one pool
pool = socketpool.SocketPool(wifi.radio)

displayio.release_displays()
DISPLAY_WIDTH = 64
DISPLAY_HEIGHT = 32
DISPLAY_ROTATION = 0
BIT_DEPTH = 4
AUTO_REFRESH = True

# Seconds between OpenWeatherMap polling
# 600 = 10 mins, 900 = 15 mins, 1800 = 30 mins, 3600 = 1 hour
sleep_time = 600
scroll_delay = 0.05  # Scroll Speed
Time_Format = "Civilian"  # Military or Civilian

# Use settings.toml for credentials
ssid = os.getenv("WIFI_SSID")
appw = os.getenv("WIFI_PASSWORD")
# Local time & weather from lat/lon
OWKEY = os.getenv("openweather_token")
OWLAT = os.getenv("openweather_lat")
OWLON = os.getenv("openweather_lon")
OWUNITS = os.getenv("openweather_units")

matrix = rgbmatrix.RGBMatrix(
    width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, bit_depth=BIT_DEPTH,
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
    doublebuffer=True)

# Associate the RGB matrix with a Display so we can use displayio
display = framebufferio.FramebufferDisplay(matrix, auto_refresh=AUTO_REFRESH, rotation=DISPLAY_ROTATION)

# OpenWeatherMap 2.5 Free API
DATA_SOURCE = "https://api.openweathermap.org/data/2.5/onecall?"
DATA_SOURCE += "lat=" + OWLAT
DATA_SOURCE += "&lon=" + OWLON
DATA_SOURCE += "&exclude=hourly,daily"
DATA_SOURCE += "&appid=" + OWKEY
DATA_SOURCE += "&units=" + OWUNITS

# Converts seconds to minutes/hours/days
# Attribution: Written by DJDevon3 & refined by Elpekenin
def time_calc(input_time):
    if input_time < 60:
        return f"{input_time:.0f} seconds"
    if input_time < 3600:
        return f"{input_time / 60:.0f} minutes"
    if input_time < 86400:
        return f"{input_time / 60 / 60:.0f} hours"
    return f"{input_time / 60 / 60 / 24:.1f} days"

def _format_date(datetime):
    return "{:02}/{:02}/{:02}".format(
        datetime.tm_year,
        datetime.tm_mon,
        datetime.tm_mday,
    )

def _format_mil_time(datetime):
    return "{:02}:{:02}".format(
        datetime.tm_hour,
        datetime.tm_min,
        # datetime.tm_sec,
    )
    
def _format_time(datetime):
    hour = datetime.tm_hour % 12
    if hour == 0:
        hour = 12
    am_pm = "AM"
    if datetime.tm_hour / 12 >= 1:
        am_pm = "PM"
    return "{:d}:{:02d} {}".format(hour, datetime.tm_min, am_pm)

tiny5_font = bitmap_font.load_font("/fonts/tiny3x5.bdf")
tiny6_font = bitmap_font.load_font("/fonts/4x6.bdf")
small_font = bitmap_font.load_font("/fonts/Arial-12.bdf")

TEMP_COLOR = 0xFFA800
MAIN_COLOR = 0x9000FF
DESCRIPTION_COLOR = 0x00D3FF
TIMESTAMP_COLOR = 0x9000FF
HUMIDITY_COLOR = 0x0000AA
WIND_COLOR = 0xCCCCCC

# Static Labels
temp_text = Label(tiny5_font)
temp_text.anchor_point = (1.0, 0.0)
temp_text.anchored_position = (DISPLAY_WIDTH, 6)
temp_text.color = TEMP_COLOR
pressure_text = Label(tiny6_font)
pressure_text.anchor_point = (1.0, 0.0)
pressure_text.anchored_position = (DISPLAY_WIDTH-20, 6)
pressure_text.color = TEMP_COLOR
time_text = Label(tiny6_font)
time_text.anchor_point = (1.0, 0.0)
time_text.anchored_position = (DISPLAY_WIDTH, 0)
time_text.color = TIMESTAMP_COLOR

# Scrolling Labels
description_text = Label(small_font)
description_text.color = DESCRIPTION_COLOR
humidity_text = Label(small_font)
humidity_text.color = HUMIDITY_COLOR
wind_text = Label(small_font)
wind_text.color = WIND_COLOR
gust_text = Label(small_font)
gust_text.color = WIND_COLOR

# Splash Loading Image
background = displayio.OnDiskBitmap("/icons/loading.bmp")
background_tile = displayio.TileGrid(
    background,
    pixel_shader=background.pixel_shader,
    width=1,
    height=1,
    tile_width=DISPLAY_WIDTH,
    tile_height=DISPLAY_HEIGHT,
)

# Weather Icon Spritesheet
icons = displayio.OnDiskBitmap("/icons/weather-icons.bmp")
icon_sprite = displayio.TileGrid(
    icons,
    pixel_shader=icons.pixel_shader,
    tile_width=16,
    tile_height=16,
)

# scrolling_texts is a list not a group
# Appends labels to scrolling list
scrolling_texts = []
scrolling_texts.append(description_text)
scrolling_texts.append(humidity_text)
scrolling_texts.append(wind_text)
scrolling_texts.append(gust_text)

# Splash Loading Image Group
splash = displayio.Group()
splash.append(background_tile)

# Create Main Display Groups
main_group = displayio.Group()
icon_group = displayio.Group()
text_group = displayio.Group()
scrolling_group = displayio.Group()

# Append labels to Groups
text_group.append(temp_text)
text_group.append(pressure_text)
text_group.append(time_text)
main_group.append(icon_group)
main_group.append(text_group)
main_group.append(scrolling_group)

def set_icon(icon_name):
    icon_map = ("01", "02", "03", "04", "09", "10", "11", "13", "50")
    if icon_group:
        icon_group.pop()
    if icon_name is not None:
        row = None
        for index, icon in enumerate(icon_map):
            if icon == icon_name[0:2]:
                row = index
                break
        column = 0
        if icon_name[2] == "n":
            column = 1
        if row is not None:
            icon_sprite[0] = (row * 2) + column
            icon_group.append(icon_sprite)

# adafruit_requests.Session should always be outside the loop
# otherwise you get Out of Socket errors.
requests = adafruit_requests.Session(pool, ssl.create_default_context())

current_label = None
display.root_group = splash
First_Run = True
last = time.monotonic()

while True:
    debug_OWM = False  # Set True for Serial Print Debugging
    print("Board Uptime: ", time_calc(time.monotonic()))
    print("| Connecting to WiFi...")

    while not wifi.radio.ipv4_address:
        try:
            wifi.radio.connect(ssid, appw)
        except ConnectionError as e:
            print("Connection Error:", e)
            print("Retrying in 10 seconds")
            time.sleep(10)
    print("| ✅ WiFi!")

    while wifi.radio.ipv4_address:
        try:
            print("| | Attempting to GET Weather!")
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
                        print(f"| | ❌ OpenWeatherMap Error:  {owm_response['message']}")
                        owm_request.close()
                except (KeyError) as e:
                    owm_response = owm_request.json()
                    print("| | Account within Request Limit", e)
                    print("| | ✅ Connected to OpenWeatherMap")

                    # Timezone & offset determined by lat/lon
                    get_timezone_offset = int(owm_response["timezone_offset"])
                    tz_offset_seconds = get_timezone_offset
                    if debug_OWM:
                        print(f"| | | Timezone Offset (in seconds): {get_timezone_offset}")
                    get_timestamp = int(owm_response["current"]["dt"] + int(tz_offset_seconds))
                    current_unix_time = time.localtime(get_timestamp)
                    current_struct_time = time.struct_time(current_unix_time)
                    current_date = "{}".format(_format_date(current_struct_time))
                    if Time_Format == "Military":
                        current_time = "{}".format(_format_mil_time(current_struct_time))
                    if Time_Format == "Civilian":
                        current_time = "{}".format(_format_time(current_struct_time))
                    
                    owm_icon = owm_response["current"]["weather"][0]["icon"]
                    owm_temp = owm_response["current"]["temp"]
                    owm_pressure = owm_response["current"]["pressure"]
                    owm_humidity = owm_response["current"]["humidity"]
                    owm_describe = owm_response["current"]["weather"][0]["description"]
                    owm_describe = owm_describe.upper()
                    owm_windspeed = owm_response["current"]["wind_speed"]
                    owm_winddirection = int(owm_response["current"]["wind_deg"])
                    
                    # Print to Serial Console
                    if debug_OWM:
                        print("| | | Temp:", owm_temp)
                        print("| | | Pressure:", owm_pressure)
                        print("| | | Humidity:", owm_humidity)
                        print("| | | Wind Speed:", owm_windspeed)
                        print("| | | Wind Direction:", owm_winddirection)
                        print("| | | Timestamp:", current_date + " " + current_time)
                    
                    # Static Labels on Matrix Display
                    set_icon(owm_icon)
                    temp_text.text = f"{owm_temp:.0f}°F"
                    time_text.text = f"{current_time}"
                    pressure_text.text = f"{owm_pressure}"
                    
                    # Scrolling Labels on Matrix Display
                    description_text.text = f"{owm_describe}"
                    humidity_text.text = f"HUMIDITY {owm_humidity}%"
                    wind_text.text = f"WIND {owm_windspeed} MPH"
                    
                    # Special since there might be no key:value returned
                    try:
                        owm_windgust = int(owm_response["current"]["wind_gust"])
                        gust_text.text = f"GUSTING {owm_windgust}"
                        if debug_OWM:
                            print("| | | Wind Gust:", owm_windgust)
                    except KeyError as e:
                        print("| | | No Gust Data", e)
                        pass
                    pass
                    
        except (ValueError, RuntimeError, OSError) as e:
            print("ValueError: Failed to get OWM data, retrying\n", e)
            break
        print("| | ✂️ Disconnected from OpenWeatherMap")
        print("Next Update: ", time_calc(sleep_time))
        
        if First_Run:
            First_Run = False
            # Switch from splash to main_group
            display.root_group = main_group
            splash.remove(background_tile)
            
        while (time.monotonic() - last) <= sleep_time:
            # Next Label Function
            if current_label is not None and scrolling_group:
                current_text = scrolling_texts[current_label]
                text_width = current_text.bounding_box[2]
                for i in range(text_width + 1):
                    scrolling_group.x = scrolling_group.x - 1
                    time.sleep(scroll_delay)

            if current_label is not None:
                current_label += 1
            if current_label is None or current_label >= len(scrolling_texts):
                current_label = 0
            # Setup the scrolling group by removing any existing
            if scrolling_group:
                scrolling_group.pop()
            # Then add the current label
            current_text = scrolling_texts[current_label]
            scrolling_group.append(current_text)
            text_width = current_text.bounding_box[2]
            scrolling_group.x = display.width
            scrolling_group.y = 23
            # print(f"Current Text: {current_text.text}")

            # Loop until label is offscreen again and leave function
            for i in range(display.width):
                scrolling_group.x = scrolling_group.x - 1
                time.sleep(scroll_delay)
                
            # By blocking other code we will never leave the label half way scrolled
        last = time.monotonic()
        break