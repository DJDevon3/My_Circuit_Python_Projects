# SPDX-FileCopyrightText: 2022 DJDevon3 for Adafruit Industries
# SPDX-License-Identifier: MIT
# Transmitter.py
# Adafruit CircuitPython 8.0.4 on 2023-03-15; Adafruit Feather M4 Express with samd51j19
import gc
import time
import board
import busio
import digitalio
import adafruit_rfm9x
import adafruit_vl53l4cd

# VL53L4CD Time of Flight Sensor
i2c = board.I2C()  # uses board.SCL and board.SDA
vl53 = adafruit_vl53l4cd.VL53L4CD(i2c)
# Optional: can set non-default values
vl53.inter_measurement = 0
vl53.timing_budget = 200

# For RFM95x Featherwing
CS = digitalio.DigitalInOut(board.D10)
RESET = digitalio.DigitalInOut(board.D6)
# Uncomment below for Feather M0 RFM9x board
# CS = digitalio.DigitalInOut(board.RFM9X_CS)
# RESET = digitalio.DigitalInOut(board.RFM9X_RST)

# Define the onboard LED
LED = digitalio.DigitalInOut(board.D13)
LED.direction = digitalio.Direction.OUTPUT

# Initialize SPI bus.
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# Initialze RFM radio
RADIO_FREQ_MHZ = 915.0  # Frequency of the radio in Mhz
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)

# Radio configured in RFM95/LoRa mode. You can't control sync
# encryption, frequency deviation, or other settings!
rfm9x.tx_power = 13  # Transmit Power. Default 13dB. RFM95 (0-23)dB:
rfm9x.enable_crc = True  # Ensures packets are correctly formatted
rfm9x.ack_retries = 5  # Number of retries to send an ack packet
rfm9x.ack_delay = .1  # If ACK's are being missed try .1 or .2
rfm9x.xmit_timeout = 2.0 # Recommended at least 2 seconds for HW reliability
# The receiver undertakes a preamble detection process that periodically restarts.
# All devices should be configured to identical preamble lengths
# Use max preamble length if preamble length is unknown.
rfm9x.preamble_length = 8 # (8-12)
# Bandwidth defaults to RadioHead compatible Bw125Cr45Sf128 mode.
rfm9x.signal_bandwidth = 125000
# Values (5-8) Error correction tolerance.
# Higher value more noise tolerance. Lower value increases bit rate.
rfm9x.coding_rate = 5
# If SF = 6 all packets sent without headers on HW side!
# Default and recommended setting is 7
rfm9x.spreading_factor = 7
# Node Address (0-255) If not 255, only receive at node address.
# This int is the 1st byte in the header
rfm9x.node = 255
# Node Destination (0-255) If not 255, only send to node address.
# This int is the 2nd byte in the header
rfm9x.destination = 255

with_header = True  # Set if you want header bytes printed for debug

def _format_datetime(datetime):
    return "{:02}/{:02}/{} {:02}:{:02}:{:02}".format(
        datetime.tm_mon,
        datetime.tm_mday,
        datetime.tm_year,
        datetime.tm_hour,
        datetime.tm_min,
        datetime.tm_sec,
    )

print("-"*80, "\n")
while True:
    # Can only process one 252 byte packet at a time.
    print("Waiting for packet...")
    # Time in seconds from when board was powered on
    now = time.monotonic()
    # Show fictional timestamp starting in year 2000.
    # Fake date are great for syn/ack timestamps on boards with no RTC or Wifi
    # Just don't print timestamps to end user in these scenarios.
    # It would obviously confuse them if they think the timestamps are wrong, they're not.
    
    # If your board DOES have wifi time server or RTC (not included) 
    # plug your fetched unix time into unix_time and uncomment below
    # unix_time = 1660764970 # Wed Aug 17 2022 19:36:10 GMT+0000
    # tz_offset_seconds = -14400  # NY Timezone
    # get_timestamp = int(unix_time + tz_offset_seconds)
    # and swap out CURRENT_UNIX_TIME with this one
    # current_unix_time = time.localtime(get_timestamp)
    
    current_unix_time = time.localtime()
    current_struct_time = time.struct_time(current_unix_time)
    current_date = "{}".format(_format_datetime(current_struct_time))

    # Changing timeout and sleep duration definitely has an effect on dropped packets.
    packet = rfm9x.receive(keep_listening=False, timeout=rfm9x.xmit_timeout, with_header=with_header)

    # If no packet was received during timeout then packet=None is returned.
    if packet is None:
        # Packet has not been received
        LED.value = False
        print("Packet: None - Sleep for " + str(rfm9x.xmit_timeout) + " seconds...")
    else:
        # Now we're inside a received packet!
        LED.value = True
        try:
            # Header bytes are raw bytes. Good for debugging.
            if with_header:
                packet_text = str(packet)
            # No header strips header bytes and decodes to ascii.
            if not with_header:
                packet_text = str(packet, "ascii")
        except (UnicodeError) as e:
            print("Unicode Error", e)
            continue

        # received sig strenth and sig/noise
        rssi = rfm9x.last_rssi
        last_snr = rfm9x.last_snr
        # Debug printing of packet data:
        debug_raw_received = False
        if debug_raw_received:
            # Print out the raw bytes of the packet:
            print("Received (raw bytes): {0}".format(packet))
            print("Timestamp: ", now)
            print("Localtime: ", current_date)
            
        debug_radio_antenna = False
        if debug_radio_antenna:
            print("Signal Noise: {0} dB".format(last_snr))
            print("Signal Strength: {0} dB".format(rssi))
            
        debug_ascii_received = True
        if debug_ascii_received:
            text_length = len(packet_text)+4
            print("\nReceived Packet!!!")
            print("-"*text_length)
            print("| {0}".format(packet_text), "|")
            print("-"*text_length)
            

    # Original New Packet Transmit (252 byte maximum)
    # Each send waits for previous send to finish
    vl53.start_ranging()
    if vl53.distance <= 50:
        while not vl53.data_ready:
            pass
        vl53.clear_interrupt()
        print("Distance: {} cm".format(vl53.distance))
        print(vl53.distance)
        
        # Transmit Test
        message = str("Feather M4 Test 🙂")
        rfm9x.send(bytes(str(now) + " " + message + "\r\n", "utf-8"), keep_listening=False)
        print("(Sent)" + " " + message)
        print("Monotonic: " + str(now), "\n")
    time.sleep(0.5) # The smaller the delay the more likely for packet loss. There is a speed limit.
