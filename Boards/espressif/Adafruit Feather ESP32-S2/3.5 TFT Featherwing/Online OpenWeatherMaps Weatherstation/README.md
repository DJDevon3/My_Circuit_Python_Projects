![](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/espressif/Adafruit%20Feather%20ESP32-S2/3.5%20TFT%20Featherwing/Online%20OpenWeatherMaps%20Weatherstation/screenshot.bmp)

# Online OpenWeatherMaps Weatherstation (for ESP32-S2)
- pulls info from OpenWeatherMaps
- displays weather data on 3.5" TFT Featherwing

## Hardware Used:
- Adafruit Feather ESP32-S2
- Adafruit 3.5" TFT Featherwing

## Other Requirements:
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
You can use this working example to customize the weather data you want from OpenWeatherMap (tons more data available) for your project. I'm only pulling basic data and in limited quantity because there is a limitation for how many calls you can make per day.
