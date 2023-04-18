# SPDX-FileCopyrightText: 2022 DJDevon3
# SPDX-License-Identifier: MIT
# Coded for Circuit Python 8.0
# DJDevon3 Steam_CSV_Wishlist_Parser
import os
import time
import board
import busio
import circuitpython_csv as csv
from adafruit_ht16k33 import segments
import adafruit_tca9548a

# Reads a specifically named CSV file /CSV/SteamWishlists_xxxxxx_all.csv
# File is updated daily by the batch script so it's always the same filename
# with updated data and moved to this device's CSV directory.

Wishlist_Title = "xxxxxxx"  # Game appid
CSV_directory = "/CSV/"  # directory for CSV's just in case

# Initialize I2C 14-Segment Display
i2c = board.I2C()
display = segments.Seg14x4(board.I2C())
tca = adafruit_tca9548a.TCA9548A(i2c)
blue = segments.Seg14x4(tca[0], address=(0x71,0x72))

all_files = os.listdir(CSV_directory)  ## List all files in directory
Wishlist_all = ("SteamWishlists_GameAppID_all.csv")  # Generic Demonstration
#Wishlist_all = ("SteamWishlists_"+Wishlist_Title+"_all.csv")
PATH = (CSV_directory) + (Wishlist_all)

#print ("\nFiles in Directory : ", all_files)
print ("\nFile Path : ", PATH)
print("CSV Parsing...")
# Header currently unused, document for reference in case Steam changes it.
header = ["DateLocal", "Game", "Adds", "Deletes", "PurchasesAndActivations", "Gifts"]

sums = 0
with open(PATH) as csvfile:
    sep = ","
    while (line := csvfile.readline()) != "\n":
        if line[:4] == "sep=":
            sep = line.strip()[4:]
            # print(f"Delimiter is {sep}")
    for line in csv.DictReader(csvfile, delimiter=sep):
        try:
            sums += int(line['Adds'])
        except (TypeError, ValueError):
            pass
print("Calculating Sums...")
blue.fill(0)
blue.brightness = 0.5
blue.marquee("GAME APPID ALL TIME ADDS", loop=False)  # Intentionally generic demo
blue.fill(0)
time.sleep(2)
blue.print(sums)
print("appID Total Adds: ", sums)
