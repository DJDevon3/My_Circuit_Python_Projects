Check out [TodBot's Circuit Python Tricks](https://github.com/todbot/circuitpython-tricks#circuitpython-tricks) an amazing collection of specialized code snippets for Circuit Python.

# DJDevon3's Snippets

These are a few common code snippets that I continually find myself looking at past projects to snag. No sense in re-inventing the wheel. 

## Unix to Struct Time Formatting
```py
import time
def _format_datetime(datetime):
    return "{:02}/{:02}/{} {:02}:{:02}:{:02}".format(
        datetime.tm_mon,
        datetime.tm_mday,
        datetime.tm_year,
        datetime.tm_hour,
        datetime.tm_min,
        datetime.tm_sec,
    )
# Plug the time in seconds into unix_time example provided.
unix_time = 1660764970 # Wed Aug 17 2022 19:36:10 GMT+0000
tz_offset_seconds = -14400  # NY Timezone

get_timestamp = int(unix_time + tz_offset_seconds)
current_unix_time = time.localtime(get_timestamp)
current_struct_time = time.struct_time(current_unix_time)
current_date = "{}".format(_format_datetime(current_struct_time))

print("Timestamp:", current_date)
```
code.py output:

`Timestamp: 08/17/2022 15:36:10`

## Seconds to Minutes/Hours/Days function
```py
def time_calc(time):
    if time < 60:
        sleep_int = time
        time_output = f"{sleep_int:.0f} seconds"
        return time_output
    elif 60 <= time < 3600:
        sleep_int = time / 60
        time_output = f"{sleep_int:.0f} minutes"
        return time_output
    elif 3600 <= time < 86400:
        sleep_int = time / 60 / 60
        time_output = f"{sleep_int:.0f} hours"
        return time_output
    elif 86400 <= time < 432000:
        sleep_int = time / 60 / 60 / 24
        time_output = f"{sleep_int:.1f} days"
        return time_output
    else:  # if > 5 days convert float to int & display whole days
        sleep_int = time / 60 / 60 / 24
        time_output = f"{sleep_int:.0f} days"
        return time_output

print("Calc Time: ", time_calc(900))  # time conversion testing
```
code.py output:

`Calc Time:  15 minutes`

## Get Time from Online (ESP32-S2)
For boards with WiFi and no RTC
```py
import gc
import time
import wifi, ssl, socketpool
import adafruit_requests
try:
    from secrets import secrets
except ImportError:
    print("Secrets File Import Error")
    raise
# Initialize Wifi SocketPool
pool = socketpool.SocketPool(wifi.radio)
# Time between retry events
# 900 = 15 mins, 1800 = 30 mins, 3600 = 1 hour
sleep_time = 10

if sleep_time < 60:
    sleep_time_conversion = "seconds"
    sleep_int = sleep_time
elif 60 <= sleep_time < 3600:
    sleep_int = sleep_time / 60
    sleep_time_conversion = "minutes"
elif 3600 <= sleep_time < 86400:
    sleep_int = sleep_time / 60 / 60
    sleep_time_conversion = "hours"
else:
    sleep_int = sleep_time / 60 / 60 / 24
    sleep_time_conversion = "days"

# Check secrets.py to adjust timezone
tz_offset_seconds = int(secrets["timezone_offset"])

def _format_datetime(datetime):
    return "{:02}/{:02}/{} {:02}:{:02}:{:02}".format(
        datetime.tm_mon,
        datetime.tm_mday,
        datetime.tm_year,
        datetime.tm_hour,
        datetime.tm_min,
        datetime.tm_sec,
    )
    
# Connect to Wi-Fi
print("\n===============================")
print("Connecting to WiFi...")

while True:
    while not wifi.radio.ipv4_address:
        try:
            request = adafruit_requests.Session(pool, ssl.create_default_context())
            wifi.radio.enabled = False
            wifi.radio.enabled = True
            wifi.radio.connect(secrets['ssid'], secrets['password'])
        except ConnectionError as e:
            print("Connection Error:", e)
            print("Retrying in 10 seconds")
        time.sleep(10)
        gc.collect()
    print("Connected to WiFi...")
    
    while wifi.radio.ipv4_address:
        request = adafruit_requests.Session(pool, ssl.create_default_context())
        # Connect to WorldTimeAPI
        # print("Getting Time from WorldTimeAPI")
        try:
            response = request.get("http://worldtimeapi.org/api/ip")
            time_data = response.json()
        except RuntimeError as e:
            print("Time API Connection Error:", e)
            print("Retrying in %s %s" % (int(sleep_int), sleep_time_conversion))

        unix_time = int(time_data['unixtime'])
        get_timestamp = int(unix_time + tz_offset_seconds)
        current_unix_time = time.localtime(get_timestamp)
        current_struct_time = time.struct_time(current_unix_time)
        current_date = "{}".format(_format_datetime(current_struct_time))
        
        print("Timestamp:", current_date)
        gc.collect()
        time.sleep(sleep_time)
```
code.py output:

```py
===============================
Connecting to WiFi...
Connected to WiFi...
Timestamp: 09/07/2022 03:50:49
Timestamp: 09/07/2022 03:50:59
Time API Connection Error: Sending request failed
Retrying in 10 seconds
Timestamp: 09/07/2022 03:50:59
Connection Error: No network with that ssid
Retrying in 10 seconds
Connection Error: No network with that ssid
Retrying in 10 seconds
Connection Error: No network with that ssid
Retrying in 10 seconds
Connected to WiFi...
Timestamp: 09/07/2022 03:52:14
```
Built-in error correction fails gracefully if no SSID (WiFi goes down) or time server cannot be contacted. Configurable sleep_time constant so you can easily change the duration of retry attempts. Use longer attempts for IO weather updates for example and shorter updates for retrying WiFi connection.

## Common Secrets.py Config
for AdafruitIO, OpenWeatherMaps, and Time
```py
secrets = {
    "ssid": "Your Wifi SSID",
    "password": "Your WiFi Password",
    "aio_username" : "Your AdafruitIO Username",
    "aio_key" : "Your AdafruitIO Token",
    "openweather_token" : "Your OpenWeatherMaps Token",
    "openweather_lat" : "40.7259", #default lat/lon is adafruit industries
    "openweather_lon" : "-74.0055",
    "timezone": "America/New_York",  # Check http://worldtimeapi.org/timezones
    "timezone_offset": "-14400",  # timezone offset in seconds (plus, 0, or minus)
    }
```
