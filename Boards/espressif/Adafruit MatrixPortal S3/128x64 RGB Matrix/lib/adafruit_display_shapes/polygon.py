# SPDX-FileCopyrightText: 2019 Limor Fried for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`polygon`
================================================================================

Various common shapes for use with displayio - Polygon shape!


* Author(s): Melissa LeBlanc-Williams

Implementation Notes
--------------------

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""

try:
    from typing import Optional, List, Tuple
except ImportError:
    pass

import displayio

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_Display_Shapes.git"


class Polygon(displayio.TileGrid):
    """A polygon.

    :param list points: A list of (x, y) tuples of the points
    :param int|None outline: The outline of the polygon. Can be a hex value for a color or
                    ``None`` for no outline.
    :param bool close: (Optional) Wether to connect first and last point. (True)
    :param int colors: (Optional) Number of colors to use. Most polygons would use two, one for
                    outline and one for fill. If you're not filling your polygon, set this to 1
                    for smaller memory footprint. (2)
    """

    _OUTLINE = 1
    _FILL = 2

    def __init__(
        self,
        points: List[Tuple[int, int]],
        *,
        outline: Optional[int] = None,
        close: Optional[bool] = True,
        colors: Optional[int] = 2,
    ) -> None:
        (x_s, y_s) = zip(*points)

        x_offset = min(x_s)
        y_offset = min(y_s)

        # Find the largest and smallest X values to figure out width for bitmap
        width = max(x_s) - min(x_s) + 1
        height = max(y_s) - min(y_s) + 1

        self._palette = displayio.Palette(colors + 1)
        self._palette.make_transparent(0)
        self._bitmap = displayio.Bitmap(width, height, colors + 1)

        shifted = [(x - x_offset, y - y_offset) for (x, y) in points]

        if outline is not None:
            self.outline = outline
            self.draw(self._bitmap, shifted, self._OUTLINE, close)

        super().__init__(
            self._bitmap, pixel_shader=self._palette, x=x_offset, y=y_offset
        )

    @staticmethod
    def draw(
        bitmap: displayio.Bitmap,
        points: List[Tuple[int, int]],
        color_id: int,
        close: Optional[bool] = True,
    ) -> None:
        """Draw a polygon conecting points on provided bitmap with provided color_id

        :param displayio.Bitmap bitmap: bitmap to draw on
        :param list points: A list of (x, y) tuples of the points
        :param int color_id: Color to draw with
        :param bool close: (Optional) Wether to connect first and last point. (True)
        """

        if close:
            points.append(points[0])

        for index in range(len(points) - 1):
            Polygon._line_on(bitmap, points[index], points[index + 1], color_id)

    # pylint: disable=too-many-arguments
    def _line(
        self,
        x_0: int,
        y_0: int,
        x_1: int,
        y_1: int,
        color: int,
    ) -> None:
        self._line_on(self._bitmap, (x_0, y_0), (x_1, y_1), color)

    # pylint: enable=too-many-arguments

    @staticmethod
    def _safe_draw(
        bitmap: displayio.Bitmap,
        point: Tuple[int, int],
        color: int,
    ) -> None:
        (x, y) = point
        if 0 <= x < bitmap.width and 0 <= y < bitmap.height:
            bitmap[x, y] = color

    # pylint: disable=too-many-branches, too-many-locals
    @staticmethod
    def _line_on(
        bitmap: displayio.Bitmap,
        p_0: Tuple[int, int],
        p_1: Tuple[int, int],
        color: int,
    ) -> None:
        (x_0, y_0) = p_0
        (x_1, y_1) = p_1

        def pt_on(x, y):
            Polygon._safe_draw(bitmap, (x, y), color)

        if x_0 == x_1:
            if y_0 > y_1:
                y_0, y_1 = y_1, y_0
            for _h in range(y_0, y_1 + 1):
                pt_on(x_0, _h)
        elif y_0 == y_1:
            if x_0 > x_1:
                x_0, x_1 = x_1, x_0
            for _w in range(x_0, x_1 + 1):
                pt_on(_w, y_0)
        else:
            steep = abs(y_1 - y_0) > abs(x_1 - x_0)
            if steep:
                x_0, y_0 = y_0, x_0
                x_1, y_1 = y_1, x_1

            if x_0 > x_1:
                x_0, x_1 = x_1, x_0
                y_0, y_1 = y_1, y_0

            d_x = x_1 - x_0
            d_y = abs(y_1 - y_0)

            err = d_x / 2

            if y_0 < y_1:
                ystep = 1
            else:
                ystep = -1

            for x in range(x_0, x_1 + 1):
                if steep:
                    pt_on(y_0, x)
                else:
                    pt_on(x, y_0)
                err -= d_y
                if err < 0:
                    y_0 += ystep
                    err += d_x

    # pylint: enable=too-many-branches, too-many-locals

    @property
    def outline(self) -> Optional[int]:
        """The outline of the polygon. Can be a hex value for a color or
        ``None`` for no outline."""
        return self._palette[self._OUTLINE]

    @outline.setter
    def outline(self, color: Optional[int]) -> None:
        if color is None:
            self._palette[self._OUTLINE] = 0
            self._palette.make_transparent(self._OUTLINE)
        else:
            self._palette[self._OUTLINE] = color
            self._palette.make_opaque(self._OUTLINE)
