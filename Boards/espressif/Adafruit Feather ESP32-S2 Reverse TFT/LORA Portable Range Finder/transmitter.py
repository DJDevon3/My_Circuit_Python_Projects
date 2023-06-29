# SPDX-FileCopyrightText: 2023 DJDevon3
# SPDX-License-Identifier: MIT
# Transmitter.py
# Adafruit CircuitPython 8.2 Adafruit Feather ESP32-S2 TFT with RFM95 Featherwing
import time
import supervisor
import board
import busio
import digitalio
import displayio
import terminalio
import adafruit_imageload
import adafruit_rfm9x
from adafruit_display_text import label
from adafruit_max1704x import MAX17048

# ESP32-S2 TFT is 240x135
DISPLAY_WIDTH = 240
DISPLAY_HEIGHT = 135
display = board.DISPLAY

battery_monitor = MAX17048(board.I2C())

# For RFM95x Featherwing
CS = digitalio.DigitalInOut(board.D10)
RESET = digitalio.DigitalInOut(board.D6)
# Uncomment below for Feather M0 RFM9x board
# CS = digitalio.DigitalInOut(board.RFM9X_CS)
# RESET = digitalio.DigitalInOut(board.RFM9X_RST)

# Define the onboard LED
LED = digitalio.DigitalInOut(board.D13)
LED.direction = digitalio.Direction.OUTPUT

# Initialize RFM Featherwing SPI bus.
spi = board.SPI()

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

hello_label = label.Label(terminalio.FONT)
hello_label.anchor_point = (0, 1.0)
hello_label.anchored_position = (5, 15)
hello_label.scale = (1)
hello_label.color = TEXT_WHITE

rssi_label = label.Label(terminalio.FONT)
rssi_label.anchor_point = (0.5, 0.5)
rssi_label.anchored_position = (DISPLAY_WIDTH/2, 75)
rssi_label.scale = (3)
rssi_label.color = TEXT_WHITE

vbat_label = label.Label(terminalio.FONT)
vbat_label.anchor_point = (1.0, 1.0)
vbat_label.anchored_position = (DISPLAY_WIDTH - 15, 20)
vbat_label.scale = 2

plugbmp_label = label.Label(terminalio.FONT)
plugbmp_label.anchor_point = (1.0, 1.0)
plugbmp_label.scale = 1

greenbmp_label = label.Label(terminalio.FONT)
greenbmp_label.anchor_point = (1.0, 1.0)
greenbmp_label.scale = 1

bluebmp_label = label.Label(terminalio.FONT)
bluebmp_label.anchor_point = (1.0, 1.0)
bluebmp_label.scale = 1

yellowbmp_label = label.Label(terminalio.FONT)
yellowbmp_label.anchor_point = (1.0, 1.0)
yellowbmp_label.scale = 1

orangebmp_label = label.Label(terminalio.FONT)
orangebmp_label.anchor_point = (1.0, 1.0)
orangebmp_label.scale = 1

redbmp_label = label.Label(terminalio.FONT)
redbmp_label.anchor_point = (1.0, 1.0)
redbmp_label.scale = 1

# Load battery voltage icons (from 1 sprite sheet image)
sprite_sheet, palette = adafruit_imageload.load("/icons/vbat_spritesheet.bmp",
                                                bitmap=displayio.Bitmap,
                                                palette=displayio.Palette)
sprite = displayio.TileGrid(sprite_sheet, pixel_shader=palette,
                            width=1,
                            height=1,
                            tile_width=11,
                            tile_height=20)
sprite_group = displayio.Group(scale=1)
sprite_group.append(sprite)
sprite_group.x = DISPLAY_WIDTH-11
sprite_group.y = 0

# Create subgroups
text_group = displayio.Group()
main_group = displayio.Group()

# Add subgroups to main display group
main_group.append(text_group)
main_group.append(sprite_group)

