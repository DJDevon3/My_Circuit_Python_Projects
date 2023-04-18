# SPDX-FileCopyrightText: 2022 DJDevon3 for Adafruit Industries
# SPDX-License-Identifier: MIT

# RFM95 LoRa Featherwing Example
import time
import board
import busio
import digitalio
import adafruit_rfm9x
# MAILBOX TRANSMITTER

# Define Frequency
RADIO_FREQ_MHZ = 915.0  # Frequency of the radio in Mhz. Must match your
# module! Can be a value like 915.0, 433.0, etc.

# Initialize LORA Pins
# This setup works for most Feathers
CS = digitalio.DigitalInOut(board.D10)
RESET = digitalio.DigitalInOut(board.D6)

# Define the onboard LED
LED = digitalio.DigitalInOut(board.D13)
LED.direction = digitalio.Direction.OUTPUT

# Initialize SPI bus.
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# Initialze RFM radio
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)

# Radio in LoRa mode, you can't control sync word, encryption,
# frequency deviation, or other settings!
# Default is 13 dB, RFM95 can go up to 23 dB
rfm9x.tx_power = 13
rfm9x.node = 10

# Max Packet Size is 252 bytes
print("Starting Packet Transmitter...\n")

while True:
    # Time in seconds from when board was powered on
    now = time.monotonic()

    # Send 3 separate packets
    print("Time: ", now)
    rfm9x.send(bytes("Hello\r\n", "utf-8"))
    # Short sleep between packets can help, unecessary for high baudrate
    time.sleep(2)
    rfm9x.send(bytes("World!\r\n", "utf-8"))
    time.sleep(2)
    rfm9x.send(bytes("Third Syn\r\n", "utf-8"))
    print("Packet Transmitted\n")
    time.sleep(60)
