# TR-Cowbell
TR Cowbell powered by Raspberry Pi Pico by DJDevon3

![Based on PicoStepSeq by @Todbot](https://github.com/todbot/picostepseq)

My first major custom board! Project is progressing very slowly. 

![](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/raspberrypi/Raspberry%20Pi%20Pico/TR%20Cowbell/Pictures/IMG_0449.JPG)

### Version 1.0 (prototype)
Gorgeous PCB but there are hardware problems in the initial design that had to be fixed with bodge wire. All of these issues are my fault due to adding complexity with an I2C expander design.

![](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/raspberrypi/Raspberry%20Pi%20Pico/TR%20Cowbell/Pictures/IMG_0453.jpg)

### Design Screw Ups
- Bad pull up design to MCP23017 I2C SDA & SCL pins. Pull ups were unpowered so they became pull downs, oops.
- Backwards pinouts on MCP23017 due to using a confusing footprint from EasyEda.
- Resistor values for switch LED's too low (4.7K too dim in daylight) changed to 500 ohm.
### Design Happy Accidents
- Instead of going with the impulse of putting all 16 led's on 1 chip, I split the current load of 8 LED's to both chips.
- Very safe LED resistor value of 4.7K ensured I didn't burn out an LED or chip with high current load.
- Pico reset switch works great
- Encoders work but are too close together (replacing with single ANO encoder in v1.2)
- Dark colored board makes LED's stand out more. Will likely go with purple again for v1.2
- Obnoxiously loud name tag, I like it, it stays.
- External SPI breakout provided easy access to 3V3 power bus and GND in case they were needed, and they were.

https://user-images.githubusercontent.com/49322231/191885653-31921617-1a46-4c9c-91a2-286ba2231128.mov

Finished with the hw test of the LED's and switches.

Next is to integrate the keypad library

### Version 1.2 (re-design phase)
- Schematic, PCB, and BOM available on my ![TR-Cowbell EasyEDA OSHWLab Project Page](https://oshwlab.com/djdevon3/tr-cowbell)
- Design screw ups already fixed in the v1.2 PCB layout.
- Replaced dual rotary encoders with single ANO encoder wheel
- Added breakout for ANO encoder for enclosures
- Replaced my name on top silkscreen with TR-Cowbell, moved name to bottom silkscreen in Papyrus font.
- Not yet ready to print v1.2 PCB as all HW tests have yet to be conducted and confirmed (Midi in/out).
