# SPDX-FileCopyrightText: 2025 DJDevon3
# SPDX-License-Identifier: MIT
# Coded for Circuit Python 9.2.3
"""Matrix Portal S3 NTP Clock"""

import os
import time
import board
import microcontroller
import displayio
import terminalio
import rgbmatrix
import framebufferio
import wifi
import socketpool
import adafruit_connection_manager
import adafruit_requests
import rtc
import adafruit_ntp
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
displayio.release_displays()

# Initalize Wifi, Socket Pool, Request Session
pool = adafruit_connection_manager.get_radio_socketpool(wifi.radio)
requests = adafruit_requests.Session(pool)

# Use settings.toml for credentials
ssid = os.getenv("CIRCUITPY_WIFI_SSID")
password = os.getenv("CIRCUITPY_WIFI_PASSWORD")
TZ_OFFSET = -5  # time zone offset in hours from UTC
Time_Format = "24"  # 12 hour (AM/PM) or 24 hour (military) clock

# Time in seconds between updates (polling)
# 600 = 10 mins, 900 = 15 mins, 1800 = 30 mins, 3600 = 1 hour
SLEEP_TIME = 900

DISPLAY_WIDTH = 64
DISPLAY_HEIGHT = 32
DISPLAY_ROTATION = 0
BIT_DEPTH = 4
AUTO_REFRESH = True
DEBUG_TIME = False  # For manually testing times

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

# Publicly Open NTP Time Server
# No AdafruitIO credentials required
ntp = adafruit_ntp.NTP(pool, tz_offset=TZ_OFFSET)

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
    """ Get the current minute"""
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

print("===============================")
while True:
    now = time.localtime()
    if DEBUG_TIME:
        print(f"Now: {now}")
    board_uptime = time.monotonic()

    current_time = "{}".format(_format_time(now, format=Time_Format))
    current_min = "{}".format(_format_min(now))
    current_sec = "{}".format(_format_sec(now))
    clock_label.text = f"{current_time}"
    
    print(f"Monotonic: {time.monotonic()}")
    print(f"Current Time: {current_time}")
    print("Board Uptime: ", time_calc(board_uptime))
    print("Next Update:", time_calc(SLEEP_TIME))
    print("Finished!")
    time.sleep(0.5)
    print("===============================")
            
    if board_uptime > 86400:
        print("24 Hour Uptime Restart")
        microcontroller.reset()
        
    # Synchronize RTC from NTP every 1 hour on the hour
    print(f"Current Minute: {current_min}:{current_sec}")
    if current_min is "00" and current_sec is "00":
        time.sleep(0.5)
        try:
            rtc.RTC().datetime = ntp.datetime
            print("------------------------------ Synchronized Time")
        except OSError as e:
            print(f"RTC or NTP Error: {e}")
            time.sleep(60)
            continue
