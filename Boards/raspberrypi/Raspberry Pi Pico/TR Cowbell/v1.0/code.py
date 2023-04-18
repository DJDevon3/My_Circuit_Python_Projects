# DJDevon3 TR-Cowbell Hardware Test
# Based on PicoStepSeq by @todbot Tod Kurt
# https://github.com/todbot/picostepseq/

import time
import board
import busio
import digitalio
import rotaryio
import adafruit_debouncer
from adafruit_mcp230xx.mcp23017 import MCP23017
from digitalio import Direction, Pull

# Initialize MCP23017
i2c = busio.I2C(board.GP21, board.GP20)
i2c2 = busio.I2C(board.GP27, board.GP26)
mcp = MCP23017(i2c)  # Switches 1-8
mcp2 = MCP23017(i2c2)  # Switches 9-16
# Change I2C address if you set any of the A0, A1, A2
# mcp = MCP23017(i2c, address=0x21)  # MCP23017 0x21 is w/ A0 set

# Acts just like digitalio.DigitalInOut class instance
# Pins not in order from the chip which is fine
# because you can remap them here in software anyway
led01 = mcp.get_pin(8)
led02 = mcp.get_pin(10)
led03 = mcp.get_pin(12)
led04 = mcp.get_pin(14)
led05 = mcp.get_pin(7)
led06 = mcp.get_pin(5)
led07 = mcp.get_pin(3)
led08 = mcp.get_pin(1)
led09 = mcp2.get_pin(8)
led10 = mcp2.get_pin(10)
led11 = mcp2.get_pin(12)
led12 = mcp2.get_pin(14)
led13 = mcp2.get_pin(7)
led14 = mcp2.get_pin(5)
led15 = mcp2.get_pin(3)
led16 = mcp2.get_pin(1)

# As long as have all pins wired to MCP GPIO
# you can correct pinouts in software.
sw01 = mcp.get_pin(9)
sw02 = mcp.get_pin(11)
sw03 = mcp.get_pin(13)
sw04 = mcp.get_pin(15)
sw05 = mcp.get_pin(6)
sw06 = mcp.get_pin(4)
sw07 = mcp.get_pin(2)
sw08 = mcp.get_pin(0)
sw09 = mcp2.get_pin(9)
sw10 = mcp2.get_pin(11)
sw11 = mcp2.get_pin(13)
sw12 = mcp2.get_pin(15)
sw13 = mcp2.get_pin(6)
sw14 = mcp2.get_pin(4)
sw15 = mcp2.get_pin(2)
sw16 = mcp2.get_pin(0)

led_pins = [led01, led02, led03, led04,
            led05, led06, led07, led08,
            led09, led10, led11, led12,
            led13, led14, led15, led16]
            
led_names = ["LED 1","LED 2","LED 3","LED 4",
            "LED 5","LED 6","LED 7","LED 8",
            "LED 9","LED 10","LED 11","LED 12",
            "LED 13","LED 14","LED 15","LED 16"]

key_pins = [sw01, sw02, sw03, sw04,
            sw05, sw06, sw07, sw08,
            sw09, sw10, sw11, sw12,
            sw13, sw14, sw15, sw16]
            
key_names = ["Switch 1","Switch 2","Switch 3","Switch 4",
            "Switch 5","Switch 6","Switch 7","Switch 8",
            "Switch 9","Switch 10","Switch 11","Switch 12",
            "Switch 13","Switch 14","Switch 15","Switch 16"]

while True:
    for key, kname, led, lname in zip(key_pins, key_names, led_pins, led_names):
        key.switch_to_output(value=True)
        led.switch_to_output(value=True)
        print(f'Key: {key} LED: {led} Key Name: {kname} LED Name: {lname} Key Fell')
        time.sleep(.125)
        key.switch_to_output(value=False)
        led.switch_to_output(value=False)
        print(f'Key: {key} LED: {led} Key Name: {kname} LED Name: {lname} Key Rose')
        time.sleep(.125)

