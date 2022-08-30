# SPDX-FileCopyrightText: 2022 DJDevon3 for Adafruit Industries
# SPDX-License-Identifier: MIT
"""DJDevon3 Simple Offline/Online Weatherstation"""
import time
import board
import busio
import displayio
from digitalio import DigitalInOut
import neopixel
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager
from adafruit_hx8357 import HX8357

# 3.5" TFT Featherwing is 480x320
DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 320

# Initialize Busses
i2c = board.I2C()
spi = board.SPI()

displayio.release_displays()
# Initialize TFT
tft_cs = board.D9
tft_dc = board.D10
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = HX8357(display_bus, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT)
# Will allocate but not use SPIM3. SPIM3 doesn't work when not powered by USB.
do_not_use_this_spi = busio.SPI(clock=board.A0, MOSI=board.A1)
try:
    from secrets import secrets
except ImportError:
    print("Secrets File Import Error")
    raise

# Initilize ESP32 Airlift on SPI bus
esp32_cs = DigitalInOut(board.D13)
esp32_ready = DigitalInOut(board.D11)
esp32_reset = DigitalInOut(board.D12)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
status_light = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2)
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)

# Fill OpenWeather 2.5 API with token data
# OpenWeather free account & token are required
timezone = secrets['timezone']
tz_offset_seconds = int(secrets['timezone_offset'])

# OpenWeather 2.5 Free API
DATA_SOURCE = "https://api.openweathermap.org/data/2.5/onecall?"
DATA_SOURCE += "lat="+secrets['openweather_lat']
DATA_SOURCE += "&lon="+secrets['openweather_lon']
DATA_SOURCE += "&timezone="+timezone
DATA_SOURCE += "&timezone_offset="+str(tz_offset_seconds)
DATA_SOURCE += "&exclude=hourly,daily"
DATA_SOURCE += "&appid="+secrets['openweather_token']
DATA_SOURCE += "&units=imperial"
print(DATA_SOURCE)

# Connect to WiFi
print("\n===============================")
print("Connecting to WiFi...")
wifi.connect()
print("Connected!\n")

# Some boards don't have deep sleep, can use time.sleep instead
sleep_time = 8000  # Time between Get/Post weather updates

if (sleep_time) < 60:
    sleep_time_conversion = "seconds"
elif (sleep_time) >= 60 and (sleep_time) < 3600:
    sleep_int = sleep_time / 60
    sleep_time_conversion = "minutes"
elif (sleep_time) >= 3600:
    sleep_int = sleep_time / 60 / 60
    sleep_time_conversion = "hours"

def _format_date(datetime):
    return "{:02}/{:02}/{:02}".format(
        datetime.tm_year,
        datetime.tm_mon,
        datetime.tm_mday,
    )

def _format_time(datetime):
    return "{:02}:{:02}:{:02}".format(
        datetime.tm_hour,
        datetime.tm_min,
        datetime.tm_sec,
    )

while True:
    try:
        print("Attempting to GET Weather!")
        print("===============================\n")

        response = wifi.get(DATA_SOURCE).json()
        print("Response is", response)

        get_timestamp = int(response['current']['dt'] + tz_offset_seconds)
        current_unix_time = time.localtime(get_timestamp)
        current_struct_time = time.struct_time(current_unix_time)
        current_date = "{}".format(_format_date(current_struct_time))
        current_time = "{}".format(_format_time(current_struct_time))

        sunrise = int(response['current']['sunrise'] + tz_offset_seconds)
        sunrise_unix_time = time.localtime(sunrise)
        sunrise_struct_time = time.struct_time(sunrise_unix_time)
        sunrise_time = "{}".format(_format_time(sunrise_struct_time))

        sunset = int(response['current']['sunset'] + tz_offset_seconds)
        sunset_unix_time = time.localtime(sunset)
        sunset_struct_time = time.struct_time(sunset_unix_time)
        sunset_time = "{}".format(_format_time(sunset_struct_time))

        temp_day = response['current']['temp']
        pressure = response['current']['pressure']
        humidity = response['current']['humidity']
        weather_type = response['current']['weather'][0]['main']

        print("\n")
        print("Timestamp:", current_date + " " + current_time)
        print("Sunrise:", sunrise_time)
        print("Sunset:", sunset_time)
        print("Temp:", temp_day)
        print("Pressure:", pressure)
        print("Humidity:", humidity)
        print("Weather Type:", weather_type)

        print("\nNext Update in %s %s" % (int(sleep_int), sleep_time_conversion))
        print("\n===============================")
    except (ValueError, RuntimeError) as e:
        print("Failed to get data, retrying\n", e)
        wifi.reset()
        time.sleep(60)
        continue
    response = None
    time.sleep(sleep_time)
