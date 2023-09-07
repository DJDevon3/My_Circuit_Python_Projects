# SPDX-FileCopyrightText: 2019 Limor Fried for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`circle`
================================================================================

Various common shapes for use with displayio - Circle shape!


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

from adafruit_display_shapes.roundrect import RoundRect

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_Display_Shapes.git"


class Circle(RoundRect):
    # pylint: disable=too-few-public-methods, invalid-name
    """A circle.

    :param int x0: The x-position of the center.
    :param int y0: The y-position of the center.
    :param int r: The radius of the circle.
    :param int|None fill: The color to fill the circle. Can be a hex value for a color or
                 ``None`` for transparent.
    :param int|None outline: The outline of the circle. Can be a hex value for a color or
                 ``None`` for no outline.
    :param int stroke: Used for the outline. Will not change the radius.

    """

    def __init__(
        self,
        x0: int,
        y0: int,
        r: int,
        *,
        fill: Optional[int] = None,
        outline: Optional[int] = None,
        stroke: int = 1,
    ) -> None:
        super().__init__(
            x0 - r,
            y0 - r,
            2 * r + 1,
            2 * r + 1,
            r,
            fill=fill,
            outline=outline,
            stroke=stroke,
        )
        self.r = r

    @property
    def x0(self) -> int:
        """The x-position of the center of the circle."""
        return self.x + self.r

    @property
    def y0(self) -> int:
        """The y-position of the center of the circle."""
        return self.y + self.r

    @x0.setter
    def x0(self, x0: int) -> None:
        self.x = x0 - self.r

    @y0.setter
    def y0(self, y0: int) -> None:
        self.y = y0 - self.r
