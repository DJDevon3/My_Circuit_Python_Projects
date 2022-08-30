import board
import digitalio
import displayio
import sdcardio
import storage
import os
import time
from adafruit_hx8357 import HX8357

spi = board.SPI()
# Use adafruit_sdcard library if your board doesn't support sdcardio
# import adafruit_sdcard
# sdcard = adafruit_sdcard.SDCard(spi, cs)
# cs = digitalio.DigitalInOut(board.D5)

# Initialize SDCard to SPI bus
sdcard = sdcardio.SDCard(spi, board.D5)
vfs = storage.VfsFat(sdcard)
displayio.release_displays()

# This sketch should also work for the 2.5" TFT, just change the size.
DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 320

# Release any resources currently in use for the displays
displayio.release_displays()
spi = board.SPI()
tft_cs = board.D9
tft_dc = board.D10
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = HX8357(display_bus, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT)

# Mounts virtual folder "sd" to your CIRCUITPY board.
# Ensure the folder DOES NOT EXIST or it will throw an error.
# vfs is a Virtual File System. An invisible temporary folder, it's not a USB drive.
virtual_root = "/sd"
storage.mount(vfs, virtual_root)

# System Stats
u_name = os.uname()
print("Board: ", u_name[4])
print("Type: ", u_name[0])
print("Version: ", u_name[3])

# Volume Information Stats
SD_Card_Size = os.statvfs(virtual_root)
print("\n")
print("SD Card Info:")
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
time.sleep(10.0)
    
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

print("\n")
print("SD Card Files:")
print("===========================")
print_directory(virtual_root)

# Quick help to remove stuff. Directories must be empty before deleted.
# os.remove("/sd/backgrounds/image.bmp")
# os.rmdir("/sd/backgrounds")

# You can run libraries and .py files from the SD card by appending the system path.
# import something_on_the_sd_card
# sys.path.append("/sd")