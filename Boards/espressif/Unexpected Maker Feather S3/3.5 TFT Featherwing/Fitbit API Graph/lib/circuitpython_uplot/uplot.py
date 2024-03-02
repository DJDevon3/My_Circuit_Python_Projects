# SPDX-FileCopyrightText: 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT

"""

`uplot`
================================================================================

CircuitPython Plot Class

* Author(s): Jose D. Montoya

Implementation Notes
--------------------

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""

# pylint: disable=too-many-statements, unused-import, no-member
# pylint: disable=unused-import, import-outside-toplevel, undefined-variable
# pylint: disable=attribute-defined-outside-init

try:
    from typing import Union, Tuple
    from typing_extensions import Literal
except ImportError:
    pass
import displayio
import terminalio
from bitmaptools import draw_line
from vectorio import Circle
from ulab import numpy as np


__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/jposada202020/CircuitPython_uplot.git"


class Uplot(displayio.Group):
    """
    Canvas Class to add different elements to the screen.
    The origin point set by ``x`` and ``y`` properties

    :param int x: origin x coordinate
    :param int y: origin y coordinate
    :param int width: plot box width in pixels
    :param int height: plot box height in pixels
    :param int padding: padding for the plot box in all directions
    :param bool show_box: select if the plot box is displayed
    :param int background_color: background color in HEX. Defaults to black ``0x000000``
    :param int box_color: allows to choose the box line color. Defaults to white ''0xFFFFFF``
    :param int tickx_height: x axes tick height in pixels. Defaults to 8.
    :param int ticky_height: y axes tick height in pixels. Defaults to 8.
    :param int scale: scale of the plot. Defaults to 1.

    """

    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 100,
        height: int = 100,
        padding: int = 25,
        show_box: bool = True,
        background_color: int = 0x000000,
        box_color: int = 0xFFFFFF,
        tickx_height: int = 8,
        ticky_height: int = 8,
        scale: int = 1,
    ) -> None:
        if width not in range(50, 481) and scale == 1:
            print("Be sure to verify your values. Defaulting to width=100")
            width = 100
        if height not in range(50, 321) and scale == 1:
            print("Be sure to verify your values. Defaulting to height=100")
            height = 100
        if x + width > 481:
            print(
                "Modify this settings. Some of the graphics will not shown int the screen"
            )
            print("Defaulting to x=0")
            x = 0
        if y + height > 321:
            print(
                "Modify this settings. Some of the graphics will not shown int the screen"
            )
            print("Defaulting to y=0")
            y = 0

        super().__init__(x=x, y=y, scale=scale)

        self._axesparams = "box"

        self._width = width
        self._height = height

        self.padding = padding
        self._newxmin = padding
        self._newxmax = width - padding

        self._newymin = height - padding
        self._newymax = padding

        self._cartesianfirst = True
        self._loggingfirst = True

        self._showtext = False

        self._tickheightx = tickx_height
        self._tickheighty = ticky_height
        self._tickcolor = 0xFFFFFF
        self._showticks = False
        self._tickgrid = False

        self._grid_espace = 2
        self._grid_lenght = 2

        self._barcolor = 0x69FF8F

        self._piecolor = 0x8B77FF

        self._index_colorused = 4

        self._plotbitmap = displayio.Bitmap(width, height, 17)

        if show_box:
            self._drawbox()

        self._plot_palette = displayio.Palette(20)
        self._plot_palette[0] = background_color
        self._plot_palette[1] = box_color
        self._plot_palette[2] = self._tickcolor
        self._plot_palette[3] = self._barcolor
        self._plot_palette[4] = 0x149F14  # Pie Chart color 1
        self._plot_palette[5] = 0x647182  # Pie Chart color 2
        self._plot_palette[6] = 0x7428EF  # Pie Chart color 3
        self._plot_palette[7] = 0x005E99  # Pie Chart color 4
        self._plot_palette[8] = 0x00A76D  # Pie Chart color 5
        self._plot_palette[9] = 0x2C4971  # Pie Chart color 6
        self._plot_palette[10] = 0x64A813
        self._plot_palette[11] = 0x0F4E12
        self._plot_palette[12] = 0xF0075E
        self._plot_palette[13] = 0x123456
        self._plot_palette[14] = 0xFF00FF
        self._plot_palette[15] = 0xFF0000
        self._plot_palette[16] = 0x440044
        self._plot_palette[17] = 0x2222FF
        self._plot_palette[18] = 0x1A50FF
        self._plot_palette[19] = 0xF0FF32

        self.append(
            displayio.TileGrid(
                self._plotbitmap, pixel_shader=self._plot_palette, x=0, y=0
            )
        )

    def axs_params(self, axstype: Literal["box", "cartesian", "line"] = "box") -> None:
        """
        Setting up axs visibility

        :param axstype: argument with the kind of axs you selected

        :return: None

        """
        self._axesparams = axstype

    def _drawbox(self) -> None:
        """
        Draw the plot box

        :return: None

        """

        if self._axesparams == "cartesian":
            draw_box = [True, True, False, False]
        elif self._axesparams == "line":
            draw_box = [False, True, False, False]
        else:
            draw_box = [True, True, True, True]

        if draw_box[0]:
            # y axes line
            draw_line(
                self._plotbitmap,
                self.padding,
                self.padding,
                self.padding,
                self._height - self.padding,
                1,
            )
        if draw_box[1]:
            draw_line(
                self._plotbitmap,
                self.padding,
                self._height - self.padding,
                self._width - self.padding,
                self._height - self.padding,
                1,
            )
        if draw_box[2]:
            draw_line(
                self._plotbitmap,
                self._width - self.padding,
                self.padding,
                self._width - self.padding,
                self._height - self.padding,
                1,
            )
        if draw_box[3]:
            draw_line(
                self._plotbitmap,
                self.padding,
                self.padding,
                self._width - self.padding,
                self.padding,
                1,
            )

    def draw_circle(self, radius: int = 5, x: int = 100, y: int = 100) -> None:
        """
        Draw a circle in the plot area

        :param int radius: circle radius
        :param int x: circles center x coordinate position in pixels, Defaults to 100.
        :param int y: circles center y coordinate position in pixels. Defaults to 100.

        :return: None

        """
        palette = displayio.Palette(1)
        palette[0] = 0xFFFFFF
        self.append(Circle(pixel_shader=palette, radius=radius, x=x, y=y))

    @staticmethod
    def transform(
        oldrangemin: Union[float, int],
        oldrangemax: Union[float, int],
        newrangemin: Union[float, int],
        newrangemax: Union[float, int],
        value: Union[float, int],
    ) -> Union[float, int]:
        """
        This function converts the original value into a new defined value in the new range

        :param int|float oldrangemin: minimum of the original range
        :param int|float oldrangemax: maximum of the original range
        :param int|float newrangemin: minimum of the new range
        :param int|float newrangemax: maximum of the new range
        :param int|float value: value to be converted

        :return int|float: converted value

        """

        return (
            ((value - oldrangemin) * (newrangemax - newrangemin))
            / (oldrangemax - oldrangemin)
        ) + newrangemin

    def _draw_ticks(self, x: int, y: int) -> None:
        """
        Draw ticks in the plot area

        :param int x: x coord
        :param int y: y coord

        :return:None

        """

        ticks = np.array([10, 30, 50, 70, 90])
        subticks = np.array([20, 40, 60, 80])
        ticksxnorm = np.array(self.transform(0, 100, np.min(x), np.max(x), ticks))
        ticksynorm = np.array(self.transform(0, 100, np.min(y), np.max(y), ticks))

        subticksxnorm = np.array(self.transform(0, 100, np.min(x), np.max(x), subticks))
        subticksynorm = np.array(self.transform(0, 100, np.min(y), np.max(y), subticks))

        ticksxrenorm = np.array(
            self.transform(
                np.min(x), np.max(x), self._newxmin, self._newxmax, ticksxnorm
            ),
            dtype=np.int16,
        )
        ticksyrenorm = np.array(
            self.transform(
                np.min(y), np.max(y), self._newymin, self._newymax, ticksynorm
            ),
            dtype=np.int16,
        )
        subticksxrenorm = np.array(
            self.transform(
                np.min(x), np.max(x), self._newxmin, self._newxmax, subticksxnorm
            ),
            dtype=np.int16,
        )
        subticksyrenorm = np.array(
            self.transform(
                np.min(y), np.max(y), self._newymin, self._newymax, subticksynorm
            ),
            dtype=np.int16,
        )
        for i, tick in enumerate(ticksxrenorm):
            draw_line(
                self._plotbitmap,
                tick,
                self._newymin,
                tick,
                self._newymin - self._tickheightx,
                2,
            )
            if self._showtext:
                self.show_text(
                    "{:.2f}".format(ticksxnorm[i]), tick, self._newymin, (0.5, 0.0)
                )
        for i, tick in enumerate(ticksyrenorm):
            draw_line(
                self._plotbitmap,
                self._newxmin,
                tick,
                self._newxmin + self._tickheighty,
                tick,
                2,
            )
            if self._showtext:
                self.show_text(
                    "{:.2f}".format(ticksynorm[i]), self._newxmin, tick, (1.0, 0.5)
                )
        for tick in subticksxrenorm:
            draw_line(
                self._plotbitmap,
                tick,
                self._newymin,
                tick,
                self._newymin - self._tickheightx // 2,
                2,
            )
        for tick in subticksyrenorm:
            draw_line(
                self._plotbitmap,
                self._newxmin,
                tick,
                self._newxmin + self._tickheighty // 2,
                tick,
                2,
            )

        if self._tickgrid:
            self._draw_gridx(ticksxrenorm)
            self._draw_gridy(ticksyrenorm)

    def tick_params(
        self,
        show_ticks=True,
        tickx_height: int = 8,
        ticky_height: int = 8,
        tickcolor: int = 0xFFFFFF,
        tickgrid: bool = False,
        showtext: bool = False,
    ) -> None:
        """
        Function to set ticks parameters

        :param int tickx_height: X axes tick height in pixels. Defaults to 8
        :param int ticky_height: Y axes tick height in pixels. Defaults to 8
        :param int tickcolor: tick color in hex. Defaults to white. ``0xFFFFFF``
        :param bool tickgrid: defines if the grid is to be shown. Defaults to `False`
        :param bool showtext: Show Axes text. Defaults to `False`

        :return: None

        """

        self._showticks = show_ticks
        self._tickheightx = tickx_height
        self._tickheighty = ticky_height
        self._plot_palette[2] = tickcolor
        self._tickgrid = tickgrid
        self._showtext = showtext
        if self._showtext:
            from adafruit_display_text import bitmap_label

            self.bitmap_label = bitmap_label

    def _draw_gridx(self, ticks_data: list[int]) -> None:
        """
        Draws the plot grid

        :param list[int] ticks_data: ticks data information

        :return: None

        """
        for tick in ticks_data:
            start = self._newymin
            while start - self._grid_lenght - self._grid_espace >= self._newymax:
                draw_line(
                    self._plotbitmap,
                    tick,
                    start,
                    tick,
                    start - self._grid_lenght,
                    2,
                )
                start = start - self._grid_espace - self._grid_lenght

    def _draw_gridy(self, ticks_data: list[int]) -> None:
        """
        Draws plot grid in the y axs

        :param list[int] ticks_data: ticks data information

        :return: None

        """
        for tick in ticks_data:
            start = self._newxmin
            while start + self._grid_lenght <= self._newxmax:
                draw_line(
                    self._plotbitmap,
                    start,
                    tick,
                    start + self._grid_lenght,
                    tick,
                    2,
                )
                start = start + self._grid_espace + self._grid_lenght

    def update_plot(self) -> None:
        """
        Function to update graph

        :return: None

        """

        self._drawbox()

    def show_text(
        self, text: str, x: int, y: int, anchorpoint: Tuple = (0.5, 0.0)
    ) -> None:
        """

        Show desired text in the screen
        :param str text: text to be displayed
        :param int x: x coordinate
        :param int y: y coordinate
        :param Tuple anchorpoint: Display_text anchor point. Defaults to (0.5, 0.0)
        :return: None
        """
        if self._showtext:
            text_toplot = self.bitmap_label.Label(terminalio.FONT, text=text, x=x, y=y)
            text_toplot.anchor_point = anchorpoint
            text_toplot.anchored_position = (x, y)
            self.append(text_toplot)


# pylint: disable=missing-class-docstring, too-few-public-methods, invalid-name
class color:
    WHITE = 0xFFFFFF
    BLACK = 0x000000
    RED = 0xFF0000
    GREEN = 0x00FF00
    BLUE = 0x0000FF
    PURPLE = 0x440044
    YELLOW = 0xFFFF00
    ORANGE = 0xFF9933
    TEAL = 0x158FAD
    GRAY = 0x808080
