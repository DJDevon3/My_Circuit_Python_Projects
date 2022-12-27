# TR-Cowbell Page (all versions)
TR Cowbell is a Midi Sequencer/Macropad PCB designed by DJDevon3 & powered by Raspberry Pi Pico or Pico W.

![Based on PicoStepSeq by @Todbot](https://github.com/todbot/picostepseq)

![](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/raspberrypi/Raspberry%20Pi%20Pico/TR%20Cowbell/Pictures/v1.2_screenshot.jpg)


Watch FoamyGuy bring the TR-Cowbell to life! Image is link to YouTube video.
[![Foamy_Guy_TR-Cowbell](https://user-images.githubusercontent.com/49322231/209728878-aee7aa86-ee7d-4b8d-9cf7-07cdacc37603.PNG)](https://youtu.be/QR1UXm6L_6I)


Please ensure you're looking at the correct version of the schematics & PCB for your version. v1.3 is in development and I can't guarantee it will always show the v1.2 version by default. The bottom right hand corner of the schematic view shows the schematic (board) version. I use EasyEDA online editor for PCB design (like an online version of EAGLE), EasyEDA projects can be shared directly to the public via a built-in integration with OSHWLab (Open-Source Hardware Lab).

[![TR-Cowbell_v1 2-Schematic](https://user-images.githubusercontent.com/49322231/209725513-20c01e94-87d0-4c22-b644-affb2cfb170e.jpg)](https://oshwlab.com/djdevon3/tr-cowbell) 


### MCP23017 Notes:
You cannot use the Adafruit Keypad library with MCP23017 chips due to a difference in the way it reads shift registers. You must instead use the MCP23017_scanner library (by Neradoc) which is a keypad library specifically for MPC23017 chips. Think of it more as a MCP23017_Keypad library.

If this is your first time working with the MCP23017 please note that the Circuit Python MCP23017 library expects a pin value of 0-15. They are in order of Port A on the right side of the chip from bottom to top, then top to bottom on Port B which is the left side of the chip. It's very easy to confuse the pinouts since they're in opposite order from the physical pin order. The order of the scanner library prioritizes Port A first then Port B in a counter-clockwise order. It makes more sense working with the library if you consider Port A pins come first.

![](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/raspberrypi/Raspberry%20Pi%20Pico/TR%20Cowbell/MCP%20Diagram.jpg)

You can manually specify if a pin should be an INPUT (switch) or OUTPUT (led) pin `pin.direction = Direction.INPUT` There is no PWM or voltage capability only on/off by pulling a pin high or low, it's digital.

Reset should be provided 3v3 and you pull that to GND to actually reset the chip. It's easier most cases to just reset the board but in the unlikely event that you should ever need a physical chip reset, that feature is built into the chip. Since it's tied to 3v3 the MCP chips reset whenever the TR-Cowbell is reset or unpowered/powered. This is by design to make things easier but if it becomes an issue for modifications you want to do in the future please realize the chip reset traces are part of the board design.

### MCP23017 I2C Pull-Up Circuit
This is now a known good circuit for the MCP23017 (I designed it). This will allow your chip to be detected by the microcontroller as an I2C device. You can have up to 8 chips on the same physical bus. The chip only allows for a maximum of 8 different I2C addresses via solder jumper pads. Since I'm using the Pi Pico which has 2 separate I2C busses you can have a maximum of 16 chips per microcontroller in a non-matrix layout. 8 chips per bus, 2 busses. With 16 GPIO per chip x 16 chips = 256 GPIO maximum! My board only uses 32 on 2 chips.

On my next revision I'm going to rename the LED nets to match the pins. LED1 currently = GP0, will change to LED0 = GP0 so everything cleanly lines up.

![](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/raspberrypi/Raspberry%20Pi%20Pico/TR%20Cowbell/MCP23017_Pullup_Diagram.PNG)

## MCP23017 I2C Addressing
The way I laid out the addressing in v1.2 is incorrect. Each address pin (3 of them) can either be high (3v3) or low (GND).  Since I only provided jumper pads to GND it means you can only have the address of 0x20 (all 3 pads grounded). You cannot leave any address floating (unsoldered), the MCP23017 chip will exhibit erratic behavior with a floating address pin. It will randomly change addresses leaving you scratching your head and later pulling your hair out. Each address must absolutely either be high or low. All low is 0x20. The reason both MCP23017's are all soldered low on the TR-Cowbell v1.2 is because they're on 2 different I2C buses. This was a big mistake as the Pico only has 2 I2C buses, and both buses are always "in use" each by 1 MCP23017 chip. :(

To change the address on an MCP23017 both GND and 3v3 pads should have been be provided. This is something I've already fixed in v1.3 with dip switches, no soldering of jump pads will be necessary to change the I2C address of the MCP chips in future revisions. 

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

### MCP23017 Pin Confusion
It's OK to be confused at some point about which pins go where. There are so many overlapping numbers it's quite easy to mix things up. As long as all MCP pins are traced to switches and or LED's you can always fix pin mappings in software.
