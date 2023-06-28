# SPDX-FileCopyrightText: 2023 DJDevon3
# SPDX-License-Identifier: MIT
# Adafruit ESP32-S3 Feather Weather with MQTT
# Coded for Circuit Python 8.1

import gc
import os
import supervisor
import time
import board
import displayio
import digitalio
import terminalio
import adafruit_imageload
import adafruit_sdcard
import storage
import ssl
import wifi
import socketpool
import json
import adafruit_requests
import ulab.numpy as np
import adafruit_minimqtt.adafruit_minimqtt as MQTT
from adafruit_minimqtt.adafruit_minimqtt import MMQTTException
from adafruit_io.adafruit_io import IO_MQTT, AdafruitIO_MQTTError
from adafruit_display_text import label
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_bitmap_font import bitmap_font
from adafruit_bitmapsaver import save_pixels
from adafruit_lc709203f import LC709203F
from adafruit_bme280 import basic as adafruit_bme280
from adafruit_hx8357 import HX8357

# 3.5" TFT Featherwing is 480x320
displayio.release_displays()
DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 320

# Initialize Web Sockets (This should always be near the top of a script!)
# There can be only one pool
pool = socketpool.SocketPool(wifi.radio)

try:
    from secrets import secrets
except ImportError:
    print("Secrets File Import Error")
    raise

aio_username = secrets['aio_username']
aio_key = secrets['aio_key']
OWKEY = secrets['openweather_token']
OWLAT = secrets['openweather_lat']
OWLON = secrets['openweather_lon']
timezone = secrets['timezone']
tz_offset_seconds = secrets['timezone_offset']

# MQTT Topic
# Use this format for a standard MQTT broker
# mqtt_topic = "test/topic"

# AdafruitIO MMQTT Topic
# Use this format for io.adafruit.com
# /g/ is group and /f/ is feed
mqtt_topic = aio_username + '/g/default'

# Creates & Publishes to default AdafruitIO group
feed_01 = "BME280-Unbiased"
feed_02 = "BME280-RealTemp"
feed_03 = "BME280-Pressure"
feed_04 = "BME280-Humidity"
feed_05 = "BME280-Altitude"

# Time in seconds between updates (polling)
# 600 = 10 mins, 900 = 15 mins, 1800 = 30 mins, 3600 = 1 hour
sleep_time = 900

# Initialize TFT Display
spi = board.SPI()
tft_cs = board.D9
tft_dc = board.D10
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = HX8357(display_bus, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT)

# Initialize BME280 Sensor
i2c = board.STEMMA_I2C()  # uses board.SCL and board.SDA
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
bme280.sea_level_pressure = bme280.pressure
# print("Sea Level Pressure: ", bme280.sea_level_pressure)
# print("Altitude = %0.2f meters" % bme280.altitude)

# Initialize SDCard on TFT Featherwing
cs = digitalio.DigitalInOut(board.D5)
sdcard = adafruit_sdcard.SDCard(spi, cs)
vfs = storage.VfsFat(sdcard)
virtual_root = "/sd"
storage.mount(vfs, virtual_root)

i2c = board.I2C()
battery_monitor = LC709203F(board.I2C())
# LC709203F github repo library
# https://github.com/adafruit/Adafruit_CircuitPython_LC709203F/blob/main/adafruit_lc709203f.py
# only up to 3000 supported, don't use PackSize if battery larger than 3000mah
# battery_monitor.pack_size = PackSize.MAH3000
battery_monitor.thermistor_bconstant = 3950
battery_monitor.thermistor_enable = True

# Converts seconds in minutes/hours/days
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
    else:
        sleep_int = input_time / 60 / 60 / 24
        time_output = f"{sleep_int:.1f} days"
    return time_output

# Quick Colors for Labels
TEXT_BLACK = 0x000000
TEXT_BLUE = 0x0000FF
TEXT_CYAN = 0x00FFFF
TEXT_GRAY = 0x8B8B8B
TEXT_GREEN = 0x00FF00
TEXT_LIGHTBLUE = 0x90C7FF
TEXT_MAGENTA = 0xFF00FF
TEXT_ORANGE = 0xFFA500
TEXT_PURPLE = 0x800080
TEXT_RED = 0xFF0000
TEXT_WHITE = 0xFFFFFF
TEXT_YELLOW = 0xFFFF00

