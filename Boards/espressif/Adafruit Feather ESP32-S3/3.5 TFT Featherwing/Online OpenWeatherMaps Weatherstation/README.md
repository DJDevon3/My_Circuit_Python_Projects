![screenshot](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/espressif/Adafruit%20Feather%20ESP32-S3/3.5%20TFT%20Featherwing/Online%20OpenWeatherMaps%20Weatherstation/demo_screenshot.bmp)
- Labels in blue are from online data (Adafruit HQ in NY), orange is local sensors (Florida).
- Default online lat/lon is set to Adafruit HQ location

# Online/Offline OpenWeatherMaps Weatherstation (for ESP32-S3)
- pulls info from OpenWeatherMaps in JSON format to display
- local environment data from BME280 sensor connected via STEMMA
- displays weather data on 3.5" TFT Featherwing & serial console
- displays battery voltage and has USB sensing to know if it's plugged into USB 5V supply (battery or plug icon)

# Purpose:
- Combined with a large 10000mah battery this serves as a real-time environment station during a power outage.
- This device has been through a hurricane in 2021 and 2 hurricanes in 2022.
- This not an early warning device, it's a danger level device during a hurricane.
- As barometric pressure drops the strength of damage in a hurricane is often higher
- The BME280 barometric sensor on this device in particular is extremely accurate.

## Hardware Used:
- [Adafruit Feather ESP32-S3](https://www.adafruit.com/product/5477)
- [Adafruit 3.5" TFT Featherwing](https://www.adafruit.com/product/3651)
- [Adafruit BME280](https://www.adafruit.com/product/2651) Barometric Pressure, Temperature, Humidity Sensor

## Requirement:
- OpenWeatherMaps Account & API Token

## Demonstration Serial Print Output:
- Good for debugging or if you don't have a display. Serial output to the REPL console can be helpful.
```py
===============================
Connecting to WiFi...
Connected!

USB Sense:  True
Attempting to GET Weather!

===============================
OpenWeather Success
Timestamp: 2023/04/16 03:40
Sunrise: 06:15
Sunset: 19:35
Temp: 58.3
Pressure: 1011
Humidity: 93
Weather Type: Mist

Next Update in 15 minutes
===============================
```
You can use this working example to customize the weather data you want from OpenWeatherMap (tons more data available) for your project. I'm only pulling basic data and in limited quantity because there is a limitation for how many calls you can make per day. Consult the OpenWeatherMaps API Docs to see the oodles of JSON data you can pull from.
