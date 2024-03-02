# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT

"""

`ubar`
================================================================================

CircuitPython scatter graph

* Author(s): Jose D. Montoya


"""

try:
    from circuitpython_uplot.uplot import Uplot
except ImportError:
    pass
import math
from displayio import Palette
from bitmaptools import draw_line
from vectorio import Rectangle, Polygon

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/CircuitPython_uplot.git"

# pylint: disable=protected-access
# pylint: disable=no-self-use


class ubar:
    """
    Main class to display different graphics
    """

    def __init__(
        self,
        plot: Uplot,
        x: list,
        y: list,
        color: int = 0xFFFFFF,
        fill: bool = False,
        bar_space=16,
        xstart=50,
        projection=False,
        color_palette=None,
        max_value=None,
    ) -> None:
        """
        :param Uplot plot: Plot object for the scatter to be drawn
        :param list x: x data
        :param list y: y data
        :param int color: boxes color. Defaults to const:``0xFFFFFF``
        :param bool fill: boxes fill attribute. Defaults to `False`
        :param int bar_space: space in pixels between the bars
        :param int xstart: start point in the x axis for the bar to start. Defaults to :const:`50`
        :param bool projection: creates projection of the bars given them depth.
        :param list color_palette: list of colors to be used for the bars. Defaults to None.
         Be aware that you need to include the same number if colors as your data.
         This functionality will only work with filled bars.
        :param int max_value: for filled unprojected bars will setup the maxium value for the bars.
         This allows the user to update the bars in real-time. There is an example in the examples
         folder showing this functionality

        """
        self._bars = []
        self._plot_obj = plot
        self._projection = projection
        self._filled = fill

        if max_value is None:
            y_max = max(y)
        else:
            y_max = max_value

        self._y = [i * plot.scale for i in y]
        self._bar_space = int(bar_space / plot.scale)
        self._graphx = plot.scale * int(
            abs(plot._newxmax - plot._newxmin) / (len(x) + 4)
        )
        self._graphy = plot.scale * int(
            abs(plot._newymax - plot._newymin) / (y_max + 2)
        )

        self._new_min = int(plot.transform(0, y_max, y_max, 0, 0))
        self._new_max = int(plot.transform(0, y_max, y_max, 0, y_max))

        if color_palette is not None:
            if projection:
                color_count = 2
            else:
                color_count = 1
            self._color_palette = Palette(len(color_palette) * color_count)
            for i, selected_color in enumerate(color_palette):
                self._color_palette[i] = selected_color
            self._color_index = 0
        else:
            self._color_palette = plot._plot_palette
            self._color_index = plot._index_colorused
            self._color_palette[self._color_index] = color

        if plot._index_colorused >= 14:
            plot._index_colorused = 2
            self._color_index = 2
            if color_palette:
                self._color_index = 0

        if fill:
            for i, _ in enumerate(x):
                self._create_bars(xstart, i)

                if projection:
                    self._create_projections(xstart, i, len(color_palette))

                plot.show_text(
                    str(y[i]),
                    xstart + (i * self._graphx) + self._graphx // 2,
                    plot._newymin,
                )
                xstart = xstart + self._bar_space
                plot._index_colorused = plot._index_colorused + 1
                self._color_index = self._color_index + 1
        else:
            for i, _ in enumerate(x):
                self._draw_rectangle(
                    plot,
                    xstart + (i * self._graphx),
                    plot._newymin,
                    self._graphx,
                    self._graphy * y[i],
                    plot._index_colorused,
                )
                delta = 20
                rx = int(delta * math.cos(-0.5))
                ry = int(delta * math.sin(-0.5))
                x0 = xstart + (i * self._graphx)
                y0 = plot._newymin - self._graphy * y[i]
                x1 = xstart + (i * self._graphx) + self._graphx
                y1 = plot._newymin - self._graphy * y[i]

                draw_line(
                    plot._plotbitmap, x0, y0, x0 - rx, y0 + ry, plot._index_colorused
                )
                draw_line(
                    plot._plotbitmap, x1, y1, x1 - rx, y1 + ry, plot._index_colorused
                )
                draw_line(
                    plot._plotbitmap,
                    x0 - rx,
                    y0 + ry,
                    x1 - rx,
                    y1 + ry,
                    plot._index_colorused,
                )
                draw_line(
                    plot._plotbitmap,
                    x0 - rx,
                    y0 + ry,
                    x0 - rx,
                    plot._newymin,
                    plot._index_colorused,
                )

                xstart = xstart + bar_space
                plot._index_colorused = plot._index_colorused + 1
                plot.show_text(
                    str(y[i]),
                    xstart + (i * self._graphx) - bar_space + self._graphx // 2,
                    plot._newymin,
                )

    def _create_bars(self, xstart: int, indice: int):
        """
        create plot bars
        """

        self._bars.append(
            Rectangle(
                pixel_shader=self._color_palette,
                width=self._graphx,
                height=self._graphy * self._y[indice],
                x=xstart + (indice * self._graphx),
                y=int(
                    self._plot_obj._newymin
                    - self._graphy * self._y[indice] / self._plot_obj.scale
                ),
                color_index=self._color_index,
            )
        )
        self._plot_obj.append(self._bars[indice])

    def _create_projections(self, xstart: int, indice: int, color_lenght: int):
        delta = 20
        rx = int(delta * math.cos(-0.5))
        ry = int(delta * math.sin(-0.5))
        points = [
            (0, 0),
            (self._graphx, 0),
            (self._graphx - rx, 0 + ry),
            (0 - rx, 0 + ry),
        ]

        self._color_palette[self._color_index + color_lenght] = color_fader(
            self._color_palette[self._color_index], 0.7, 1
        )

        self._plot_obj.append(
            Polygon(
                pixel_shader=self._color_palette,
                points=points,
                x=xstart + (indice * self._graphx),
                y=self._plot_obj._newymin - self._graphy * self._y[indice],
                color_index=self._color_index + color_lenght,
            )
        )
        points = [
            (0, 0),
            (0 - rx, 0 + ry),
            (0 - rx, self._graphy * self._y[indice]),
            (0, self._graphy * self._y[indice]),
        ]
        self._plot_obj.append(
            Polygon(
                pixel_shader=self._color_palette,
                points=points,
                x=xstart + (indice * self._graphx),
                y=self._plot_obj._newymin - self._graphy * self._y[indice],
                color_index=self._color_index + color_lenght,
            )
        )

    def _draw_rectangle(
        self, plot: Uplot, x: int, y: int, width: int, height: int, color: int
    ) -> None:
        """
        Helper function to draw bins rectangles
        """
        draw_line(plot._plotbitmap, x, y, x + width, y, color)
        draw_line(plot._plotbitmap, x, y, x, y - height, color)
        draw_line(plot._plotbitmap, x + width, y, x + width, y - height, color)
        draw_line(plot._plotbitmap, x + width, y - height, x, y - height, color)

    def update_values(self, values: list = None):
        """
        Update Values of the bars
        """
        if self._projection:
            raise AttributeError("Library is not designed to update projected Bars")
        if not self._filled:
            raise AttributeError("Library is not designed to update shell Bars")
        if values is None:
            raise ValueError("You must provide a list of values")
        for i, element in enumerate(self._bars):
            height = self._graphy * values[i]
            y = int(
                self._plot_obj._newymin
                - self._graphy * values[i] / self._plot_obj.scale
            )
            element.height = height
            element.y = y


