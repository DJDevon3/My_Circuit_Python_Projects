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
This is now a known good circuit for the MCP23017 (I designed it). This will allow your chip to be detected by the microcontroller as an I2C device. You can have up to 8 chips on the same physical bus. The chip only allows for a maximum of 8 different I2C addresses via solder jumper pads (to GND). Since I'm using the Pi Pico which has 2 separate I2C busses you can have a maximum of 16 chips per microcontroller in a non-matrix layout. 8 chips per bus, 2 busses. With 16 GPIO per chip x 16 chips = 256 GPIO maximum! My board only uses 32 on 2 chips.

On my next revision I'm going to rename the LED nets to match the pins. LED1 currently = GP0, will change to LED0 = GP0 so everything cleanly lines up.

![](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/raspberrypi/Raspberry%20Pi%20Pico/TR%20Cowbell/MCP23017_Pullup_Diagram.PNG)

### Keys with LED's
- If your board has keys with LED's (like the TR-Cowbell does) it's best to put the corresponding LED & Key on the same pin # per port.  So LED0 would be on Library Pin 8 and Switch0 would be on Library Pin 0.
- Example: 8 and 0, 9 and 1, 10 and 2, etc...  This scheme is present on the TR-Cowbell.
- This is because the main MCP23017 library has a built in way to automatically map Port A pin 0 to Port B pin 0 and so on. Specifically designed with key + led in mind. To make your life easier I highly recommend using this design.
- Also it's best practice to split the chip into half switches and half LED's to keep the overall max current draw to a minimum. It is possible to fry the chip if you fill it with 16 high power LED's drawing 25-30ma of current per LED for example (and using no resistor). 
- You still need to add a resistor per output LED (not required for input switches). Resistor value recommended around 500 ohm for normal 2-pin LED's. Anywhere between 100 ohm down to 1000 ohm is fine. LED starts getting too dim to see around 3K ohm.

### Keys without LED's
- Though not used in my particular board design if you want to make a keyboard with the maximum amount of keys and no LED's then load up each GPIO with switches. Keyboard keys are input devices and consume no current unlike output devices like LED's so it's safe to load up all 16 with input switches.
- If you intend on making a keyboard with MCP23017 chips a better idea is to use the mcp23017_scanner matrix class and example within the mcp23017_scanner library. You can split each GPIO as a row or column for 64 keys (8x8 grid) per chip! With a maximum of 16 chips (8 chips per I2C bus) that means the total possible amount of keys is 64 * 16 = 1024 keys!!! 
- Ask in Adafruit Discord what the best PCB layout for the mcp23017_scanner matrix library expects to work with (probably diode matrix).

### Pin Confusion
It's OK to be confused at some point about which pins go where. There are so many overlapping numbers it's quite easy to mix things up. If you're a board designer just stick with the layout I have here and you'll be OK. You can always fix pin mapping in software though you will complicate your life in using the Adafruit libraries if you do as the pin maps are intended to be used in a specific way.
