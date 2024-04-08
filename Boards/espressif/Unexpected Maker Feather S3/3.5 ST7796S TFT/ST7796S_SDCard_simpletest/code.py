# SPDX-FileCopyrightText: 2024 DJDevon3
# SPDX-License-Identifier: MIT
# ST7796S TFT display SDCard simpletest
# Coded with Circuit Python 9.0

import time
import os
import board
import displayio
import sdcardio
import storage
import fourwire
from circuitpython_st7796s import ST7796S

displayio.release_displays()
# 4.0" ST7796S Display
DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 320

tft_cs = board.D9
tft_dc = board.D10
tft_rst = board.D17
sd_cs = board.D5

spi = board.SPI()
# Initialize SPI SDCard prior to other SPI peripherals!
try:
    print("Attempting to mount sd card")
    sdcard = sdcardio.SDCard(spi, sd_cs) 
    vfs = storage.VfsFat(sdcard)
    virtual_root = "/sd"
    storage.mount(vfs, virtual_root)
    print(os.listdir("/sd"))
except Exception as e:
    print("no sd card:", e)
    print("continuing")

display_bus = fourwire.FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_rst)
display = ST7796S(display_bus, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, rotation=180)

# System Stats
u_name = os.uname()
print("Board: ", u_name[4])
print("Type: ", u_name[0])
print("Version: ", u_name[3])

# Volume Information Stats
SD_Card_Size = os.statvfs(virtual_root)

print("\n🛠️ SD Card Info:")
print("===========================")
print("Block Size: ", SD_Card_Size[0])
print("Fragment Size: ", SD_Card_Size[1])
print("Free Blocks: ", SD_Card_Size[3])
print("Free Blocks Unpriv: ", SD_Card_Size[4])
print("Inodes: ", SD_Card_Size[5])
print("Free Inodes: ", SD_Card_Size[6])
print("Free Inodes Unpriv: ", SD_Card_Size[7])
print("Mount Flags: ", SD_Card_Size[8])
print("Max Filename Length: ", SD_Card_Size[9])
if (SD_Card_Size[0] * SD_Card_Size[3] / 1024 / 1024 / 1024) >= 1.0:
    print("Free Space GB: ", SD_Card_Size[0] * SD_Card_Size[3] / 1024 / 1024 / 1024)
if (SD_Card_Size[0] * SD_Card_Size[3] / 1024 / 1024 / 1024) <= 1.0:
    print("Free Space MB: ", SD_Card_Size[0] * SD_Card_Size[3] / 1024 / 1024)
    
# Small pause (in seconds) on Stats before File Directory is shown
time.sleep(3.0)
    
def print_directory(path, tabs=0):
    for file in os.listdir(path):
        stats = os.stat(path + "/" + file)
        filesize = stats[6]
        isdir = stats[0] & 0x4000

        if filesize < 1000:
            sizestr = str(filesize) + " by"
        elif filesize < 1000000:
            sizestr = "%0.1f KB" % (filesize / 1000)
        else:
            sizestr = "%0.1f MB" % (filesize / 1000000)

        prettyprintname = ""
        for _ in range(tabs):
            prettyprintname += "   "
        prettyprintname += file
        if isdir:
            prettyprintname += "/"
        print('{0:<40} Size: {1:>10}'.format(prettyprintname, sizestr))

        # recursively print directory contents
        if isdir:
            print_directory(path + "/" + file, tabs + 1)

print("\n💾 SD Card Files:")
print("===========================")
print_directory(virtual_root)

# Quick help to remove stuff. Directories must be empty before deleted.
# os.remove("/sd/backgrounds/image.bmp")
# os.rmdir("/sd/backgrounds")

# You can run libraries and .py files from the SD card by appending the system path.
# import something_on_the_sd_card
# sys.path.append("/sd")