#FeatherS3 Helper Library
# 2022 Seon Rozenblum, Unexpected Maker
#
# Project home:
#   https://feathers3.io
#

# Import required libraries
import time
import board
from digitalio import DigitalInOut, Direction, Pull
from analogio import AnalogIn

# Init Blink LED
led13 = DigitalInOut(board.LED)
led13.direction = Direction.OUTPUT

# Init LDO2 Pin
ldo2 = DigitalInOut(board.LDO2)
ldo2.direction = Direction.OUTPUT

# Setup the BATTERY voltage sense pin
vbat_voltage = AnalogIn(board.BATTERY)

# Setup the VBUS sense pin
vbus_sense = DigitalInOut(board.VBUS_SENSE)
vbus_sense.direction = Direction.INPUT


# Helper functions

def led_blink():
    """Set the internal LED IO13 to it's inverse state"""
    led13.value = not led13.value

def led_set( state ):
    """Set the internal LED IO13 to this state"""
    led13.value = state

def set_ldo2_power(state):
    """Enable or Disable power to the onboard NeoPixel to either show colour, or to reduce power fro deep sleep."""
    global ldo2
    ldo2.value = state

def get_battery_voltage():
    """Get the approximate battery voltage."""
    global vbat_voltage
    battery_voltage = (vbat_voltage.value * 3.3) / 65536 * 3.9
    return battery_voltage

def get_vbus_present():
    """Detect if VBUS (5V) power source is present"""
    global vbus_sense
    return vbus_sense.value

def rgb_color_wheel(wheel_pos):
    """Color wheel to allow for cycling through the rainbow of RGB colors."""
    wheel_pos = wheel_pos % 255

    if wheel_pos < 85:
        return 255 - wheel_pos * 3, 0, wheel_pos * 3
    elif wheel_pos < 170:
        wheel_pos -= 85
        return 0, wheel_pos * 3, 255 - wheel_pos * 3
    else:
        wheel_pos -= 170
        return wheel_pos * 3, 255 - wheel_pos * 3, 0


