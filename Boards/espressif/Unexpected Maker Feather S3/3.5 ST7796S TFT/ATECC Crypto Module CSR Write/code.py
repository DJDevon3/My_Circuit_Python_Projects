# SPDX-FileCopyrightText: 2024 DJDevon3
# SPDX-License-Identifier: MIT
# Coded for Circuit Python 8.x ST7796S TFT Featherwing
# ATECC Crypto Module display example
# https://www.adafruit.com/product/4314

# THIS EXAMPLE IS HORRIBLY BROKEN & PROOF OF CONCEPT ONLY.
# I HAD TO REMOVE EVERYTHING TO DO WITH THE SERIAL NUMBER TO GET IT WORKING-ish.

import board
import busio
import displayio
from adafruit_atecc.adafruit_atecc import ATECC, _WAKE_CLK_FREQ, CFG_TLS
import adafruit_atecc.adafruit_atecc_cert_util as cert_utils
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label
from circuitpython_st7796s import ST7796S

spi = board.SPI()
tft_cs = board.D9
tft_dc = board.D10
tft_rst = board.D17

# 4.0" ST7796S Display
DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 320

displayio.release_displays()
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_rst)
display = ST7796S(display_bus, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, rotation=180)

# -- Enter your configuration below -- #
# I2C Wake Frequency
_WAKE_CLK_FREQ = 75000
# WARNING: LOCK_ATECC=TRUE WILL PERMANENTLY LOCK THE CHIP!
# Fill in the config now, can never be reconfigured once you flip it to True!
LOCK_ATECC = False
# 2-letter country code
MY_COUNTRY = "US"
# State or Province Name
MY_STATE = "New York"
# City Name
MY_CITY = "New York"
# Organization Name
MY_ORG = "Adafruit"
# Organizational Unit Name
MY_SECTION = "Crypto"
# Which ATECC slot (0-4) to use
ATECC_SLOT = 0
# Generate new private key, or use existing key
GENERATE_PRIVATE_KEY = True

# -- END Configuration, code below -- #

i2c = busio.I2C(board.SCL, board.SDA, frequency=75000)
atecc = ATECC(i2c_bus=i2c, address=0x60, debug=False)
# Initialize the SHA256 calculation engine
print("WE MADE IT OUT OF THE LIBRARY LOOP!")

try:
    atecc.sha_start()
except OSError as e:
    print(e)

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

atecc_serialnum = atecc.serial_number
atecc_random_value = atecc.random(rnd_max=1024)
atecc_counter = atecc.counter(1, increment_counter=True)
atecc_counter_ascii = [hex(x) for x in atecc_counter]
atecc_counter_int_big = int.from_bytes(atecc_counter, "big")
atecc_counter_int_little = int.from_bytes(atecc_counter, "little")

print("ATECC Serial: ", atecc_serialnum)
# Generate a random number with a maximum value of 1024
print("Random Value: ", atecc_random_value)
# Print out the value from one of the ATECC's counters
# You should see this counter increase on every time the code.py runs.
print(f"ATECC Counter: {atecc_counter}")
print(f"ATECC Counter ASCII: {atecc_counter_ascii}")
print(f"ATECC Counter Big Int: {atecc_counter_int_big}")
print(f"ATECC Counter Little Int: {atecc_counter_int_little}")

print("Generating Certificate Signing Request...")
# Initialize a certificate signing request with provided info

csr = cert_utils.CSR(
    atecc,
    ATECC_SLOT,
    GENERATE_PRIVATE_KEY,
    MY_COUNTRY,
    MY_STATE,
    MY_CITY,
    MY_ORG,
    MY_SECTION,
)
# Generate CSR
my_csr = csr.generate_csr()
print("-----BEGIN CERTIFICATE REQUEST-----\n")
print(my_csr.decode("utf-8"))
print("-----END CERTIFICATE REQUEST-----")

while True:
    hello_label.text = f"SN: {atecc_serialnum}\nRand: {atecc_random_value}\nCount: {atecc_counter_int_little}\nMemory Slot: {ATECC_SLOT}\nCountry: {MY_COUNTRY}\nState: {MY_STATE}\nCity: {MY_CITY}\nOrganization: {MY_ORG}\nDepartment: {MY_SECTION}"


