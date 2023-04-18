![screenshot](https://user-images.githubusercontent.com/49322231/189921153-f18aa425-7e45-4438-804b-2c6da8016deb.jpg)

# Online OpenWeatherMaps Weatherstation (for ESP32-S2)
- pulls info from OpenWeatherMaps in JSON format
- parses JSON data to a format circuit python can display
- displays weather data on 3.5" TFT Featherwing & serial console

## Hardware Used:
- Adafruit Feather ESP32-S2
- Adafruit 3.5" TFT Featherwing

## Requirement:
- OpenWeatherMaps Account & API Token

## Demonstration Serial Print Output:
- Good for debugging or if you don't have a TFT. Pure serial output format can be helpful.
```py
===============================
Connecting to WiFi...
Connected!

Attempting to GET Weather!

===============================
OpenWeather Success
Timestamp: 2022/08/30 20:37
Sunrise: 06:21
Sunset: 19:32
Temp: 78.67
Pressure: 1007
Humidity: 79
Weather Type: Clear

Next Update in 15 minutes
===============================
```
You can use this working example to customize the weather data you want from OpenWeatherMap (tons more data available) for your project. I'm only pulling basic data and in limited quantity because there is a limitation for how many calls you can make per day. Consult the OpenWeatherMaps API Docs to see the oodles of JSON data you can pull from.
