# TR-Cowbell
TR Cowbell v1.2 (powered by Raspberry Pi Pico) by DJDevon3

![Based on PicoStepSeq by @Todbot](https://github.com/todbot/picostepseq)

![](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/raspberrypi/Raspberry%20Pi%20Pico/TR%20Cowbell/Pictures/v1.2_screenshot.jpg)

### Version 1.2
- Replaced dual rotary encoders with 1 encoder + 5 buttons for menu navigation
- Added header breakout for 10 unused pins (GP0-GP9). Includes GND & 3V3. Good for adding peripherals.
- Added Stemma I2C connector (GP26 & GP27 on I2C Bus 1) on backplane plus Stemma breakout
- Added MCP23017 I2C addressing jumper pads near chips (1 chip is on I2C Bus 0 other is on Bus 1)
- Added MCP23017 interrupt breakout pins
- Reorganized MCP23017 pinouts to be in correct order for the chip design. (half were backwards in 1.0)
- Replaced my name on top silkscreen with TR-Cowbell, moved name to bottom silkscreen in Papyrus font.
- Confirmed working with Raspberry Pi Pico & Pico W boards

# BOM (Bill of Materials)
### For basic USB MIDI functionality:
- 1 - "TR-Cowbell" PCB ([JLPCB](https://oshwlab.com/djdevon3/tr-cowbell))
- 1 - Raspberry Pi Pico ([Digikey](https://www.digikey.com/en/products/detail/raspberry-pi/SC0915/13624793), [Adafruit](https://www.adafruit.com/product/4864)) OR Pi Pico W ([Digikey](https://www.digikey.com/en/products/detail/raspberry-pi/SC0918/16608263))
- 16 - PB86A "step switch" w/ built-in LED ([Adafruit](https://www.adafruit.com/product/5519))
- 1 - PEC11R (S-Type) Rotary Encoder ([Digikey](https://www.digikey.com/en/products/detail/bourns-inc/PEC11R-4215F-S0024/4499665))
- 16 - LED resistor value anywhere between 400 ohm to 1000 ohm (R1-R16) ([Digikey](https://www.digikey.com/en/products/detail/yageo/CFR-12JR-52-470R/17647), [Adafruit](https://www.adafruit.com/product/2781))
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
- You will also need enough female headers for any breakout pins (external spi display, ano encoder, mcp interrupts)


