# SPDX-FileCopyrightText: 2021 Phillip Burgess for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# MACROPAD Hotkeys example: Adobe Photoshop for Windows

from adafruit_hid.keycode import Keycode # REQUIRED if using Keycode.* values

app = {                       # REQUIRED dict, must be named 'app'
    'name' : 'Win Photoshop', # Application name
    'macros' : [              # List of button macros...
        # COLOR    LABEL    KEY SEQUENCE
        # 1st row ----------
        (0x004000, 'Undo', [Keycode.CONTROL, 'z']),
        (0x004000, 'Redo', [Keycode.CONTROL, 'Z']),
        (0x000040, 'Brush', 'B'),   # Cycle brush modes
        # 2nd row ----------
        (0x101010, 'B&W', 'd'),     # Default colors
        (0x101010, 'Marquee', 'M'), # Cycle rect/ellipse marquee (select)
        (0x000040, 'Eraser', 'E'),  # Cycle eraser modes
        # 3rd row ----------
        (0x101010, 'Swap', 'x'),    # Swap foreground/background colors
        (0x101010, 'Move', 'v'),    # Move layer
        (0x000040, 'Fill', 'G'),    # Cycle fill/gradient modes
        # 4th row ----------
        (0x101010, 'Eyedrop', 'I'), # Cycle eyedropper/measure modes
        (0x101010, 'Wand', 'W'),    # Cycle "magic wand" (selection) modes
        (0x000040, 'Heal', 'J'),    # Cycle "healing" modes
        # Encoder button ---
        (0x000000, '', [Keycode.CONTROL, Keycode.ALT, 'S']) # Save for web
    ]
}
