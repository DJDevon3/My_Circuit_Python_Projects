## ESP32-S3 Feather Weather MQTT with Touchscreen
- pulls data from OpenWeatherMaps API in JSON format to display (including timezone from lat/lon)
- local environment data from BME280 sensor connected via STEMMA
- displays weather data on 3.5" TFT Featherwing & serial console
- displays battery voltage and has USB sensing to know if it's plugged into USB 5V supply (battery or plug icon)
- publishes BME280 sensor data to AdafruitIO via MQTT

### Requirements:
- ESP32-S3 (or better) with at least 8MB of Flash & 2MB PSRAM (graphic & RAM requirements too much for an M0 or M4 chip).
- AdafruitIO Token (free)
- OpenWeatherMap Token (free)
- Touchscreen display (resistive or capacitive)

### Menu & Page Switching System
- This example has 1 main menu button with 5 option pages and 3 main pages.
- Previous & Next button cycles through main pages manually.
- Menu Button currently leads to:
  - Preferences
  - WiFi Credentials (with truncated *'s to replace all but first 2 characters)
  - RSSI Scan (wifi signal strength scan)
  - System Info (Circuit Python version and other system details)
  - Change Credentials (soft keyboard work in progress) 

![Touch_Button_Pages](https://github.com/DJDevon3/My_Circuit_Python_Projects/assets/49322231/93a94244-e42a-4c84-aff6-68b8b04881d7)
