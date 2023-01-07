### I2C Bus Fix
[Long form YouTube video detailing the steps here](https://www.youtube.com/watch?v=9BEkuAYmjx0) if you're more comfortable seeing someone else walk through the fix.


[![YT_thumb](https://user-images.githubusercontent.com/49322231/211144300-f74537c0-09ea-4c44-a715-41851e6dc60d.PNG)](https://www.youtube.com/watch?v=9BEkuAYmjx0)

There are 3 steps that are highly recommended for all existing TR-Cowbell v1.2 owners. Any future v1.2 boards going out to new owners will already have the traces cut.

The order in which these 3 modifications are done doesn't matter as long as all 3 are done.

- Trace Cut (if you're a new owner and there's a purple blob there it's already been done for you)

![Trace Cut](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/raspberrypi/Raspberry%20Pi%20Pico/TR%20Cowbell/v1.2%20Hardware%20I2C%20Bus%20Fix/Trace_Cut.jpg)

- Multiplexer I2C Chaining

![Chip to Chip Bodge Wire](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/raspberrypi/Raspberry%20Pi%20Pico/TR%20Cowbell/v1.2%20Hardware%20I2C%20Bus%20Fix/Chip-to-chip_Bus_Fix.jpg)

- I2C Address Change for Multiplexer Chip

This only applies to the left multiplexer chip. The right multiplexer chip should have all 3 pads soldered to GND.

![I2C Address Change](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/raspberrypi/Raspberry%20Pi%20Pico/TR%20Cowbell/v1.2%20Hardware%20I2C%20Bus%20Fix/Address_Fix.jpg)

### Result
- Both multiplxers will be on a single bus. Bus I2C0. The first multiplexer will have the address 0x21 and the second will be 0x20.
- Completely frees up I2C Bus 1 (any pin on I2C1 becomes available).
- Allows the Stemma QT port and Stemma breakout to work on pins GP27 & GP26.
