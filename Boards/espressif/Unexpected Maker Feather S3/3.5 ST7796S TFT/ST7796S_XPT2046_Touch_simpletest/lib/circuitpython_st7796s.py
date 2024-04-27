# SPDX-FileCopyrightText: 2023 DJDevon3 with OpenAI ChatGPT 3.5
# SPDX-License-Identifier: MIT
# Circuit Python Driver for ST7796S display
# https://help.openai.com/en/articles/6825453-chatgpt-release-notes
# https://chat.openai.com/share/22db9572-8ad6-4dfc-8b97-43f60afc2ef3

try:
    # used for typing only
    from typing import Any
except ImportError:
    pass

# Support both 8.x.x and 9.x.x. Change when 8.x.x is discontinued as a stable release.
try:
    from fourwire import FourWire
    from busdisplay import BusDisplay
except ImportError:
    from displayio import FourWire
    from displayio import Display as BusDisplay

# Landscape Mode
_INIT_SEQUENCE = bytearray(
    b"\x01\x80\x01"  # Software reset and Delay 150ms
    b"\x11\x80\x01"  # Sleep out and Delay 500ms
    b"\x3A\x81\x55\x0A"  # Set color mode to 16 bits per pixel and Delay 10ms
    b"\x29\x80\x01"  # Display on and Delay 500ms
)


# pylint: disable=too-few-public-methods
class ST7796S(BusDisplay):
    """ST7796S display driver

    :param FourWire bus: bus that the display is connected to
    :param bool portrait: (Optional) Portrait or Landscape mode (default=False)
    :param bool invert: (Optional) Invert the colors (default=False)
    """

    def __init__(
        self, bus: FourWire, *, portrait: bool = False, invert: bool = False, **kwargs: Any
    ):
        init_sequence = _INIT_SEQUENCE
        if portrait:
            init_sequence += (
                b"\x36\x01\x48"  # _MADCTL for portrait mode
            )
        else:
            init_sequence += (
                b"\x36\x01\x28"  # _MADCTL for landscape mode
            )
        if invert:
            init_sequence += b"\x21\x00"  # _INVON inverted color
        super().__init__(bus, init_sequence, **kwargs)
