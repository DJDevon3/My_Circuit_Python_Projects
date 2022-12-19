# TR-Cowbell v1.2 Soldering

### Soldering Sequence:
1. Solder all 16 step switches first. The reason is due to GND trace length which requires very long heating duration, if you have a hotplate or pre-heater you could try that. I don't have one so I had to hold the iron on a GND pin for minutes sometime as the entire GND plane of the board heated up. The positive pins on the step switches heat up extremely fast. **(I will add pictures here soon)** to detail which pins are GND that are likely to give you the most trouble and cold solder joints galore.
2. The 16x 500 ohm resistors are actually 68 Ohm resistors. It's all I had. If you want to substitute for different values by all means do.
3. All female header sockets & stacking headers on the Pico W.
4. 28-pin DIP sockets and press fit the MCP23017 chips in them.
5. Solder jump all 6 I2C address pads. The MCP chips will provide wild results if those pads are left floating unjumped. Each MCP23017 has hex address 0x20, 1 per I2C bus (a mistake since there are only 2 busses).
6. The 8-pin optoisolator chip (no DIP socket included) must be soldered directly to the board.
7. Do not attempt to pre-tin the pads for the TRS midi jacks. There are alignment holes. Press fit the jacks and solder in place.
8. 4.7K and remaining resistors and small round capacitor.
9. Rotary encoder. The large legs require a ton of solder, you'll find the small GND pins just as hard to solder as the step switch GND pins. Without a lot of heat you'll get cold joints and intermittent connection.
10. 6mm buttons legs can only be installed in the correct orientation, kind of dummy proof, same for Pico Reset button.

### Installing Circuit Python
When you've got everything soldered up and ready then head over to CircuitPython.org/downloads and get the 8.0 beta release for the Pi Pico W. 

Demo code (including necessary libraries) and here on Github in the TR Cowbell directory. All it does is blink like a sequencer. I have yet to write any functional audio code but when that happens all updates will be found in this repository. 

### TR-Cowbell Updates
All anouncements for updates will probably made via my Mastodon account so if you haven't added me yet please do TreasureDev@Hackaday.social

### Issues
1. The stemma port and stemma breakout don't work unless you bodge wire a fix. It's easier just to plug into the stacking header for pins (GP10 & GP11 for I2C bus 1) or (GP12 & GP13 for bus 0). This is why I included stacking headers for easy breakouts in case something went wrong, and it did.
2. Some beta testers will have missing extra components as I ran out of parts. They don't detract from the function of the board via serial print. All core components required to get the board working are included.

### Extra's Info
1. Some kits came with an SSD1306 display. There's different example code in the repo for a board with or without the display.
