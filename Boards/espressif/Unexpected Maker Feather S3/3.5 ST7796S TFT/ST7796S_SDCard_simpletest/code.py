# SPDX-FileCopyrightText: 2023 DJDevon3
# SPDX-License-Identifier: MIT
# ST7796S TFT display SDCard simpletest

import os
import board
import displayio
import sdcardio
import storage
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
    storage.mount(vfs, '/sd')  
    print(os.listdir("/sd"))
except Exception as e:
    print("no sd card:", e)
    print("continuing")

display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_rst)
display = ST7796S(display_bus, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, rotation=180)

# System Stats
u_name = os.uname()
print("Board: ", u_name[4])
print("Type: ", u_name[0])
print("Version: ", u_name[3])
