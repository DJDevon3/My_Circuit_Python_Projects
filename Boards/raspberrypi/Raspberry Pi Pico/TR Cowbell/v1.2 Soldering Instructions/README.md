# TR-Cowbell v1.2 Soldering

### Soldering Sequence:
1. Solder all 16 step switches first. The reason is due to GND trace length which requires very long heating duration, if you have a hotplate or pre-heater you could try that. I don't have one so I had to hold the iron on a GND pin for minutes sometime as the entire GND plane of the board heated up. The positive pins on the step switches heat up extremely fast. 

![Step_Switch_Soldering](https://user-images.githubusercontent.com/49322231/208536970-5ecae4f0-c8e8-4ae8-b795-24cea7dcfd85.jpg)

2. The 16x 500 ohm resistors are actually 68 Ohm resistors. It's all I had. 68 ohms works fine even while all lit up simultaneously for hours. It's just a bit brighter. If you want to substitute higher resistor values for dimmer LED's by all means do.
3. All female header sockets on the PCB & stacking headers on the Pico W. I highly recommend using the included stacking headers for easy GPIO breakouts on any pin.
4. Solder both 28-pin female DIP sockets to the board. When finished press fit the MCP23017 chips into them.
5. Solder jump only the first 2 I2C address pads to GND for the left multiplexer chip (the reason why detailed in step 12). 
6. The second multiplexer chip should have all 3 I2C address pads soldered to the GND pads.
7. The 8-pin optoisolator chip (no DIP socket included) must be soldered directly to the board.
8. Do not attempt to pre-tin the pads for the TRS midi jacks. There are alignment holes. Press fit the jacks and solder in place.
9. 4.7K and remaining resistors and small round capacitor.
10. Rotary encoder. The large legs require a ton of solder, you'll find the small GND pins just as hard to solder as the step switch GND pins. Without a lot of heat you'll get cold joints and intermittent connection.
11. 6mm buttons legs can only be installed in the correct orientation, kind of dummy proof, same for Pico Reset button.
12. After the board is complete then some [bodge fixes for the I2C bus design flaw must be done](https://github.com/DJDevon3/My_Circuit_Python_Projects/tree/main/Boards/raspberrypi/Raspberry%20Pi%20Pico/TR%20Cowbell/v1.2%20Hardware%20I2C%20Bus%20Fix).

### Installing Circuit Python
With all soldering complete head over to CircuitPython.org/downloads and get the 8.0 beta release for the Pi Pico W. 

Demo code (including necessary libraries) are hosted here on Github in the TR Cowbell directory. All it does is blink like a sequencer. I have yet to write any functional audio code but when that happens all updates will be found in this repository. 

### TR-Cowbell Updates
All anouncements will be made via Adafruit Discord & on Mastodon. If you haven't added me yet please do TreasureDev@Hackaday.social Feel free to reach out to me at any time with any questions or just to chat. My door is open at all times.

The beauty of Circuit Python is when there is an update
1. It's not forced upon you. You choose if or when to update.
2. Updates are drag & drop to the Pi Pico USB drive, simple & efficient.
3. You can submit PR's for code examples, improvements, bugs, issues, etc.. right here through Github. Simply clone the repo and push a PR the same as you'd do for Circuit Python Github.

### Extra's
- Some beta testers will have missing extra components as I ran out of parts. All core components required to get the board working are included. Some kits came with an SSD1306 display. There is different example code in the repo for a board with or without a display.
