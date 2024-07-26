# SPDX-FileCopyrightText: 2018 Scott Shawcroft for Adafruit Industries
# SPDX-FileCopyrightText: 2022-2023 Matt Land
# SPDX-FileCopyrightText: Brooke Storm
# SPDX-FileCopyrightText: Sam McGahan
#
# SPDX-License-Identifier: MIT

"""
`adafruit_imageload.pnm`
====================================================

Load pixel values (indices or colors) into a bitmap and colors into a palette.

* Author(s): Matt Land, Brooke Storm, Sam McGahan

"""
# pylint: disable=import-outside-toplevel

try:
    from typing import (
        Tuple,
        Iterator,
        Optional,
        List,
        Iterable,
        Union,
        Callable,
    )
    from io import BufferedReader
    from displayio import Palette, Bitmap
    from ..displayio_types import PaletteConstructor, BitmapConstructor
except ImportError:
    pass

__version__ = "1.19.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_ImageLoad.git"


def load(
    file: BufferedReader,
    header: bytes,
    *,
    bitmap: Optional[BitmapConstructor] = None,
    palette: Optional[PaletteConstructor] = None
) -> Tuple[Optional[Bitmap], Optional[Palette]]:
    """
    Scan for netpbm format info, skip over comments, and delegate to a submodule
    to do the actual data loading.
    Formats P1, P4 have two space padded pieces of information: width and height.
    All other formats have three: width, height, and max color value.
    This load function will move the file stream pointer to the start of data in all cases.
    """
    # pylint: disable=too-many-branches
    magic_number = header[:2]
    file.seek(2)
    pnm_header = []  # type: List[int]
    next_value = bytearray()
    while True:
        # We have all we need at length 3 for formats P2, P3, P5, P6
        if len(pnm_header) == 3:
            if magic_number in [b"P2", b"P5"]:
                from . import pgm

                return pgm.load(
                    file,
                    magic_number,
                    pnm_header,
                    bitmap=bitmap,
                    palette=palette,
                )

            if magic_number == b"P3":
                from . import ppm_ascii

                return ppm_ascii.load(
                    file,
                    pnm_header[0],
                    pnm_header[1],
                    bitmap=bitmap,
                    palette=palette,
                )

            if magic_number == b"P6":
                from . import ppm_binary

                return ppm_binary.load(
                    file,
                    pnm_header[0],
                    pnm_header[1],
                    bitmap=bitmap,
                    palette=palette,
                )

        if len(pnm_header) == 2 and magic_number in [b"P1", b"P4"]:
            if not bitmap:
                raise RuntimeError(
                    "A bitmap constructor is required for this type of pnm format file"
                )
            bitmap_obj = bitmap(pnm_header[0], pnm_header[1], 1)
            palette_obj = None
            if palette:
                palette_obj = palette(1)
                palette_obj[0] = b"\xFF\xFF\xFF"
            if magic_number.startswith(b"P1"):
                from . import pbm_ascii

                return pbm_ascii.load(
                    file,
                    pnm_header[0],
                    pnm_header[1],
                    bitmap=bitmap_obj,
                    palette=palette_obj,
                )

            from . import pbm_binary

            return pbm_binary.load(
                file,
                pnm_header[0],
                pnm_header[1],
                bitmap=bitmap_obj,
                palette=palette_obj,
            )

        next_byte = file.read(1)
        if next_byte == b"":
            raise RuntimeError("Unsupported image format {!r}".format(magic_number))
        if next_byte == b"#":  # comment found, seek until a newline or EOF is found
            while file.read(1) not in [b"", b"\n"]:  # EOF or NL
                pass
        elif not next_byte.isdigit():  # boundary found in header data
            if next_value:
                # pull values until space is found
                pnm_header.append(int("".join(["%c" % char for char in next_value])))
                next_value = bytearray()  # reset the byte array
        else:
            next_value += next_byte  # push the digit into the byte array
