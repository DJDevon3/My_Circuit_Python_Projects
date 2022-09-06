Check out [TodBot's Circuit Python Tricks](https://github.com/todbot/circuitpython-tricks#circuitpython-tricks)

# DJDevon3's Snippets

These are a few common code snippets that I continually find myself looking at past projects to snag. No sense in re-inventing the wheel. 

### Unix to Struct Time Formatting
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

### Get Time from Online (ESP32-S2)
For boards with WiFi and no RTC
```py
import gc
import time
import wifi, ssl, socketpool
import adafruit_requests
from secrets import secrets

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
            wifi.radio.enabled = False
            wifi.radio.enabled = True
            wifi.radio.connect(secrets['ssid'], secrets['password'])
        except ConnectionError as e:
            print("Connection Error:", e)
            print("Retrying in 10 seconds")
        time.sleep(10)
        gc.collect()
    print("Connected to WiFi...")
    
    # Connect to WorldTimeAPI
    # Check secrets.py to adjust timezone
    tz_offset_seconds = int(secrets["timezone_offset"])
    # print("Getting Time from WorldTimeAPI")
    pool = socketpool.SocketPool(wifi.radio)
    request = adafruit_requests.Session(pool, ssl.create_default_context())
    response = request.get("http://worldtimeapi.org/api/ip")
    time_data = response.json()

    unix_time = int(time_data['unixtime'])
    get_timestamp = int(unix_time + tz_offset_seconds)
    current_unix_time = time.localtime(get_timestamp)
    current_struct_time = time.struct_time(current_unix_time)
    current_date = "{}".format(_format_datetime(current_struct_time))
    
    print("Timestamp:", current_date)
    gc.collect()
    time.sleep(10)
```

### Common Secrets.py Config
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
