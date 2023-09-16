# SPDX-FileCopyrightText: 2022 Matt Land
#
# SPDX-License-Identifier: MIT
"""
`adafruit_imageload.displayio_types`
====================================================

This is a utility file for type aliases.
https://mypy.readthedocs.io/en/stable/kinds_of_types.html#type-aliases
Type aliases contain compound declarations (used many places in the project) with a single
definition readable by humans.

* Author(s): Matt Land

"""
try:
    from typing import Callable
    from displayio import Palette, Bitmap

    PaletteConstructor = Callable[[int], Palette]
    BitmapConstructor = Callable[[int, int, int], Bitmap]
except ImportError:
    pass

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_ImageLoad.git"
