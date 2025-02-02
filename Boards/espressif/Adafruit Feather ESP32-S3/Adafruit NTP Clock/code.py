# SPDX-FileCopyrightText: 2025 DJDevon3
# SPDX-License-Identifier: MIT
# Coded for Circuit Python 9.2.3
"""Adafruit NTP Offset Example"""

import os
import time
import board
import wifi
import adafruit_connection_manager
import adafruit_requests
import rtc
import adafruit_ntp

# Initalize Wifi, Connection Manager, Request Session
pool = adafruit_connection_manager.get_radio_socketpool(wifi.radio)
requests = adafruit_requests.Session(pool)

# Use settings.toml for credentials
ssid = os.getenv("CIRCUITPY_WIFI_SSID")
password = os.getenv("CIRCUITPY_WIFI_PASSWORD")

TZ_OFFSET = -5  # time zone offset in hours from UTC
Time_Format = "24"  # 12 hour (AM/PM) or 24 hour (military) clock

def time_calc(input_time):
    """Converts seconds to minutes/hours/days"""
    if input_time < 60:
        return f"{input_time:.0f} seconds"
    if input_time < 3600:
        return f"{input_time / 60:.0f} minutes"
    if input_time < 86400:
        return f"{input_time / 60 / 60:.1f} hours"
    return f"{input_time / 60 / 60 / 24:.2f} days"

# Custom timestamp functions use struct time format
# You can easily change them to your preferred format
# https://docs.circuitpython.org/en/latest/shared-bindings/time/index.html#time.struct_time
def _format_datetime(datetime):
    """ F-String formatted struct time conversion"""
    return (f"{datetime.tm_mon:02}/" +
            f"{datetime.tm_mday:02}/" +
            f"{datetime.tm_year:02} " +
            f"{datetime.tm_hour:02}:" +
            f"{datetime.tm_min:02}:" +
            f"{datetime.tm_sec:02}")

def _format_min(datetime):
    """ Get the current minute"""
    return (f"{datetime.tm_min:02}")

def _format_sec(datetime):
    """ Get the current second"""
    return (f"{datetime.tm_sec:02}")

def _format_time(datetime, format="12"):
    """ Time is 12 hour or 24 hour format"""
    if format == "12":
        hour = datetime.tm_hour % 12
        min = datetime.tm_min
        if hour == 0:
            hour = 12
        am_pm = "AM"
        if datetime.tm_hour / 12 >= 1:
            am_pm = "PM"
        if DEBUG_TIME:
            # Set debug to True & change these to test different times
            debug_hour = "09"
            debug_min = "09"
            return (f"{debug_hour:01}:{debug_min:02} {am_pm}")
        else:
            return (f"{hour:01}:{min:02} {am_pm}")
    if format == "24":
        return (f"{datetime.tm_hour:02}:{datetime.tm_min:02}:{datetime.tm_sec:02}")

# Publicly Open NTP Time Server
# No AdafruitIO credentials required
ntp = adafruit_ntp.NTP(pool, tz_offset=TZ_OFFSET)
now = time.localtime()
current_datestamp = "{}".format(_format_datetime(now))
try:
    rtc.RTC().datetime = ntp.datetime
    print(f"Initial Synchronize: {current_datestamp}")
    time.sleep(1)
except OSError as e:
    print(f"RTC or NTP Error: {e}")

def RTC_Offset(rtc_time=ntp.datetime, local_time=time.localtime(), offset=0):
    """ Return NTP Time & Manually Adjusted Offset Time """
    rtc_time = ntp.datetime
    format_rtc_time = "{}".format(_format_datetime(ntp.datetime))
    local_time = time.localtime()
    format_local_time = "{}".format(_format_datetime(time.localtime()))
    
    struct_time = time.localtime()
    unix_time = time.mktime(struct_time)
    new_unix_time = int(unix_time) + int(offset)
    offset_time = time.localtime(new_unix_time)
    format_offset_time = "{}".format(_format_datetime(offset_time))
    print("===============================")
    print(f"RTC Time: {format_rtc_time}")
    print(f"Local Time: {format_local_time}")
    print(f"Offset Time: {format_offset_time}")
    
RTC_Offset(offset=-720)  # Offset in seconds
time.sleep(30)
RTC_Offset(offset=-720)