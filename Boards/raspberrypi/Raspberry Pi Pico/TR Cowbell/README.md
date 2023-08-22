# TR-Cowbell Page (all versions)
TR Cowbell is a Midi Sequencer/Macropad PCB designed by DJDevon3 & powered by Raspberry Pi Pico or Pico W.

![Based on PicoStepSeq by @Todbot](https://github.com/todbot/picostepseq)

# Features
- 16 TR-808 style sequencer switches
- 5 tacticle general purpose buttons
- 1 general purpose rotary encoder
- 1 TRS MIDI IN
- 1 TRS MIDI OUT
- 1 board reset tacticle button

![](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/raspberrypi/Raspberry%20Pi%20Pico/TR%20Cowbell/Pictures/v1.2_screenshot.jpg)


Watch FoamyGuy bring the TR-Cowbell to life with bleeps and bloops! Image is a link to his YouTube video.  
[![Foamy_Guy_TR-Cowbell](https://user-images.githubusercontent.com/49322231/209728878-aee7aa86-ee7d-4b8d-9cf7-07cdacc37603.PNG)](https://youtu.be/QR1UXm6L_6I)

- I highly recommend using [FoamyGuy's TR-Cowbell Sequencer Software](https://github.com/FoamyGuy/TR_Cowbell_Sequencer_Software) instead of my basic code.py demo for real midi usage. 


[OSWHLab Schematic View](https://oshwlab.com/djdevon3/tr-cowbell) Click On "Open in Editor" to get to the interactive view. 

Please ensure you're looking at the correct version of the schematics & PCB for your version. v1.3 is currently in development and I can't guarantee it will always show the v1.2 version by default. The bottom right hand corner of the schematic view shows the schematic (board) version. I use EasyEDA online editor for PCB design (like an online version of EAGLE), EasyEDA projects can be shared directly to the public via a built-in integration with OSHWLab (Open-Source Hardware Lab).

[![Interactive Schematic](https://user-images.githubusercontent.com/49322231/211129691-dff79537-d356-4c8f-8018-5aee37fdd8c6.PNG)](https://oshwlab.com/djdevon3/tr-cowbell) 

[OSWHLab PCB View](https://oshwlab.com/djdevon3/tr-cowbell) Click On "Open in Editor" to get to the interactive view. 
[![board_edit](https://user-images.githubusercontent.com/49322231/211129802-da455512-baab-4bc4-bef5-35cfddc2690f.PNG)](https://oshwlab.com/djdevon3/tr-cowbell) 

### MCP23017 Notes:
You cannot use the Adafruit Keypad library with MCP23017 chips due to a difference in the way it reads shift registers. You must instead use the MCP23017_scanner library (by Neradoc) which is a keypad library specifically for MPC23017 chips. Think of it more as a MCP23017_Keypad library.

If this is your first time working with the MCP23017 please note that the Circuit Python MCP23017 library expects a pin value of 0-15. They are in order of Port A on the right side of the chip from bottom to top, then top to bottom on Port B which is the left side of the chip. It's very easy to confuse the pinout numbers. The order of the scanner library prioritizes Port A first then Port B in a counter-clockwise order. It makes more sense working with the library if you consider Port A pins come first.

![](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/raspberrypi/Raspberry%20Pi%20Pico/TR%20Cowbell/MCP%20Diagram.jpg)

You can manually specify if a pin should be an INPUT (switch) or OUTPUT (led) pin `pin.direction = Direction.INPUT` There is no PWM or voltage capability only on/off by pulling a pin high or low, it's digital.

Reset should be provided 3v3 and you pull that to GND to actually reset the chip. It's easier most cases to just reset the board but in the unlikely event that you should ever need a physical chip reset, that feature is built into the chip. Since it's tied to 3v3 the MCP chips reset whenever the TR-Cowbell is reset or unpowered/powered. This is by design to make things easier but if it becomes an issue for modifications you want to do in the future please realize the chip reset traces are part of the board design.

### MCP23017 I2C Pull-Up Circuit
This is now a known good circuit for the MCP23017 (I designed it). This will allow your chip to be detected by the microcontroller as an I2C device. Only 1 of 2 MCP's are shown here but both are identical schematics except for the net port. Chip 0 is on bus 0 and chip 1 is on bus 1. What I should have done is use a net label instead of a net port so both MCP chips would have used the same SDA and SCL traces. That would have chained them to the same bus. It's already been corrected in v1.3 but sometimes it's important to document your failures as well as your successes.

![](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/raspberrypi/Raspberry%20Pi%20Pico/TR%20Cowbell/MCP23017_Pullup_Diagram.PNG)

## MCP23017 I2C Addressing
- This is advice aimed at other PCB designers on the internet who are working with the MCP23017 multiplexer. Learn from my mistake.

The way I laid out the I2C addresses pads in v1.2 is incorrect. It definitely works for the purpose of the board but it prevents I2C expansion. 

Each address signal pin (3 of them) should either be high (3v3) or low (GND). I was treating it like a normal I2C device that only needed GND to change the address. I've learned the hard way that is incorrect for the MCP23017. Since I only provided jumper pads to GND it means you can only have the address of 0x20 (all 3 pads grounded). 

The MCP chips do not allow for any address floating (unsoldered), the MCP23017 chip will exhibit erratic behavior with a floating address pin. It will randomly change addresses leaving you scratching your head and later pulling your hair out. Each address must absolutely either be high or low. All low is 0x20. 

The reason both MCP23017's were all (originally) soldered low (both have address 0x20) on the TR-Cowbell v1.2 is because they're on 2 different I2C buses. While it does work it doesn't allow for easy I2C expansion. This was a big mistake as the Pico only has 2 I2C buses, and both buses are always "in use" each by 1 MCP23017 chip. The bodge fix now fixes that issue. 

Mistake: 2 rows of pads (GND, Signal). Correct: 3 rows of pads (GND, Signal, 3V3)

![MCP23017 Addressing](https://user-images.githubusercontent.com/49322231/209738852-a7c5ebf0-e847-41f2-91fd-223725190221.jpg)

To change the address on an MCP23017 both GND and 3v3 pads should have been be provided (as pictured). This is something I've already fixed in v1.3 with dip switches, no soldering of jump pads will be necessary to change the I2C address of the MCP chips in future revisions. As for a bodge fix to change the address on 1 of the chips means using the signal pad and running a wire to a 3v3 source. That will only change the address, ensuring both chips are on the same bus is a different issue.

![i2c_devices](https://user-images.githubusercontent.com/49322231/209739560-fe98bdec-a6be-4387-ac1d-8067821e12e9.png)

### Adding I2C Devices to the Pi Pico on the TR-Cowbell v1.2
You can still tap into either I2C bus using GP10 & GP11 for Bus 1 or GP12 & GP13 for Bus 0. This is the reason why I included stacking headers with all kits. I highly recommend using the stacking headers as it will make your life easier if you ever decide to use the Pico for external purposes like adding a display. Doing the [bodge I2c fix](https://github.com/DJDevon3/My_Circuit_Python_Projects/tree/main/Boards/raspberrypi/Raspberry%20Pi%20Pico/TR%20Cowbell/v1.2%20Hardware%20I2C%20Bus%20Fix) addresses the issue of using up both I2C busses for v1.2 owners.

### MCP23017 Pin Confusion
It's OK to be confused at some point about which pins go where. There are so many overlapping numbers it's quite easy to mix things up. As long as all MCP pins are traced to switches and or LED's you can always fix pin mappings in software.
