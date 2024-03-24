# SPDX-FileCopyrightText: 2021 Jose David
#
# SPDX-License-Identifier: MIT
"""

`slider`
================================================================================
A slider widget with a rectangular shape.

* Author(s): Jose David M.

Implementation Notes
--------------------

**Hardware:**

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""

################################
# A slider widget for CircuitPython, using displayio and adafruit_display_shapes
#
# Features:
#  - slider to represent non discrete values
#
# Future options to consider:
# ---------------------------
# different orientations (horizontal, vertical, flipped)
#

from adafruit_display_shapes.roundrect import RoundRect
from adafruit_displayio_layout.widgets.widget import Widget
from adafruit_displayio_layout.widgets.control import Control
from adafruit_displayio_layout.widgets.easing import quadratic_easeinout as easing

try:
    from typing import Tuple
except ImportError:
    pass

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/jposada202020/CircuitPython_slider.git"


class Slider(Widget, Control):
    """

    :param int x: pixel position, defaults to 0
    :param int y: pixel position, defaults to 0
    :param int width: width of the slider in pixels. It is recommended to use 100
     the height will auto-size relative to the width. Defaults to :const:`100`
    :param int height: height of the slider in pixels, defaults to 40 pixels
    :param int touch_padding: the width of an additional border surrounding the switch
     that extends the touch response boundary, defaults to 0

    :param anchor_point: starting point for the annotation line, where ``anchor_point`` is
     an (A,B) tuple in relative units of the size of the widget, for example (0.0, 0.0) is
     the upper left corner, and (1.0, 1.0) is the lower right corner of the widget.
     If :attr:`anchor_point` is `None`, then :attr:`anchored_position` is used to set the
     annotation line starting point, in widget size relative units.
     Defaults to :const:`(0.0, 0.0)`
    :type anchor_point: Tuple[float, float]

    :param anchored_position: pixel position starting point for the annotation line
     where :attr:`anchored_position` is an (x,y) tuple in pixel units relative to the
     upper left corner of the widget, in pixel units (default is None).
    :type anchored_position: Tuple[int, int]

    :param fill_color: (*RGB tuple or 24-bit hex value*) slider fill color, default
     is :const:`(66, 44, 66)` gray.
    :param outline_color: (*RGB tuple or 24-bit hex value*) slider outline color,
     default is :const:`(30, 30, 30)` dark gray.
    :param background_color: (*RGB tuple or 24-bit hex value*) background color,
     default is :const:`(255, 255, 255)` white

    :param int switch_stroke: outline stroke width for the switch and background, in pixels,
     default is 2
    :param Boolean value: the initial value for the switch, default is False


    **Quickstart: Importing and using Slider**

    Here is one way of importing the `Slider` class so you can use it as
    the name ``Slider``:

    .. code-block:: python

        from adafruit_displayio_layout.widgets.slider import Slider

    Now you can create a Slider at pixel position x=20, y=30 using:

    .. code-block:: python

        my_slider=Slider(x=20, y=30)

    Once your setup your display, you can now add ``my_slider`` to your display using:

    .. code-block:: python

        display.show(my_slider) # add the group to the display

    If you want to have multiple display elements, you can create a group and then
    append the slider and the other elements to the group.  Then, you can add the full
    group to the display as in this example:

    .. code-block:: python

        my_slider= Slider(20, 30)
        my_group = displayio.Group() # make a group
        my_group.append(my_slider) # Add my_slider to the group

        #
        # Append other display elements to the group
        #

        display.show(my_group) # add the group to the display


    **Summary: Slider Features and input variables**

    The ``Slider`` widget has some options for controlling its position, visible appearance,
    and value through a collection of input variables:

        - **position**: :const:`x`, ``y`` or ``anchor_point`` and ``anchored_position``

        - **size**: :const:`width` and ``height`` (recommend to leave ``height`` = None to use
          preferred aspect ratio)

        - **switch color**: :const:`fill_color`, :const:`outline_color`

        - **background color**: :const:`background_color`

        - **linewidths**: :const:`switch_stroke`

        - **value**: Set ``value`` to the initial value (True or False)

        - **touch boundaries**: :attr:`touch_padding` defines the number of additional pixels
          surrounding the switch that should respond to a touch.  (Note: The ``touch_padding``
          variable updates the ``touch_boundary`` Control class variable.  The definition of
          the ``touch_boundary`` is used to determine the region on the Widget that returns
          `True` in the `when_inside` function.)

    **The Slider Widget**

    .. figure:: slider.png
       :scale: 100 %
       :figwidth: 80%
       :align: center
       :alt: Diagram of the slider widget.

       This is a diagram of a slider with component parts


    """

    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 100,  # recommend to default to
        height: int = 40,
        touch_padding: int = 0,
        anchor_point: Tuple[int, int] = None,
        anchored_position: Tuple[int, int] = None,
        fill_color: Tuple[int, int, int] = (66, 44, 66),
        outline_color: Tuple[int, int, int] = (30, 30, 30),
        background_color: Tuple[int, int, int] = (255, 255, 255),
        value: bool = False,
        **kwargs,
    ) -> None:
        Widget.__init__(self, x=x, y=y, height=height, width=width, **kwargs)
        Control.__init__(self)

        self._knob_width = height // 2
        self._knob_height = height

        self._knob_x = self._knob_width
        self._knob_y = self._knob_height

        self._slider_height = height // 5

        self._height = self.height

        # pylint: disable=access-member-before-definition)

        if self._width is None:
            self._width = 100
        else:
            self._width = self.width

        self._fill_color = fill_color
        self._outline_color = outline_color
        self._background_color = background_color

        self._switch_stroke = 2

        self._touch_padding = touch_padding

        self._value = value

        self._anchor_point = anchor_point
        self._anchored_position = anchored_position

        self._create_slider()

    def _create_slider(self) -> None:
        # The main function that creates the switch display elements
        self._x_motion = self._width
        self._y_motion = 0

        self._frame = RoundRect(
            x=0,
            y=0,
            width=self.width,
            height=self.height,
            r=4,
            fill=0x990099,
            outline=self._outline_color,
            stroke=self._switch_stroke,
        )

        self._switch_handle = RoundRect(
            x=0,
            y=0,
            width=self._knob_width,
            height=self._knob_height,
            r=4,
            fill=self._fill_color,
            outline=self._outline_color,
            stroke=self._switch_stroke,
        )

        self._switch_roundrect = RoundRect(
            x=2,
            y=self.height // 2 - self._slider_height // 2,
            r=2,
            width=self._width - 4,
            height=self._slider_height,
            fill=self._background_color,
            outline=self._background_color,
            stroke=self._switch_stroke,
        )

        self._bounding_box = [
            0,
            0,
            self.width,
            self._knob_height,
        ]

        self.touch_boundary = [
            self._bounding_box[0] - self._touch_padding,
            self._bounding_box[1] - self._touch_padding,
            self._bounding_box[2] + 2 * self._touch_padding,
            self._bounding_box[3] + 2 * self._touch_padding,
        ]

        self._switch_initial_x = self._switch_handle.x
        self._switch_initial_y = self._switch_handle.y

        for _ in range(len(self)):
            self.pop()

        self.append(self._frame)
        self.append(self._switch_roundrect)
        self.append(self._switch_handle)

        self._update_position()

    def _get_offset_position(self, position) -> Tuple[int, int]:
        x_offset = int(self._x_motion * position // 2)
        y_offset = int(self._y_motion * position)

        return x_offset, y_offset

    def _draw_position(self, position: Tuple[int, int]) -> None:
        # apply the "easing" function to the requested position to adjust motion
        position = easing(position)

        # Get the position offset from the motion function
        x_offset, y_offset = self._get_offset_position(position)

        # Update the switch x- and y-positions
        self._switch_handle.x = self._switch_initial_x + x_offset
        self._switch_handle.y = self._switch_initial_y + y_offset

    def when_selected(self, touch_point: int) -> int:
        """
        Manages internal logic when widget is selected
        """

        if touch_point[0] <= self.x + self._knob_width:
            touch_x = touch_point[0] - self.x
        else:
            touch_x = touch_point[0] - self.x - self._knob_width

        touch_y = touch_point[1] - self.y

        self.selected((touch_x, touch_y, 0))
        self._switch_handle.x = touch_x
        return self._switch_handle.x

    def when_inside(self, touch_point: int) -> bool:
        """Checks if the Widget was touched.

        :param touch_point: x,y location of the screen, in absolute display coordinates.
        :return: Boolean

        """
        touch_x = (
            touch_point[0] - self.x
        )  # adjust touch position for the local position
        touch_y = touch_point[1] - self.y

        return self.contains((touch_x, touch_y, 0))

    @property
    def value(self) -> int:
        """The current switch value (Boolean).

        :return: Boolean
        """
        return self._value
