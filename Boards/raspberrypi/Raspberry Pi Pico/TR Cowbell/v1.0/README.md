# TR-Cowbell
TR Cowbell powered by Raspberry Pi Pico by DJDevon3

![Based on PicoStepSeq by @Todbot](https://github.com/todbot/picostepseq)

My first major custom board!!!

![](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/raspberrypi/Raspberry%20Pi%20Pico/TR%20Cowbell/Pictures/IMG_0449_oshwa.jpg)

### Version 1.0 (prototype)
Gorgeous PCB but there are hardware problems in the initial design that had to be fixed with bodge wire. All of these issues are my fault due to adding complexity with an I2C expander design.

![](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/raspberrypi/Raspberry%20Pi%20Pico/TR%20Cowbell/Pictures/IMG_0453.jpg)

### Design Screw Ups
- Bad pull up design to MCP23017 I2C SDA & SCL pins. Pull ups were unpowered so they became pull downs, oops.
- Backwards pinouts on MCP23017 due to using a confusing footprint from EasyEda. Fixed by remapping pins in software.
- Resistor values for switch LED's too low (4.7K too dim in daylight) changed to 500 ohm.
- Wrong footprint for encoder, had to cut the bottom of the pins on an angle to fit into the hole.
- Encoders work but are too close together (replacing 1 of them with 6mm button switches in v1.2)
- The board does work, just requires bodge wire in a few places.

### Design Happy Accidents
- Instead of going with the impulse of putting all 16 led's on 1 chip, I split the current load of 8 LED's to both chips.
- Very safe LED resistor value of 4.7K ensured I didn't burn out an LED or chip with high current load.
- Pico reset switch works great
- Dark colored board makes LED's stand out more in the dark. Will likely go with purple again for v1.2
- External SPI breakout provided easy access to 3V3 power bus and GND in case they were needed, and they were.

https://user-images.githubusercontent.com/49322231/191885653-31921617-1a46-4c9c-91a2-286ba2231128.mov

Finished with the hw test of the LED's and switches.

Next is to integrate the keypad library

### Version 1.2 (re-design phase)
- Schematic, PCB, and BOM available on my ![TR-Cowbell EasyEDA OSHWLab Project Page](https://oshwlab.com/djdevon3/tr-cowbell)
- Design screw ups already fixed in the v1.2 PCB layout.
- Replaced dual rotary encoders with 1x encoder and 5x 6mm buttons.
- Fixed encoder footprint to use proper PECL11 footprint. Fits great now!
- Added 10 pin GPIO breakout header (all remaining unused pins) from the Pico 
- Replaced my name on top silkscreen with TR-Cowbell, moved name to bottom silkscreen in Papyrus font.
- Replaced 500 ohm resistors with 68 ohm resistors for maximum brightness. All light up no problem. Didn't have any resistors in the 100 ohm range on hand, ordered a bunch. 68 ohm is skirting it pretty close to the MCP's maximum current draw for 8x 20ma LED's.

# BOM (Bill of Materials)
### For basic USB MIDI functionality:
- 1 - "TR-Cowbell" PCB ([JLPCB](https://oshwlab.com/djdevon3/tr-cowbell))
- 1 - Raspberry Pi Pico ([Digikey](https://www.digikey.com/en/products/detail/raspberry-pi/SC0915/13624793), [Adafruit](https://www.adafruit.com/product/4864)) OR Pi Pico W ([Digikey](https://www.digikey.com/en/products/detail/raspberry-pi/SC0918/16608263))
- 16 - PB86A "step switch" w/ built-in LED ([Adafruit](https://www.adafruit.com/product/5519))
- 1 - PEC11R (S-Type) Rotary Encoder ([Digikey](https://www.digikey.com/en/products/detail/bourns-inc/PEC11R-4215F-S0024/4499665))
- 2 - Anodized Aluminum Machined Knob - Blue - 20mm Diameter ([Adafruit](https://www.adafruit.com/product/5529))
- 16 - LED resistor value anywhere between 100 to 1000 ohm (R1-R16) ([Digikey](https://www.digikey.com/en/products/detail/yageo/CFR-12JR-52-470R/17647), [Adafruit](https://www.adafruit.com/product/2781))
- 2 - MCP2307 E/SP I2C Expander Bare Chips ([Digikey](https://www.digikey.com/en/products/detail/microchip-technology/MCP23017-E-SP/894272), [Adafruit](https://www.adafruit.com/product/732))
- 2 - 28-pin .3" ZIF sockets for MCP23107 chips (Optional but recommended) ([Adafruit](https://www.adafruit.com/product/2205))
- 6 - 6mm tactile button switches (Pico Reset & Navigation) ([Adafruit](https://www.adafruit.com/product/367))

### For both USB + Serial MIDI, add:
- 2 - 3.5mm TRS jack, SJ-3523-SMT-TR (J3, J4)
([Digikey](https://www.digikey.com/en/products/detail/cui-devices/SJ-3523-SMT-TR/281297))
- 1 - 6N138 optoisolator (U2) ([Digikey](https://www.digikey.com/en/products/detail/liteon/6N138/1969179))
- 1 - 100n capacitor (C2) ([Digikey](https://www.digikey.com/en/products/detail/vishay-beyschlag-draloric-bc-components/K104K15X7RF5TL2/286538), [Adafruit](https://www.adafruit.com/product/753))
- 1 - resistor 220 ohm (R17)
- 1 - resistor 33 ohm (R19) (47 ohm also works)
- 1 - resistor 10 ohm (R20)
- 5 - resistor 4.7k ohm (R18, R21, R22, R23, R24)

And if you've not used ["TRS MIDI"](https://minimidi.world/#types) and have normal 5-pin DIN MIDI jacks
on your gear, you'll need a few:
- Type A" MIDI adapter ([PerfectCircuit](https://www.perfectcircuit.com/make-noise-0-coast-midi-cable.html) or [Amazon](https://amzn.to/3Tb6DiU))

### Pico Headers and Headers for Breakout Boards
- 2 - 20-pin header socket ([Digikey](https://www.digikey.com/en/products/detail/sullins-connector-solutions/PPPC201LFBN-RC/810192), [Adafruit](https://www.adafruit.com/product/5583))
- 2 - 20-pin header pins ([Digikey](https://www.digikey.com/en/products/detail/adam-tech/PH1-20-UA/9830398), [Adafruit ](https://www.adafruit.com/product/392))
- 1 - 3-pin female (same as above, break off 3-pin chunk)
- You will also need enough female headers for any breakout pins (external display, swd, stemma, mcp interrupts)
