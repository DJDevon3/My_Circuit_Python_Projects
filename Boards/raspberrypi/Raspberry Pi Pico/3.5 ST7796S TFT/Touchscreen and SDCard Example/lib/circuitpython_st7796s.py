# SPDX-FileCopyrightText: 2023 DJDevon3 with OpenAI ChatGPT 3.5
# SPDX-License-Identifier: MIT
# Circuit Python Driver for ST7796S display
# https://help.openai.com/en/articles/6825453-chatgpt-release-notes
# https://chat.openai.com/share/22db9572-8ad6-4dfc-8b97-43f60afc2ef3

import displayio

# Landscape Mode
_INIT_SEQUENCE_L = (
    b"\x01\x80\x01"  # Software reset and Delay 150ms
    b"\x11\x80\x01"  # Sleep out and Delay 500ms
    b"\x3A\x81\x55\x0A"  # Set color mode to 16 bits per pixel and Delay 10ms
    b"\x36\x01\x28"  # Set MADCTL for landscape mode
    b"\x20\x80\x01"  # Turn off inversion and Delay 10ms
    b"\x13\x80\x01"  # Normal display mode on and Delay 10ms
    b"\x29\x80\x01"  # Display on and Delay 500ms
)
# Portrait Mode
_INIT_SEQUENCE_P = (
    b"\x01\x80\x01"  # Software reset and Delay 150ms
    b"\x11\x80\x01"  # Sleep out and Delay 500ms
    b"\x3A\x81\x55\x0A"  # Set color mode to 16 bits per pixel and Delay 10ms
    b"\x36\x01\x48"  # Set MADCTL for portrait mode
    b"\x20\x80\x01"  # Turn off inversion and Delay 10ms
    b"\x13\x80\x01"  # Normal display mode on and Delay 10ms
    b"\x29\x80\x01"  # Display on and Delay 500ms
)


# pylint: disable=too-few-public-methods
class ST7796S(displayio.Display):
    """ST7796S driver"""

    def __init__(self, bus: displayio.FourWire, **kwargs) -> None:
        super().__init__(bus, _INIT_SEQUENCE_L, **kwargs)
