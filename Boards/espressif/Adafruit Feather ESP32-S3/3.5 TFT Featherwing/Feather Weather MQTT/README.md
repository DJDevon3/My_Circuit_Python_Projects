# This project no longer works (deprecated) because OpenWeatherMaps API is no longer freely open to the public.
# Please use [Feather Weather for Open-Meteo](https://github.com/DJDevon3/My_Circuit_Python_Projects/tree/main/Boards/espressif/Unexpected%20Maker%20Feather%20S3/3.5%20TFT%20Featherwing/Feather%20Weather%20MQTT%20Touch%20Open-Meteo) instead. 

# ESP32-S3 Feather Weather with MQTT
- pulls data from OpenWeatherMaps API in JSON format to display (including timezone from lat/lon)
- local environment data from BME280 sensor connected via STEMMA
- displays weather data on 3.5" TFT Featherwing & serial console
- displays battery voltage and has USB sensing to know if it's plugged into USB 5V supply (battery or plug icon)
- publishes sensor data to AdafruitIO group feed (you must create and customize a dashboard)
- 
![screenshot](https://github.com/DJDevon3/My_Circuit_Python_Projects/assets/49322231/35a53c35-349e-4b11-bbd2-4d005b161859)
- Labels in blue are from online data, orange is BME280 sensor data.
- Default online lat/lon is set to Adafruit HQ location, ideally you'd also set this to your location
 
 # Pressure Warning Correlation:
- This is a screenshot from a radar website to show my storm warnings work quite well.
- In 2023 I detected a sub-tropical system 300 miles away.
- All you really need is accurate sensors for temp, humidity, and especially pressure to detect storms.
- The Adafruit BME280 has been exceptional to work with.
![Capture](https://user-images.githubusercontent.com/49322231/235323256-1daa61f0-caa2-432b-9cb6-3666e063a1fc.JPG)

# Purpose:
- Combined with a large 10000mah battery this serves as a real-time environment station while online or offline (power outage).
- In offline mode it will continue to function it simply won't update the blue labels.
- This device has been through a hurricane in 2021 and 2 hurricanes in 2022.
- This is not designed as an early warning device although it does work well for that.
- This device was designed as a danger level device during a hurricane.
- As barometric pressure drops the strength of damage in a hurricane is often greater
- The BME280 barometric sensor on this device in particular, is extremely accurate.

## Hardware Used:
- [Adafruit Feather ESP32-S3](https://www.adafruit.com/product/5477)
- [Adafruit 3.5" TFT Featherwing](https://www.adafruit.com/product/3651)
- [Adafruit BME280](https://www.adafruit.com/product/2651) Barometric Pressure, Temperature, Humidity Sensor

## Requirement:
- [OpenWeatherMap](https://openweathermap.org) Account & API Token (free)
- [AdafruitIO](https://io.adafruit.com/) MQTT logging dashboard (free)

## Demonstration Serial Print Output:
- Good for debugging or if you don't have a display. Serial output to the REPL console can be helpful.
```py
===============================
Board Uptime:  11 hours
Temp:  77.6511
Actual Temp: 79.1
| Connecting to WiFi...
| ✅ WiFi!
| | Attempting to GET Weather!
| | Account within Request Limit
| | ✅ Connected to OpenWeatherMap
| | | Sunrise: 06:48
| | | Sunset: 17:27
| | | Temp: 65.98
| | | Pressure: 1018
| | | Humidity: 86
| | | Weather Type: Clouds
| | | Wind Speed: 1.01
| | | Timestamp: 2023/11/23 21:06
| | ✂️ Disconnected from OpenWeatherMap
| | ✅ Connected to MQTT Broker!
| | | ✅ Publishing BME280-Unbiased: 77.65 | BME280-RealTemp: 79.09 | BME280-Pressure: 1018.1 | BME280-Humidity: 60.1 | BME280-Altitude: 0.1
| | ✂️ Disconnected from MQTT Broker
| ✂️ Disconnected from Wifi
Next Update:  15 minutes
```

# AdafruitIO Dashboard Example:
![Feather Weather AdafruitIO](https://github.com/DJDevon3/My_Circuit_Python_Projects/assets/49322231/5d2ee2b0-95f7-40b2-9dbd-8542a8e40aeb)

# Bias Adjustment
- This version of Feather Weather includes a [temperature bias adjusting algorithm](https://github.com/DJDevon3/My_Circuit_Python_Projects/tree/main/Circuit%20Python%20Snippets#temp-sensor-bias-adjust-algorithm-bme280). You are encouraged to add data points comparing it against a NIST traceable thermometer to increase the accuracy of your temperature readings.  Being within 2% of the actual temperature is considered acceptable. By calibrating the bias adjustment data points I have successfully gotten it to within 1% accurate (0.9% to be exact). Attempting to compare your local sensor (BME280) against NOAA data is a fool's errand as the temperature where they are measuring is not where you are measuring. ;) Build your data points manually over time and you'll have an extremely accurate sensor with the numpy interpolation algorithm. 


You can use this working example to customize the weather data you want from OpenWeatherMap (tons more data available) for your project. I'm only pulling basic data and in limited quantity because there is a limitation for how many calls you can make per day. Consult the OpenWeatherMap & AdafruitIO API Docs.
