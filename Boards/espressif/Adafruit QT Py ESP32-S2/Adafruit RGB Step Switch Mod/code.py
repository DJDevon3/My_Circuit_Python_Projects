# RGB Step Switch Mod on Qt Py for Circuit Python 8.0 by DJDevon3
import time
import board
from rainbowio import colorwheel
import adafruit_rgbled


# Pin the Red LED is connected to
RED_LED = board.A2

# Pin the Green LED is connected to
GREEN_LED = board.A1

# Pin the Blue LED is connected to
BLUE_LED = board.A0

# Use inverted PWM for common annode RGB LED
led = adafruit_rgbled.RGBLED(RED_LED, GREEN_LED, BLUE_LED, invert_pwm=True)


def rainbow_cycle(wait):
    for i in range(255):
        i = (i + 1) % 256
        led.color = colorwheel(i)
        time.sleep(wait)


while True:
    """
    led.color = (255, 0, 0)
    time.sleep(1)

    led.color = (0, 255, 0)
    time.sleep(1)

    led.color = (0, 0, 255)
    time.sleep(1)
    """
    # rainbow cycle the RGB LED
    rainbow_cycle(0.005)
