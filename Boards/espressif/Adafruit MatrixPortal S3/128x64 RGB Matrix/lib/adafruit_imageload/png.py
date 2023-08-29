# SPDX-FileCopyrightText: 2022 Radomir Dopieralski
# SPDX-FileCopyrightText: 2023 Matt Land
#
# SPDX-License-Identifier: MIT

"""
`adafruit_imageload.png`
====================================================

Load pixel values (indices or colors) into a bitmap and colors into a palette
from a PNG file.

* Author(s): Radomir Dopieralski, Matt Land

"""

try:
    from io import BufferedReader
    from typing import Optional, Tuple
    from displayio import Palette, Bitmap
    from .displayio_types import PaletteConstructor, BitmapConstructor
except ImportError:
    pass

import struct
import zlib

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_ImageLoad.git"


def load(
    file: BufferedReader,
    *,
    bitmap: BitmapConstructor,
    palette: Optional[PaletteConstructor] = None
) -> Tuple[Bitmap, Optional[Palette]]:
    """
    Loads a PNG image from the open ``file``.
    Only supports indexed color images.

    Returns tuple of bitmap object and palette object.

    :param io.BufferedReader file: Open file handle or compatible (like `io.BytesIO`)
      with the data of a PNG file.
    :param object bitmap: Type to store bitmap data. Must have API similar to
      `displayio.Bitmap`.
    :param object palette: Type to store the palette. Must have API similar to
      `displayio.Palette`. Will be skipped if None.
    """
    # pylint: disable=too-many-locals,too-many-branches
    header = file.read(8)
    if header != b"\x89PNG\r\n\x1a\n":
        raise ValueError("Not a PNG file")
    del header
    data = bytearray()
    pal = None
    mode = None
    depth = 0
    width = 0
    height = 0
    while True:
        size, chunk = struct.unpack(">I4s", file.read(8))
        if chunk == b"IHDR":
            (
                width,
                height,
                depth,
                mode,
                compression,
                filters,
                interlaced,
            ) = struct.unpack(">IIBBBBB", file.read(13))
            if interlaced:
                raise NotImplementedError("Interlaced images unsupported")
            # compression and filters must be 0 with current spec
            assert compression == 0
            assert filters == 0
        elif chunk == b"PLTE":
            if palette is None:
                file.seek(size, 1)
            else:
                if mode != 3:
                    raise NotImplementedError("Palette in non-indexed image")
                pal_size = size // 3
                pal = palette(pal_size)
                for i in range(pal_size):
                    pal[i] = file.read(3)
        elif chunk == b"IDAT":
            data.extend(file.read(size))
        elif chunk == b"IEND":
            break
        else:
            file.seek(size, 1)  # skip unknown chunks
        file.seek(4, 1)  # skip CRC
    data_bytes = zlib.decompress(data)
    bmp = bitmap(width, height, 1 << depth)
    scanline = (width * depth + 7) // 8
    mem = memoryview(bmp)
    for y in range(height):
        dst = y * scanline
        src = y * (scanline + 1) + 1
        filter_ = data_bytes[src - 1]
        if filter_ == 0:
            mem[dst : dst + scanline] = data_bytes[src : src + scanline]
        else:
            raise NotImplementedError("Filters not supported")
    return bmp, pal
