# SPDX-FileCopyrightText: 2022 DJDevon3 for Adafruit Industries
# SPDX-License-Identifier: MIT

# RFM95 LoRa Featherwing Example
import gc
import time
import board
import busio
import digitalio
import adafruit_rfm9x

# Choose the Mode (receive or transmit)

# RECEIVER MODE (HOUSE)
import receiver

# TRANSMITTER MODE (MAILBOX)
# import transmitter
