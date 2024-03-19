![](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/nrf/Adafruit%20Feather%20Bluefruit%20Sense/Adafruit%203.5%20TFT%20Featherwing/Simple_Offline_Weatherstation/screenshot.bmp)

# Project Description:

A project that began on Arduino and used daily for 2 years. Then one day I decided to update the Arduino IDE and libraries and it broke the code so horribly that I decided to start from scratch and try Circuit Python 7.x instead. [The difference in result between Arduino and Circuit Python is self evident.](https://github.com/DJDevon3/Arduino/tree/master/Adafruit%20NRF52840%20Feather%20Sense)

There is no online or BLE used in this project. All sensor data comes from the board. Default sleep timer is 60 seconds (configurable). Will stay alive on battery power for about 30 hours (tested with Adafruit 3x 18650 battery pack). Recommended as a permanent install with USB power and backup battery for a power outage.

# Hardware Required:
- Adafruit NRF52840 Bluefruit Sense Board (running Circuit Python)
- Adafruit 3.5" TFT Featherwing

The wallpaper image must be 8-bit indexed BMP format. I've included BMP's in the images folder as examples. If you attempt to use 16-bit or higher BMP's you'll get an error message on the TFT about true color BMP's not being supported. This is a limitation of the circuit python graphics library as true color BMP's work fine in my Arduino version on the same hardware. 

You can choose to use the default TERMINALIO font instead of the bitmap fonts for much faster loading time (first display initialization). TERMINALIO doesn't look as nice but will "boot up" much faster. For a weatherstation that only updates every 60 seconds the "boot up" taking 20 seconds more is an acceptable sacrifice for better font aesthetics.

Circuit Python is more resource intensive than Arduino. If your project becomes too big (loading too large of an image) you can more easily run out of memory. With that said, while running only 1 wallpaper image there's still plenty of overhead for larger sketches on the Bluefruit Sense. What really chews up the storage vs Arduino code is the amount of circuit python libraries for sketches.

I've been running this in my garage for the past 2 years and it works wonderfully. The pressure sensor in particular is an extremely precise sensor and valuable data point to anyone living in an area of the world prone to large storms.
