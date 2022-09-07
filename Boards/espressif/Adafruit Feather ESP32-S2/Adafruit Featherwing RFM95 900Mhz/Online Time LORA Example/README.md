# Adafruit Featherwing LORA RFM95 with Feather ESP32-S2
### Online Time LORA Example by DJDevon3

This code includes *improved* error handling correction from my original commit. 

It will now gracefully revert back to looking for the time server and/or WiFi if SSID not found without crashing the program (hopefully).

This example requires a secrets.py file

Circuit Python 7.3.3

![](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/espressif/Adafruit%20Feather%20ESP32-S2/Adafruit%20Featherwing%20RFM95%20900Mhz/Online%20Time%20LORA%20Example/Adafruit%20LoRa%20Radio%20FeatherWing%20RFM95W%20900%20MHz_screenshot.jpg)

# Transmitter Output Example:
```py
Auto-reload is on. Simply save files over USB to run them or enter REPL to disable.
code.py output:
Starting Packet Transmitter...

Time:  6073.9
Packet Transmitted

Time:  6138.6
Packet Transmitted

Time:  6203.29
Packet Transmitted
```

# Receiver Output Example:
```py
Auto-reload is on. Simply save files over USB to run them or enter REPL to disable.
code.py output:

===============================
Connecting to WiFi...
Connected to WiFi - Waiting for LORA Packet...
Timestamp: 09/07/2022 03:06:27
No Packet Found: Timeout for 15
 
Timestamp: 09/07/2022 03:06:42
No Packet Found: Timeout for 15
 
Timestamp: 09/07/2022 03:06:58
No Packet Found: Timeout for 15
 
Received (raw bytes): bytearray(b"it was more of a fun aside than anything I'd pinned hopes and dreams on \xf0\x9f\x99\x82\r\n")
Byte Length:  75
Timestamp: 09/07/2022 03:07:13
Signal Noise: 6.25 dB
Signal Strength: -109 dB
Received (ASCII): it was more of a fun aside than anything I'd pinned hopes and dreams on 🙂

Received (raw bytes): bytearray(b'my partner and I have these rad Keyboard Featherwings from Solder Party and were wanting to make communicators.\r\n')
Byte Length:  113
Timestamp: 09/07/2022 03:07:24
Signal Noise: 6.25 dB
Signal Strength: -109 dB
Received (ASCII): my partner and I have these rad Keyboard Featherwings from Solder Party and were wanting to make communicators.

Received (raw bytes): bytearray(b'might have to pick your brain about LoRa sometime. I experimented a bit using some very weird sparkfun boards (expLoRaBLE) a year or so ago, but finding libraries that were actually up to date/worked was rough.\r\n')
Byte Length:  212
Timestamp: 09/07/2022 03:07:27
Signal Noise: 6.25 dB
Signal Strength: -109 dB
Received (ASCII): might have to pick your brain about LoRa sometime. I experimented a bit using some very weird sparkfun boards (expLoRaBLE) a year or so ago, but finding libraries that were actually up to date/worked was rough.

```
I used some random chat messages pasted from discord for the msg examples. It will send/receive long messages reliably now. When no message is received it goes into a timeout mode waiting for a new message, gracefully, without crashing the program. Also, has basic emoji support 🙂 if used with Mu.

The projects in this section are specifically for Adafruit ESP32-S2 based boards running Circuit Python.
