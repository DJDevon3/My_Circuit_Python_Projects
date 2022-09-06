# Get Time from Online (ESP32-S2)
Your board doesn't need to have an RTC to set the time. As long as your board has Wifi you can get time from the internet.
```py
import time
import rtc, wifi, ssl, socketpool
import adafruit_requests
import adafruit_ntp
from secrets import secrets

my_tz_offset = -5  # EDT

wifi.radio.connect(secrets["ssid"], secrets["password"])
print("Connected, getting WorldTimeAPI time")
pool = socketpool.SocketPool(wifi.radio)
request = adafruit_requests.Session(pool, ssl.create_default_context())

response = request.get("http://worldtimeapi.org/api/ip")
time_data = response.json()
unixtime = int(time_data['unixtime']) + int(time_data['raw_offset'])
print("URL time: ", response.headers['date'])

rtc.RTC().datetime = time.localtime( unixtime ) # create time struct and set RTC with it

while True:
    # Time in seconds from when board was powered on
    now = time.monotonic()
    print("current datetime: ", time.localtime())

```
