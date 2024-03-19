# Project Description:
Quick demo for those who have a Bluefruit Sense triple stack with TFT featherwing and Airlift featherwing (multiple SPI bus devices). 

The adafruit_esp32spi helper library was specifically written for the airlift and esp32-S2/S3 breakout modules only. It will not work on a feather main board that has a built-in esp32-S2/S3 (use adafruit_minimqtt instead).

# Hardware:
- Adafruit NRF52840 Bluefruit Sense Board https://www.adafruit.com/product/4516
- Adafruit 3.5" TFT Featherwing https://www.adafruit.com/product/3651
- Adafruit Airlift ESP32 Featherwing https://www.adafruit.com/product/4264

# Circuit Python 7.3.x Libraries:
- adafruit_esp32spi (required for airlift featherwing)
- adafruit_hx8357 (required for 3.5" TFT featherwing)

[Get the adafruit-circuitpython-bundle-7.x here](https://circuitpython.org/libraries)
Only put the library folders you actively need in CIRCUITPY/lib

# AdafruitIO:
- AdafruitIO account username & key (edit secrets.py file)

# AdafruitIO Feed Key Example
The feed key isn't necessarily the same as your feed name. You can change the name of an AdafruitIO feed. You cannot change the name of a feed key once created. When you create a new feed in AdafruitIO a feed key is automatically generated based on the feed name. You can only get the feed key after you've created a new feed.

![](https://raw.githubusercontent.com/DJDevon3/CircuitPython/main/Airlift%20AdafruitIO%20Test/AdafruitIO_Feed_Key_Example.PNG)


# Serial and TFT Output Example:

This demo code will connect to your AdafruitIO feed key named "sense-temp" and POST a float temperature value in Fareinheit from the on-board BMP280 sensor. It will then GET and return the same value. This should complete the basics you need to start interacting with your AdafruitIO feeds and dashboard. Finally it will tell you how long until the next update (configurable with sleep timer).
```
Auto-reload is on. Simply save files over USB to run them or enter REPL to disable.
code.py output:

===============================
Connecting to WiFi...
Connected!

Connecting to AdafruitIO...
Connected!
===============================

POST Value...
{'created_at': '2022-06-25T10:32:54Z', 'id': 'obfuscated', 'expiration': '2022-07-25T10:32:54Z', 'created_epoch': 1656153174, 'feed_id': obfuscated, 'value': '87.0', 'feed_key': 'sense-temp'}

GET Response...
Number of Items in Dictionary:  7
{'expiration': '2022-07-25T10:32:54Z', 'id': 'obfuscated', 'feed_key': 'sense-temp', 'created_epoch': 1656153174, 'feed_id': obfuscated, 'value': '87.0', 'created_at': '2022-06-25T10:32:54Z'}
Circuit Python Object Type : <class 'dict'>
Return Single Value! : 87.0

Next Update in 2 hours

===============================
```
# Warning about SPI bus lock ups on initial pin configuration
The SPI bus can get locked sometimes while attempting to figure out your initial featherwing SPI pin configurations. 
If your SPI bus is locked it will throw the error `ValueError: SCK in use` no matter what software pin you attempt to choose.
When the SPI bus gets locked it can persist through code changes and soft-reboots!
A simple board reset (physical button reset) after a code change involving SPI bus can solve that. Reset the board and run your code again. Since figuring out the correct pinouts to use with my setup I've never had a single lock up. When it works like it should you'll have no problems from there on out.

# Default Sleep Timer
For the purpose of testing it's set to 10 seconds. `time.sleep(10)` Set to 3600 for hourly updates when you finalize your code.
AdafruitIO free accounts have a 1000 update daily limit which you can easily exceed by posting every 10 seconds. The most you can safely post 1 value within a 24 hour period without going over the 1000 limit is once every 1.5 minutes (90 seconds).
