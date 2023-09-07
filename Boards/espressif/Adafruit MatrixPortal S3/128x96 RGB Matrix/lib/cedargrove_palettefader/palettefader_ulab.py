# SPDX-FileCopyrightText: Copyright (c) 2022 JG for Cedar Grove Maker Studios
#
# SPDX-License-Identifier: MIT
"""
`cedargrove_palettefader`
================================================================================

PaletteFader is a CircuitPython driver class for brightness-adjusting color
lists and displayio palettes. Normalization is optionally applied to the palette
prior to brightness and gamma adjustments. Transparency index values are
preserved and associated with the adjusted palette. Creates an adjusted
displayio color palette object (displayio.Palette) that can also be read as a
color list.

For adjusting a single color value, create a list containing a single color or
use cedargrove_unit_converter.color.colorfader.color_fader().

cedargrove_palettefader.py v2.0.1 2022-09-03

* Author(s): JG for Cedar Grove Maker Studios

Implementation Notes
--------------------

The ulab-based reference palette creation code runs slightly faster than the
"vanilla" version. The ulab code was adapted from the Adafruit Ocean Epoxy
Lightbox project's Reshader class; Copyright 2020 J Epler and L Fried.
<https://learn.adafruit.com/ocean-epoxy-resin-lightbox-with-rgb-led-matrix-image-scroller>

**Hardware:**

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  <https://circuitpython.org/downloads>

"""

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/CedarGroveStudios/CircuitPython_PaletteFader.git"

from ulab import numpy
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

        # Create the ulab array reference palette with source palette RGB values
        self._ref_palette = numpy.zeros((len(self._src_palette), 3), dtype=numpy.uint8)
        for index, rgb in enumerate(self._src_palette):
            if rgb is not None:
                self._ref_palette[index, 2] = rgb & 0x0000FF
                self._ref_palette[index, 1] = (rgb & 0x00FF00) >> 8
                self._ref_palette[index, 0] = (rgb & 0xFF0000) >> 16

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
            self._ref_palette_max = numpy.max(self._ref_palette)
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

        # Adjust for normalization and brightness
        norm_palette = numpy.array(
            self._ref_palette * self._norm_factor, dtype=numpy.uint8
        )
        # Adjust result for gamma
        norm_palette = numpy.array(norm_palette**self._gamma, dtype=numpy.uint8)

        # Build new_palette with the newly adjusted color values
        for index in range(len(norm_palette)):
            self._new_palette[index] = (
                (norm_palette[index, 0] << 16)
                + (norm_palette[index, 1] << 8)
                + norm_palette[index, 2]
            )

            if index in self._list_transparency:
                # Set new_palette color index transparency status
                self._new_palette.make_transparent(index)
