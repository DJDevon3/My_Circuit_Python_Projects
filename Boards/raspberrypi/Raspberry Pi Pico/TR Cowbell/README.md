# TR-Cowbell
TR Cowbell powered by Raspberry Pi Pico by DJDevon3

![Based on PicoStepSeq by @Todbot](https://github.com/todbot/picostepseq)

My first major custom board!!!

![](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/raspberrypi/Raspberry%20Pi%20Pico/TR%20Cowbell/Pictures/v1.2_screenshot.jpg)

https://user-images.githubusercontent.com/49322231/191885653-31921617-1a46-4c9c-91a2-286ba2231128.mov

### MCP23017 Notes:
You cannot use the Adafruit Keypad library with MCP23017 chips due to a difference in the way it reads shift registers. You must instead use the MCP23017_scanner library which is a keypad library built specifically for MPC3017 chips. Think of it more as a MCP23017_Keypad library.

If this is your first time working with the MCP23017 please note that the Circuit Python MCP23017 library expects a pin value of 0-15. They are in order of Port A on the right side of the chip from bottom to top, then top to bottom on Port B which is the left side of the chip. It's very easy to confuse the pinouts since they're in opposite logical order from what most people would consider a normal order.

![](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/raspberrypi/Raspberry%20Pi%20Pico/TR%20Cowbell/MCP%20Diagram.jpg)

Reset should be provided 3v3 and you pull that to GND to actually reset the chip. It's easier most cases to just reset the board but in the unlikely event that you should ever need it that feature is available.

### MCP23017 I2C Pull-Up Circuit
This is now a known good circuit for the MCP23017 (I designed it). This will allow your chip to be detected by the microcontroller as an I2C device. You can have up to 8 chips on the same physical bus. The chip only allows for a maximum of 8 different I2C addresses via solder jumper pads (to GND). Since I'm using the Pi Pico which has 2 separate I2C busses you can have a maximum of 16 chips per microcontroller, 8 chips per bus. With 16 GPIO per chip x 16 chips = 256 GPIO maximum! My board only uses 32 on 2 chips.

![](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/raspberrypi/Raspberry%20Pi%20Pico/TR%20Cowbell/MCP23017_Pullup_Diagram.PNG)
