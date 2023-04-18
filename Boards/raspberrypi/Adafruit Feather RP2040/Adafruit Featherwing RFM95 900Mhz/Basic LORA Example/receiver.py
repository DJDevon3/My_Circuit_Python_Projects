# SPDX-FileCopyrightText: 2022 DJDevon3 for Adafruit Industries
# SPDX-License-Identifier: MIT

# RFM95 LoRa Featherwing Example
import gc
import time
import board
import busio
import digitalio
import adafruit_rfm9x
# RECEIVER MODE

# Define Frequency
RADIO_FREQ_MHZ = 915.0  # Frequencies must match!

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

# Max Packet Size is 252 bytes
print("Starting Packet Receiver...\n")
# During Timeout, automatically wakes if a packet is received
timeout_length = 15

while True:
    # Time in seconds from when board was powered on
    now = time.monotonic()

    packet = rfm9x.receive(keep_listening=True, timeout=timeout_length)
    # If no packet was received during the timeout then None is returned.
    if packet is None:
        # Packet has not been received
        LED.value = False
        print("Time: ", now)
        print("Clear: Hibernating for", timeout_length)
        print(" ")
        gc.collect()
    else:
        try:
            # Received a packet!
            LED.value = True
            packet_text = str(packet, "ascii")
            rssi = rfm9x.last_rssi
            last_snr = rfm9x.last_snr
            # Print raw UTF-8/ASCII bytes of the packet:
            print("Received (raw bytes): {0}".format(packet))
            print("Byte Length: ", len(packet_text))
            # Decode to ASCII. Always receive raw bytes and convert
            # to text format like ASCII for string processing on your data.
            # Sending side must send in ASCII data before you try to decode!
            print("Time: ", now)
            print("Signal Noise: {0} dB".format(last_snr))
            print("Signal Strength: {0} dB".format(rssi))
            print("Received (ASCII): {0}".format(packet_text))
            LED.value = False
            gc.collect()
        except (UnicodeError) as e:
            print("Unicode Decode Failure, retrying\n", e)
            continue
