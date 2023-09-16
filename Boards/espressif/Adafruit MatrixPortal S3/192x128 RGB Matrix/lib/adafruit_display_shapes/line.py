# SPDX-FileCopyrightText: 2019 Limor Fried for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`line`
================================================================================

Various common shapes for use with displayio - Line shape!


* Author(s): Melissa LeBlanc-Williams

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

from adafruit_display_shapes.polygon import Polygon

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_Display_Shapes.git"


class Line(Polygon):
    # pylint: disable=too-many-arguments,invalid-name, too-few-public-methods
    """A line.

    :param int x0: The x-position of the first vertex.
    :param int y0: The y-position of the first vertex.
    :param int x1: The x-position of the second vertex.
    :param int y1: The y-position of the second vertex.
    :param int color: The color of the line.
    """

    def __init__(
        self,
        x0: int,
        y0: int,
        x1: int,
        y1: int,
        color: int,
    ) -> None:
        super().__init__([(x0, y0), (x1, y1)], outline=color)

    @property
    def color(self) -> Optional[int]:
        """The line color value. Can be a hex value for a color or
        ``None`` for no line color."""
        return self.outline

    @color.setter
    def color(self, color: Optional[int]) -> None:
        self.outline = color
