# SPDX-FileCopyrightText: Copyright (c) 2022 JG for Cedar Grove Maker Studios
#
# SPDX-License-Identifier: MIT
"""
`cedargrove_palettefader_mp`
================================================================================

PaletteFader is a CircuitPython driver class for brightness-adjusting color
lists and displayio palettes. Normalization is optionally applied to the palette
prior to brightness and gamma adjustments. Transparency index values are
preserved and associated with the adjusted palette. Creates an adjusted
displayio color palette object (displayio.Palette) that can also be read as a
color list.

For adjusting a single color value, create a list containing a single color or
use cedargrove_unit_converter.color.colorfader.color_fader().

cedargrove_palettefader_mp.py v2.0.1 2022-10-02

* Author(s): JG for Cedar Grove Maker Studios

Implementation Notes
--------------------

**Hardware:**

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  <https://circuitpython.org/downloads>

"""

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/CedarGroveStudios/CircuitPython_PaletteFader.git"

import displayio


class PaletteFader:
    """Displayio palette fader with normalization, brightness (fading), and
    gamma control. Returns an adjusted displayio palette object."""

    def __init__(self, source_palette, brightness=1.0, gamma=1.0, normalize=False):
        """Instantiate the palette fader. Creates a displayio palette object
        with faded source palette/List color values. Transparency is preserved.

        :param union(list, displayio.Palette) source_palette: The color source
          list or displayio palette object. No default.
        :param float brightness: The brightness value for palette adjustment.
          Value range is 0.0 to 1.0. Default is 1.0 (maximum brightness).
        :param float gamma: The gamma value for palette adjustment. Value range
          is 0.0 to 2.0. Default is 1.0 (no gamma adjustment).
        :param bool normalize: The boolean normalization state. True to
          normalize; False to skip normalization. Default is False (no
          normalization)."""

        self._src_palette = source_palette
        self._brightness = brightness
        self._gamma = gamma
        self._normalize = normalize

        self._list_transparency = []  # List of transparent items in a color list

        self._ref_palette = []
        # Create the reference palette list with source palette RGB values

        for index, rgb in enumerate(self._src_palette):
            if rgb is not None:
                b = rgb & 0x0000FF
                g = (rgb & 0x00FF00) >> 8
                r = (rgb & 0xFF0000) >> 16
                self._ref_palette.append([r, g, b])

                if not isinstance(self._src_palette, list):
                    # Record palette transparency color index
                    if self._src_palette.is_transparent(index):
                        self._list_transparency.append(index)
            else:
                """Color is None; replace with BLACK in the reference palette
                and record the color index in the transparency list."""
                self._ref_palette[index] = [0, 0, 0]
                self._list_transparency.append(index)

        # Find the brightest RGB component for the normalization process
        if self._normalize:
            self._ref_palette_max = max(max(self._ref_palette))
        else:
            # Set the maximum value to the 8-bit limit (no normalization)
            self._ref_palette_max = 0xFF
        self.fade_normalize()

    @property
    def brightness(self):
        """The palette's overall brightness level, 0.0 to 1.0."""
        return self._brightness

    @brightness.setter
    def brightness(self, new_brightness):
        if self._brightness != new_brightness:
            self._brightness = new_brightness
            self.fade_normalize()

    @property
    def gamma(self):
        """The adjusted palette's gamma value, typically from 0.0 to 2.0. The
        gamma adjustment is applied after the palette is normalized and
        brightness-adjusted."""
        return self._gamma

    @property
    def normalize(self):
        """The palette's normalization mode state; True for normalization
        applied; False for no normalization."""
        return self._normalize

    @property
    def palette(self):
        """The adjusted displayio palette."""
        return self._new_palette

    def fade_normalize(self):
        """Create an adjusted displayio palette from the reference palette. Use
        the current brightness, gamma, and normalize parameters to build the
        adjusted palette. The reference palette is first adjusted for
        brightness and normalization (if enabled) followed by the gamma
        adjustment. Transparency index values are preserved."""

        # Determine the normalization factor to apply to the palette
        self._norm_factor = round((0xFF / self._ref_palette_max) * self._brightness, 3)

        # Create a clean new palette
        self._new_palette = displayio.Palette(len(self._src_palette))

        # Adjust for normalization, brightness, and gamma
        norm_palette = []
        for index, color in enumerate(self._ref_palette):
            new_r = int(min((color[0] * self._norm_factor) ** self._gamma, 0xFF))
            new_g = int(min((color[1] * self._norm_factor) ** self._gamma, 0xFF))
            new_b = int(min((color[2] * self._norm_factor) ** self._gamma, 0xFF))

            norm_palette.append([new_r, new_g, new_b])

        # Build new_palette with the newly adjusted color values
        for index, color in enumerate(norm_palette):
            self._new_palette[index] = (color[0] << 16) + (color[1] << 8) + color[2]

            if index in self._list_transparency:
                # Set new_palette color index transparency status
                self._new_palette.make_transparent(index)
