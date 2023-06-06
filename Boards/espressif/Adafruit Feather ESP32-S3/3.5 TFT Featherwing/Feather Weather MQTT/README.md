# ESP32-S3 Feather Weather with MQTT
- pulls info from OpenWeatherMaps in JSON format to display
- local environment data from BME280 sensor connected via STEMMA
- displays weather data on 3.5" TFT Featherwing & serial console
- displays battery voltage and has USB sensing to know if it's plugged into USB 5V supply (battery or plug icon)
- publishes sensor data to AdafruitIO group feed (you must create and customize a dashboard)

![screenshot](https://user-images.githubusercontent.com/49322231/235323187-4bcce094-0927-4b9e-b5cf-2646f0b6944d.jpg)
- Labels in blue are from online data (Adafruit HQ in NY), orange is local sensors (Florida).
- Default online lat/lon is set to Adafruit HQ location, ideally you'd also this this to your location
 
 Storm Warning Example:
 This is a screenshot from a local weatherstation (not included in the script) just the weatherstation's website screenshot to show the storm warning I built in does in fact work well for a notification of incoming storms.
![Capture](https://user-images.githubusercontent.com/49322231/235323256-1daa61f0-caa2-432b-9cb6-3666e063a1fc.JPG)

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

Board Uptime:  38 minutes
Temp:  82.96
Actual Temp: 80.0
Connecting to Adafruit IO...
Connected to MQTT Broker!
Publishing BME280-Unbiased: 82.96 | BME280-RealTemp: 80.01 | BME280-Pressure: 1012.5 | BME280-Pressure: 55.4
Next Update:  15 minutes
===============================
```

# AdafruitIO Dashboard Example:
![Feather Weather AdafruitIO](https://github.com/DJDevon3/My_Circuit_Python_Projects/assets/49322231/5d2ee2b0-95f7-40b2-9dbd-8542a8e40aeb)


You can use this working example to customize the weather data you want from OpenWeatherMap (tons more data available) for your project. I'm only pulling basic data and in limited quantity because there is a limitation for how many calls you can make per day. Consult the OpenWeatherMaps & AdafruitIO API Docs.
