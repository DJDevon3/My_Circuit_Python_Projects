import time
import board
from digitalio import DigitalInOut, Direction, Pull
import neopixel

# Enable external power pin
external_power = DigitalInOut(board.EXTERNAL_POWER)
external_power.direction = Direction.OUTPUT
external_power.value = True

# Initialize LED animations
PIXEL_PIN = board.EXTERNAL_NEOPIXELS
NUM_PIXELS = 50
ANIMATION_NEXT_DELAY = 0.01  # can be a float (0.01)
AUTO_WRITE = True
ORDER = neopixel.GRB
led_strip = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, auto_write=AUTO_WRITE, pixel_order=ORDER)

black = (0, 0, 0)
red = (255, 0, 0)
orange = (255, 165, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
violet = (138, 43, 226)

# Main loop
while True:
        for i in range(1, 50):
            led_strip[i] = red
        for i in range(1, 50):
            led_strip[i] = black
        for i in range(1, 50):
            led_strip[-i] = red
        for i in range(1, 50):
            led_strip[-i] = black
        
        for i in range(1, 50):
            led_strip[i] = green
        for i in range(1, 50):
            led_strip[i] = black
        for i in range(1, 50):
            led_strip[-i] = green
        for i in range(1, 50):
            led_strip[-i] = black
            
        for i in range(1, 50):
            led_strip[i] = blue
        for i in range(1, 50):
            led_strip[i] = black
        for i in range(1, 50):
            led_strip[-i] = blue
        for i in range(1, 50):
            led_strip[-i] = black
            
        for i in range(1, 50):
            led_strip[i] = violet
        for i in range(1, 50):
            led_strip[i] = black
        for i in range(1, 50):
            led_strip[-i] = violet
        for i in range(1, 50):
            led_strip[-i] = black
            
        for i in range(1, 50):
            led_strip[i] = orange
        for i in range(1, 50):
            led_strip[i] = black
        for i in range(1, 50):
            led_strip[-i] = orange
        for i in range(1, 50):
            led_strip[-i] = black
            

            

