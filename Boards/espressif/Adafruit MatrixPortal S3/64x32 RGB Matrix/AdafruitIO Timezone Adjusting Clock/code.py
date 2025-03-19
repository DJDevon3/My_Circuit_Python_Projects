# SPDX-FileCopyrightText: 2025 DJDevon3
# SPDX-License-Identifier: MIT
# Coded for Circuit Python 9.2.3
"""Matrix Portal S3 AdafruitIO Automatic Timezone Adjusting Clock"""

import os
import time
import board
import microcontroller
import displayio
import terminalio
import rgbmatrix
import framebufferio
import wifi
import adafruit_connection_manager
import adafruit_requests
import rtc
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
displayio.release_displays()

# Initalize Wifi, Socket Pool, Request Session
pool = adafruit_connection_manager.get_radio_socketpool(wifi.radio)
ssl_context = adafruit_connection_manager.get_radio_ssl_context(wifi.radio)
requests = adafruit_requests.Session(pool, ssl_context)

# Use settings.toml for credentials
ssid = os.getenv("CIRCUITPY_WIFI_SSID")
password = os.getenv("CIRCUITPY_WIFI_PASSWORD")
# AdafruitIO Credentials Required 
AIO_USERNAME = os.getenv("AIO_USERNAME")
AIO_KEY = os.getenv("AIO_KEY")
# Settings.toml format TIMEZONE = "America/New_York" 
TIMEZONE = os.getenv("TIMEZONE")

DISPLAY_WIDTH = 64
DISPLAY_HEIGHT = 32
DISPLAY_ROTATION = 0
BIT_DEPTH = 4
AUTO_REFRESH = True
DEBUG_TIME = False  # For manually testing times
Time_Format = "24"  # 12 hour (AM/PM) or 24 hour (military) clock


# Instantiate 64x32 Matrix Panel
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

# Associate RGB matrix as a Display so we can use displayio
display = framebufferio.FramebufferDisplay(
        matrix, auto_refresh=AUTO_REFRESH,
        rotation=DISPLAY_ROTATION
)

def time_calc(input_time):
    """Converts seconds to minutes/hours/days"""
    if input_time < 60:
        return f"{input_time:.0f} seconds"
    if input_time < 3600:
        return f"{input_time / 60:.0f} minutes"
    if input_time < 86400:
        return f"{input_time / 60 / 60:.1f} hours"
    return f"{input_time / 60 / 60 / 24:.2f} days"

# Custom timestamp functions use struct time format
# You can easily change them to your preferred format
# https://docs.circuitpython.org/en/latest/shared-bindings/time/index.html#time.struct_time
def _format_datetime(datetime):
    """ F-String formatted struct time conversion"""
    return (f"{datetime.tm_mon:02}/" +
            f"{datetime.tm_mday:02}/" +
            f"{datetime.tm_year:02} " +
            f"{datetime.tm_hour:02}:" +
            f"{datetime.tm_min:02}:" +
            f"{datetime.tm_sec:02}")

def _format_min(datetime):
    """ Get the current minute"""
    return (f"{datetime.tm_min:02}")

def _format_sec(datetime):
    """ Get the current second"""
    return (f"{datetime.tm_sec:02}")

def _format_time(datetime, format="12"):
    """ Time is 12 hour or 24 hour format"""
    if format == "12":
        hour = datetime.tm_hour % 12
        min = datetime.tm_min
        if hour == 0:
            hour = 12
        am_pm = "AM"
        if datetime.tm_hour / 12 >= 1:
            am_pm = "PM"
        if DEBUG_TIME:
            # Set debug to True & change these to test different times
            debug_hour = "09"
            debug_min = "09"
            return (f"{debug_hour:01}:{debug_min:02} {am_pm}")
        else:
            return (f"{hour:01}:{min:02} {am_pm}")
    if format == "24":
        return (f"{datetime.tm_hour:02}:{datetime.tm_min:02}:{datetime.tm_sec:02}")


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
TEXT_TEAL = 0xB2D8D8
TEXT_WHITE = 0xFFFFFF
TEXT_YELLOW = 0xFFFF00

# To use custom font uncomment below and change terminalio.FONT
# font_IBMPlex = bitmap_font.load_font("/fonts/IBMPlexMono-Medium-24_jep.bdf")

clock_label = label.Label(terminalio.FONT)
clock_label.anchor_point = (0.5, 0.5)
clock_label.anchored_position = (DISPLAY_WIDTH / 2, DISPLAY_HEIGHT / 2)
clock_label.scale = 1
clock_label.color = TEXT_RED

