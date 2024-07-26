# SPDX-FileCopyrightText: 2019 Radomir Dopieralski for Adafruit Industries
# SPDX-FileCopyrightText: 2022-2023 Matt Land
#
# SPDX-License-Identifier: MIT

"""
`adafruit_imageload.gif`
====================================================

Load pixel values (indices or colors) into a bitmap and colors into a palette
from a GIF file.

* Author(s): Radomir Dopieralski, Matt Land

"""

import struct

try:
    from typing import Tuple, Iterator, Optional, List
    from io import BufferedReader
    from displayio import Palette, Bitmap
    from .displayio_types import PaletteConstructor, BitmapConstructor
except ImportError:
    pass

__version__ = "1.19.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_ImageLoad.git"


def load(
    file: BufferedReader,
    *,
    bitmap: BitmapConstructor,
    palette: Optional[PaletteConstructor] = None
) -> Tuple[Bitmap, Optional[Palette]]:
    """Loads a GIF image from the open ``file``.

    Returns tuple of bitmap object and palette object.

    :param io.BufferedReader file: Open file handle or compatible (like `io.BytesIO`)
      with the data of a GIF file.
    :param object bitmap: Type to store bitmap data. Must have API similar to `displayio.Bitmap`.
    :param object palette: Type to store the palette. Must have API similar to
      `displayio.Palette`. Will be skipped if None.
    """
    header = file.read(6)
    if header not in {b"GIF87a", b"GIF89a"}:
        raise ValueError("Not a GIF file")
    width, height, flags, _, _ = struct.unpack(  # pylint: disable=no-member
        "<HHBBB", file.read(7)
    )
    if (flags & 0x80) != 0:
        if not palette:
            raise RuntimeError("palette argument required")
        palette_size = 1 << ((flags & 0x07) + 1)
        palette_obj = palette(palette_size)
        for i in range(palette_size):
            palette_obj[i] = file.read(3)
    else:
        palette_obj = None
    color_bits = ((flags & 0x70) >> 4) + 1
    bitmap_obj = bitmap(width, height, (1 << color_bits) - 1)
    while True:
        block_type = file.read(1)[0]
        if block_type == 0x2C:  # frame
            _read_frame(file, bitmap_obj)
        elif block_type == 0x21:  # extension
            _ = file.read(1)[0]
            # 0x01 = label, 0xfe = comment
            _ = bytes(_read_blockstream(file))
        elif block_type == 0x3B:  # terminator
            break
        else:
            raise ValueError("Bad block type")
    return bitmap_obj, palette_obj


def _read_frame(file: BufferedReader, bitmap: Bitmap) -> None:
    """Read a single frame and apply it to the bitmap."""
    ddx, ddy, width, _, flags = struct.unpack(  # pylint: disable=no-member
        "<HHHHB", file.read(9)
    )
    if (flags & 0x40) != 0:
        raise NotImplementedError("Interlacing not supported")
    if (flags & 0x80) != 0:
        palette_size = 1 << ((flags & 0x07) + 1)
        for _ in range(palette_size):
            _ = file.read(3)
    min_code_size = file.read(1)[0]
    x = 0
    y = 0
    for decoded in lzw_decode(_read_blockstream(file), min_code_size):
        for byte in decoded:
            bitmap[ddx + x, ddy + y] = byte
            x += 1
            if x >= width:
                x = 0
                y += 1


def _read_blockstream(file: BufferedReader) -> Iterator[int]:
    """Read a block from a file."""
    while True:
        size = file.read(1)[0]
        if size == 0:
            break
        for _ in range(size):
            yield file.read(1)[0]


class EndOfData(Exception):
    """Signified end of compressed data."""


class LZWDict:
    """A dictionary of LZW codes."""

    def __init__(self, code_size: int) -> None:
        self.code_size = code_size
        self.clear_code = 1 << code_size
        self.end_code = self.clear_code + 1
        self.codes = []  # type: List[bytes]
        self.last = b""
        self.clear()

    def clear(self) -> None:
        """Reset the dictionary to default codes."""
        self.last = b""
        self.code_len = self.code_size + 1
        self.codes[:] = []

    def decode(self, code: int) -> bytes:
        """Decode a code."""
        if code == self.clear_code:
            self.clear()
            return b""
        if code == self.end_code:
            raise EndOfData()
        if code < self.clear_code:
            value = bytes([code])
        elif code <= len(self.codes) + self.end_code:
            value = self.codes[code - self.end_code - 1]
        else:
            value = self.last + self.last[0:1]
        if self.last:
            self.codes.append(self.last + value[0:1])
        if (
            len(self.codes) + self.end_code + 1 >= 1 << self.code_len
            and self.code_len < 12
        ):
            self.code_len += 1
        self.last = value
        return value


def lzw_decode(data: Iterator[int], code_size: int) -> Iterator[bytes]:
    """Decode LZW-compressed data."""
    dictionary = LZWDict(code_size)
    bit = 0
    try:
        byte = next(data)  # pylint: disable=stop-iteration-return
        try:
            while True:
                code = 0
                for i in range(dictionary.code_len):
                    code |= ((byte >> bit) & 0x01) << i
                    bit += 1
                    if bit >= 8:
                        bit = 0
                        byte = next(data)  # pylint: disable=stop-iteration-return
                yield dictionary.decode(code)
        except EndOfData:
            while True:
                next(data)  # pylint: disable=stop-iteration-return
    except StopIteration:
        pass
