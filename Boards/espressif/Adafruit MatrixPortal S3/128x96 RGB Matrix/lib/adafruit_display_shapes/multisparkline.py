# SPDX-FileCopyrightText: 2020 Kevin Matocha
#
# SPDX-License-Identifier: MIT

"""
`multisparkline`
================================================================================

Various common shapes for use with displayio - Multiple Sparklines on one chart!


* Author(s): Kevin Matocha, Maciej Sokolowski

Implementation Notes
--------------------

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""

try:
    from typing import Optional, List, TypeVar

    T = TypeVar("T")
except ImportError:
    pass
import displayio
from adafruit_display_shapes.polygon import Polygon


class _CyclicBuffer:
    def __init__(self, size: int, init_value: T) -> None:
        self._buffer = [init_value] * size
        self._start = 0  # between 0 and size-1
        self._end = 0  # between 0 and 2*size-1

    def push(self, value: T) -> None:
        """Pushes value at the end of the buffer.

        :param T value: value to be pushed

        """

        if self.len() == len(self._buffer):
            raise RuntimeError("Trying to push to full buffer")
        self._buffer[self._end % len(self._buffer)] = value
        self._end += 1

    def pop(self) -> T:
        """Pop value from the start of the buffer and returns it."""

        if self.len() == 0:
            raise RuntimeError("Trying to pop from empty buffer")
        result = self._buffer[self._start]
        self._start += 1
        if self._start == len(self._buffer):
            self._start -= len(self._buffer)
            self._end -= len(self._buffer)
        return result

    def len(self) -> int:
        """Returns count of valid data in the buffer."""

        return self._end - self._start

    def clear(self) -> None:
        """Marks all data as invalid."""

        self._start = 0
        self._end = 0

    def values(self) -> List[T]:
        """Returns valid data from the buffer."""

        if self.len() == 0:
            return []
        start = self._start
        end = self._end % len(self._buffer)
        if start < end:
            return self._buffer[start:end]
        return self._buffer[start:] + self._buffer[:end]


class MultiSparkline(displayio.TileGrid):
    """A multiple sparkline graph.

    :param int width: Width of the multisparkline graph in pixels
    :param int height: Height of the multisparkline graph in pixels
    :param int max_items: Maximum number of values housed in each sparkline
    :param bool dyn_xpitch: (Optional) Dynamically change xpitch (True)
    :param list y_mins: Lower range for the y-axis per line.
                        Set each to None for autorange of respective line.
                        Set to None for autorange of all lines.
    :param list y_maxs: Upper range for the y-axis per line.
                        Set each to None for autorange of respective line.
                        Set to None for autorange of all lines.
    :param int x: X-position on the screen, in pixels
    :param int y: Y-position on the screen, in pixels
    :param list colors: Each line color. Number of items in this list determines maximum
                       number of sparklines

    Note: If dyn_xpitch is True (default), each sparkline will allways span
    the complete width. Otherwise, each sparkline will grow when you
    add values. Once the line has reached the full width, each sparkline
    will scroll to the left.
    """

    # pylint: disable=too-many-arguments, too-many-instance-attributes
    def __init__(
        self,
        width: int,
        height: int,
        max_items: int,
        colors: List[int],  # each line color
        dyn_xpitch: Optional[bool] = True,  # True = dynamic pitch size
        y_mins: Optional[List[Optional[int]]] = None,  # None = autoscaling
        y_maxs: Optional[List[Optional[int]]] = None,  # None = autoscaling
        x: int = 0,
        y: int = 0,
    ) -> None:
        # define class instance variables
        self._max_items = max_items  # maximum number of items in the list
        self._lines = len(colors)
        self._buffers = [
            _CyclicBuffer(self._max_items, 0.0) for i in range(self._lines)
        ]  # values per sparkline
        self._points = [
            _CyclicBuffer(self._max_items, (0, 0)) for i in range(self._lines)
        ]  # _points: all points of sparkline
        self.dyn_xpitch = dyn_xpitch
        if not dyn_xpitch:
            self._xpitch = (width - 1) / (self._max_items - 1)
        self.y_mins = (
            [None] * self._lines if y_mins is None else y_mins
        )  # minimum of each y-axis (None: autoscale)
        self.y_maxs = (
            [None] * self._lines if y_maxs is None else y_maxs
        )  # maximum of each y-axis (None: autoscale)
        self.y_bottoms = self.y_mins.copy()
        # y_bottom: The actual minimum value of the vertical scale, will be
        # updated if autorange
        self.y_tops = self.y_maxs.copy()
        # y_top: The actual maximum value of the vertical scale, will be
        # updated if autorange
        self._palette = displayio.Palette(self._lines + 1)
        self._palette.make_transparent(0)
        for i, color in enumerate(colors):
            self._palette[i + 1] = color
        self._bitmap = displayio.Bitmap(width, height, self._lines + 1)

        super().__init__(self._bitmap, pixel_shader=self._palette, x=x, y=y)

    # pylint: enable=too-many-arguments

    def clear_values(self) -> None:
        """Clears _buffer and removes all lines in the group"""
        self._bitmap.fill(0)
        for buffer in self._buffers:
            buffer.clear()

    def add_values(self, values: List[float], update: bool = True) -> None:
        """Add a value to each sparkline.

        :param list values: The values to be added, one per sparkline
        :param bool update: trigger recreation of primitives

        Note: when adding multiple values per sparkline it is more efficient to call
        this method with parameter 'update=False' and then to manually
        call the update()-method
        """

        for i, value in enumerate(values):
            if value is not None:
                top = self.y_tops[i]
                bottom = self.y_bottoms[i]
                if (
                    self._buffers[i].len() >= self._max_items
                ):  # if list is full, remove the first item
                    first = self._buffers[i].pop()
                    # check if boundaries have to be updated
                    if self.y_mins[i] is None and first == bottom:
                        bottom = min(self._buffers[i].values())
                    if self.y_maxs[i] is None and first == self.y_tops[i]:
                        top = max(self._buffers[i].values())
                self._buffers[i].push(value)

                if self.y_mins[i] is None:
                    bottom = value if not bottom else min(value, bottom)
                if self.y_maxs[i] is None:
                    top = value if not top else max(value, top)

                self.y_tops[i] = top
                self.y_bottoms[i] = bottom

                if update:
                    self.update_line(i)

    def _add_point(
        self,
        line: int,
        x: int,
        value: float,
    ) -> None:
        # Guard for y_top and y_bottom being the same
        top = self.y_tops[line]
        bottom = self.y_bottoms[line]
        if top == bottom:
            y = int(0.5 * self.height)
        else:
            y = int((self.height - 1) * (top - value) / (top - bottom))
        self._points[line].push((x, y))

    def _draw(self) -> None:
        self._bitmap.fill(0)
        for i in range(self._lines):
            Polygon.draw(self._bitmap, self._points[i].values(), i + 1, close=False)

    def update_line(self, line: int = None) -> None:
        """Update the drawing of the sparkline.
        param int|None line: Line to update. Set to None for updating all (default).
        """

        if line is None:
            lines = range(self._lines)
        else:
            lines = [line]

        redraw = False
        for a_line in lines:
            # bail out early if we only have a single point
            n_points = self._buffers[a_line].len()
            if n_points < 2:
                continue

            redraw = True
            if self.dyn_xpitch:
                # this is a float, only make int when plotting the line
                xpitch = (self.width - 1) / (n_points - 1)
            else:
                xpitch = self._xpitch

            self._points[a_line].clear()  # remove all points

            for count, value in enumerate(self._buffers[a_line].values()):
                self._add_point(a_line, int(xpitch * count), value)

        if redraw:
            self._draw()

    def values_of(self, line: int) -> List[float]:
        """Returns the values displayed on the sparkline at given index."""

        return self._buffers[line].values()

    @property
    def width(self) -> int:
        """
        :return: the width of the graph in pixels
        """
        return self._bitmap.width

    @property
    def height(self) -> int:
        """
        :return: the height of the graph in pixels
        """
        return self._bitmap.height
