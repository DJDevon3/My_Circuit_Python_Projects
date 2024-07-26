# SPDX-FileCopyrightText: 2018 Scott Shawcroft for Adafruit Industries
# SPDX-FileCopyrightText: 2022-2023 Matt Land
# SPDX-FileCopyrightText: Brooke Storm
# SPDX-FileCopyrightText: Sam McGahan
#
# SPDX-License-Identifier: MIT

"""
`adafruit_imageload.pnm.pbm_binary`
====================================================

Load pixel values (indices or colors) into a bitmap and for an ascii ppm,
return None for pallet.

* Author(s):  Matt Land, Brooke Storm, Sam McGahan

"""
try:
    from typing import Tuple, Optional, Iterator
    from io import BufferedReader
    from displayio import Palette, Bitmap
except ImportError:
    pass

__version__ = "1.19.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_ImageLoad.git"


def load(
    file: BufferedReader,
    width: int,
    height: int,
    bitmap: Bitmap,
    palette: Optional[Palette] = None,
) -> Tuple[Bitmap, Optional[Palette]]:
    """
    Load a P4 'PBM' binary image into the Bitmap
    """
    x = 0
    y = 0
    while True:
        next_byte = file.read(1)
        if not next_byte:
            break  # out of bits
        for bit in iterbits(next_byte):
            bitmap[x, y] = bit
            x += 1
            if x > width - 1:
                y += 1
                x = 0
            if y > height - 1:
                break
    return bitmap, palette


def iterbits(b: bytes) -> Iterator[int]:
    """
    generator to iterate over the bits in a byte (character)
    """
    in_char = reverse(int.from_bytes(b, "little"))
    for i in range(8):
        yield (in_char >> i) & 1


def reverse(b: int) -> int:
    """
    reverse bit order so the iterbits works
    """
    b = (b & 0xF0) >> 4 | (b & 0x0F) << 4
    b = (b & 0xCC) >> 2 | (b & 0x33) << 2
    b = (b & 0xAA) >> 1 | (b & 0x55) << 1
    return b
