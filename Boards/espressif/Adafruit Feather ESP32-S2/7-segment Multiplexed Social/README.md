# Adafruit Feather ESP32-S2
Social Media Tracker Project

Uses 10x 7-segment clock display backpacks and multiplexer to exceed the default 8x I2C address limit. It tracks the amount of followers/subscribers I have across multiple social media platforms. Uses Adafruit's Circuit Python requests library. All code is open source including the individual API integrations I wrote and contributed to Adafruit's example library. This project takes all the individual API's (social media site API's) and combines them into 1 display as a demonstration of multiple-API integrations.

https://user-images.githubusercontent.com/49322231/227807810-f3f5ae5a-ba3e-4756-8a7d-cdd30b6a0f5e.mov

### Software Requirement:
- Youtube API Developer Account Token
- Twitter API Developer Account Token
- Github API Developer Account Token
- Twitch API Developer Account Token
- Discord User Account (uses web scraping, no developer account required)
- Mastodon User Account (uses web scraping, no developer account required)

### Language Used:
- [Adafruit's Circuit Python](https://www.CircuitPython.org) (a fork of Micropython for microcontrollers)

### Hardware Used:
- 1x [Adafruit Feather ESP32-S2 4 MB Flash + 2 MB PSRAM](https://www.adafruit.com/product/5000)
- 1x [Adafruit PCA9548 8-Channel Multiplexer](https://www.adafruit.com/product/5626)
- 10x [Adafruit 7-Segment Stemma Backpacks (clock style segments)](https://www.adafruit.com/product/5599) 2x each in different colors
- 9x [Adafruit 300mm Stemma male to male wire connectors](https://www.adafruit.com/product/5384)
- 1x [Adafruit 30mm Arcade button](https://www.adafruit.com/product/3488) Recommend the ![mini-Ardcade button instead](https://www.adafruit.com/product/3431)
- 1x [10x8x2.5" Shadow Box](https://www.amazon.com/gp/product/B07QJX512S) Amazon $20
- 1x [8x10 Black Uncut Mat Boards](https://www.amazon.com/gp/product/B087Z64YL5) Amazon $15
- 1x [Roll of static mirror film](https://www.amazon.com/gp/product/B07X7DHLXB/) Amazon $15


## Total Project Cost: Approximately $200 (as of November 2022)

![](https://github.com/DJDevon3/My_Circuit_Python_Projects/blob/main/Boards/espressif/Adafruit%20Feather%20ESP32-S2/7-segment%20Multiplexed%20Social/IMG_0596.JPG)

### HT16K33 I2C Conflict with PCA9548 Multiplexers
Segmented backpacks shared an identical I2C address range of 0x70-0x77 with the PCA9548 multiplexers. This means you can only use a maximum of 4 multiplexers before you start running into conflicts. Here's my recommended setup that will maximize the amount of backpacks you can use.  Keep in mind this is PER I2C BUS. Most of Adafruit's microcontrollers allow for 2 I2C busses so you would basically multiply what you see in the graphic times four. The theoretical maximum amount of devices is in the hundreds. Obviously, that should be plenty for just about any project you can think of and if it's not then what in the heck are you building!?!? You'll run into power delivery issues long before you max out the I2C bus communication limit.

### Below Example Image
I'm only showing half of each multiplexer channels used because... it's a ridiculously big enough graphic as it is. Hopefully you get the point of how to add tons of 7 segment displays even with the conflicting address space. The maximum amount of devices with this setup is 256 backpacks using 2 I2C buses.

![](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/espressif/Adafruit%20Feather%20ESP32-S2/7-segment%20Multiplexed%20Social/Adafruit_Multiplexed_Backpacks.png)

The projects in this section are specifically for Adafruit ESP32-S2 based boards running Circuit Python.
