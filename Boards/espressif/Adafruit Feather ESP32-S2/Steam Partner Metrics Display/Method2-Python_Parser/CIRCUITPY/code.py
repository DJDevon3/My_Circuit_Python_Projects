# SPDX-FileCopyrightText: 2023 DJDevon3
# SPDX-License-Identifier: MIT
# Coded for Circuit Python 8.0
# JSON_File_Parser

import os
import time
import board
import busio
import json
from adafruit_ht16k33 import segments

# Reads JSON file /JSON/Wishlists.json
# File is updated daily by accompanying Windows batch script
# Ensure batch script is pointing at USB drive letter for CIRCUITPY device

Wishlist_path = "/JSON/Wishlists.json"  # directory for JSON file just in case

# Initialize I2C 14-Segment Display
i2c = board.STEMMA_I2C()
blue = segments.Seg14x4(i2c, address=(0x71,0x72))
blue.brightness = 0.5

with open(Wishlist_path, 'r') as openfile:
    json_object = json.load(openfile)

print_all = True  # Show full JSON serial response (for debugging)
if print_all:
    print(json_object)

while True:
    # Show on blue alphanumeric display
    blue.fill(0)
    blue.marquee("ALL TIME ADDS", loop=False)  # Intentionally generic
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
