# SPDX-FileCopyrightText: 2018 Scott Shawcroft for Adafruit Industries
# SPDX-FileCopyrightText: 2022-2023 Melissa LeBlanc-Williams
#
# SPDX-License-Identifier: MIT

"""
`adafruit_imageload.bmp.truecolor`
====================================================

Load pixel colors into a bitmap from an truecolor BMP and return the correct colorconverter.

* Author(s): Melissa LeBlanc-Williams

"""

import sys

try:
    from typing import Union, Optional, Tuple
    from io import BufferedReader
    from ..displayio_types import BitmapConstructor
except ImportError:
    pass

from displayio import ColorConverter, Colorspace, Bitmap

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_ImageLoad.git"

bitfield_colorspaces = (
    {  # 16-bit RGB555
        "mask_values": (0x00007C00, 0x000003E0, 0x0000001F),
        "color_space": Colorspace.RGB555,
    },
    {  # 16-bit RGB565
        "mask_values": (0x0000F800, 0x000007E0, 0x0000001F),
        "color_space": Colorspace.RGB565,
    },
    {  # 24 or 32-bit RGB888 (Alpha ignored for 32-bit)
        "mask_values": (0x0000FF00, 0x00FF0000, 0xFF000000),
        "color_space": Colorspace.RGB888,
    },
)


def bitfield_format(bitfield_mask):
    """Returns the colorspace for the given bitfield mask"""
    mask = (bitfield_mask["red"], bitfield_mask["green"], bitfield_mask["blue"])
    for colorspace in bitfield_colorspaces:
        if colorspace["mask_values"] == mask:
            return colorspace["color_space"]
    return None


def load(
    file: BufferedReader,
    width: int,
    height: int,
    data_start: int,
    color_depth: int,
    bitfield_masks: Union[dict, None],
    *,
    bitmap: Optional[BitmapConstructor] = None,
) -> Tuple[Optional[Bitmap], Optional[ColorConverter]]:
    """Loads truecolor bitmap data into bitmap and palette objects. Due to the 16-bit limit
    that the bitmap object can hold, colors will be converted to 16-bit RGB565 values.

    :param file file: The open bmp file
    :param int width: Image width in pixels
    :param int height: Image height in pixels
    :param int data_start: Byte location where the data starts (after headers)
    :param int color_depth: Number of bits used to store a value
    :param dict bitfield_masks: The bitfield masks for each color if using bitfield compression
    :param BitmapConstructor bitmap: a function that returns a displayio.Bitmap
    """
    # pylint: disable=too-many-arguments,too-many-locals,too-many-branches
    converter_obj = None
    bitmap_obj = None
    if bitmap:
        # Set up a ColorConverter object and set appropriate colorspace
        # to convert from based on the color depth
        input_colorspace = Colorspace.RGB888
        if bitfield_masks is not None:
            colorspace = bitfield_format(bitfield_masks)
            if colorspace is not None:
                input_colorspace = colorspace
            else:
                raise NotImplementedError("Bitfield mask not supported")
        elif color_depth == 16:
            input_colorspace = Colorspace.RGB555
        converter_obj = ColorConverter(input_colorspace=input_colorspace)
        if sys.maxsize > 1073741823:
            # pylint: disable=import-outside-toplevel, relative-beyond-top-level
            from .negative_height_check import negative_height_check

            # convert unsigned int to signed int when height is negative
            height = negative_height_check(height)
        bitmap_obj = Bitmap(width, abs(height), 65535)
        file.seek(data_start)
        line_size = width * (color_depth // 8)
        # Set the seek direction based on whether the height value is negative or positive
        if height > 0:
            range1 = height - 1
            range2 = -1
            range3 = -1
        else:
            range1 = 0
            range2 = abs(height)
            range3 = 1
        chunk = bytearray(line_size)
        for y in range(range1, range2, range3):
            file.readinto(chunk)
            bytes_per_pixel = color_depth // 8
            offset = y * width

            for x in range(width):
                i = x * bytes_per_pixel
                if bitfield_masks is not None:
                    color = 0
                    for byte in range(bytes_per_pixel):
                        color |= chunk[i + byte] << (8 * byte)
                    mask = (
                        bitfield_masks["red"]
                        | bitfield_masks["green"]
                        | bitfield_masks["blue"]
                    )
                    if color_depth in (24, 32):
                        mask = mask >> 8
                    pixel = color & mask
                else:
                    if color_depth == 16:
                        pixel = chunk[i] | chunk[i + 1] << 8
                    else:
                        pixel = chunk[i + 2] << 16 | chunk[i + 1] << 8 | chunk[i]
                bitmap_obj[offset + x] = converter_obj.convert(pixel)

    return bitmap_obj, ColorConverter(input_colorspace=Colorspace.RGB565)
