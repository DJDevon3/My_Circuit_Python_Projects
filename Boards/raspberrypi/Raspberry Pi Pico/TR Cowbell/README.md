# TR-Cowbell
TR Cowbell powered by Raspberry Pi Pico by DJDevon3

![Based on PicoStepSeq by @Todbot](https://github.com/todbot/picostepseq)

My first major custom board!!!

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
- Not yet ready to print v1.2 PCB, waiting for OSHW certification

# BOM (Bill of Materials)
### For basic USB MIDI functionality:
- 1 - "TR-Cowbell" PCB [JLPCB](https://oshwlab.com/djdevon3/tr-cowbell)
- 1 - Raspberry Pi Pico ([Adafruit](https://www.adafruit.com/product/4864), [Digikey](https://www.digikey.com/en/products/detail/raspberry-pi/SC0915/13624793))
- 1 - ANO Encoder Wheel [Adafruit](https://www.adafruit.com/product/5001)
- 1 - (optional breakout if you want to mount on enclosure) ANO Encoder Breakout PCB [Adafruit](https://www.adafruit.com/product/5221)
- 16 - "step switch" w/ built-in LED ([Adafruit](https://www.adafruit.com/product/5519)]
- 16 - LED resistor value anywhere between 400 to 1000 ohm (R1-R16) ([Digikey](https://www.digikey.com/en/products/detail/yageo/CFR-12JR-52-470R/17647), [Adafruit](https://www.adafruit.com/product/2781)]
- 2 - MCP2307 E/SP I2C Expander Bare Chips [Adafruit](https://www.adafruit.com/product/732)
- 2 - (Optional but recommended) 28-pin .3" ZIF sockets for MCP23107 chips [Adafruit](https://www.adafruit.com/product/2205)

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
- 1 - 4-pin female (same as above, break off 4-pin chunk)
- You will also need enough female headers for any breakout pins (external spi display, ano encoder, mcp interrupts)


