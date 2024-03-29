# SPDX-FileCopyrightText: 2024 DJDevon3
# SPDX-License-Identifier: MIT
# Coded for Circuit Python 9.0 ST7796S TFT Featherwing
# ATECC Crypto Module display example
# https://www.adafruit.com/product/4314

import time
import board
import busio
import displayio
import fourwire
import terminalio
import random
from adafruit_binascii import hexlify, unhexlify, a2b_base64, b2a_base64
from adafruit_atecc.adafruit_atecc import ATECC
import adafruit_atecc.adafruit_atecc_cert_util as cert_utils
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label, wrap_text_to_pixels
from circuitpython_st7796s import ST7796S

spi = board.SPI()
tft_cs = board.D9
tft_dc = board.D10
tft_rst = board.D17

# 3.5" ST7796S Display
DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 320

displayio.release_displays()
display_bus = fourwire.FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_rst)
display = ST7796S(display_bus, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, rotation=180)

i2c = busio.I2C(board.SCL, board.SDA, frequency=70000)
atecc = ATECC(i2c, address=0x60, debug=False)
# Initialize the SHA256 calculation engine
atecc.sha_start()

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

Arial16_font = bitmap_font.load_font("/fonts/Arial-16.bdf")

# Label Customizations
hello_label = label.Label(Arial16_font)
hello_label.anchor_point = (0.0, 0.0)
hello_label.anchored_position = (5, 20)
hello_label.scale = (1)
hello_label.color = TEXT_WHITE

# Create Display Groups
text_group = displayio.Group()
text_group.append(hello_label)
display.root_group = text_group

def generate_random_number(minimum, maximum):
    return random.randint(minimum, maximum)

# -- Enter your configuration below -- #

# Lock the ATECC module when the code is run?
LOCK_ATECC = True
# 2-letter country code
MY_COUNTRY = "US"
# State or Province Name
MY_STATE = "Florida"
# City Name
MY_CITY = "Miami"
# Organization Name
MY_ORG = "Treasure Coast Designs"
# Organizational Unit Name
MY_SECTION = "Crypto"
# Which ATECC slot (0-4) to use
ATECC_SLOT = 0
# Generate new private key, or use existing key
GENERATE_PRIVATE_KEY = False

# -- END Configuration, code below -- #

# Example usage:
min_num = 100000
max_num = 999999
random_num = generate_random_number(min_num, max_num)

atecc_serialnum = atecc.serial_number
atecc_random_value = atecc.random(rnd_min=500, rnd_max=1024)
#atecc_counter = atecc.counter(1, increment_counter=True)
# atecc_counter_ascii = [hex(x) for x in atecc_counter]
# atecc_counter_int_big = int.from_bytes(atecc_counter, "big")
# atecc_counter_int_little = int.from_bytes(atecc_counter, "little")

print(f"ATECC Serial: {atecc.serial_number}")
# Generate a random number with a maximum value of 1024
print(f"Random Value: {atecc_random_value}")
# Print out the value from one of the ATECC's counters
# You should see this counter increase on every time the code.py runs.
# print(f"ATECC Counter: {atecc_counter}")
# print(f"ATECC Counter ASCII: {atecc_counter_ascii}")
# print(f"ATECC Counter Big Int: {atecc_counter_int_big}")
# print(f"ATECC Counter Little Int: {atecc_counter_int_little}")

csr = cert_utils.CSR(atecc, ATECC_SLOT, GENERATE_PRIVATE_KEY, MY_COUNTRY, MY_STATE,
                     MY_CITY, MY_ORG, MY_SECTION)
# Generate CSR
my_csr = csr.generate_csr()
print("-----BEGIN CERTIFICATE REQUEST-----\n")
print(my_csr.decode('utf-8'))
print("-----END CERTIFICATE REQUEST-----")

while True:
    hello_label.text = f"SN: {atecc_serialnum}\nATECC Rand: {atecc_random_value}\nCircuit Python Random: {random_num}"
