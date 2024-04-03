# SPDX-FileCopyrightText: 2024 DJDevon3
# SPDX-License-Identifier: MIT
# Coded for Circuit Python 9.x
"""Queue-Times.com API w/Display Example"""

import os
import time

import adafruit_connection_manager
import wifi

import adafruit_requests
import displayio
import terminalio
import board
from adafruit_display_text import label, wrap_text_to_pixels
from circuitpython_st7796s import ST7796S

# Initalize Wifi, Socket Pool, Request Session
pool = adafruit_connection_manager.get_radio_socketpool(wifi.radio)
ssl_context = adafruit_connection_manager.get_radio_ssl_context(wifi.radio)
requests = adafruit_requests.Session(pool, ssl_context)

# Time between API refreshes
# 900 = 15 mins, 1800 = 30 mins, 3600 = 1 hour
SLEEP_TIME = 300

# Get WiFi details, ensure these are setup in settings.toml
ssid = os.getenv("CIRCUITPY_WIFI_SSID")
password = os.getenv("CIRCUITPY_WIFI_PASSWORD")

spi = board.SPI()
tft_cs = board.D9
tft_dc = board.D10
tft_rst = board.D17

# 4.0" ST7796S Display
DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 320

displayio.release_displays()
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_rst)
display = ST7796S(display_bus, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, rotation=180)

# Source URL of the JSON data
QTIMES_SOURCE = "https://queue-times.com/parks/16/queue_times.json"

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

font = terminalio.FONT

# Label Customizations
land_text = label.Label(font)
land_text.anchor_point = (0.0, 0.0)
land_text.anchored_position = (2, 0)  # X,Y coordinates
land_text.scale = 1
land_text.color = TEXT_LIGHTBLUE

ride_text = label.Label(font)
ride_text.anchor_point = (0.0, 0.0)
ride_text.anchored_position = (2, 16)
ride_text.scale = 1
ride_text.color = TEXT_WHITE

# Create Display Groups
text_group = displayio.Group()
text_group.append(land_text)
text_group.append(ride_text)
display.root_group = text_group


def time_calc(input_time):
    """Converts seconds to minutes/hours/days"""
    if input_time < 60:
        return f"{input_time:.0f} seconds"
    if input_time < 3600:
        return f"{input_time / 60:.0f} minutes"
    if input_time < 86400:
        return f"{input_time / 60 / 60:.0f} hours"
    return f"{input_time / 60 / 60 / 24:.1f} days"


def dontpanic(panic):
    ride_text.text = "\n".join(
        wrap_text_to_pixels(panic, DISPLAY_WIDTH - 2, font)
    )

qtimes_json = {}
while True:
    now = time.monotonic()
    # Connect to Wi-Fi
    print("\n===============================")
    print("Connecting to WiFi...")
    while not wifi.radio.ipv4_address:
        try:
            wifi.radio.connect(ssid, password)
        except ConnectionError as e:
            print("❌ Connection Error:", e)
            print("Retrying in 10 seconds")
    print("✅ WiFi!")

    try:
        print(" | Attempting to GET Queue-Times JSON!")
        try:
            qtimes_response = requests.get(url=QTIMES_SOURCE)
            qtimes_json = qtimes_response.json()
        except ConnectionError as e:
            print("Connection Error:", e)
            print("Retrying in 10 seconds")
        print(" | ✅ Queue-Times JSON!")
        
        DEBUG_QTIMES = False
        if DEBUG_QTIMES:
            print("Full API GET URL: ", QTIMES_SOURCE)
            print(qtimes_json)
        qtimes_response.close()
        print("✂️ Disconnected from Queue-Times API")

        print("\nFinished!")
        print(f"Board Uptime: {time_calc(time.monotonic())}")
        print(f"Next Update: {time_calc(SLEEP_TIME)}")
        print("===============================")
    except (ValueError, RuntimeError) as e:
        print("Failed to get data, retrying\n", e)
        time.sleep(60)
        break
        
    # Loop infinitely and get updates after the list finishes displaying
    if time.monotonic() - now <= SLEEP_TIME:
        for land in qtimes_json["lands"]:
            qtimes_lands = str(land["name"])
            print(f" |  | Lands: {qtimes_lands}")
            land_text.text = f"Land: {qtimes_lands}"
            time.sleep(3)
            
            # Loop through each ride in the land
            for ride in land["rides"]:
                qtimes_rides = str(ride["name"])
                qtimes_queuetime = str(ride["wait_time"])
                qtimes_isopen = str(ride["is_open"])
                
                print(f" |  | Rides: {qtimes_rides}")
                print(f" |  | Queue Time: {qtimes_queuetime} Minutes")
                if qtimes_isopen == "False":
                    print(" |  | Status: Closed")
                    dontpanic(f"{qtimes_rides}\n{qtimes_queuetime} Minutes (Closed)")
                elif qtimes_isopen == "True":
                    print(" |  | Status: Open")
                    dontpanic(f"{qtimes_rides}\n{qtimes_queuetime} Minutes (Open)")
                else:
                    print(" |  | Status: Unknown")
                    dontpanic(f"{qtimes_rides}\n{qtimes_queuetime} Minutes (Unknown)")
                    
                time.sleep(5)
    else:
        break