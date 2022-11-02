# DJDevon3 Dragon Mask Gemma M0
# Controller for 2x 12 pixel rings
import board
import neopixel
from adafruit_led_animation.animation.pulse import Pulse
from adafruit_led_animation.color import RED

pixel_pin = board.D1
pixel_num = 24

pixels = neopixel.NeoPixel(pixel_pin, pixel_num, brightness=0.5, auto_write=False)
pulse = Pulse(pixels, speed=0.1, color=RED, period=3)

while True:
    pulse.animate()
