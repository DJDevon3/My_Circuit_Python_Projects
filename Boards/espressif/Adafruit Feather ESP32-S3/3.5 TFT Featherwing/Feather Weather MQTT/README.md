# ESP32-S3 Feather Weather with MQTT
- pulls info from OpenWeatherMaps in JSON format to display
- local environment data from BME280 sensor connected via STEMMA
- displays weather data on 3.5" TFT Featherwing & serial console
- displays battery voltage and has USB sensing to know if it's plugged into USB 5V supply (battery or plug icon)
- publishes sensor data to AdafruitIO group feed (you must create and customize a dashboard)

![screenshot](https://user-images.githubusercontent.com/49322231/235323187-4bcce094-0927-4b9e-b5cf-2646f0b6944d.jpg)
- Labels in blue are from online data (Adafruit HQ in NY), orange is local sensors (Florida).
- Default online lat/lon is set to Adafruit HQ location, ideally you'd also this this to your location
 
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
- OpenWeatherMaps Account & API Token

## Demonstration Serial Print Output:
- Good for debugging or if you don't have a display. Serial output to the REPL console can be helpful.
```py
===============================
Board Uptime:  56 minutes
Temp:  86.4131
Actual Temp: 85.2
===============================
Connecting to WiFi...
WiFi! ✅
Connecting to Adafruit IO...
Connected to MQTT Broker! ✅
Publishing BME280-Unbiased: 86.41 | BME280-RealTemp: 85.22 | BME280-Pressure: 1012.1 | BME280-Humidity: 65.1
Next Update:  15 minutes
===============================
```

# AdafruitIO Dashboard Example:
![Feather Weather AdafruitIO](https://github.com/DJDevon3/My_Circuit_Python_Projects/assets/49322231/5d2ee2b0-95f7-40b2-9dbd-8542a8e40aeb)

# Bias Adjustment
- This version of Feather Weather includes a [temperature bias adjusting algorithm](https://github.com/DJDevon3/My_Circuit_Python_Projects/tree/main/Circuit%20Python%20Snippets#temp-sensor-bias-adjust-algorithm-bme280). You are encouraged to add data points comparing it against a NIST traceable thermometer to increase the accuracy of your temperature readings.  Being within 2% of the actual temperature is considered acceptable. By calibrating the bias adjustment data points I have successfully gotten it to within 1% accurate (0.9% to be exact). Attempting to compare your local sensor (BME280) against NOAA data is a fool's errand as the temperature where they are measuring is not where you are measuring. ;) Build your data points manually over time and you'll have an extremely accurate sensor with the numpy interpolation algorithm. 


You can use this working example to customize the weather data you want from OpenWeatherMap (tons more data available) for your project. I'm only pulling basic data and in limited quantity because there is a limitation for how many calls you can make per day. Consult the OpenWeatherMaps & AdafruitIO API Docs.