# Fonts are optional
medium_font = bitmap_font.load_font("/fonts/Arial-16.bdf")
huge_font = bitmap_font.load_font("/fonts/GoodTimesRg-Regular-121.bdf")

# NOAA Animated Gif
# Customize here: https://radar.weather.gov/region/conus/standard
NOAA_MAP_SOURCE = "https://radar.weather.gov/ridge/standard/SOUTHEAST_0.gif"

# OpenWeather 2.5 Free API
DATA_SOURCE = "https://api.openweathermap.org/data/2.5/onecall?"
DATA_SOURCE += "lat=" + OWLAT
DATA_SOURCE += "&lon=" + OWLON
DATA_SOURCE += "&timezone=" + timezone
DATA_SOURCE += "&timezone_offset=" + str(tz_offset_seconds)
DATA_SOURCE += "&exclude=hourly,daily"
DATA_SOURCE += "&appid=" + OWKEY
DATA_SOURCE += "&units=imperial"

def _format_datetime(datetime):
    return "{:02}/{:02}/{} {:02}:{:02}:{:02}".format(
        datetime.tm_mon,
        datetime.tm_mday,
        datetime.tm_year,
        datetime.tm_hour,
        datetime.tm_min,
        datetime.tm_sec,
    )

def _format_date(datetime):
    return "{:02}/{:02}/{:02}".format(
        datetime.tm_year,
        datetime.tm_mon,
        datetime.tm_mday,
    )

def _format_time(datetime):
    return "{:02}:{:02}".format(
        datetime.tm_hour,
        datetime.tm_min,
        # datetime.tm_sec,
    )

# Individual customizable position labels
# https://learn.adafruit.com/circuitpython-display-support-using-displayio/text
hello_label = label.Label(terminalio.FONT)
hello_label.anchor_point = (0.5, 1.0)
hello_label.anchored_position = (DISPLAY_WIDTH/2, 15)
hello_label.scale = (1)
hello_label.color = TEXT_WHITE

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

date_label = label.Label(medium_font)
# Anchor point bottom center of text
date_label.anchor_point = (0.0, 0.0)
# Display width divided in half for center of display (x,y)
date_label.anchored_position = (5, 5)
date_label.scale = 1
date_label.color = TEXT_LIGHTBLUE

time_label = label.Label(medium_font)
# Anchor point bottom center of text
time_label.anchor_point = (0.0, 0.0)
# Display width divided in half for center of display (x,y)
time_label.anchored_position = (5, 25)
time_label.scale = 2
time_label.color = TEXT_LIGHTBLUE

temp_label = label.Label(medium_font)
temp_label.anchor_point = (1.0, 1.0)
temp_label.anchored_position = (475, 145)
temp_label.scale = 2
temp_label.color = TEXT_ORANGE

temp_data_label = label.Label(huge_font)
temp_data_label.anchor_point = (0.5, 1.0)
temp_data_label.anchored_position = (DISPLAY_WIDTH / 2, 200)
temp_data_label.scale = 1
temp_data_label.color = TEXT_ORANGE

temp_data_shadow = label.Label(huge_font)
temp_data_shadow.anchor_point = (0.5, 1.0)
temp_data_shadow.anchored_position = (DISPLAY_WIDTH / 2 + 2, 200 + 2)
temp_data_shadow.scale = 1
temp_data_shadow.color = TEXT_BLACK

owm_temp_data_label = label.Label(medium_font)
owm_temp_data_label.anchor_point = (0.5, 1.0)
owm_temp_data_label.anchored_position = (DISPLAY_WIDTH / 2, 100)
owm_temp_data_label.scale = 2
owm_temp_data_label.color = TEXT_LIGHTBLUE

owm_temp_data_shadow = label.Label(medium_font)
owm_temp_data_shadow.anchor_point = (0.5, 1.0)
owm_temp_data_shadow.anchored_position = (DISPLAY_WIDTH / 2 + 2, 100 + 2)
owm_temp_data_shadow.scale = 2
owm_temp_data_shadow.color = TEXT_BLACK

