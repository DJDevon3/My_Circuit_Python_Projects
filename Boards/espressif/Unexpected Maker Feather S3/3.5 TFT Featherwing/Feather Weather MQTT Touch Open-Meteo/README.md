## Circuit Python Feather Weather for Unexpected Maker FeatherS3

![screenshot](https://github.com/user-attachments/assets/d3e02e73-cdfe-4ec6-bc5f-0e70463ea007)

### Hardware:
- Unexpected Maker FeatherS3 [Adafruit Store](https://www.adafruit.com/product/5399) or [Unexpected Maker Store](https://unexpectedmaker.com/shop.html#!/FeatherS3/p/577111310)
- [Adafruit 3.5" 480x320 TFT Featherwing](https://www.adafruit.com/product/3651)
- [Adafruit BME280](https://www.adafruit.com/product/2652) I2C Temperature/Humidity/Barometric Pressure Sensor module (shown in orange labels)
- [Adafruit 10ah Lipo Battery](https://www.adafruit.com/product/5035)
- [Sandisk 128GB Micro SD Card](https://www.amazon.com/gp/product/B073JYC4XM)

### Features
- Pulls geographic data via latitude/longitude from Open-Meteo (all online elements are labeled in blue)
- Reads Temperature, Humidity, Pressure from a BME280 sensor (all sensor elements are labeled in orange)
- Publishes sensor data to AdafruitIO (free API) for graphing
- Built-in battery charger, voltage monitor, and USB 5V sensing for battery recharging.
- Sunrise/Sunset timestamps at the top.
- Updates every 15 minutes (this is the maximum allowed by Open-Meteo's free api)
- Multi-page touch navigation GUI

### Open-Meteo Endpoints (based on your lattitude/longitude)
- Timestamp with timezone offset
- Relative Humidity
- Barometric Pressure
- Temperature
- Wind speed
- Sunrise
- Sunset
- Is day or night boolean
- Current weather description
- URL for current weather icon (unused)

### Font
- [Good Times BDF Font](https://github.com/DJDevon3/GoodTimes_BDF_Font)

Touch Menu Popout

![menu_popout](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/refs/heads/main/Boards/espressif/Unexpected%20Maker%20Feather%20S3/3.5%20TFT%20Featherwing/Feather%20Weather%20MQTT%20Touch%20Open-Meteo/Pictures/menu_popout.png)

Customizable blank page 2 (top right button)

![page2](https://github.com/user-attachments/assets/04a1707c-1c26-4d3d-afd7-6dc583d4bfa1)

You can scroll back and forth between Main Page, Page 2, and Page 3 with top right navigation buttons. 

![page3](https://github.com/user-attachments/assets/5e00941e-560d-475d-abd1-08df922b91bb)

Display brightness touch slider (preferences work in progress)

![preferences](https://github.com/user-attachments/assets/3325898a-331b-44fd-907e-d26a43ae8109)

WiFi Scanner

![rssi](https://github.com/user-attachments/assets/991a28da-21a0-4466-b6bd-9aae661107e7)

Soft Keyboard for changing WiFi Credentials (work in progress)

![soft_keyboard](https://github.com/user-attachments/assets/c6bd3da9-2485-4272-b373-84ef50c29fd4)

System Information including SD Card details (if you have an SD Card inserted into the TFT Featherwing)

![system_info](https://github.com/user-attachments/assets/e64be2ca-11db-48eb-b65b-856342e5eb7d)

Shows currently connected SSID with obfuscated stars

![wifi_settings](https://github.com/user-attachments/assets/a7cad19a-b8f0-4018-a660-f5ab80f96590)

[Adafruit IO](https://io.adafruit.com) Graphing your published AIO data (browser screenshot)

![AdafruitIO](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/refs/heads/main/Boards/espressif/Unexpected%20Maker%20Feather%20S3/3.5%20TFT%20Featherwing/Feather%20Weather%20MQTT%20Touch%20Open-Meteo/Pictures/AdafruitIO_Dashboard_Graphing.PNG)
