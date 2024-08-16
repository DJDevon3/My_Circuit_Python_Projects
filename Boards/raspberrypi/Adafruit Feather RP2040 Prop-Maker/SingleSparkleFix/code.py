
import board
from digitalio import DigitalInOut, Direction
import neopixel
from adafruit_led_animation.animation.sparkle import Sparkle
from adafruit_led_animation.sequence import AnimationSequence
from adafruit_led_animation.color import AMBER, JADE

# Enable external power pin
external_power = DigitalInOut(board.EXTERNAL_POWER)
external_power.direction = Direction.OUTPUT
external_power.value = True

# Initialize LED animations
PIXEL_PIN = board.EXTERNAL_NEOPIXELS
NUM_PIXELS = 100
ANIMATION_NEXT_DELAY = 0.01  # can be a float (0.01)
AUTO_WRITE = False
ORDER = neopixel.GRB
led_strip = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, brightness=0.5, pixel_order=ORDER)
sparkle = Sparkle(led_strip, speed=0.05, color=JADE, num_sparkles=1)

animations = AnimationSequence(
    sparkle,
    auto_clear=True,
)

while True:
    animations.animate()
