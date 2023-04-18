# SPDX-FileCopyrightText: 2022 DJDevon3
# SPDX-License-Identifier: MIT
# Coded for Circuit Python 8.0
# DJDevon3 Steam_CSV_Wishlist_Parser
import os
import time
import board
import busio
import json
from adafruit_ht16k33 import segments
import adafruit_tca9548a

# Reads a specifically named CSV file /CSV/SteamWishlists_xxxxxx_all.csv
# File is updated daily by the batch script so it's always the same filename
# with updated data and moved to this device's CSV directory.

Wishlist_path = "/JSON/Wishlists.json"  # directory for CSV's just in case

# Initialize I2C 14-Segment Display
i2c = board.I2C()
display = segments.Seg14x4(board.I2C())
tca = adafruit_tca9548a.TCA9548A(i2c)
blue = segments.Seg14x4(tca[0], address=(0x71,0x72))
blue.brightness = 0.5

with open(Wishlist_path, 'r') as openfile:
    json_object = json.load(openfile)

print_all = True  # Show full JSON response (for debugging)
if print_all:
    print(json_object)

while True:
    # Show on blue 14-Segment Display
    blue.fill(0)
    blue.marquee("ALL TIME ADDS", loop=False)  # Intentionally generic demo
    time.sleep(3)

    blue.fill(0)
    blue.marquee("GAME0", loop=False)  # Intentionally generic demo
    time.sleep(1)
    blue.fill(0)
    blue.print(json_object['Game0'])
    time.sleep(3)

    blue.fill(0)
    blue.marquee("GAME1", loop=False)  # Intentionally generic demo
    time.sleep(1)
    blue.fill(0)
    blue.print(json_object['Game1'])
    time.sleep(3)

    blue.fill(0)
    blue.marquee("GAME2", loop=False)  # Intentionally generic demo
    time.sleep(1)
    blue.fill(0)
    blue.print(json_object['Game2'])
    time.sleep(3)

    blue.fill(0)
    blue.marquee("GAME3", loop=False)  # Intentionally generic demo
    time.sleep(1)
    blue.fill(0)
    blue.print(json_object['Game3'])
    time.sleep(3)

    blue.fill(0)
    blue.marquee("GAME4", loop=False)  # Intentionally generic demo
    time.sleep(1)
    blue.fill(0)
    blue.print(json_object['Game4'])
    time.sleep(3)

    blue.fill(0)
    blue.marquee("GAME5", loop=False)  # Intentionally generic demo
    time.sleep(1)
    blue.fill(0)
    blue.print(json_object['Game5'])
    time.sleep(3)

    blue.fill(0)
    blue.marquee("GAME6", loop=False)  # Intentionally generic demo
    time.sleep(1)
    blue.fill(0)
    blue.print(json_object['Game6'])
    time.sleep(3)

    blue.fill(0)
    blue.marquee("GAME7", loop=False)  # Intentionally generic demo
    time.sleep(1)
    blue.fill(0)
    blue.print(json_object['Game7'])
    time.sleep(3)

    blue.fill(0)
    blue.marquee("GAME8", loop=False)  # Intentionally generic demo
    time.sleep(1)
    blue.fill(0)
    blue.print(json_object['Game8'])
    time.sleep(3)

    blue.fill(0)
    blue.marquee("GAME9", loop=False)  # Intentionally generic demo
    time.sleep(1)
    blue.fill(0)
    blue.print(json_object['Game9'])
    time.sleep(3)
