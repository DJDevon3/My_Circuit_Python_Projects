# SPDX-FileCopyrightText: 2024 Tim Cocks, DJDevon3
#
# SPDX-License-Identifier: MIT

import json
import time
from displayio import Group
from adafruit_display_text import label
from adafruit_displayio_layout.layouts.grid_layout import GridLayout
from adafruit_bitmap_font import bitmap_font

PRINTABLE_CHARACTERS = (
    "`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=",
    "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "",
    "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "a", "b", "c", "d", "e",
    "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "",
    "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", ",", ".", "/", "\\", "'",
    "[", "]", ";", " "
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
    :param str layout_config: Filename for JSON layout. None defaults to default_layout.json

    """

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-instance-attributes
    
    DEFAULT_HIGHLIGHT_TIME = 0.2
    DEFAULT_KEYPRESS_COOLDOWN = 0.2

    def __init__(self, x, y, width, height,
                 character_font, symbol_font,
                 keypress_cooldown=DEFAULT_KEYPRESS_COOLDOWN,
                 highlight_duration=DEFAULT_HIGHLIGHT_TIME,
                 allow_sticky_repeat=False, layout_config=None):
        super().__init__()
        self.shift_mode = False
        self.layout_config = layout_config
        lib_path = __file__
        lib_path = lib_path.split("/")[:-1]
        if self.layout_config is None:
            f = open(f"{'/'.join(lib_path)}/default_layout.json", "r")
        else:
            f = open(f"{'/'.join(lib_path)}/{layout_config}", "r")
        self.layout_config = json.loads(f.read())
        # print(f"Layout Config: {layout_config}")

        layout = GridLayout(
            x=x,  # layout x
            y=y,  # layout y
            width=width,
            height=height,
            grid_size=tuple(self.layout_config['base_grid_size']),  # Grid Layout width,height
            cell_padding=2,
            divider_lines=True,  # divider lines around every cell
            cell_anchor_point=(0.5, 0.5)
        )
        self.highlight_duration = highlight_duration
        self.keypress_cooldown = keypress_cooldown
        self._highlighted_views = []
        self.last_keypressed_time = -1
        self.keypress_debounced = None
        self.allow_sticky_repeat = allow_sticky_repeat
        self.shift_key_view = None

        for row_idx, row in enumerate(self.layout_config["rows"]):
            cur_span_offset = 0
            for col_idx, key in enumerate(row["keys"]):
                _font = character_font
                if "font" in key:
                    if key["font"] == "symbol_font":
                        _font = symbol_font
                _scale = 2
                if "scale" in key:
                    _scale = key["scale"]
                l = label.Label(_font, scale=_scale, text=key["label"])
                l.key_config = key
                size = (1, 1)
                if "col_span" in key:
                    size = (key["col_span"], 1)

                position = (col_idx + cur_span_offset, row_idx)
                layout.add_content(l, grid_position=position, cell_size=size, layout_cells=False)
                if "col_span" in key:
                    cur_span_offset += key["col_span"] - 1
        layout.layout_cells()
        self.layout = layout
        self.append(layout)

    @property
    def height(self):
        return self.layout.height

    @property
    def width(self):
        return self.layout.width

    def check_touches(self, touch_point):
        now = time.monotonic()

        for _view, unhighlight_time in self._highlighted_views:
            if now > unhighlight_time:
                _view.color = 0xffffff
                _view.background_color = None
                # None looks better when used with background images

        if touch_point:

            # if sticky repeat is on, or if the most recent keypress has been debounced i.e. released
            if self.allow_sticky_repeat or self.keypress_debounced:
                touched_cell = self.layout.which_cell_contains(touch_point)
                if touched_cell:
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
                            pressed_value = touched_cell_view.key_config["key_value"]

                        print(f"key_text: {pressed_value}")

                        self.last_keypressed_time = now
                        self.keypress_debounced = False

                        if pressed_value == 225:  # 0xE1 shift key
                            self.shift_mode = not self.shift_mode
                            if self.shift_mode:
                                touched_cell_view.background_color = 0x0000ff
                                self.shift_key_view = touched_cell_view
                            else:
                                touched_cell_view.background_color = 0x000000
                        else:
                            # non-special highlighting
                            touched_cell_view.background_color = 0x00ff00
                            touched_cell_view.color = 0x000000
                            self._highlighted_views.append((touched_cell_view, now + self.keypress_cooldown))

                        return pressed_value
        # keypress is None
        else:
            self.keypress_debounced = True
