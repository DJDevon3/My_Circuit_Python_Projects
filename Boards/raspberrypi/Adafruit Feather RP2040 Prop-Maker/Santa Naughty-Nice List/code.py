import os
import time
import random
import board
import audiomp3
import audiobusio
import audiomixer
from digitalio import DigitalInOut, Direction, Pull
from adafruit_led_animation.animation.rainbowsparkle import RainbowSparkle
from adafruit_led_animation.animation.rainbowcomet import RainbowComet
from adafruit_led_animation.animation.rainbowchase import RainbowChase
from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.animation.pulse import Pulse
from adafruit_led_animation.animation.sparkle import Sparkle
from adafruit_led_animation.color import RED, GREEN, BLUE, BLACK, RAINBOW
import neopixel

# Enable external power pin
external_power = DigitalInOut(board.EXTERNAL_POWER)
external_power.direction = Direction.OUTPUT
external_power.value = True

# Initialize external buttons
naughty_button = DigitalInOut(board.D5)  # Connect to pin D5
nice_button = DigitalInOut(board.D6)  # Connect to pin D6

naughty_button.direction = nice_button.direction = Direction.INPUT
naughty_button.pull = nice_button.pull = Pull.UP

# Define the directories for WAV files
naughty_directory = "/naughty"
nice_directory = "/nice"

# Lists to hold the file paths
naughty_snd = [
    naughty_directory + "/" + filename
    for filename in os.listdir(naughty_directory)
    if filename.lower().endswith(".mp3") and not filename.startswith(".")
]
nice_snd = [
    nice_directory + "/" + filename
    for filename in os.listdir(nice_directory)
    if filename.lower().endswith(".mp3") and not filename.startswith(".")
]

# Initialize LED animations
PIXEL_PIN = board.EXTERNAL_NEOPIXELS
NUM_PIXELS = 50
ORDER = neopixel.GRB
BRIGHTNESS = 0.2
PIXELS = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, auto_write=False, pixel_order=ORDER)

# Define LED colors
BLUE_BRIGHT = [value * BRIGHTNESS for value in BLUE]
RED_BRIGHT = [value * BRIGHTNESS for value in RED]
GREEN_BRIGHT = [value * BRIGHTNESS for value in GREEN]

# Define animation objects
RainbowChase_Larson = RainbowChase(PIXELS, speed=0.07, size=50, spacing=3)
RainbowSparkle_Larson = RainbowSparkle(PIXELS, speed=0.03, period=5, background_brightness=0.0)
Rainbow_Larson = RainbowComet(PIXELS, bounce=True, speed=0.03, tail_length=NUM_PIXELS // 2)
LARSON_BLUE = Comet(PIXELS, bounce=True, speed=0.03, tail_length=NUM_PIXELS, color=BLUE_BRIGHT, reverse=True)
LARSON_RED = Comet(PIXELS, bounce=True, speed=0.03, tail_length=NUM_PIXELS, color=RED_BRIGHT, reverse=False)
pulse = Pulse(PIXELS, speed=0.05, color=BLUE_BRIGHT, period=3)
sparkle = Sparkle(PIXELS, speed=0.2, color=RED_BRIGHT, num_sparkles=10)

# Initialize audio components
audio = audiobusio.I2SOut(board.I2S_BIT_CLOCK, board.I2S_WORD_SELECT, board.I2S_DATA)
mixer = audiomixer.Mixer(
    voice_count=1,
    sample_rate=22050,
    channel_count=1,
    bits_per_sample=16,
    samples_signed=True,
    buffer_size=32768,
)
mixer.voice[0].level = 1
audio.play(mixer)


def play_snd(snd_list, led_color):
    sound_file = open(random.choice(snd_list), "rb")
    audio_stream = audiomp3.MP3Decoder(sound_file)
    mixer.voice[0].play(audio_stream, loop=False)
    PIXELS.fill(led_color)
    PIXELS.show()
    while mixer.playing:
        pass  # Wait for audio to finish playing
    PIXELS.fill(BLACK)
    PIXELS.show()


# Main loop
while True:
    if not naughty_button.value:
        play_snd(naughty_snd, RED_BRIGHT)
        pass
    elif not nice_button.value:
        play_snd(nice_snd, GREEN_BRIGHT)
        pass
    else:
        LARSON_BLUE.animate()
