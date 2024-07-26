# SPDX-FileCopyrightText: 2018 Scott Shawcroft for Adafruit Industries
# SPDX-FileCopyrightText: 2022-2023 Matt Land
# SPDX-FileCopyrightText: Brooke Storm
# SPDX-FileCopyrightText: Sam McGahan
#
# SPDX-License-Identifier: MIT

"""
`adafruit_imageload.pnm.pgm`
====================================================

Load pixel values (indices or colors) into a bitmap and colors into a palette.

* Author(s): Matt Land, Brooke Storm, Sam McGahan

"""
# pylint: disable=import-outside-toplevel
try:
    from typing import Tuple, Optional, Set, List
    from io import BufferedReader
    from displayio import Palette, Bitmap
    from ...displayio_types import PaletteConstructor, BitmapConstructor
except ImportError:
    pass


def load(
    file: BufferedReader,
    magic_number: bytes,
    header: List[int],
    *,
    bitmap: Optional[BitmapConstructor] = None,
    palette: Optional[PaletteConstructor] = None
) -> Tuple[Optional[Bitmap], Optional[Palette]]:
    """
    Perform the load of Netpbm greyscale images (P2, P5)
    """
    if header[2] > 256:
        raise NotImplementedError("16 bit files are not supported")
    width = header[0]
    height = header[1]

    if magic_number == b"P2":  # To handle ascii PGM files.
        from . import ascii as pgm_ascii

        return pgm_ascii.load(file, width, height, bitmap=bitmap, palette=palette)

    if magic_number == b"P5":  # To handle binary PGM files.
        from . import binary

        return binary.load(file, width, height, bitmap=bitmap, palette=palette)

    raise NotImplementedError("Was not able to send image")