humidity_label = label.Label(medium_font)
humidity_label.anchor_point = (0.0, 1.0)
humidity_label.anchored_position = (5, DISPLAY_HEIGHT - 23)
humidity_label.scale = 1
humidity_label.color = TEXT_GRAY

humidity_data_label = label.Label(medium_font)
humidity_data_label.anchor_point = (0.0, 1.0)
humidity_data_label.anchored_position = (5, DISPLAY_HEIGHT)
humidity_data_label.scale = 1
humidity_data_label.color = TEXT_ORANGE

owm_humidity_data_label = label.Label(medium_font)
owm_humidity_data_label.anchor_point = (0.0, 1.0)
owm_humidity_data_label.anchored_position = (5, DISPLAY_HEIGHT - 55)
owm_humidity_data_label.scale = 1
owm_humidity_data_label.color = TEXT_LIGHTBLUE

barometric_label = label.Label(medium_font)
barometric_label.anchor_point = (1.0, 1.0)
barometric_label.anchored_position = (470, DISPLAY_HEIGHT - 27)
barometric_label.scale = 1
barometric_label.color = TEXT_GRAY

barometric_data_label = label.Label(medium_font)
barometric_data_label.anchor_point = (1.0, 1.0)
barometric_data_label.anchored_position = (470, DISPLAY_HEIGHT)
barometric_data_label.scale = 1
barometric_data_label.color = TEXT_ORANGE

owm_barometric_data_label = label.Label(medium_font)
owm_barometric_data_label.anchor_point = (1.0, 1.0)
owm_barometric_data_label.anchored_position = (470, DISPLAY_HEIGHT - 55)
owm_barometric_data_label.scale = 1
owm_barometric_data_label.color = TEXT_LIGHTBLUE

vbat_label = label.Label(medium_font)
vbat_label.anchor_point = (1.0, 1.0)
vbat_label.anchored_position = (DISPLAY_WIDTH - 15, 20)
vbat_label.scale = 1

plugbmp_label = label.Label(terminalio.FONT)
plugbmp_label.anchor_point = (1.0, 1.0)
plugbmp_label.scale = 1

greenbmp_label = label.Label(terminalio.FONT)
greenbmp_label.anchor_point = (1.0, 1.0)
greenbmp_label.scale = 1

bluebmp_label = label.Label(terminalio.FONT)
bluebmp_label.anchor_point = (1.0, 1.0)
bluebmp_label.scale = 1

yellowbmp_label = label.Label(terminalio.FONT)
yellowbmp_label.anchor_point = (1.0, 1.0)
yellowbmp_label.scale = 1

orangebmp_label = label.Label(terminalio.FONT)
orangebmp_label.anchor_point = (1.0, 1.0)
orangebmp_label.scale = 1

redbmp_label = label.Label(terminalio.FONT)
redbmp_label.anchor_point = (1.0, 1.0)
redbmp_label.scale = 1

# Load Bitmap to tile grid first (Background layer)
DiskBMP = displayio.OnDiskBitmap("/images/Astral_Fruit_8bit.bmp")
tile_grid = displayio.TileGrid(
    DiskBMP,
    pixel_shader=DiskBMP.pixel_shader,
    width=1,
    height=1,
    tile_width=DISPLAY_WIDTH,
    tile_height=DISPLAY_HEIGHT)

# Load battery voltage icons (from 1 sprite sheet image)
sprite_sheet, palette = adafruit_imageload.load("/icons/vbat_spritesheet.bmp",
                                                bitmap=displayio.Bitmap,
                                                palette=displayio.Palette)
sprite = displayio.TileGrid(sprite_sheet, pixel_shader=palette,
                            width=1,
                            height=1,
                            tile_width=11,
                            tile_height=20)
sprite_group = displayio.Group(scale=1)
sprite_group.append(sprite)
sprite_group.x = 470
sprite_group.y = 0

# Warning label RoundRect
roundrect = RoundRect(int(DISPLAY_WIDTH/2-140), int(DISPLAY_HEIGHT-75), 280, 75, 10, fill=0x0, outline=0xFFFFFF, stroke=1)

