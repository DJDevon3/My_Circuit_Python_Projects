# Adafruit Featherwing LORA RFM95 with Feather RP2040
### Basic Example by DJDevon3 based on code by Tony Dicola.

This code includes basic error handling correction the original lacked.

Circuit Python 7.3.3

![](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/raspberrypi/Adafruit%20Feather%20RP2040/Adafruit%20Featherwing%20RFM95%20900Mhz/Basic%20LORA%20Example/Adafruit%20LoRa%20Radio%20FeatherWing%20RFM95W%20900%20MHz_screenshot.jpg)

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
Starting Packet Receiver...

Received (raw bytes): bytearray(b'Hello\r\n')
Byte Length:  7
Time:  69758.3
Signal Noise: 6.0 dB
Signal Strength: -113 dB
Received (ASCII): Hello

Received (raw bytes): bytearray(b'World!\r\n')
Byte Length:  8
Time:  69760.1
Signal Noise: 6.25 dB
Signal Strength: -112 dB
Received (ASCII): World!

Received (raw bytes): bytearray(b'Third Syn\r\n')
Byte Length:  11
Time:  69762.2
Signal Noise: 6.25 dB
Signal Strength: -112 dB
Received (ASCII): Third Syn

Time:  69764.2
Clear: Hibernating for 15
 
Time:  69779.2
Clear: Hibernating for 15
```

The projects in this section are specifically for Adafruit Feather RP2040 based boards running Circuit Python.
