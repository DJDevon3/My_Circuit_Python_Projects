# DJDevon3 TR-Cowbell Hardware Test
# 2022/11/09 - Neradoc & DJDevon3
# Based on PicoStepSeq by @todbot Tod Kurt
# https://github.com/todbot/picostepseq/
import asyncio
import time
import board
import busio
from digitalio import Direction, Pull
from supervisor import ticks_ms
from adafruit_mcp230xx.mcp23017 import MCP23017
from mcp23017_scanner import McpKeysScanner
from multi_macropad import MultiKeypad

# Initialize 2 Separate Physical I2C busses
i2c0 = busio.I2C(board.GP13, board.GP12)  # Bus I2C0
i2c1 = busio.I2C(board.GP11, board.GP10)  # Bus I2C1

# Initialize MCP Chip 1 Step Switches 0-7
mcp1 = MCP23017(i2c0, address=0x26)
# Initalize MCP Chip 2 Step Switches 8-15
mcp2 = MCP23017(i2c1, address=0x20)

PINS1 = [0, 1, 2, 3, 4, 5, 6, 7]
PINS2 = [0, 1, 2, 3, 4, 5, 6, 7]

# MCP scanner and multikeypad
scanner1 = McpKeysScanner(mcp1, PINS1)
scanner2 = McpKeysScanner(mcp2, PINS2)
all_scanner = MultiKeypad(scanner1, scanner2)

# LED pins on ports B
mcp1_led_pins = [mcp1.get_pin(pin) for pin in range(8, 16)]
mcp2_led_pins = [mcp2.get_pin(pin) for pin in range(8, 16)]

# all the LED pins organized per MCP chip
led_pins_per_chip = (mcp1_led_pins, mcp2_led_pins)

# ordered list of led coordinates
led_pins = [(a, b) for a in range(2) for b in range(8)]

# Set all LED pins to output
for (m,x) in led_pins:
    led_pins_per_chip[m][x].direction = Direction.OUTPUT

# status of the button latches
latches = [False] * 16
def toggle_latch(mcp, pin):
    print(mcp, pin)
    latches[mcp * 8 + pin] = not latches[mcp * 8 + pin]
def get_latch(mcp, pin):
    return latches[mcp * 8 + pin]

# NOTE: it is assumed that key number x (port A) on MCP number y matches
# the LED numnber x (port B) on the same MCP number y
# if not, a conversion function could be used to translate:
# (key_x, key_y) -> (led_x, led_y)

# midi setup
midi_tx_pin, midi_rx_pin = board.GP16, board.GP17
midi_timeout = 0.01
uart = busio.UART(tx=midi_tx_pin, rx=midi_rx_pin,
                  baudrate=31250, timeout=midi_timeout)

async def blink_the_leds(delay=0.125):
    while True:
        # blink all the LEDs together
        for (x,y) in led_pins:
            if not get_latch(x, y):
                led_pins_per_chip[x][y].value = True
                time.sleep(0.001)
                led_pins_per_chip[x][y].value = False
                await asyncio.sleep(delay)

async def read_buttons():
    while True:
        # scan the buttons
        scanner1.update()
        scanner2.update()
        # treat the events
        while event := all_scanner.next_event():
            mcp_number = event.pad_number
            key_number = event.key_number
            if event.pressed:
                print(f"Key pressed : {mcp_number} / {key_number}")
                # key pressed, find the matching LED
                led_pin = led_pins_per_chip[mcp_number][key_number]
                # invert the latch value (independently of the LED)
                toggle_latch(mcp_number, key_number)
                # change the LED value to match the latch
                led_pin.value = get_latch(mcp_number, key_number)
            # make sure to yield during the reading of the buttons
            await asyncio.sleep(0)
        # slow down the loop a little bit, can be adjusted
        await asyncio.sleep(0.005)

async def main():
    await asyncio.gather(
        asyncio.create_task(blink_the_leds()),
        asyncio.create_task(read_buttons()),
    )

asyncio.run(main())
