import time
import board
import digitalio
import math
import pwmio
import re
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

ble = BLERadio()
uart_service = UARTService()
advertisement = ProvideServicesAdvertisement(uart_service)

def PWM_RGB (rcycle, gcycle, bcycle):  # (0-255) scale
    RED_LED.duty_cycle = 65535-int(rcycle/255*65535)
    GREEN_LED.duty_cycle = 65535-int(gcycle/255*65535)
    BLUE_LED.duty_cycle = 65535-int(bcycle/255*65535)

def rainbow_cycle(delay):
    for i in range(255):
        pixel_index = (i * 256)
        pixels[i] = colorwheel(pixel_index & 255)
        pixels.show()
        time.sleep(delay)

def solid(new_color):
    pixels.fill(new_color)
    pixels.show()

def map_value(value, in_min, in_max, out_min, out_max):
    out_range = out_max - out_min
    in_range = in_max - in_min
    return out_min + out_range * ((value - in_min) / in_range)

def constrain(value, floor, ceiling):
    return max(floor, min(value, ceiling))

def change_speed(mod, old_speed):
    new_speed = constrain(old_speed + mod, 1.0, 10.0)
    return(new_speed, map_value(new_speed, 10.0, 0.0, 0.01, 0.3))

def animate(pause, top):
    # Determine animation based on mode
    if mode == 0:
        top = audio_meter(top)
    elif mode == 1:
        rainbow_cycle(0.001)
    elif mode == 2:
        larsen(pause)
    elif mode == 3:
        solid(user_color)
    return top

# User input vars
mode = 0 # 0=audio, 1=rainbow, 2=larsen_scanner, 3=solid
#led.color = (255,50,0)  # Set to orange by default
user_color = (127,0,0)
speed = 6.0
wait = 0.097

while True:
    PWM_RGB(255,50,0)  # Set to orange by default
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
                print(user_color[0])
                PWM_RGB(user_color[0],user_color[1],user_color[2])


            # Received ButtonPacket
            elif isinstance(packet, ButtonPacket):
                if packet.pressed:
                    if packet.button == ButtonPacket.UP:
                        speed, wait = change_speed(1, speed)
                    elif packet.button == ButtonPacket.DOWN:
                        speed, wait = change_speed(-1, speed)
                    elif packet.button == ButtonPacket.BUTTON_1:
                        mode = 0
                    elif packet.button == ButtonPacket.BUTTON_2:
                        mode = 1
                    elif packet.button == ButtonPacket.BUTTON_3:
                        mode = 2
                    elif packet.button == ButtonPacket.BUTTON_4:
                        mode = 3

        # Animate while connected
        ble_led.value = True
        time.sleep(1)