# Create subgroups
text_group = displayio.Group()
text_group.append(tile_grid)
temp_group = displayio.Group()
warning_group = displayio.Group()
main_group = displayio.Group()

# Add subgroups to main display group
main_group.append(text_group)
main_group.append(warning_group)
main_group.append(temp_group)
main_group.append(sprite_group)

# Add warning popup group
warning_group.append(roundrect)
warning_group.append(warning_label)
warning_group.append(warning_text_label)

# Label Display Group (foreground layer)
text_group.append(hello_label)
text_group.append(date_label)
text_group.append(time_label)
temp_group.append(temp_label)
temp_group.append(temp_data_shadow)
temp_group.append(temp_data_label)
temp_group.append(owm_temp_data_shadow)
temp_group.append(owm_temp_data_label)
text_group.append(humidity_label)
text_group.append(humidity_data_label)
text_group.append(owm_humidity_data_label)
text_group.append(barometric_label)
text_group.append(barometric_data_label)
text_group.append(owm_barometric_data_label)
text_group.append(vbat_label)
text_group.append(plugbmp_label)
text_group.append(greenbmp_label)
text_group.append(bluebmp_label)
text_group.append(yellowbmp_label)
text_group.append(orangebmp_label)
text_group.append(redbmp_label)
display.show(main_group)

def show_warning(title, text):
    warning_label.text = title
    warning_text_label.text = text
    warning_group.hidden = False
def hide_warning():
    warning_group.hidden = True

# Define callback methods when events occur
def connect(mqtt_client):
    # This function will be called when the mqtt_client is connected
    # successfully to the broker.
    print("Connected to MQTT Broker! ✅")

def disconnect(mqtt_client, userdata, rc):
    # This method is called when the mqtt_client disconnects
    # from the broker.
    print("Disconnected from MQTT Broker!")

def subscribe(mqtt_client, userdata, topic, granted_qos):
    # This method is called when the mqtt_client subscribes to a new feed.
    print("Subscribed to {0} with QOS level {1}".format(topic, granted_qos))

def unsubscribe(mqtt_client, userdata, topic, pid):
    # This method is called when the mqtt_client unsubscribes from a feed.
    print("Unsubscribed from {0} with PID {1}".format(topic, pid))

def publish(mqtt_client, userdata, topic, pid):
    # This method is called when the mqtt_client publishes data to a feed.
    print("Published to {0} with PID {1}".format(topic, pid))

def message(client, topic, message):
    # Method called when a client's subscribed feed has a new value.
    print("New message on topic {0}: {1}".format(topic, message))

# Initialize a new MQTT Client object
mqtt_client = MQTT.MQTT(
    broker="io.adafruit.com",
    port=1883,
    username=aio_username,
    password=aio_key,
    socket_pool=pool,
    ssl_context=ssl.create_default_context(),
)

# Initialize an Adafruit IO MQTT Client
io = IO_MQTT(mqtt_client)

# Connect callback handlers to mqtt_client
io.on_connect = connect
io.on_disconnect = disconnect
io.on_subscribe = subscribe
io.on_unsubscribe = unsubscribe
io.on_publish = publish
io.on_message = message

last = 0
display_temperature = 0
# Define the input range and output range
# pressure at 1014 & 88F at 100% accurate. sea level pressure affects temp?
input_range = [50.0, 70, 80, 88.0, 120.0]
output_range = [50.0 - 0.1, 70.0 - 2.0, 80 - 1.0, 88.0 - 0.0, 120.0 - 2.2]

