# SPDX-FileCopyrightText: 2018 Scott Shawcroft for Adafruit Industries
# SPDX-FileCopyrightText: 2022-2023 Matt Land
#
# SPDX-License-Identifier: MIT

"""
`adafruit_imageload`
====================================================

Load pixel values (indices or colors) into a bitmap and colors into a palette.

* Author(s): Scott Shawcroft, Matt Land

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
    )
    from io import BufferedReader
    from displayio import Palette, Bitmap
    from .displayio_types import PaletteConstructor, BitmapConstructor
except ImportError:
    pass

__version__ = "1.19.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_ImageLoad.git"


def load(
    file_or_filename: Union[str, BufferedReader],
    *,
    bitmap: Optional[BitmapConstructor] = None,
    palette: Optional[PaletteConstructor] = None
) -> Tuple[Bitmap, Optional[Palette]]:
    """Load pixel values (indices or colors) into a bitmap and colors into a palette.

    bitmap is the desired type. It must take width, height and color_depth in the constructor. It
    must also have a _load_row method to load a row's worth of pixel data.

    palette is the desired palette type. The constructor should take the number of colors and
    support assignment to indices via [].
    """
    if not bitmap or not palette:
        try:
            # use displayio if available
            import displayio

            if not bitmap:
                bitmap = displayio.Bitmap
            if not palette:
                palette = displayio.Palette
        except ModuleNotFoundError:
            # meh, we tried
            pass

    if isinstance(file_or_filename, str):
        open_file = open(file_or_filename, "rb")
    else:
        open_file = file_or_filename

    with open_file as file:
        header = file.read(3)
        file.seek(0)
        if header.startswith(b"BM"):
            from . import bmp

            return bmp.load(file, bitmap=bitmap, palette=palette)
        if header.startswith(b"P"):
            from . import pnm

            return pnm.load(file, header, bitmap=bitmap, palette=palette)
        if header.startswith(b"GIF"):
            if not bitmap:
                raise RuntimeError("bitmap argument required")

            from . import gif

            return gif.load(file, bitmap=bitmap, palette=palette)
        if header.startswith(b"\x89PN"):
            if not bitmap:
                raise RuntimeError("bitmap argument required")
            from . import png

            return png.load(file, bitmap=bitmap, palette=palette)
        raise RuntimeError("Unsupported image format")