def color_fader(source_color=None, brightness=1.0, gamma=1.0):
    """
    Function taken from https://github.com/CedarGroveStudios
    Copyright (c) 2022 JG for Cedar Grove Maker Studios
    License: MIT

    Scale a 24-bit RGB source color value in proportion to the brightness
    setting (0 to 1.0). Returns an adjusted 24-bit RGB color value or None if
    the source color is None (transparent). The adjusted color's gamma value is
    typically from 0.0 to 2.0 with a default of 1.0 for no gamma adjustment.

    :param int source_color: The color value to be adjusted. Default is None.
    :param float brightness: The brightness value for color value adjustment.
      Value range is 0.0 to 1.0. Default is 1.0 (maximum brightness).
    :param float gamma: The gamma value for color value adjustment. Value range
      is 0.0 to 2.0. Default is 1.0 (no gamma adjustment).

    :return int: The adjusted color value."""

    if source_color is None:
        return source_color

    # Extract primary colors and scale to brightness
    r = min(int(brightness * ((source_color & 0xFF0000) >> 16)), 0xFF)
    g = min(int(brightness * ((source_color & 0x00FF00) >> 8)), 0xFF)
    b = min(int(brightness * ((source_color & 0x0000FF) >> 0)), 0xFF)

    # Adjust result for gamma
    r = min(int(round((r**gamma), 0)), 0xFF)
    g = min(int(round((g**gamma), 0)), 0xFF)
    b = min(int(round((b**gamma), 0)), 0xFF)

    return (r << 16) + (g << 8) + b
