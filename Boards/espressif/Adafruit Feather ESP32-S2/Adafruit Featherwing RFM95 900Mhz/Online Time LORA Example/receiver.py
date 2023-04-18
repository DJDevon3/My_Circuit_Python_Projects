# SPDX-FileCopyrightText: 2022 DJDevon3 for Adafruit Industries
# SPDX-License-Identifier: MIT

# RFM95 LoRa Featherwing Example
import gc
import time
import board
import busio
import digitalio
import adafruit_rfm9x
import rtc, wifi, ssl, socketpool
import adafruit_requests
import adafruit_ntp
# RECEIVER MODE

from secrets import secrets
# Check secrets.py to adjust timezone
tz_offset_seconds = int(secrets["timezone_offset"])

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

# During Timeout, automatically wakes if a packet is received
timeout_length = 15

def _format_datetime(datetime):
    return "{:02}/{:02}/{} {:02}:{:02}:{:02}".format(
        datetime.tm_mon,
        datetime.tm_mday,
        datetime.tm_year,
        datetime.tm_hour,
        datetime.tm_min,
        datetime.tm_sec,
    )

# Connect to Wi-Fi
print("\n===============================")
print("Connecting to WiFi...")

while True:
    while not wifi.radio.ipv4_address:
        try:
            pool = socketpool.SocketPool(wifi.radio)
            request = adafruit_requests.Session(pool, ssl.create_default_context())
            wifi.radio.enabled = False
            wifi.radio.enabled = True
            wifi.radio.connect(secrets['ssid'], secrets['password'])
        except ConnectionError as e:
            print("Connection Error:", e)
            print("Retrying in 10 seconds")
        time.sleep(10)
        gc.collect()
    print("Connected to WiFi - Waiting for LORA Packet...")
    while wifi.radio.ipv4_address:
        pool = socketpool.SocketPool(wifi.radio)
        request = adafruit_requests.Session(pool, ssl.create_default_context())
        # Connect to WorldTimeAPI
        # print("Getting Time from WorldTimeAPI")
        try:
            response = request.get("http://worldtimeapi.org/api/ip")
            time_data = response.json()
        except RuntimeError as e:
            print("Time API Connection Error:", e)
            print("Retrying in 10 seconds")

        unix_time = int(time_data['unixtime'])
        get_timestamp = int(unix_time + tz_offset_seconds)
        current_unix_time = time.localtime(get_timestamp)
        current_struct_time = time.struct_time(current_unix_time)
        current_date = "{}".format(_format_datetime(current_struct_time))

        packet = rfm9x.receive(keep_listening=True, timeout=timeout_length)
        # If no packet was received during timeout then None is returned.
        if packet is None:
            # Packet has not been received
            LED.value = False
            print("Timestamp:", current_date)
            print("No Packet Found: Timeout for", timeout_length)
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
                # Max Packet Size is 252 bytes
                print("Received (raw bytes): {0}".format(packet))
                print("Byte Length: ", len(packet_text))
                # Decode to ASCII. Always receive raw bytes and convert
                # to text format like ASCII for string processing on your data.
                # Sending side must send in ASCII data before you try to decode!
                print("Timestamp:", current_date)
                print("Signal Noise: {0} dB".format(last_snr))
                print("Signal Strength: {0} dB".format(rssi))
                print("Received (ASCII): {0}".format(packet_text))
                LED.value = False
                gc.collect()
            except (UnicodeError) as e:
                print("Unicode Decode Failure, retrying\n", e)
                continue
