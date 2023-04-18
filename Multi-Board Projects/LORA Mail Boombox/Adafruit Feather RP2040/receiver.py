# SPDX-FileCopyrightText: 2022 DJDevon3 for Adafruit Industries
# SPDX-License-Identifier: MIT
# Receiver.py
# Adafruit CircuitPython 8.0.3 on 2023-03-14; Adafruit Feather RP2040 & RFM95 Featherwing
import os
import gc
import time
import random
import board
import pwmio
import busio
import audiomixer
import audiobusio
import audiomp3
import digitalio
import adafruit_rfm9x
import neopixel
from adafruit_motor import servo

# Initialize small I2S Module Sound Out
audio = audiobusio.I2SOut(bit_clock=board.A2, word_select=board.A3, data=board.D24)
i2s_sound_level = 0.0

# file system setup
mp3s = []
for filename in os.listdir('/Sounds/Mail/'):
    if filename.lower().endswith('.mp3') and not filename.startswith('.'):
        mp3s.append("/Sounds/Mail/"+filename)

mp3s.sort()  # filenames must be in "Track#_Artist_Song_.mp3" format

track_number = 0
mp3_filename = mp3s[track_number]
mp3_bytes = os.stat(mp3_filename)[6]  # size in bytes is position 6
mp3_file = open(mp3_filename, "rb")
mp3stream = audiomp3.MP3Decoder(mp3_file)

def tracktext(full_path_name, position):
    return full_path_name.split('_')[position].split('.')[0]

song_name_text = tracktext(mp3_filename, 2)

mixer = audiomixer.Mixer(voice_count=1, sample_rate=22050, channel_count=1,
                         bits_per_sample=16, samples_signed=True)
mixer.voice[0].level = 0.005
mixer.voice[0].level = 0.05
audio.play(mixer)

def change_track(tracknum):
    # pylint: disable=global-statement
    global mp3_filename
    mp3_filename = mp3s[tracknum]
    song_name_fc = tracktext(mp3_filename, 2)
    artist_name_fc = tracktext(mp3_filename, 1)
    mp3_file_fc = open(mp3_filename, "rb")
    mp3stream_fc = audiomp3.MP3Decoder(mp3_file_fc)
    mp3_bytes_fc = os.stat(mp3_filename)[6]  # size in bytes is position 6
    return (mp3_file_fc, mp3stream_fc, song_name_fc, artist_name_fc, mp3_bytes_fc)

play_state = False  # so we know if we're auto advancing when mixer finishes a song
last_debug_time = 0  # for timing track position
last_percent_done = 0.01

pixel_pin = board.D25
num_pixels = 144
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.6, auto_write=True)
Clear_Pixels = (0, 0, 0)

CS = digitalio.DigitalInOut(board.D10)
RESET = digitalio.DigitalInOut(board.D11)
# Feather M0 with integrated RFM use below instead
# CS = digitalio.DigitalInOut(board.RFM9X_CS)
# RESET = digitalio.DigitalInOut(board.RFM9X_RST)

# Define the onboard LED
LED = digitalio.DigitalInOut(board.D13)
LED.direction = digitalio.Direction.OUTPUT

# Setup Servo Motor
flag = pwmio.PWMOut(board.D12, frequency=50)
servo_1 = servo.Servo(flag)

# Hardwired RFM Featherwing SPI pins (cannot not change these)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# Initialze RFM radio
RADIO_FREQ_MHZ = 915.0  # Frequency of the radio in Mhz
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)

# Radio configured in LoRa mode. You can't control sync
# encryption, frequency deviation, or other settings!
rfm9x.tx_power = 13  # Transmit Power. Default 13dB. RFM95 (0-23)dB:
rfm9x.enable_crc = False
rfm9x.xmit_timeout = 2.0  # Recommended at least 2 seconds for HW reliability
with_header = True  # Set if you want header bytes printed for debug

# Node (0-255) Only packets addressed to this node will be accepted.
# Comment out to disable and receive all packets from anywhere
# rfm9x.node = 13
print("-"*80, "\n")
while True:
    # Can only process one 252 byte packet at a time.
    print("Waiting for packet...")

    # Time in seconds from when board was powered on
    now = time.monotonic()
    # Changing timeout and sleep duration definitely has an effect on dropped packets.
    # Timeout 5 and sleep 0.5 works great with no dropped packets in my experience.
    packet = rfm9x.receive(keep_listening=True, timeout=rfm9x.xmit_timeout, with_header=False)
    # If no packet was received during timeout then packet=None is returned.
    if packet is None:
        # Packet has not been received
        LED.value = False
        print("Packet: None - Sleep for " + str(rfm9x.xmit_timeout) + " seconds...")
    else:
        # Now we're inside a received packet!
        LED.value = True
        play_state = True
        mp3_file, mp3stream, song_name, artist_name, mp3_bytes = change_track(track_number)
        mixer.voice[0].play(mp3stream, loop=False)
        track_number = ((track_number + 1) % len(mp3s))

        while mixer.playing:
            Random_Red = random.randint(0,255)
            Random_Green = random.randint(0,255)
            Random_Blue = random.randint(0,255)
            Random_Color = [Random_Red, Random_Green, Random_Blue]
            mixer.voice[0].level = i2s_sound_level

            pixels.fill(Random_Color)
            time.sleep(0.05)
            pixels.fill(Clear_Pixels)
            time.sleep(0.05)
            pixels.fill(Random_Color)
            time.sleep(0.05)
            pixels.fill(Clear_Pixels)
            time.sleep(0.05)
        print("MP3 Played: ", song_name)
        mixer.voice[0].level = 0.0
        try:
            # Header bytes are raw bytes. Good for debugging.
            if with_header:
                packet_text = str(packet)
            # Strips header bytes and decodes to ascii.
            if not with_header:
                packet_text = str(packet, "ascii")
        except (UnicodeError) as e:
            print("Unicode Error", e)
            continue
        debug_flagservo = True
        if debug_flagservo:
            servo_1.angle = 110
            time.sleep(1)
            servo_1.angle = 0
        rssi = rfm9x.last_rssi
        last_snr = rfm9x.last_snr
        debug_raw_received = False
        if debug_raw_received:
            # Print out the raw bytes of the packet:
            print("Received (raw bytes): {0}".format(packet))
            print("Timestamp: ", now)
        # And decode to ASCII text and print it too.  Note that you always
        # receive raw bytes and need to convert to a text format like ASCII
        # if you intend to do string processing on your data.  Make sure the
        # sending side is sending ASCII data before you try to decode!
        debug_radio_antenna = False
        if debug_radio_antenna:
            print("Signal Noise: {0} dB".format(last_snr))
            print("Signal Strength: {0} dB".format(rssi))
        debug_ascii_received = True
        if debug_ascii_received:
            text_length = len(packet_text)+4
            print("Received Packet!!!")
            print("-"*text_length)
            print("| {0}".format(packet_text), "|")
            print("-"*text_length)
        gc.collect
    message = str("Feather RP2040 Msg Test 😇 ")  # Transmit Test MSG
    
    # Transmit Test
    rfm9x.send(bytes(str(now) + " " + message + "\r\n", "utf-8"), keep_listening=True)
    print("(Sent)" + " " + message)
    
    print("Timestamp: " + str(now), "\n")
    time.sleep(2) # The smaller the delay the more likely for packet loss. There is a speed limit.
