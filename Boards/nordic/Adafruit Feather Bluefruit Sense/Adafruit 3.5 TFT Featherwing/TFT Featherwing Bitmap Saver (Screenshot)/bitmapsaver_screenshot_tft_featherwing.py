# SPDX-FileCopyrightText: 2019 Dave Astels for Adafruit Industries
# SPDX-License-Identifier: MIT


"""Screenshot on a 3.5" TFT Featherwing (integrated SD Card)"""

# pylint:disable=invalid-name
import board
import digitalio
import displayio
import adafruit_sdcard
from adafruit_bitmapsaver import save_pixels
import storage
from adafruit_hx8357 import HX8357

# Will also work on 2.5" TFT Featherwing just change the size.
DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 320

# Initialize Protocol Busses and SD Card
i2c = board.I2C()
spi = board.SPI()
cs = digitalio.DigitalInOut(board.D5)
sdcard = adafruit_sdcard.SDCard(spi, cs)
vfs = storage.VfsFat(sdcard)
displayio.release_displays()

# Setup Pinouts according to your feather board
tft_cs = board.D9
tft_dc = board.D10
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = HX8357(display_bus, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT)

# Mount Virtual File System
virtual_root = "/sd"
storage.mount(vfs, virtual_root)

print("Taking Screenshot... ")
save_pixels("/sd/screenshot.bmp", display)
print("Screenshot taken")