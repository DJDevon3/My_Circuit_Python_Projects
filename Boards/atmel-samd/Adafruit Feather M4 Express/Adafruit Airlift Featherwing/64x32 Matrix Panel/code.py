# SPDX-FileCopyrightText: 2023 John Park & DJDevon3
#
# SPDX-License-Identifier: MIT
# OpenWeatherMap Single Matrix Panel Display
# For 64 x 32 RGB LED Matrix display
"""
Queries OpenWeatherMap.org API
Returns weather & time using lat/lon
"""
import gc
import time
import board
import busio
import displayio
import rgbmatrix
import framebufferio
from digitalio import DigitalInOut
import adafruit_requests as requests
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font

displayio.release_displays()
DISPLAY_WIDTH = 64
DISPLAY_HEIGHT = 32

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

SSID = secrets["ssid"]
APPW = secrets["password"]
OWLAT = secrets["openweather_lat"]
OWLON = secrets["openweather_lon"]
OWKEY = secrets["openweather_token"]
OWUNITS = secrets["openweather_units"]

# Seconds between OpenWeatherMap polling
# 600 = 10 mins, 900 = 15 mins, 1800 = 30 mins, 3600 = 1 hour
sleep_time = 600
# Scroll speed
scroll_delay = 0.03
Time_Format = "Civilian" # Military or Civilian

# AirLift Featherwing:
esp32_cs = DigitalInOut(board.D13)
esp32_ready = DigitalInOut(board.D11)
esp32_reset = DigitalInOut(board.D12)
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
requests.set_socket(socket, esp)

# If using an M4 Matrix Portal
# from adafruit_matrixportal.matrix import Matrix
# matrix = Matrix()

# Custom Wired to Feather M4 Express
matrix = rgbmatrix.RGBMatrix(
    width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, bit_depth=6,
    rgb_pins=[board.D6, board.D5, board.D9, board.D4, board.D10, board.SCL],
    addr_pins=[board.A5, board.A4, board.A3, board.A2],
    clock_pin=board.A1,
    latch_pin=board.RX,
    output_enable_pin=board.TX,
    doublebuffer=True)

# Associate RGB matrix with a Display to use displayio
display = framebufferio.FramebufferDisplay(matrix, auto_refresh=True)

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
    return "{:d}:{:02d} {}".format(hour, datetime.tm_min, am_pm
    )


small_font = bitmap_font.load_font("/fonts/Arial-12.bdf")
medium_font = bitmap_font.load_font("/fonts/Arial-14.bdf")

TEMP_COLOR = 0xFFA800
MAIN_COLOR = 0x9000FF
DESCRIPTION_COLOR = 0x00D3FF
TIMESTAMP_COLOR = 0x9000FF
HUMIDITY_COLOR = 0x0000AA
WIND_COLOR = 0xCCCCCC

# Labels
temp_text = label.Label(small_font)
temp_text.anchor_point = (1.0, 0.0)
temp_text.anchored_position = (DISPLAY_WIDTH, 0)
temp_text.color = TEMP_COLOR
description_text = label.Label(small_font)
description_text.color = DESCRIPTION_COLOR
timestamp_text = label.Label(small_font)
timestamp_text.color = TIMESTAMP_COLOR
humidity_text = label.Label(small_font)
humidity_text.color = HUMIDITY_COLOR
wind_text = label.Label(small_font)
wind_text.color = WIND_COLOR
gust_text = label.Label(small_font)
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
scrolling_texts.append(timestamp_text)
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
main_group.append(icon_group)
main_group.append(text_group)
main_group.append(scrolling_group)

def set_icon(icon_name):
    icon_map = ("01", "02", "03", "04", "09", "10", "11", "13", "50")
    if icon_group:
        icon_group.pop()
        gc.collect()
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

current_label = None
display.root_group = splash
First_Run = True
last = time.monotonic()

while True:
    debug_OWM = False  # Set True for Serial Print Debugging
    print("Board Uptime: ", time_calc(time.monotonic()))
    print("| Connecting to WiFi...")
    while not esp.is_connected:
        try:
            esp.connect(secrets)
        except RuntimeError as e:
            print("could not connect to AP, retrying: ", e)
            continue
    while esp.is_connected:
        print("| ✅ WiFi!")
        try:
            print("| | Attempting to GET Weather!")
            if debug_OWM:
                print("Full API GET URL: ", DATA_SOURCE)
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
                    get_timezone_offset = int(owm_response["timezone_offset"])  # 1
                    tz_offset_seconds = get_timezone_offset
                    if debug_OWM:
                        print(f"| | | Timezone Offset (in seconds): {get_timezone_offset}")
                    get_timestamp = int(owm_response["current"]["dt"] + int(tz_offset_seconds))  # 2
                    current_unix_time = time.localtime(get_timestamp)
                    current_struct_time = time.struct_time(current_unix_time)
                    current_date = "{}".format(_format_date(current_struct_time))
                    if Time_Format is "Military":
                        current_time = "{}".format(_format_mil_time(current_struct_time))
                    if Time_Format is "Civilian":
                        current_time = "{}".format(_format_time(current_struct_time))
                    
                    owm_icon = owm_response["current"]["weather"][0]["icon"]
                    owm_temp = owm_response["current"]["temp"]
                    owm_pressure = owm_response["current"]["pressure"]
                    owm_humidity = owm_response["current"]["humidity"]
                    owm_describe = owm_response["current"]["weather"][0]["description"]
                    owm_describe = owm_describe[0].upper() + owm_describe[1:]
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
                    
                    # Scrolling Labels on Matrix Display
                    timestamp_text.text = f"UPDATED {current_time}"
                    description_text.text = f"{owm_describe}"
                    humidity_text.text = f"HUMIDITY {owm_humidity}%"
                    wind_text.text = f"WIND SPEED {owm_windspeed} MPH"
                    
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
            gc.collect()
            
        while (time.monotonic() - last) <= sleep_time:
            # Next Label Function
            if current_label is not None and scrolling_group:
                current_text = scrolling_texts[current_label]
                text_width = current_text.bounding_box[2]
                for _ in range(text_width + 1):
                    scrolling_group.x = scrolling_group.x - 1
                    time.sleep(scroll_delay)

            if current_label is not None:
                current_label += 1
            if current_label is None or current_label >= len(
                    scrolling_texts
            ):
                current_label = 0
            # Setup the scrolling group by removing any existing
            if scrolling_group:
                scrolling_group.pop()
                gc.collect()
            # Then add the current label
            current_text = scrolling_texts[current_label]
            scrolling_group.append(current_text)
            scrolling_group.x = display.width
            scrolling_group.y = 23

            # Loop until label is offscreen again and leave function
            for _ in range(display.width):
                scrolling_group.x = scrolling_group.x - 1
                time.sleep(scroll_delay)
            # By blocking other code we will never leave the label half way scrolled
        last = time.monotonic
        break