# Label Display Group (foreground layer)
text_group.append(hello_label)
text_group.append(vbat_label)
text_group.append(plugbmp_label)
text_group.append(greenbmp_label)
text_group.append(bluebmp_label)
text_group.append(yellowbmp_label)
text_group.append(orangebmp_label)
text_group.append(redbmp_label)
text_group.append(rssi_label)
display.show(main_group)

# Initialze RFM radio
RADIO_FREQ_MHZ = 915.0  # Frequency of the radio in Mhz
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)

# Radio configured in RFM95/LoRa mode. You can't control sync
# encryption, frequency deviation, or other settings!
rfm9x.tx_power = 13  # Transmit Power. Default 13dB. RFM95 (0-23)dB:
rfm9x.enable_crc = True  # Ensures packets are correctly formatted
rfm9x.ack_retries = 5  # Number of retries to send an ack packet
rfm9x.ack_delay = .1  # If ACK's are being missed try .1 or .2
rfm9x.xmit_timeout = 2.0  # Recommended at least 2 seconds for HW reliability
# The receiver undertakes a preamble detection process that periodically restarts.
# All devices should be configured to identical preamble lengths
# Use max preamble length if preamble length is unknown.
rfm9x.preamble_length = 8  # (8-12)
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

board.DISPLAY.show(main_group)

print("-"*80, "\n")
while True:
    hello_label.text = "RFM95 Range Finder"
    print("===============================")
    debug_OWM = False  # Set to True for Serial Print Debugging

    # USB Power Sensing
    try:
        vbat_label.text = f"{battery_monitor.cell_voltage:.2f}"
    except (ValueError, RuntimeError, OSError) as e:
        print("MAX17048 Error: \n", e)
    # Set USB plug icon and voltage label to white
    usb_sense = supervisor.runtime.serial_connected
    if debug_OWM:
        print("USB Sense: ", usb_sense)
    if usb_sense:  # if on USB power show plug sprite icon
        vbat_label.color = TEXT_WHITE
        sprite[0] = 5
    if not usb_sense:  # if on battery power only
        # Changes battery voltage color depending on charge level
        if vbat_label.text >= "4.23":
            vbat_label.color = TEXT_WHITE
            sprite[0] = 5
        elif "4.10" <= vbat_label.text <= "4.22":
            vbat_label.color = TEXT_GREEN
            sprite[0] = 0
        elif "4.00" <= vbat_label.text <= "4.09":
            vbat_label.color = TEXT_LIGHTBLUE
            sprite[0] = 1
        elif "3.90" <= vbat_label.text <= "3.99":
            vbat_label.color = TEXT_YELLOW
            sprite[0] = 2
        elif "3.80" <= vbat_label.text <= "3.89":
            vbat_label.color = TEXT_ORANGE
            sprite[0] = 3
        elif vbat_label.text <= "3.79":
            vbat_label.color = TEXT_RED
            sprite[0] = 4
        else:
            vbat_label.color = TEXT_WHITE

    time.sleep(0.5)

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
    packet = rfm9x.receive(keep_listening=True, timeout=rfm9x.xmit_timeout, with_header=with_header)

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
        debug_raw_received = True
        if debug_raw_received:
            # Print out the raw bytes of the packet:
            print("Received (raw bytes): {0}".format(packet))
            print("Timestamp: ", now)
            print("Localtime: ", current_date)

        debug_radio_antenna = True
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

    # Transmit Test
    rssi_label.text = f"RSSI: {rfm9x.last_rssi}"
    print("Received RSSI: {0}".format(rfm9x.last_rssi))
    message = str("Test 🙂")
    rfm9x.send(bytes(str(now) + " " + message + "\r\n", "utf-8"), keep_listening=True)
    print("(Sent)" + " " + message)
    print("Monotonic: " + str(now), "\n")
    time.sleep(2) # The smaller the delay the more likely for packet loss. There is a speed limit.
