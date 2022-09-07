# Adafruit Featherwing LORA RFM95 with Feather RP2040
### Online Time LORA Example by DJDevon3

This code includes improved error handling correction for connecting to wifi & time server.
It will now gracefully revert back to looking for the time server if not found or WiFi if SSID not found without crashing the program (hopefully).
This code requires a secrets.py file

Circuit Python 7.3.3

![](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/raspberrypi/Adafruit%20Feather%20RP2040/Adafruit%20Featherwing%20RFM95%20900Mhz/Online%20Time%20LORA%20Example/Adafruit%20LoRa%20Radio%20FeatherWing%20RFM95W%20900%20MHz_screenshot.jpg)

# Transmitter Output Example:
```py
Auto-reload is on. Simply save files over USB to run them or enter REPL to disable.
code.py output:
Starting Packet Transmitter...

Time:  66509.7
Packet Transmitted

Time:  66573.8
Packet Transmitted
```

# Receiver Output Example:
```py
Auto-reload is on. Simply save files over USB to run them or enter REPL to disable.
code.py output:

===============================
Connecting to WiFi...
Connected to WiFi - Waiting for LORA Packet...
Timestamp: 09/06/2022 06:05:58
No Packet Found: Timeout for 15
 
Connected to WiFi - Waiting for LORA Packet...
Received (raw bytes): bytearray(b'Hello\r\n')
Byte Length:  7
Timestamp: 09/06/2022 06:06:13
Signal Noise: 6.25 dB
Signal Strength: -110 dB
Received (ASCII): Hello

Connected to WiFi - Waiting for LORA Packet...
Received (raw bytes): bytearray(b'World!\r\n')
Byte Length:  8
Timestamp: 09/06/2022 06:06:21
Signal Noise: 6.25 dB
Signal Strength: -110 dB
Received (ASCII): World!

Connected to WiFi - Waiting for LORA Packet...
Received (raw bytes): bytearray(b'Third Syn\r\n')
Byte Length:  11
Timestamp: 09/06/2022 06:06:23
Signal Noise: 6.25 dB
Signal Strength: -110 dB
Received (ASCII): Third Syn

Connected to WiFi - Waiting for LORA Packet...
```

The projects in this section are specifically for Adafruit RP2040 based boards running Circuit Python.
