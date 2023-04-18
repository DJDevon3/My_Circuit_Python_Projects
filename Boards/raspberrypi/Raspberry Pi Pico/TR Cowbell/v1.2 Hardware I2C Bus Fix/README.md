# TR-Cowbell I2C Bus Fix
[YouTube video detailing the steps here:](https://www.youtube.com/watch?v=3ejMCdRwh7k) if you're more comfortable watching along through the fix.

[![TR-Cowbell_BusFixShort_YT_Thumb](https://user-images.githubusercontent.com/49322231/211189901-b09f23b2-a9f9-4fdd-8465-f19c128467ff.PNG)](https://www.youtube.com/watch?v=3ejMCdRwh7k)

After the board is completely soldered (refer to soldering instructions) there are 3 steps that are highly recommended for all existing TR-Cowbell v1.2 owners. Any future v1.2 boards going out to new owners will already have the traces cut, forcing them to do this modification to finish the board.

The order in which these 3 modifications are done doesn't matter as long as all 3 are done.

## (1) Trace Cuts of GP10 & GP11
If you've received a board during the 2nd batch the trace cuts have already been done for you. You will see a purple nail polish blob on the area of the trace cuts to denote step 1 has already been done. 

1st batch owners all received boards prior to Christmas 2022 did not have this modification done prior to shipping. I didn't find the issue until after batch 1 shipped.

![Trace Cut](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/raspberrypi/Raspberry%20Pi%20Pico/TR%20Cowbell/v1.2%20Hardware%20I2C%20Bus%20Fix/Trace_Cut.jpg)

## (2) Multiplexer I2C Chaining
![Chip-to-chip_Bus_Fix](https://user-images.githubusercontent.com/49322231/222978434-7d9709ab-7461-4cfc-8b64-d47d8ed059f4.jpg)
![image1](https://user-images.githubusercontent.com/49322231/222978596-13afe27b-b334-4ccf-8545-d01a4a31efd7.jpg)

## (3) I2C Address Change

This only applies to the left multiplexer chip. The right multiplexer chip should have all 3 pads soldered to GND.

![I2C Address Change](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/raspberrypi/Raspberry%20Pi%20Pico/TR%20Cowbell/v1.2%20Hardware%20I2C%20Bus%20Fix/Address_Fix.jpg)

![image0](https://user-images.githubusercontent.com/49322231/222978591-6c1f40ce-90d2-47fa-a2a1-304b7bff9a8b.jpg)

### Result
- Both multiplxers will be on a single bus. Bus I2C0. The first multiplexer will have the address 0x21 and the second will be 0x20.
- Completely frees up I2C Bus 1 (any pin on I2C1 becomes available).
- Allows the Stemma QT port and Stemma breakout to work on pins GP27 & GP26.
- INTA, INTB, and SWD debug header pins are not used but made available if desired

### The board is now complete and ready for Circuit Python use.
- Download [Circuit Python for the Raspberry Pi Pico W here](https://circuitpython.org/board/raspberry_pi_pico_w/).
- Adafruit Learn Guide for [Installing Circuit Python on the Pico W here](https://learn.adafruit.com/pico-w-wifi-with-circuitpython/installing-circuitpython).
