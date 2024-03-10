# SPDX-FileCopyrightText: 2024 DJDevon3
# SPDX-License-Identifier: MIT
# Coded for Circuit Python 8.2.x
# ATECC Crypto Module display example
# https://www.adafruit.com/product/4314

import board
import busio
from adafruit_atecc.adafruit_atecc import ATECC

# Initialize a slower i2c bus with low frequency wake up pulse
# You should not share this bus with other regular I2C devices
i2c = busio.I2C(board.SCL, board.SDA, frequency=75000)

# Initialize ATECC object
atecc = ATECC(i2c_bus=i2c, address=0x60, debug=False)

print("ATECC Serial: ", atecc.serial_number)

# Generate a random number with a maximum value of 1024
print("Random Value: ", atecc.random(rnd_max=1024))  # This does not work?!?

# Print ATECC's counter. Increases by 1 every code.py run.
print("ATECC Counter #1 Value: ", atecc.counter(1, increment_counter=True))

# Initialize the SHA256 calculation engine
atecc.sha_start()

# Append bytes to the SHA digest
print("Appending to the digest...")
atecc.sha_update(b"Nobody inspects")
print("Appending to the digest...")
atecc.sha_update(b" the spammish repetition")

# Return the digest of the data passed to sha_update
message = atecc.sha_digest()
print("SHA Digest: ", message)