# Groups Setup
main_group = displayio.Group()
main_group.append(clock_label)
display.root_group = main_group

TIME_URL = f"https://io.adafruit.com/api/v2/{AIO_USERNAME}"
TIME_URL += f"/integrations/time/struct?x-aio-key={AIO_KEY}"
TIME_URL += f"&tz={TIMEZONE}"
# print(f"Debug Time Url: {TIME_URL}")
# Connect to Wi-Fi
print("\nConnecting to WiFi...")
while not wifi.radio.connected:
    try:
        wifi.radio.connect(ssid, password)
    except ConnectionError as e:
        print("❌ Connection Error:", e)
print("✅ Wifi!")
try:
    with requests.get(url=TIME_URL) as time_response:
        print(" | ✅ Connected to AdafruitIO!")
        json_time = time_response.json()
        year = json_time["year"]
        mon = json_time["mon"]
        mday = json_time["mday"]
        hour = json_time["hour"]
        min = json_time["min"]
        sec = json_time["sec"]
        wday = json_time["wday"]
        yday = json_time["yday"]
        isdst = json_time["isdst"]
        aio_time_struct = time.struct_time((year, mon, mday, hour, min, sec, wday, yday, isdst))
        aio_unix_timestamp = time.mktime(aio_time_struct)
        if DEBUG_TIME:
            print(f" | AdafruitIO Time: {mon}/{mday}/{year} {hour}:{min}:{sec}")
            print(f" | Adafruit time.struct: {aio_time_struct}")
            print(f" | Adafruit Unix Timestamp: {aio_unix_timestamp}")
except ConnectionError as e:
    print(f"Connection Error: {e}")

now = time.localtime()
current_datestamp = "{}".format(_format_datetime(now))
board_uptime = time.monotonic()

try:
    rtc.RTC().datetime = aio_time_struct
    print(f" | ✅ Initial Synchronize: {current_datestamp}")
    print("Board Uptime: ", time_calc(board_uptime))
    time.sleep(1)
except OSError as e:
    print(f"RTC or NTP Error: {e}")

print("===============================")
while True:
    now = time.localtime()
    if DEBUG_TIME:
        print(f"Now: {now}")
        time.sleep(0.5)
    board_uptime = time.monotonic()
    current_datestamp = "{}".format(_format_datetime(now))
    current_time = "{}".format(_format_time(now, format=Time_Format))
    current_min = "{}".format(_format_min(now))
    current_sec = "{}".format(_format_sec(now))
    clock_label.text = f"{current_time}"
    if DEBUG_TIME:
        print(f"Monotonic: {time.monotonic()}")
        print(f"Current Time: {current_time}")
        print(f"Current Min:Sec: {current_min}:{current_sec}")
        print("Board Uptime: ", time_calc(board_uptime))
        time.sleep(60)
        print("===============================")

    if board_uptime > 86400:
        print("24 Hour Uptime Restart")
        microcontroller.reset()

    # Synchronize RTC every 1 hour on the hour
    if current_min == "00" and current_sec == "00":
        try:
            with requests.get(url=TIME_URL) as time_response:
                print(" | ✅ Connected to AdafruitIO!")
                json_time = time_response.json()
                year = json_time["year"]
                mon = json_time["mon"]
                mday = json_time["mday"]
                hour = json_time["hour"]
                min = json_time["min"]
                sec = json_time["sec"]
                wday = json_time["wday"]
                yday = json_time["yday"]
                isdst = json_time["isdst"]
                aio_time_struct = time.struct_time((year, mon, mday, hour, min, sec, wday, yday, isdst))
                aio_unix_timestamp = time.mktime(aio_time_struct)
                if DEBUG_TIME:
                    print(f" | AdafruitIO Time: {mon}/{mday}/{year} {hour}:{min}:{sec}")
                    print(f" | Adafruit time.struct: {aio_time_struct}")
                    print(f" | Adafruit Unix Timestamp: {aio_unix_timestamp}")
                rtc.RTC().datetime = aio_time_struct
                print(f" | ✅ Synchronized Time: {current_datestamp}")
                print(f"Board Uptime: {board_uptime}")
                time.sleep(1)
        except ConnectionError as e:
            print(f"Connection Error: {e}")
            time.sleep(60)
        except OSError as e:
            print(f"RTC or NTP Error: {e}")
            time.sleep(60)
