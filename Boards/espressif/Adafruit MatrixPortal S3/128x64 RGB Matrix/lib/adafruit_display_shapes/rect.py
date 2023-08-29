# SPDX-FileCopyrightText: 2019 Limor Fried for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`rect`
================================================================================

Various common shapes for use with displayio - Rectangle shape!


* Author(s): Limor Fried

Implementation Notes
--------------------

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""

try:
    from typing import Optional
except ImportError:
    pass

import displayio

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_Display_Shapes.git"


class Rect(displayio.TileGrid):
    """A rectangle.

    :param int x: The x-position of the top left corner.
    :param int y: The y-position of the top left corner.
    :param int width: The width of the rectangle.
    :param int height: The height of the rectangle.
    :param int|None fill: The color to fill the rectangle. Can be a hex value for a color or
                    ``None`` for transparent.
    :param int|None outline: The outline of the rectangle. Can be a hex value for a color or
                    ``None`` for no outline.
    :param int stroke: Used for the outline. Will not change the outer bound size set by ``width``
                    and ``height``.

    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        *,
        fill: Optional[int] = None,
        outline: Optional[int] = None,
        stroke: int = 1,
    ) -> None:
        if width <= 0 or height <= 0:
            raise ValueError("Rectangle dimensions must be larger than 0.")

        self._bitmap = displayio.Bitmap(width, height, 2)
        self._palette = displayio.Palette(2)

        if outline is not None:
            self._palette[1] = outline
            for w in range(width):
                for line in range(stroke):
                    self._bitmap[w, line] = 1
                    self._bitmap[w, height - 1 - line] = 1
            for _h in range(height):
                for line in range(stroke):
                    self._bitmap[line, _h] = 1
                    self._bitmap[width - 1 - line, _h] = 1

        if fill is not None:
            self._palette[0] = fill
            self._palette.make_opaque(0)
        else:
            self._palette[0] = 0
            self._palette.make_transparent(0)
        super().__init__(self._bitmap, pixel_shader=self._palette, x=x, y=y)

    @property
    def fill(self) -> Optional[int]:
        """The fill of the rectangle. Can be a hex value for a color or ``None`` for
        transparent."""
        return self._palette[0]

    @fill.setter
    def fill(self, color: Optional[int]) -> None:
        if color is None:
            self._palette[0] = 0
            self._palette.make_transparent(0)
        else:
            self._palette[0] = color
            self._palette.make_opaque(0)

    @property
    def outline(self) -> Optional[int]:
        """The outline of the rectangle. Can be a hex value for a color or ``None``
        for no outline."""
        return self._palette[1]

    @outline.setter
    def outline(self, color: Optional[int]) -> None:
        if color is None:
            self._palette[1] = 0
            self._palette.make_transparent(1)
        else:
            self._palette[1] = color
            self._palette.make_opaque(1)

    @property
    def width(self) -> int:
        """
        :return: the width of the rectangle in pixels
        """
        return self._bitmap.width

    @property
    def height(self) -> int:
        """
        :return: the height of the rectangle in pixels
        """
        return self._bitmap.height
