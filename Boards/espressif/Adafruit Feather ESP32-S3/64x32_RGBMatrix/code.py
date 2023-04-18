# SPDX-FileCopyrightText: 2022 DJDevon3 for Adafruit Industries
#
# SPDX-License-Identifier: MIT
# Used with Adafruit Feather ESP32-S3
# Coded for Circuit Python & 8.0.0-beta.1 libraries

import time
from math import sin
import board
import displayio
import rgbmatrix
import framebufferio
import adafruit_imageload
import terminalio
from adafruit_display_text.label import Label


displayio.release_displays()
matrix = rgbmatrix.RGBMatrix(
    width=64, height=32, bit_depth=6,
    rgb_pins=[board.D6, board.D5, board.D9, board.D11, board.D10, board.D12],
    addr_pins=[board.A5, board.A4, board.A3, board.A2],
    clock_pin=board.D13, latch_pin=board.RX, output_enable_pin=board.TX,
    doublebuffer=True)

# Associate the RGB matrix with a Display so we can use displayio
display = framebufferio.FramebufferDisplay(matrix, auto_refresh=False)

# Quick Colors for Labels
text_black = 0x000000
text_blue = 0x0000FF
text_cyan = 0x00FFFF
text_gray = 0x8B8B8B
text_green = 0x00FF00
text_lightblue = 0x90C7FF
text_magenta = 0xFF00FF
text_orange = 0xFFA500
text_purple = 0x800080
text_red = 0xFF0000
text_white = 0xFFFFFF
text_yellow = 0xFFFF00

g = displayio.Group()
b, p = adafruit_imageload.load("images/Adafruit_32px_RGB_Matrix_Logo.bmp")
t = displayio.TileGrid(b, pixel_shader=p)
t.x = 20
g.append(t)

l = Label(text="Adafruit\nFeather ESP32-S3", font=terminalio.FONT, color=text_magenta, line_spacing=1.0)
g.append(l)

display.show(g)

target_fps = 10
ft = 1/target_fps
now = t0 = time.monotonic_ns()
deadline = t0 + ft

p = 1
q = 17
while True:
    tm = (now - t0) * 1e-9
    x = l.x - 1
    if x < -100:
        x = 63
    y =  round(12 + sin(tm / p) * 6)
    l.x = x
    l.y = y
    display.refresh(target_frames_per_second=target_fps, minimum_frames_per_second=0)
    while True:
        now = time.monotonic_ns()
        if now > deadline:
            break
        time.sleep((deadline - now) * 1e-9)
    deadline += ft
