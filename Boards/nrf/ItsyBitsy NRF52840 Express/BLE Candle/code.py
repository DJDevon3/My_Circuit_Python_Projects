# SPDX-FileCopyrightText: 2023 DJDevon3 & Ventrue
#
# SPDX-License-Identifier: MIT
# ItsyBitsy NRF52840 Bluefruit Connect Rechargable RGB LED Candle

import time
import board
import digitalio
import pwmio
import random
from rainbowio import colorwheel
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
from adafruit_bluefruit_connect.packet import Packet
from adafruit_bluefruit_connect.color_packet import ColorPacket
from adafruit_bluefruit_connect.button_packet import ButtonPacket

# Prep the status LEDs on the ItsyBitsy (on-board LED)
ble_led = digitalio.DigitalInOut(board.L)
ble_led.direction = digitalio.Direction.OUTPUT

RED_LED = pwmio.PWMOut(board.A0)
GREEN_LED = pwmio.PWMOut(board.A1)
BLUE_LED = pwmio.PWMOut(board.A2)

PINS = (RED_LED, GREEN_LED, BLUE_LED) # List of RGB pins
GAMMA = 1.0  # For perceptually-linear brightness

ble = BLERadio()
uart_service = UARTService()
advertisement = ProvideServicesAdvertisement(uart_service)

# 4-pin RGB LED PWM Control with 0-255 scale
def PWM_Solid(rcycle, gcycle, bcycle):  # (0-255) scale
    PINS[0].duty_cycle = 65535-int(rcycle/255*65535)
    PINS[1].duty_cycle = 65535-int(gcycle/255*65535)
    PINS[2].duty_cycle = 65535-int(bcycle/255*65535)

def pulse(delay):  # delay between steps
    for i in range(0, 255, 1):  # start, stop, steps
        PINS[0].duty_cycle = 65535-int(i/255*65535)
        PINS[1].duty_cycle = 65535-int(i/255*65535)
        PINS[2].duty_cycle = 65535-int(i/255*65535)
        time.sleep(delay)
    for i in range(255, 0, -1):
        PINS[0].duty_cycle = 65535-int(i/255*65535)
        PINS[1].duty_cycle = 65535-int(i/255*65535)
        PINS[2].duty_cycle = 65535-int(i/255*65535)
        time.sleep(delay)

def map_value(value, in_min, in_max, out_min, out_max):
    out_range = out_max - out_min
    in_range = in_max - in_min
    return out_min + out_range * ((value - in_min) / in_range)

def constrain(value, floor, ceiling):
    return max(floor, min(value, ceiling))

random_low = 0
random_high = 255
# Flicker values must be between 0-255 for translation
def yellow_flicker():
    random_low = random.randint(0, 179)
    random_high = random.randint(180, 255)
    rand_sleep = random.uniform(.03, .07)
    random_range = random.randrange(random_low, random_high)
    random_offset = random_range/3
    PINS[0].duty_cycle = 65535-int(random_range/255*65535)
    PINS[1].duty_cycle = 65535-int(random_offset/255*65535)
    PINS[2].duty_cycle = 65535-int(0/255*65535)
    time.sleep(rand_sleep)

def Rainbow_Fade(delay):
    for i in range(0, 255, 1):  # start, stop, steps
        full_range=colorwheel(i)
        blue_fade=full_range&255
        green_fade=(full_range>>8)&255
        red_fade=(full_range>>16)&255
        # print(f"RainbowIO: {full_range} {red_fade} {green_fade} {blue_fade}")
        PINS[0].duty_cycle = 65535-int(red_fade/255*65535)
        time.sleep(delay)
        PINS[1].duty_cycle = 65535-int(green_fade/255*65535)
        time.sleep(delay)
        PINS[2].duty_cycle = 65535-int(blue_fade/255*65535)
        time.sleep(delay)

def change_speed(mod, old_speed):
    new_speed = constrain(old_speed + mod, 1.0, 10.0)
    return (new_speed, map_value(new_speed, 10.0, 0.0, 0.01, 0.3))

def animate():
    if mode == 1:
        yellow_flicker()
    if mode == 2:
        pulse(0.01)
    elif mode == 3:
        Rainbow_Fade(0.005)
    elif mode == 4:
        PWM_Solid(user_color[0],user_color[1],user_color[2])
    return

# User input vars
mode = 1  # 1=flicker, 2=pulse, 3=Rainbow_Fade, 4=solid
# user_color is selected using Adafruit Bluefruit Connect App
user_color = (127, 0, 0)
speed = 6.0
wait = 0.097

while True:
    PWM_Solid(255, 50, 0)  # Set to orange by default
    ble.start_advertising(advertisement)
    while not ble.connected:
        # Animate while disconnected
        ble_led.value = False
        time.sleep(1)

    # While BLE is connected
    while ble.connected:
        if uart_service.in_waiting:
            try:
                packet = Packet.from_stream(uart_service)
            # Ignore malformed packets.
            except ValueError:
                continue

            if isinstance(packet, ColorPacket):
                user_color = packet.color
                PWM_Solid(user_color[0], user_color[1], user_color[2])

            # Received ButtonPacket
            elif isinstance(packet, ButtonPacket):
                if packet.pressed:
                    if packet.button == ButtonPacket.UP:
                        speed, wait = change_speed(1, speed)
                        print(packet.button)
                    elif packet.button == ButtonPacket.DOWN:
                        speed, wait = change_speed(-1, speed)
                        print(packet.button)
                    # Yellow Flicker
                    elif packet.button == ButtonPacket.BUTTON_1:
                        mode = 1
                        print("Mode: ", mode)
                        yellow_flicker()
                    # Pulse
                    elif packet.button == ButtonPacket.BUTTON_2:
                        mode = 2
                        print("Mode: ", mode)
                    # Rainbow_Fade
                    elif packet.button == ButtonPacket.BUTTON_3:
                        mode = 3
                        print("Mode: ", mode)
                    # PWM_Solid
                    elif packet.button == ButtonPacket.BUTTON_4:
                        mode = 4
                        print("Mode: ", mode)

        # Animate while connected
        animate()
        ble_led.value = True
