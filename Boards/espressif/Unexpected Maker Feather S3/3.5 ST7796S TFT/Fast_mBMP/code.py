# SPDX-FileCopyrightText: 2023 Smitka
# SPDX-License-Identifier: MIT
# Coded for Circuit Python 8.x 
# Fast mBMP Example

import board
import struct
import time
import displayio
from circuitpython_st7796 import ST7796

displayio.release_displays()
spi = board.SPI()
tft_cs = board.D9
tft_dc = board.D10
tft_rst = board.D12

# 4.0" ST7796S Aliexpress Display
DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 320

display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs, baudrate=75000000)
display = ST7796(display_bus, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, rotation=0)

#display = board.DISPLAY
display.auto_refresh = False

def send_chunks_to_display(file_path, width=DISPLAY_WIDTH, rows = 24):

    chunk_size= 2 * width * rows # 2bytes per pixel - every chunk = row * number of rows to display at once
    chunk = bytearray(chunk_size)
    row_start = 0

    send = display.bus.send
    pack = struct.pack
    mw = memoryview

    send(42, pack(">hh", 0, width-1))

    with open(file_path, "rb") as f:
        read = f.readinto

        while True:
            n = read(chunk)
            if n == 0:
                break
            send(43, pack(">hh", row_start, row_start + rows))
            send(44, mw(chunk)[:n])
            row_start += rows

while True:
    # Bitmaps are in RGB 565 Swapped format
    # converter: https://lvgl.io/tools/imageconverter

    send_chunks_to_display("/images/frame_00_delay-0.bin")
    send_chunks_to_display("/images/frame_01_delay-0.bin")
    send_chunks_to_display("/images/frame_02_delay-0.bin")
    send_chunks_to_display("/images/frame_03_delay-0.bin")
    send_chunks_to_display("/images/frame_04_delay-0.bin")
    send_chunks_to_display("/images/frame_05_delay-0.bin")
    send_chunks_to_display("/images/frame_06_delay-0.bin")
    send_chunks_to_display("/images/frame_07_delay-0.bin")
    send_chunks_to_display("/images/frame_08_delay-0.bin")
    send_chunks_to_display("/images/frame_09_delay-0.bin")
    send_chunks_to_display("/images/frame_10_delay-0.bin")
    send_chunks_to_display("/images/frame_11_delay-0.bin")
    send_chunks_to_display("/images/frame_12_delay-0.bin")
    send_chunks_to_display("/images/frame_13_delay-0.bin")
    send_chunks_to_display("/images/frame_14_delay-0.bin")
    send_chunks_to_display("/images/frame_15_delay-0.bin")
    send_chunks_to_display("/images/frame_16_delay-0.bin")
    send_chunks_to_display("/images/frame_17_delay-0.bin")
    send_chunks_to_display("/images/frame_18_delay-0.bin")
    send_chunks_to_display("/images/frame_19_delay-0.bin")
    send_chunks_to_display("/images/frame_20_delay-0.bin")
    send_chunks_to_display("/images/frame_21_delay-0.bin")
    send_chunks_to_display("/images/frame_22_delay-0.bin")
