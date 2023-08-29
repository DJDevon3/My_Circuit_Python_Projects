# SPDX-FileCopyrightText: 2018 Scott Shawcroft for Adafruit Industries
# SPDX-FileCopyrightText: 2022 Matt Land
#
# SPDX-License-Identifier: MIT

"""
Check for negative height on the BMP.
Seperated into it's own file to support builds
without longint.

* Author(s): Tim Cocks, Matt Land
"""


def negative_height_check(height: int) -> int:
    """Check the height return modified if negative."""
    if height > 0x7FFFFFFF:
        return height - 4294967296
    return height
