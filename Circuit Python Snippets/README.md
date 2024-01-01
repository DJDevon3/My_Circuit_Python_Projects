Check out [TodBot's Circuit Python Tricks](https://github.com/todbot/circuitpython-tricks#circuitpython-tricks) an amazing collection of specialized code snippets for Circuit Python.

# DJDevon3's Snippets

These are a few common code snippets that I continually find myself looking at past projects to snag. No sense in re-inventing the wheel. 

## Make_My_Label (short form label creation function)
- This is particularly useful when you have tons of labels. Each label requires much fewer lines.
```py
# Function for minimizing labels to 1 liners
# Attribution: Anecdata (thanks!)
def make_my_label(font, anchor_point, anchored_position, scale, color):
    func_label = label.Label(font)
    func_label.anchor_point = anchor_point
    func_label.anchored_position = anchored_position
    func_label.scale = scale
    func_label.color = color
    return func_label

hello_label = make_my_label(terminalio.FONT, (0.5, 1.0), (DISPLAY_WIDTH / 2, 15), 1, TEXT_WHITE)

main_group = displayio.Group()
main_group.append(hello_label)
display.root_group = main_group
hello_label.text = "Hello World!"
```
Code.py output:
```
Hello World!
```

## Display RSSI Scan on a TFT
- Couldn't find an example of showing an Wifi Network scan on a TFT display for Circuit Python... so I made one.
```py
# Shorten Labels to 1 liners
def make_my_label(font, anchor_point, anchored_position, scale, color):
    func_label = label.Label(font)
    func_label.anchor_point = anchor_point
    func_label.anchored_position = anchored_position
    func_label.scale = scale
    func_label.color = color
    return func_label

# Create Labels
rssi_data_label0 = make_my_label(terminalio.FONT, (0.0, 0.0), (5, 50), 1, TEXT_WHITE)
rssi_data_label1 = make_my_label(terminalio.FONT, (0.0, 0.0), (5, 50 + 20), 1, TEXT_WHITE)
rssi_data_label2 = make_my_label(terminalio.FONT, (0.0, 0.0), (5, 50 + 40), 1, TEXT_WHITE)
rssi_data_label3 = make_my_label(terminalio.FONT, (0.0, 0.0), (5, 50 + 60), 1, TEXT_WHITE)
rssi_data_label4 = make_my_label(terminalio.FONT, (0.0, 0.0), (5, 50 + 80), 1, TEXT_WHITE)
rssi_data_label5 = make_my_label(terminalio.FONT, (0.0, 0.0), (5, 50 + 100), 1, TEXT_WHITE)
rssi_data_label6 = make_my_label(terminalio.FONT, (0.0, 0.0), (5, 50 + 120), 1, TEXT_WHITE)
rssi_data_label7 = make_my_label(terminalio.FONT, (0.0, 0.0), (5, 50 + 140), 1, TEXT_WHITE)
rssi_data_label8 = make_my_label(terminalio.FONT, (0.0, 0.0), (5, 50 + 160), 1, TEXT_WHITE)
rssi_data_label9 = make_my_label(terminalio.FONT, (0.0, 0.0), (5, 50 + 180), 1, TEXT_WHITE)

# Append Labels to Group
main_group = displayio.Group()
main_group.append(rssi_data_label0)
main_group.append(rssi_data_label1)
main_group.append(rssi_data_label2)
main_group.append(rssi_data_label3)
main_group.append(rssi_data_label4)
main_group.append(rssi_data_label5)
main_group.append(rssi_data_label6)
main_group.append(rssi_data_label7)
main_group.append(rssi_data_label8)
main_group.append(rssi_data_label9)
display.root_group = main_group

while display.root_group is main_group:
        # Displays available networks sorted by RSSI
        networks = []
        NetworkList =[]
        for network in wifi.radio.start_scanning_networks():
            networks.append(network)
        wifi.radio.stop_scanning_networks()
        networks = sorted(networks, key=lambda net: net.rssi, reverse=True)
        for network in networks:
            sorted_networks = {'ssid':network.ssid, 'rssi':network.rssi, 'channel':network.channel}
            NetworkList.append([sorted_networks])
            #print("ssid:",network.ssid, "rssi:",network.rssi, "channel:",network.channel)
        jsonNetworkList = json.dumps(NetworkList)
        json_list = json.loads(jsonNetworkList)
        try:
            rssi_data_label0.text = f"{json_list[0][0]['ssid']:<20}\t{json_list[0][0]['rssi']:<20}\t{json_list[0][0]['channel']:<20}\n"
            rssi_data_label1.text = f"{json_list[1][0]['ssid']:<20}\t{json_list[1][0]['rssi']:<20}\t{json_list[1][0]['channel']:<20}\n"
            rssi_data_label2.text = f"{json_list[2][0]['ssid']:<20}\t{json_list[2][0]['rssi']:<20}\t{json_list[2][0]['channel']:<20}\n"
            rssi_data_label3.text = f"{json_list[3][0]['ssid']:<20}\t{json_list[3][0]['rssi']:<20}\t{json_list[3][0]['channel']:<20}\n"
            rssi_data_label4.text = f"{json_list[4][0]['ssid']:<20}\t{json_list[4][0]['rssi']:<20}\t{json_list[4][0]['channel']:<20}\n"
            rssi_data_label5.text = f"{json_list[5][0]['ssid']:<20}\t{json_list[5][0]['rssi']:<20}\t{json_list[5][0]['channel']:<20}\n"
            rssi_data_label6.text = f"{json_list[6][0]['ssid']:<20}\t{json_list[6][0]['rssi']:<20}\t{json_list[6][0]['channel']:<20}\n"
            rssi_data_label7.text = f"{json_list[7][0]['ssid']:<20}\t{json_list[7][0]['rssi']:<20}\t{json_list[7][0]['channel']:<20}\n"
            rssi_data_label8.text = f"{json_list[8][0]['ssid']:<20}\t{json_list[8][0]['rssi']:<20}\t{json_list[8][0]['channel']:<20}\n"
            rssi_data_label9.text = f"{json_list[9][0]['ssid']:<20}\t{json_list[9][0]['rssi']:<20}\t{json_list[9][0]['channel']:<20}\n"
        except Exception as e:
            print(f"RSSI Label Refresh (index error is ok, ignore it): {e}")
            pass
```
Output: Shows SSID RSSI Channel on Display. It will properly update labels each page refresh.

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
# Plug in your unix time here
unix_time = 1660764970 # Wed Aug 17 2022 19:36:10 GMT+0000
tz_offset_seconds = -14400  # NY Timezone
print(f"Unix Time: {unix_time}")

local_unix_time = int(unix_time) + int(tz_offset_seconds)
print(f"Your Local Unix Time: {local_unix_time}")
current_struct_time = time.localtime(local_unix_time)
print(f"Struct Time Format: {current_struct_time}") 
final_timestamp = "{}".format(_format_datetime(current_struct_time))
print(f"Timestamp: {final_timestamp}")
```
code.py output:
```py
Unix Time: 1660764970 
Your Local Unix Time: 1660750570 
Struct Time Format: struct_time(tm_year=2022, tm_mon=8, tm_mday=17, tm_hour=15, tm_min=36, tm_sec=10, tm_wday=2, tm_yday=229, tm_isdst=-1)
Timestamp: 08/17/2022 15:36:10
```

## Seconds to Minutes/Hours/Days function (good for sleep or update functions)
```py
# Converts seconds to minutes/hours/days
# Attribution: Written by DJDevon3 & refined by Elpekenin
import time
# 900 = 15 mins, 1800 = 30 mins, 3600 = 1 hour
sleep_time = 1800
def time_calc(input_time):
    if input_time < 60:
        return f"{input_time:.0f} seconds"
    if input_time < 3600:
        return f"{input_time / 60:.0f} minutes"
    if input_time < 86400:
        return f"{input_time / 60 / 60:.0f} hours"
    return f"{input_time / 60 / 60 / 24:.1f} days"

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
## Timer update example with time_calc
This one is meant for finished & refined scripts not debugging.
It will only update every x amount of seconds regardless if you attempt to save in between that time or not.
```py
import time
# 900 = 15 mins, 1800 = 30 mins, 3600 = 1 hour
sleep_time = 900
def time_calc(input_time):
    if input_time < 60:
        return f"{input_time:.0f} seconds"
    if input_time < 3600:
        return f"{input_time / 60:.0f} minutes"
    if input_time < 86400:
        return f"{input_time / 60 / 60:.0f} hours"
    return f"{input_time / 60 / 60 / 24:.1f} days"
    
if (time.monotonic() - last) >= sleep_time:
    try:
        # Updates something here when sleep time exceeds last update
    except (ValueError, RuntimeError, OSError) as e:
        print("Error: \n", e)
        time.sleep(60)
        continue
    last = time.monotonic()
    
last_update = time.monotonic() - last
print("Last Updated: ", time_calc(last_update))
update_time = sleep_time - last_update
print("Next Update: ", time_calc(update_time))
time.sleep(sleep_time)
```
code.py output
```py
Last Updated:  3 minutes
Next Update:  12 minutes
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

## Temp sensor bias adjustment (BME280) (obsolete vs logarithm adjust)
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
    elif 81.0 <= temperature <= 81.9:
        display_temperature = temperature -3.2
        print("Temp Scalar 81: ")
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

## Temp Sensor Bias Adjust Algorithm (BME280)
This completely replaces the manual bias adjust example above. Less code and can be more accurate. For the most accurate readings only compare against a "NIST traceable" thermometer. The Adafruit BME280 I2C module ceases to require any adjustment below 68F.
```py
import ulab.numpy as np
# Initialize BME280 Sensor
i2c = board.STEMMA_I2C()  # uses board.SCL and board.SDA
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
display_temperature = 0

# By adding more data points you can create a curve instead of a linear interpolation.
# input_range = [0.0, 68.0, 81.0, 82.0, 82.7, 83.0, 120.0]
# output_range = [0.0, 68.0 - 0.1, 81.0 - 3.2, 82.0 - 3.1, 82.7 - 2.99, 83.0 - 2.94, 120.0 - 8.0]

# Example of linear interpolation (calibrate the data points as you go)
# Start during any season. Will take you about a year to fully calibrate.
# Being within plus/minus 2 degrees is acceptable. Being within 1% between 60F-110F is the goal.
# Below 60F there is no bias needed as there is no board heating to compensate for.
input_range = [0.0, 68.0, 120.0]
output_range = [0.0, 68.0 - 0.1, 120.0 - 2.4]
while True:
    # By default BME280 increases approximately 0.1 per 1 degree over 70F due to PCB heating
    # This algorithm is a work in progress (untested over 95F)
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

## DisplayIO Show/Hide Popup (function by Neradoc)
```py
# 3.5" TFT Featherwing is 480x320
displayio.release_displays()
DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 320

warning_label = label.Label(terminalio.FONT)
warning_label.anchor_point = (0.5, 1.0)
warning_label.anchored_position = (DISPLAY_WIDTH/2, DISPLAY_HEIGHT - 35)
warning_label.scale = (3)
warning_label.color = TEXT_RED

warning_text_label = label.Label(terminalio.FONT)
warning_text_label.anchor_point = (0.5, 1.0)
warning_text_label.anchored_position = (DISPLAY_WIDTH/2, DISPLAY_HEIGHT - 5)
warning_text_label.scale = (2)
warning_text_label.color = TEXT_RED

# Warning label RoundRect
roundrect = RoundRect(int(DISPLAY_WIDTH/2-140), int(DISPLAY_HEIGHT-75), 280, 75, 10, fill=0x0, outline=0xFFFFFF, stroke=1)

main_group = displayio.Group()
# Add warning popup group
main_group.append(warning_group)
warning_group.append(roundrect)
warning_group.append(warning_label)
warning_group.append(warning_text_label)
display.show(main_group)

def show_warning(title, text):
    warning_label.text = title
    warning_text_label.text = text
    warning_group.hidden = False
def hide_warning():
    warning_group.hidden = True
    
while True:
pressure = bme280.pressure  # designed for BME280 Pressure sensor
# Pressure based warning popups
    if pressure <= 919: # pray you never see this message
        show_warning("HOLY SHIT", "Seek Shelter!")
    elif 920 <= pressure <= 979:
        show_warning("DANGER", "Major Hurricane")
    elif 980 <= pressure <= 989:
        show_warning("DANGER", "Minor Hurricane")
    elif 990 <= pressure <= 1001:
        show_warning("WARNING", "Tropical Storm")
    elif 1002 <= pressure <= 1010:  # sudden gusty downpours
        show_warning("CAUTION", "Low Pressure System")
    elif 1018 >= pressure <= 1025:  #sudden light cold rain
        show_warning("CAUTION", "High Pressure System")
    elif pressure >= 1026:
        show_warning("WARNING", "Hail & Tornados?")
    else:
        hide_warning() # Normal pressures: 1111-1017 (no message)
```

![pressure_warning](https://github.com/DJDevon3/My_Circuit_Python_Projects/assets/49322231/f8dd297c-9ff0-41eb-8bde-cdd1092f2ced)



## Common Secrets.py Config (does not initate web workflow)
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

## Common Settings.toml Config (automatically initiates web workflow on port 80)
```py
CIRCUITPY_WIFI_SSID = "Your Wifi SSID"  # Special variable recognized by web workflow
CIRCUITPY_WIFI_PASSWORD = "Your WiFi Password"  # Special variable recognized by web workflow
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
- Updated code to unmount SD card after screenshot to avoid data corruption
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

