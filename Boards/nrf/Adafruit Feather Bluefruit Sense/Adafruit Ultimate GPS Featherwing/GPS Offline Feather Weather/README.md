# Adafruit GPS with Real Time Clock & Timezone Offset
While the microcontroller board is battery powered, using a GPS/RTC combination ensures proper time keeping even during a power outage.

This particluar GPS module doesn't have timezone capability. It reports time in UTC (0 GMT).

Timezone added manually and converted to localtime. Not DST aware code. You must set timezone & DST offset yourself. 

![](https://raw.githubusercontent.com/DJDevon3/CircuitPython/main/Ultimate%20GPS%20Featherwing/screenshot_connecting.bmp)

UTC Time = 4:39 

The -5 GMT Timezone offset incorrectly displays localtime as 11:39 during DST. 

To correct this simply set Timezone offset to -4.

![](https://raw.githubusercontent.com/DJDevon3/CircuitPython/main/Ultimate%20GPS%20Featherwing/screenshot_gps.bmp)

Quad Stack Demo (NRF52840 Sense, ESP32 Airlift Featherwing, 3.5" TFT Featherwing, Ultimate GPS Featherwing)

The Adafruit Ultimate GPS Featherwing includes a Real Time Clock with coincell battery backup

- Displays RTC localtime while connecting to GPS (will display incorrect time if RTC never previously set)
- GPS connects and receives UTC timestamp data
- GPS time updates RTC only once per reboot. (time drift will occur eventually, reboot to resync time)
- RTC permanently set with new synchronized time (even if USB power or VBAT power removed)
- Outputs RTC time with local GMT offset (customizable Timezone variable).

# Work in Progress
- Automatic DST correction + or - 1 twice a year
- Occasional error for OverflowError: overflow converting long int to machine word

Thanks to [Neradoc](https://github.com/Neradoc) for coding the Timezone offset correction for Adafruit GPS.
