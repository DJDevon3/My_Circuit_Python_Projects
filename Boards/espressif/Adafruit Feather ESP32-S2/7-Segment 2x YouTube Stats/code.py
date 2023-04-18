# SPDX-FileCopyrightText: 2022 DJDevon3 for Adafruit Industries
# SPDX-License-Identifier: MIT
# Coded for Circuit Python 8.0.x
"""DJDevon3 Adafruit Feather ESP32-S2 YouTube Subscriber Counter"""
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
# Recommend running "CircuitPython I2C Device Address Scan" to get addresses
# https://learn.adafruit.com/adafruit-esp32-s2-feather/i2c-external-sensor
display = segments.Seg7x4(i2c, address=(0x71, 0x72))

# Time between weather updates
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
            
        # Both 7-segment displays ------------------------------------------------
        display.brightness = 0.8
        display.fill(0)
        
        # Show Views First
        display.print(YT_response_channel_viewCount)
        time.sleep(60)
        display.fill(0)
        
        # Static Display on both 7-segment displays
        display.print(YT_response_channel_subscriberCount)
        
        # Marquee scrolling, 2nd parameter speed in seconds
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
