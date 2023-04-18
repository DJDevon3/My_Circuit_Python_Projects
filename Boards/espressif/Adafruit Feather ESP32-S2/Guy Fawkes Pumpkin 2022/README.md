# Adafruit Feather ESP32-S2 & Feather M4 Express + Propmaker Featherwing
Guy Fawkes Noods Pumpkin 2022 by DJDevon3

The M4 Express w/propmaker featherwing is used solely for powering the 3W RGB LED that takes place of real candle flicker... because having a candle inside the pumpkin with all the electronics is probably a bad idea.

![](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/espressif/Adafruit%20Feather%20ESP32-S2/Guy%20Fawkes%20Pumpkin%202022/IMG_0547.JPG)

![](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/espressif/Adafruit%20Feather%20ESP32-S2/Guy%20Fawkes%20Pumpkin%202022/IMG_0549.JPG)

### As Seen on DigiKey's Hack-a-Pumpkin Contest 2022
https://user-images.githubusercontent.com/49322231/198586264-08559ed8-9f2e-40ff-8640-982de1128694.mov

### Convincing Candle Flicker
https://user-images.githubusercontent.com/49322231/227809366-c0efd35b-c8db-4b36-930f-e28e6cf88156.mov

### Noods Circuit Design:
1 nood per GPIO with a 100 ohm resistor soldered in-line. Used breadboard wire to be easier to plug in during prototyping. There is a positive and negative end on the nood! If you get it backwards just flip the wire around. 

![](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/espressif/Adafruit%20Feather%20ESP32-S2/Guy%20Fawkes%20Pumpkin%202022/pictures/vlcsnap-2022-11-11-19h43m49s925.png)

All noods share a common GND (right side of image). Most feathers only provide 1 GND pin so you'll need a protoboard or perfboard to solder all the GND's together or you could splice the wires into each other and then plug it into the GND pin.  The other ends of the noods (left side of image) are going to GPIO SCK, MISO, and MOSI but any pins will work.

![](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/espressif/Adafruit%20Feather%20ESP32-S2/Guy%20Fawkes%20Pumpkin%202022/pictures/vlcsnap-2022-11-11-19h45m21s119.png)

### Candle Flicker Circuit Design:
Uses M4 Express + Propmaker Featherwing + 3W RGB LED for a bright LED. LED has a realistic orange/yellow flicker. Good coloring for a realistic candle flicker.

The projects in this section are specifically for Adafruit ESP32-S2 based boards running Circuit Python.