while True:
    hello_label.text = "ESP32-S3 MQTT Feather Weather"
    print("===============================")
    debug_OWM = False  # Set to True for Serial Print Debugging

    # USB Power Sensing
    try:
        vbat_label.text = f"{battery_monitor.cell_voltage:.2f}"
    except (ValueError, RuntimeError, OSError) as e:
        print("LC709203F Error: \n", e)
    # Set USB plug icon and voltage label to white
    usb_sense = supervisor.runtime.serial_connected
    if debug_OWM:
        print("USB Sense: ", usb_sense)
    if usb_sense:  # if on USB power show plug sprite icon
        vbat_label.color = TEXT_WHITE
        sprite[0] = 5
    if not usb_sense:  # if on battery power only
        # Changes battery voltage color depending on charge level
        if vbat_label.text >= "4.23":
            vbat_label.color = TEXT_WHITE
            sprite[0] = 5
        elif "4.10" <= vbat_label.text <= "4.22":
            vbat_label.color = TEXT_GREEN
            sprite[0] = 0
        elif "4.00" <= vbat_label.text <= "4.09":
            vbat_label.color = TEXT_LIGHTBLUE
            sprite[0] = 1
        elif "3.90" <= vbat_label.text <= "3.99":
            vbat_label.color = TEXT_YELLOW
            sprite[0] = 2
        elif "3.80" <= vbat_label.text <= "3.89":
            vbat_label.color = TEXT_ORANGE
            sprite[0] = 3
        elif vbat_label.text <= "3.79":
            vbat_label.color = TEXT_RED
            sprite[0] = 4
        else:
            vbat_label.color = TEXT_WHITE

    # Local sensor data display
    temp_label.text = "°F"

    # Board Uptime
    print("Board Uptime: ", time_calc(time.monotonic()))

    # Account for PCB heating bias, gets slightly hotter as ambient increases
    temperature = bme280.temperature * 1.8 + 32
    temp_round = round(temperature, 2)
    print("Temp: ", temperature) # biased reading
    display_temperature = np.interp(temperature, input_range, output_range)
    display_temperature = round(display_temperature[0], 2)
    print(f"Actual Temp: {display_temperature:.1f}")
    # pressure = 1000  # Manually set to debug warning message
    mqtt_humidity = round(bme280.relative_humidity, 1)
    mqtt_pressure = round(bme280.pressure, 1)
    mqtt_altitude = round(bme280.altitude, 2)

    temp_data_shadow.text = f"{display_temperature:.1f}"
    temp_data_label.text = f"{display_temperature:.1f}"
    humidity_label.text = "Humidity"
    humidity_data_label.text = f"{mqtt_humidity:.1f} %"
    barometric_label.text = "Pressure"
    barometric_data_label.text = f"{mqtt_pressure:.1f}"

    # Warnings based on local sensors
    if mqtt_pressure <= 919:  # pray you never see this message
        show_warning("HOLY SHIT", "Seek Shelter!")
    elif 920 <= mqtt_pressure <= 979:
        show_warning("DANGER", "Major Hurricane")
    elif 980 <= mqtt_pressure <= 989:
        show_warning("DANGER", "Minor Hurricane")
    elif 990 <= mqtt_pressure <= 1001:
        show_warning("WARNING", "Tropical Storm")
    elif 1002 <= mqtt_pressure <= 1009:  # sudden gusty downpours
        show_warning("CAUTION", "Low Pressure System")
    elif 1019 <= mqtt_pressure <= 1025:  #sudden light cold rain
        show_warning("CAUTION", "High Pressure System")
    elif mqtt_pressure >= 1026:
        show_warning("WARNING", "Hail & Tornados?")
    else:
        hide_warning()  # Normal pressures: 1110-1018 (no message)

    # Connect to Wi-Fi
    print("===============================")
    print("Connecting to WiFi...")
    requests = adafruit_requests.Session(pool, ssl.create_default_context())
    while not wifi.radio.ipv4_address:
        try:
            wifi.radio.connect(secrets['ssid'], secrets['password'])
        except ConnectionError as e:
            print("Connection Error:", e)
            print("Retrying in 10 seconds")
        time.sleep(10)
        gc.collect()
    print("WiFi! ✅")

    while wifi.radio.ipv4_address:
        try:
            if debug_OWM:
                print("Attempting to GET Weather!")
                # Uncomment line below to print API URL with all data filled in
                # print("Full API GET URL: ", DATA_SOURCE)
                print("\n===============================")
            response = requests.get(DATA_SOURCE).json()

            # uncomment the 2 lines below to see full json response
            # dump_object = json.dumps(response)
            # print("JSON Dump: ", dump_object)
            if int(response['current']['dt']) == "KeyError: example":
                print("Unable to retrive data due to key:value error")
                print("likely OpenWeather Throttling for too many API calls")
            else:
                if debug_OWM:
                    print("OpenWeather Success")

            get_timestamp = int(response['current']['dt'] + int(tz_offset_seconds))
            current_unix_time = time.localtime(get_timestamp)
            current_struct_time = time.struct_time(current_unix_time)
            current_date = "{}".format(_format_date(current_struct_time))
            current_time = "{}".format(_format_time(current_struct_time))

            sunrise = int(response['current']['sunrise'] + int(tz_offset_seconds))
            sunrise_unix_time = time.localtime(sunrise)
            sunrise_struct_time = time.struct_time(sunrise_unix_time)
            sunrise_time = "{}".format(_format_time(sunrise_struct_time))

            sunset = int(response['current']['sunset'] + int(tz_offset_seconds))
            sunset_unix_time = time.localtime(sunset)
            sunset_struct_time = time.struct_time(sunset_unix_time)
            sunset_time = "{}".format(_format_time(sunset_struct_time))

            owm_temp = response['current']['temp']
            owm_pressure = response['current']['pressure']
            owm_humidity = response['current']['humidity']
            weather_type = response['current']['weather'][0]['main']

            if debug_OWM:
                print("Timestamp:", current_date + " " + current_time)
                print("Sunrise:", sunrise_time)
                print("Sunset:", sunset_time)
                print("Temp:", owm_temp)
                print("Pressure:", owm_pressure)
                print("Humidity:", owm_humidity)
                print("Weather Type:", weather_type)
                print("Next Update: ", time_calc(sleep_time))
                print("===============================")

            gc.collect()
            date_label.text = current_date
            time_label.text = current_time
            owm_temp_data_shadow.text = f"{owm_temp:.1f}"
            owm_temp_data_label.text = f"{owm_temp:.1f}"
            owm_humidity_data_label.text = f"{owm_humidity:.1f} %"
            owm_barometric_data_label.text = f"{owm_pressure:.1f}"

        except (ValueError, RuntimeError) as e:
            print("Failed to get OWM data, retrying\n", e)
            time.sleep(240)
            continue
        response = None

        # Connect to Adafruit IO
        print("Connecting to Adafruit IO...")
        try:
            io.connect()
        except (ValueError, RuntimeError, AdafruitIO_MQTTError) as e:
            print("Failed to connect, retrying\n", e)

        if (time.monotonic() - last) >= sleep_time:
            try:
                print(f"Publishing {feed_01}: {temp_round} | {feed_02}: {display_temperature} | {feed_03}: {mqtt_pressure} | {feed_04}: {mqtt_humidity} | {feed_05}: {mqtt_altitude}")
                io.publish(feed_01, temp_round)
                io.publish(feed_02, display_temperature)
                io.publish(feed_03, mqtt_pressure)
                io.publish(feed_04, mqtt_humidity)
                io.publish(feed_05, mqtt_altitude)
            except (ValueError, RuntimeError, ConnectionError, OSError, MMQTTException) as e:
                print("io.publish Error: \n", e)
                time.sleep(60)
                continue
            last = time.monotonic()
        # io.disconnect()

        try:
            debug_NOAA = False
            url = 'https://radar.weather.gov/ridge/standard/SOUTHEAST_0.gif'
            r = requests.get(url)
            if debug_NOAA:
                print(r.status_code)
                print(r.headers)
                print(len(r.content))
                print("Content Type: ", r.headers.get('content-type'))
                print("Object URL: ", r)
            with open('/sd/SOUTHEAST_0.gif', 'wb') as fp:
                fp.write(r.content)
            if debug_NOAA:
                print("Wrote File: /sd/SOUTHEAST_0.gif")

        except (ValueError, RuntimeError) as e:
            print("Failed to get NOAA data, retrying\n", e)
            time.sleep(60)
            continue
        r = None

        print("Next Update: ", time_calc(sleep_time))
        print("===============================")
        gc.collect()
        time.sleep(sleep_time)
        break

    TAKE_SCREENSHOT = False  # Set to True to take a screenshot
    if TAKE_SCREENSHOT:
        print("Taking Screenshot... ")
        save_pixels("/sd/screenshot.bmp", display)
        print("Screenshot Saved")
        storage.umount(vfs)
        print("SD Card Unmounted! It is now safe to remove SD Card")
        time.sleep(120)
