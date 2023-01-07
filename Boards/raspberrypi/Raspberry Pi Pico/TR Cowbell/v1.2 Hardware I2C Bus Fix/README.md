### I2C Bus Fix
There are 3 steps that are highly recommended for all existing TR-Cowbell v1.2 owners. Any future v1.2 boards going out to new owners will already have the traces cut.

The order in which these 3 modifications are done doesn't matter as long as all 3 are done.

- Trace Cut

![Trace Cut](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/raspberrypi/Raspberry%20Pi%20Pico/TR%20Cowbell/v1.2%20Hardware%20I2C%20Bus%20Fix/Trace_Cut.jpg)

- Multiplexer I2C Chaining

![Chip to Chip Bodge Wire](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/raspberrypi/Raspberry%20Pi%20Pico/TR%20Cowbell/v1.2%20Hardware%20I2C%20Bus%20Fix/Chip-to-chip_Bus_Fix.jpg)

- I2C Address Change

![I2C Address Change](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/raspberrypi/Raspberry%20Pi%20Pico/TR%20Cowbell/v1.2%20Hardware%20I2C%20Bus%20Fix/Address_Fix.jpg)

### Result
This completely frees up I2C Bus 1 (any pin on I2C1 becomes available) plus allows the Stemma QT and Stemma breakout to work.
