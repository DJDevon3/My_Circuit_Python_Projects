# SPDX-FileCopyrightText: 2022 DJDevon3 for Adafruit Industries
# SPDX-License-Identifier: MIT
"""DJDevon3 Adafruit Feather ESP32-S2 YouTube Subscriber & View Counter"""
import gc
import time
import board
import terminalio
import digitalio
import busio
import ssl
import wifi
import json
import socketpool
import adafruit_requests
from adafruit_ht16k33 import segments

# Initialize WiFi Pool (This should always be near the top of a script!)
# anecdata: you only want to do this once early in your code pool.
# Highlander voice: "There can be only one pool"
pool = socketpool.SocketPool(wifi.radio)

#Initialize 7-Segment Backpack
i2c = busio.I2C(board.SCL, board.SDA)
display = segments.Seg7x4(i2c, address=(0x71, 0x72))
display.brightness = 0.5
display.fill(0)

# Time between GET requests
# 900 = 15 mins, 1800 = 30 mins, 3600 = 1 hour
sleep_time = 900

try:
    from secrets import secrets
except ImportError:
    print("Secrets File Import Error")
    raise

if sleep_time < 60:
    sleep_time_conversion = "seconds"
    sleep_int = sleep_time
elif 60 <= sleep_time < 3600:
    sleep_int = sleep_time / 60
    sleep_time_conversion = "minutes"
elif 3600 <= sleep_time < 86400:
    sleep_int = sleep_time / 60 / 60
    sleep_time_conversion = "hours"
else:
    sleep_int = sleep_time / 60 / 60 / 24
    sleep_time_conversion = "days"

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

# https://youtube.googleapis.com/youtube/v3/channels?part=statistics&forUsername=[YOUR_USERNAME]&key=[YOUR_API_KEY]
DATA_SOURCE = (
    "https://youtube.googleapis.com/youtube/v3/channels?"
    + "part=statistics"
    + "&forUsername="
    + secrets["YT_username"]
    + "&key="
    + secrets["YT_token"]
)

# Connect to Wi-Fi
print("\n===============================")
print("Connecting to WiFi...")
requests = adafruit_requests.Session(pool, ssl.create_default_context())
while not wifi.radio.ipv4_address:
    try:
        wifi.radio.enabled = False
        wifi.radio.enabled = True
        wifi.radio.connect(secrets['ssid'], secrets['password'])
    except ConnectionError as e:
        print("Connection Error:", e)
        print("Retrying in 10 seconds")
    time.sleep(10)
    gc.collect()
print("Connected!\n")

while True:
    try:
        print("Attempting to GET YouTube Stats!")
        # Uncomment line below to print API URL with all data filled in
        # print("Full API GET URL: ", DATA_SOURCE)
        print("===============================")
        response = requests.get(DATA_SOURCE).json()

         # Print Full JSON to Serial
        full_json_response = False # Change to true to see full response
        if full_json_response:
            dump_object = json.dumps(response)
            print("JSON Dump: ", dump_object)

        # Print Debugging to Serial
        debug = True # Change to true to see more response data
        if debug:
            print("Matching Results: ", response['pageInfo']['totalResults'])

            YT_response_channel_kind = response['kind']
            print("Response Kind: ", YT_response_channel_kind)

            YT_response_channel_kind = response['items'][0]['kind']
            print("Request Kind: ", YT_response_channel_kind)

            YT_response_channel_id = response['items'][0]['id']
            print("Channel ID: ", YT_response_channel_id)


            YT_response_channel_videoCount = response['items'][0]['statistics']['videoCount']
            print("Videos: ", YT_response_channel_videoCount)

            YT_response_channel_viewCount = response['items'][0]['statistics']['viewCount']
            print("Views: ", YT_response_channel_viewCount)

        YT_response_channel_subscriberCount = response['items'][0]['statistics']['subscriberCount']
        if debug:
            print("Subscribers: ", YT_response_channel_subscriberCount)

        # Static Display Subscribers on both 7-segment displays
        display.fill(0)
        display.print(YT_response_channel_subscriberCount)

        # Marquee scrolling instead, 2nd parameter is speed in seconds
        # display.fill(0)
        # display.marquee(YT_response_channel_subscriberCount, 0.9)

        print("Success!")
        print("Next Update in %s %s" % (int(sleep_int), sleep_time_conversion))
        print("===============================")

        gc.collect()

    except (ValueError, RuntimeError) as e:
        print("Failed to get data, retrying\n", e)
        time.sleep(60)
        continue
    response = None
    time.sleep(sleep_time)
