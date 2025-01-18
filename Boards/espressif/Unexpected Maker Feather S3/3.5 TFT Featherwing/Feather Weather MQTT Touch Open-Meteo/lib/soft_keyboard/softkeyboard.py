# SPDX-FileCopyrightText: 2024 Tim Cocks, DJDevon3
#
# SPDX-License-Identifier: MIT
"""
`softkeyboard`
================================================================================

CircuitPython software defined keyboard for touch displays using displayio GridLayout.


* Author(s): Tim Cocks, DJDevon3

Implementation Notes
--------------------

**Hardware:**

* Any touch capable display

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

"""
import gc
# imports
import json
import time
from displayio import Group
from adafruit_display_text import label
from adafruit_displayio_layout.layouts.grid_layout import GridLayout

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/Foamyguy/CircuitPython_SoftKeyboard.git"

PRINTABLE_CHARACTERS = (
    "`",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "0",
    "-",
    "=",
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "",
    "p",
    "q",
    "r",
    "s",
    "t",
    "u",
    "v",
    "w",
    "x",
    "y",
    "z",
    ",",
    ".",
    "/",
    "\\",
    "'",
    "[",
    "]",
    ";",
    " ",
)


class SoftKeyboard(Group):
    """
    CircuitPython software defined keyboard for touch displays using displayio GridLayout.

    :param int x: x location the layout should be placed. Pixel coordinates.
    :param int y: y location the layout should be placed. Pixel coordinates.
    :param int width: Width of the layout in pixels.
    :param int height: Height of the layout in pixels.
    :param str character_font: Font for normal characters (terminalio.FONT)
    :param str symbol_font: Font for symbol characters (forkawesome_font)
    :param float keypress_cooldown: Time in seconds for keypress debounce.
    :param float highlight_duration: Time in seconds for label highlight during touch
    :param bool allow_sticky_repeat: Assistive sticky keys capability boolean
    :param str layout_file: Filename for JSON layout. None defaults to default_layout.json

    """

    # pylint: disable=too-many-arguments,too-many-locals
    # pylint: disable=too-many-instance-attributes

    DEFAULT_HIGHLIGHT_TIME = 0.2
    DEFAULT_KEYPRESS_COOLDOWN = 0.2

    def __init__(
        self,
        x,
        y,
        width,
        height,
        character_font,
        symbol_font,
        keypress_cooldown=DEFAULT_KEYPRESS_COOLDOWN,
        highlight_duration=DEFAULT_HIGHLIGHT_TIME,
        allow_sticky_repeat=False,
        layout_file=None,
    ):
        super().__init__()
        self.shift_mode = False
        self._layout_file = layout_file

        if self._layout_file is None:
            self._layout_file = "default_layout.json"
            # layout_file = open(f"{'/'.join(lib_path)}/default_layout.json", "r")
        # else:

        # print(f"Layout Config: {layout_config}")
        self.highlight_duration = highlight_duration
        self.keypress_cooldown = keypress_cooldown

        self.allow_sticky_repeat = allow_sticky_repeat

        self._highlighted_views = []
        self.last_keypressed_time = -1
        self.keypress_debounced = None

        self.shift_key_view = None
        self.layout = None

        self.character_font = character_font
        self.symbol_font = symbol_font

        self.layout_x = x
        self.layout_y = y

        self.layout_width = width
        self.layout_height = height

        self._first_time = True
        self._init_layout()


    def _init_layout(self):
        lib_path = __file__
        lib_path = lib_path.split("/")[:-1]
        with open(f"{'/'.join(lib_path)}/{self._layout_file}", "r") as layout_file:
            self._layout_config = json.loads(layout_file.read())

        if self.layout is not None and self.layout in self:
            print("removing old self.layout")
            self.remove(self.layout)
            self.layout = None
            gc.collect()

        self._first_time = False
        layout = GridLayout(
            x=self.layout_x,  # layout x
            y=self.layout_y,  # layout y
            width=self.layout_width,
            height=self.layout_height,
            grid_size=tuple(
                self._layout_config["base_grid_size"]
            ),  # Grid Layout width,height
            cell_padding=2,
            divider_lines=True,  # divider lines around every cell
            cell_anchor_point=(0.5, 0.5),
        )

        for row_idx, row in enumerate(self._layout_config["rows"]):
            cur_span_offset = 0
            for col_idx, key in enumerate(row["keys"]):
                _font = self.character_font
                if "font" in key:
                    if key["font"] == "symbol_font":
                        _font = self.symbol_font
                _scale = 2
                if "scale" in key:
                    _scale = key["scale"]
                cur_lbl = label.Label(_font, scale=_scale, text=key["label"])
                cur_lbl.key_config = key
                size = (1, 1)
                if "col_span" in key:
                    size = (key["col_span"], 1)

                position = (col_idx + cur_span_offset, row_idx)
                layout.add_content(
                    cur_lbl, grid_position=position, cell_size=size, layout_cells=False
                )
                if "col_span" in key:
                    cur_span_offset += key["col_span"] - 1
        layout.layout_cells()
        self.layout = layout
        self.append(layout)


    @property
    def layout_file(self):
        return self._layout_file

    @layout_file.setter
    def layout_file(self, new_layout_file):
        self._layout_file = new_layout_file
        self._init_layout()


    @property
    def height(self):
        """
        The height of the layout
        :return:
        """
        return self.layout.height

    @property
    def width(self):
        """
        The width of the layout
        :return:
        """
        return self.layout.width

    def check_touches(self, touch_point):
        """
        Check the touch events and process any keys that have been pressed.
        :param touch_point: tuple (x, y) coordinates of touch event
        :return: The value of the key that was pressed. Either string or int.
        """
        # pylint: disable=too-many-branches,too-many-nested-blocks
        now = time.monotonic()

        for _view, unhighlight_time in self._highlighted_views:
            if now > unhighlight_time:
                _view.color = 0xFFFFFF
                _view.background_color = None
                # None looks better when used with background images

        if touch_point:
            # if sticky repeat is on, or if most recent keypress has been debounced i.e. released
            if self.allow_sticky_repeat or self.keypress_debounced:
                touched_cell = self.layout.which_cell_contains(touch_point)
                if touched_cell:
                    try:
                        if self.last_keypressed_time + self.keypress_cooldown < now:
                            touched_cell_view = self.layout.get_cell(touched_cell)

                            if not self.shift_mode:
                                pressed_value = touched_cell_view.text.lower()
                            else:
                                pressed_value = touched_cell_view.text
                                self.shift_mode = False
                                self.shift_key_view.background_color = 0x000000

                            print(touched_cell_view.key_config)
                            if "key_value" in touched_cell_view.key_config:
                                pressed_value = touched_cell_view.key_config[
                                    "key_value"
                                ]

                            print(f"key_text: {pressed_value}")

                            self.last_keypressed_time = now
                            self.keypress_debounced = False

                            if pressed_value == 225:  # 0xE1 shift key
                                self.shift_mode = not self.shift_mode
                                if self.shift_mode:
                                    touched_cell_view.background_color = 0x0000FF
                                    self.shift_key_view = touched_cell_view
                                else:
                                    touched_cell_view.background_color = 0x000000
                            else:
                                # non-special highlighting
                                touched_cell_view.background_color = 0x00FF00
                                touched_cell_view.color = 0x000000
                                self._highlighted_views.append(
                                    (touched_cell_view, now + self.keypress_cooldown)
                                )

                            return pressed_value
                    # catches touches outside on the edge of outer grid
                    except KeyError:
                        pass
        # keypress is None
        else:
            self.keypress_debounced = True
        return None
