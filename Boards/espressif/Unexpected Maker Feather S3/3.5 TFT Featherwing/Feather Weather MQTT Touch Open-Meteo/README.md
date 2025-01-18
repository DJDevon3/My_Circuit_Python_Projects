### My Circuit Python Feather Weather on Unexpected Maker FeatherS3

![screenshot](https://github.com/user-attachments/assets/d3e02e73-cdfe-4ec6-bc5f-0e70463ea007)

### My Circuit Python Feather Weather on Unexpected Maker FeatherS3
- MQTT Publishing to AdafruitIO from onboard BME280 sensors
- Multiple customizable pages designed for the TFT Featherwing touch display

### Hardware:
- Unexpected Maker FeatherS3 [Adafruit Store](https://www.adafruit.com/product/5399) or [Unexpected Maker Store](https://unexpectedmaker.com/shop.html#!/FeatherS3/p/577111310)
- [Adafruit 3.5" TFT Featherwing](https://www.adafruit.com/product/3651)
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

Customizable blank page 2

![page2](https://github.com/user-attachments/assets/04a1707c-1c26-4d3d-afd7-6dc583d4bfa1)

Customizable blank page 3

![page3](https://github.com/user-attachments/assets/5e00941e-560d-475d-abd1-08df922b91bb)

Display brightness touch slider

![preferences](https://github.com/user-attachments/assets/3325898a-331b-44fd-907e-d26a43ae8109)

WiFi Scanner

![rssi](https://github.com/user-attachments/assets/991a28da-21a0-4466-b6bd-9aae661107e7)

Soft Keyboard for changing WiFi Credentials (work in progress)

![soft_keyboard](https://github.com/user-attachments/assets/c6bd3da9-2485-4272-b373-84ef50c29fd4)

System Information including SD Card details

![system_info](https://github.com/user-attachments/assets/e64be2ca-11db-48eb-b65b-856342e5eb7d)

Shows currently connected SSID with obfuscated stars

![wifi_settings](https://github.com/user-attachments/assets/a7cad19a-b8f0-4018-a660-f5ab80f96590)
