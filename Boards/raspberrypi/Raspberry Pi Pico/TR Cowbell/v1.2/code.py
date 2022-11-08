# DJDevon3 TR-Cowbell Hardware Test
# 16 Sept 2022 - DJDevon3
# Based on PicoStepSeq by @todbot Tod Kurt
# https://github.com/todbot/picostepseq/
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
mcp = MCP23017(i2c0, address=0x26)
# Initalize MCP Chip 2 Step Switches 8-15
mcp2 = MCP23017(i2c1, address=0x20)

PINS = [0, 1, 2, 3, 4, 5, 6, 7]
PINS2 = [0, 1, 2, 3, 4, 5, 6, 7]
# Neradoc's MCPMatrixScanner
scanner = McpKeysScanner(mcp, PINS)
scanner2 = McpKeysScanner(mcp2, PINS2)
all_scanner = MultiKeypad(scanner, scanner2)

# MCP1 PORT A SWITCHES (0-7)
chip1_port_a_pins = []
for pin in range(0, 8):
    chip1_port_a_pins.append(mcp.get_pin(pin))

# MCP1 PORT B LEDS (8-15)
chip1_port_b_pins = []
for pin in range(8, 16):
    chip1_port_b_pins.append(mcp.get_pin(pin))

# MCP2 PORT A SWITCHES (0-7)
chip2_port_a_pins = []
for pin in range(0, 8):
    chip2_port_a_pins.append(mcp2.get_pin(pin))

# MCP2 PORT B LEDS (8-15)
chip2_port_b_pins = []
for pin in range(8, 16):
    chip2_port_b_pins.append(mcp2.get_pin(pin))

# Combine all pins of same type into 1 list
port_a_pins = chip1_port_a_pins + chip2_port_a_pins
port_b_pins = chip1_port_b_pins + chip2_port_b_pins

# Set all Port A Switch pins to input, with pullups!
for pin in port_a_pins:
    pin.direction = Direction.INPUT
    pin.pull = Pull.UP

# Set all Port B LED pins to output
for pin in port_b_pins:
    pin.direction = Direction.OUTPUT

# midi setup
midi_tx_pin, midi_rx_pin = board.GP16, board.GP17
midi_timeout = 0.01
uart = busio.UART(tx=midi_tx_pin, rx=midi_rx_pin,
                  baudrate=31250, timeout=midi_timeout)

while True:
    for key, led in zip(port_a_pins, port_b_pins):
        led.switch_to_output(value=True)
        led.switch_to_output(value=False)
        time.sleep(.125)

        scanner.update()
        scanner2.update()
        while event := all_scanner.next_event():
            key = event.key_number
            if event.pressed:
                print(f"Key pressed : {key}")
                led.switch_to_output(value=True)
                latched = True
            if event.released & latched:
                combine_led = event.key_number+8  # correct key_number for matching LED
                print(f"Key latched : {key} {combine_led}")
                print(led)
                latched = True
            if event.released:
                print(f"Key released: {key}")
