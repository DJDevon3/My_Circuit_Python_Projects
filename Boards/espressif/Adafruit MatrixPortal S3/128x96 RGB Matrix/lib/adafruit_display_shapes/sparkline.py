# SPDX-FileCopyrightText: 2020 Kevin Matocha
#
# SPDX-License-Identifier: MIT

# class of sparklines in CircuitPython

# See the bottom for a code example using the `sparkline` Class.

# # File: display_shapes_sparkline.py
# A sparkline is a scrolling line graph, where any values added to sparkline using `
# add_value` are plotted.
#
# The `sparkline` class creates an element suitable for adding to the display using
# `display.show(mySparkline)`
# or adding to a `displayio.Group` to be displayed.
#
# When creating the sparkline, identify the number of `max_items` that will be
# included in the graph. When additional elements are added to the sparkline and
# the number of items has exceeded max_items, any excess values are removed from
# the left of the graph, and new values are added to the right.
"""
`sparkline`
================================================================================

Various common shapes for use with displayio - Sparkline!


* Author(s): Kevin Matocha

Implementation Notes
--------------------

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""

try:
    from typing import Optional, List
except ImportError:
    pass
from adafruit_display_shapes.multisparkline import MultiSparkline


class Sparkline(MultiSparkline):
    """A sparkline graph.

    :param int width: Width of the sparkline graph in pixels
    :param int height: Height of the sparkline graph in pixels
    :param int max_items: Maximum number of values housed in the sparkline
    :param bool dyn_xpitch: (Optional) Dynamically change xpitch (True)
    :param int|None y_min: Lower range for the y-axis.  Set to None for autorange.
    :param int|None y_max: Upper range for the y-axis.  Set to None for autorange.
    :param int x: X-position on the screen, in pixels
    :param int y: Y-position on the screen, in pixels
    :param int color: Line color, the default value is 0xFFFFFF (WHITE)

    Note: If dyn_xpitch is True (default), the sparkline will allways span
    the complete width. Otherwise, the sparkline will grow when you
    add values. Once the line has reached the full width, the sparkline
    will scroll to the left.
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        width: int,
        height: int,
        max_items: int,
        dyn_xpitch: Optional[bool] = True,  # True = dynamic pitch size
        y_min: Optional[int] = None,  # None = autoscaling
        y_max: Optional[int] = None,  # None = autoscaling
        x: int = 0,
        y: int = 0,
        color: int = 0xFFFFFF,  # line color, default is WHITE
    ) -> None:
        super().__init__(
            width, height, max_items, [color], dyn_xpitch, [y_min], [y_max], x, y
        )

    # pylint: enable=too-many-arguments

    def add_value(self, value: float, update: bool = True) -> None:
        """Add a value to the sparkline.

        :param float value: The value to be added to the sparkline
        :param bool update: trigger recreation of primitives

        Note: when adding multiple values it is more efficient to call
        this method with parameter 'update=False' and then to manually
        call the update()-method
        """

        self.add_values([value], update)

    def update(self) -> None:
        """Update the drawing of the sparkline."""

        self.update_line(0)

    def values(self) -> List[float]:
        """Returns the values displayed on the sparkline."""

        return self.values_of(0)

    @property
    def y_top(self) -> float:
        """
        :return: The actual maximum value of the vertical scale, will be updated if autorange
        """
        return self.y_tops[0]

    @property
    def y_bottom(self) -> float:
        """
        :return: The actual minimum value of the vertical scale, will be updated if autorange
        """
        return self.y_bottoms[0]
