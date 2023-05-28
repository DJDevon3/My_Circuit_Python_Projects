Check out [TodBot's Circuit Python Tricks](https://github.com/todbot/circuitpython-tricks#circuitpython-tricks) an amazing collection of specialized code snippets for Circuit Python.

# DJDevon3's Snippets

These are a few common code snippets that I continually find myself looking at past projects to snag. No sense in re-inventing the wheel. 

## Unix to Struct Time Formatting (with timezone offset)
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
print(f"Unix Time: {unix_time}")

get_timestamp = int(unix_time) + int(tz_offset_seconds)
print(f"Unix Timezone Time: {get_timestamp}")
current_struct_time = time.localtime(get_timestamp)
print(f"Current Struct Time: {current_struct_time}")
current_date = "{}".format(_format_datetime(current_struct_time))
print(f"Timestamp: {current_date}")
```
code.py output:
```py
Unix Time: 1660764970
Unix Timezone Time: 1660750570
Current Struct Time: struct_time(tm_year=2022, tm_mon=8, tm_mday=17, tm_hour=15, tm_min=36, tm_sec=10, tm_wday=2, tm_yday=229, tm_isdst=-1)
Timestamp: 08/17/2022 15:36:10
```

## Seconds to Minutes/Hours/Days function (good for sleep or update functions)
```py
import time
# 900 = 15 mins, 1800 = 30 mins, 3600 = 1 hour
sleep_time = 900
def time_calc(input_time):
    if input_time < 60:
        sleep_int = input_time
        time_output = f"{sleep_int:.0f} seconds"
    elif 60 <= input_time < 3600:
        sleep_int = input_time / 60
        time_output = f"{sleep_int:.0f} minutes"
    elif 3600 <= input_time < 86400:
        sleep_int = input_time / 60 / 60
        time_output = f"{sleep_int:.0f} hours"
    elif 86400 <= input_time < 432000:
        sleep_int = input_time / 60 / 60 / 24
        time_output = f"{sleep_int:.1f} days"
    else:  # if > 5 days convert float to int & display whole days
        sleep_int = input_time / 60 / 60 / 24
        time_output = f"{sleep_int:.0f} days"
    return time_output

print("Calc Time: ", time_calc(900))  # time conversion testing
print("Board Uptime: ", time_calc(time.monotonic())) # example for board uptime
print("Next Update: ", time_calc(sleep_time))
time.sleep(sleep_time)
```
code.py output:
```py
Calc Time:  15 minutes
Board Uptime: 1.2 days
Next Update: 30 minutes
```

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
code.py example output: (shows different wifi status & graceful fails)

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

## Temp sensor bias adjustment (BME280)
```py
# Account for PCB heating bias, gets slightly hotter as ambient increases
    temperature = bme280.temperature * 1.8 + 32
    temperature = round(temperature, 1)
    print("Temp: ", temperature) # biased reading
    if temperature >= 110.0:
        display_temperature = temperature -8
        print("Temp Scalar Over 110: ")
    elif 100.0 <= temperature <= 109.9:
        display_temperature = temperature -7
        print("Temp Scalar 100: ")
    elif 90.0 <= temperature <= 99.9:
        display_temperature = temperature -6
        print("Temp Scalar 90: ")
    elif 84.0 <= temperature <= 89.9:
        display_temperature = temperature -2
        print("Temp Scalar 84: ")
    elif 83.0 <= temperature <= 83.9:
        display_temperature = temperature -3
        print("Temp Scalar 83: ")
    elif 82.0 <= temperature <= 82.9:
        display_temperature = temperature -3.1
        print("Temp Scalar 82: ")
    # biased 81.0 biased needs to be 79
    elif 81.0 <= temperature <= 81.9:
        display_temperature = temperature -3.2
        print("Temp Scalar 81: ")
    # biased 80.9 biased needs to be 78
    elif 80.0 <= temperature <= 80.9:
        display_temperature = temperature -3
        print("Temp Scalar 80: ")
    elif 79.0 <= temperature <= 79.9:
        display_temperature = temperature -2.7
        print("Temp Scalar 79: ")
    elif 70.0 <= temperature <= 78.9:
        display_temperature = temperature -2.5
        print("Temp Scalar 70: ")
    elif 60.0 <= temperature <= 69.9:
        display_temperature = temperature -2
        print("Temp Scalar 60: ")
    elif 50.0 <= temperature <= 59.9:
        display_temperature = temperature -1
        print("Temp Scalar 50: ")
    else:
        display_temperature = temperature
        print("Temp Scalar DEFAULT: ")

    print(f"Actual Temp: {display_temperature:.1f}")
```
 Output:
 ```py
Temp:  80.6
Temp Scalar 80: 
Actual Temp: 77.6
```

## Temp Sensor Logarithm Bias Adjust (BME280)
```py
import ulab.numpy as np
# Initialize BME280 Sensor
i2c = board.STEMMA_I2C()  # uses board.SCL and board.SDA
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
display_temperature = 0
# Define the input range and output range
# This might be affected by high ambient humidity?
input_range = [80.0, 81.0, 82.0, 82.7, 83.0, 110.0]
output_range = [80.0 - 3.3, 81.0 - 3.2, 82.0 - 3.1, 82.7 - 3.0, 83.0 - 2.95, 110.0 - 8.0]
while True:
    # By default BME280 increases approximately 0.1 per 1 degree over 50F due to PCB heating
    # This logarithm is a work in progress
    temperature = bme280.temperature * 1.8 + 32
    temperature = round(temperature, 1)
    print("Temp: ", temperature) # biased reading
    # ulab.numpy interpolation
    display_temperature = np.interp(temperature, input_range, output_range)
    print(f"Actual Temp: {display_temperature[0]:.1f}")
```
Output:
```py
Temp:  83.1
# Unbiased temp compared against mercury thermometers is 96% accurate
Actual Temp: 79.8
# Actual temp compared against mercury thermometers is 99.1% accurate
```

## Temp sensor data points (for my own reference)
### Unbiased BME280 vs Mercury Thermometer
- 87.2 = 83
- 87.0 = 83
- 86.5 = 83
- 86.2 = 83
- 85.5 = 82
- 85.3 = 82
- 85.1 = 82
- 84.9 = 82
- 84.8 = 82
- 84.6 = 82
- 83.8 = 81
- 82.7 = 80
- 82.4 = 80
- 82.0 = 79
- 81.9 = 79
- 81.4 = 78
- 80.9 = 78
- 80.6 = 77

## Common Secrets.py Config (Circuit Python 6 & 7 to 8.0 beta)
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

## Common Settings.toml Config (Circuit Python 8.0+)
Circuit Python now uses a Settings.toml file (also creates web workflow automatically)
```py
AP_SSID = "Your Wifi SSID"  # Special variable recognized by web workflow
AP_PASSWORD = "Your WiFi Password"  # Special variable recognized by web workflow
timezone = "America/New_York" # Check http://worldtimeapi.org/timezones
aio_username = "Your AdafruitIO Username"
aio_key = "Your AdafruitIO Token"
openweather_token = "Your OpenWeatherMaps Token"
openweather_lat = "40.7259" #default lat/lon is adafruit industries
openweather_lon = "-74.0055"
timezone = "America/New_York"  # Check http://worldtimeapi.org/timezones
timezone_offset = "-14400" # timezone offset in seconds plus or minus
```

## ESPTool.py for Circuit Python Boards
Windows Command Line Interface (Python, PIP, & ESPTool required)
```py
# Example factory reset of a Feather ESP32-S2
# This method ALSO used for a Factory Reset or Manual Installation using a .bin instead of the UF2
# Download the .bin for your board from CircuitPython.org to your Downloads folder first
# Win+R and type in cmd (or otherwise get to the Windows Command Prompt)

# Change working directory to Downloads folder
C:\Users\Devon>cd downloads
# Ensure the board will communicate (change the chip_id, if you get it wrong you'll see a list of chip types)
C:\Users\Devon\Downloads>esptool.py --chip esp32s2 chip_id
# Erase existing flash memory (all data will be lost)
C:\Users\Devon\Downloads>esptool.py --chip esp32s2 erase_flash
# Change COM port and use correct .bin for your board
C:\Users\Devon\Downloads>esptool.py --port COM69 write_flash -z 0x0 feather-esp32-s2-factory-reset-and-bootloader.bin

#example of successful write_flash
esptool.py v4.5
Serial port COM11
Connecting...
Detecting chip type... Unsupported detection protocol, switching and trying again...
Detecting chip type... ESP32-S2
Chip is ESP32-S2FNR2 (revision v0.0)
Features: WiFi, Embedded Flash 4MB, Embedded PSRAM 2MB, ADC and temperature sensor calibration in BLK2 of efuse V1
Crystal is 40MHz
MAC: xxx
Uploading stub...
Running stub...
Stub running...
Configuring flash size...
Flash will be erased from 0x00000000 to 0x002f1fff...
Compressed 3084992 bytes to 258749...
Wrote 3084992 bytes (258749 compressed) at 0x00000000 in 18.2 seconds (effective 1356.0 kbit/s)...
Hash of data verified.
```

If you've done the above using a factory reset .bin and flashed it successfully:
- Power cycle the board

If this is for a [WipperSnapper Factory Reset](https://learn.adafruit.com/adafruit-esp32-feather-v2/factory-reset) especially on a V2 that doesn't support Circuit Python:
- Go to [WipperSnapper Firmware Uploader](https://adafruit.github.io/WipperSnapper_Firmware_Uploader/?board=feather-esp32-v2) (Use Chrome Browser, Firefox doesn't support web serial)
- Run the firmware updater, add your AdafruitIO and WipperSnapper credentials and you're done!

If you're not installing WipperSnapper and using Circuit Python continue reading...
- Windows should detect a new device and attempt to install drivers.
- It will probably not show up as a USB drive yet.
- Download your boards latest stable release UF2 file from CircuitPython.org.
- Get the board into bootloader mode (FTHRBOOT) USB drive should show up.
- If the USB drive shows up as (CIRCUITPY) you are not in bootloader mode.
- Drag & drop latest version of Circuit Python UF2 to the bootloader (FTHRBOOT) USB Drive. 
- Let the file finish copying, it might automatically restart but most times it does not. 
- Restart the board
- Confirm it's running the version you installed by inspecting boot_out.txt
- You're all set up and ready to use Circuit Python

## Screenshot (Bitmap Saver)
- Requires bitmap_saver library & SD Card (either built into a device or as a module)
- After it says "Screenshot Taken" you have 120 seconds to remove the SD card, transfer the image to your PC, and reinsert the SD card back into the microcontroller otherwise the script will crash and you'll have to reboot the microcontroller.  You can set it to whatever time value you want. I find 3 minutes to be sufficient.
```py
import adafruit_sdcard
import storage
from adafruit_bitmapsaver import save_pixels

# Initialize SDCard
cs = digitalio.DigitalInOut(board.D5)
sdcard = adafruit_sdcard.SDCard(spi, cs)
vfs = storage.VfsFat(sdcard)
virtual_root = "/sd"
storage.mount(vfs, virtual_root)

TAKE_SCREENSHOT = False  # Set to True to take a screenshot
if TAKE_SCREENSHOT:
    print("Taking Screenshot... ")
    save_pixels("/sd/screenshot.bmp", display)
    print("Screenshot Saved")
    storage.umount(vfs)
    print("SD Card Unmounted")  # unsafe to remove SD card until you see this message
```

