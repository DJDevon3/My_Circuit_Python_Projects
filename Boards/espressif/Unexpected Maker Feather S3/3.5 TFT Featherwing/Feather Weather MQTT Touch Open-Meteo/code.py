# SPDX-FileCopyrightText: 2025 DJDevon3
# SPDX-License-Identifier: MIT
# Coded for Circuit Python 9.2
"""Feather Weather S3 MQTT Touchscreen"""

import os
import supervisor
import microcontroller
import time
import board
import displayio
import fourwire
import feathers3
import featherweather as FW
import digitalio
import terminalio
import pwmio
import adafruit_connection_manager
import wifi
import adafruit_requests
import json
import math
import ulab.numpy as np
import adafruit_minimqtt.adafruit_minimqtt as MQTT
from adafruit_minimqtt.adafruit_minimqtt import MMQTTException
from adafruit_bme280 import basic as adafruit_bme280
from adafruit_bitmapsaver import save_pixels

_now = time.monotonic()

# Initalize Wifi, Socket Pool, Request Session
pool = adafruit_connection_manager.get_radio_socketpool(wifi.radio)
SSL_CONTEXT = adafruit_connection_manager.get_radio_ssl_context(wifi.radio)
# adafruit_requests.Session keep outside the main loop
# otherwise you get Out of Socket errors.
requests = adafruit_requests.Session(pool, SSL_CONTEXT)

# Use settings.toml for credentials
ssid = os.getenv("WIFI_SSID")
password = os.getenv("WIFI_PASSWORD")
aio_username = os.getenv("aio_username")
aio_key = os.getenv("aio_key")
LATITUDE = os.getenv("LATITUDE")
LONGITUDE = os.getenv("LONGITUDE")
ELEVATION = os.getenv("ELEVATION")
TIMEZONE = os.getenv("TIMEZONE")

# MQTT Topic
# Use this format for a standard MQTT broker
adafruitio_errors = aio_username + "/errors"
adafruitio_throttled = aio_username + "/throttle"
feed_01 = aio_username + "/feeds/BME280-Unbiased"
feed_02 = aio_username + "/feeds/BME280-RealTemp"
feed_03 = aio_username + "/feeds/BME280-Pressure"
feed_04 = aio_username + "/feeds/BME280-Humidity"
feed_05 = aio_username + "/feeds/BME280-Altitude"

# Time in seconds between updates (polling)
# 600 = 10 mins, 900 = 15 mins, 1800 = 30 mins, 3600 = 1 hour
SLEEP_TIME = 900

# TFT Featherwing LITE Bodge Mod
# Use board.D8 for NRF52840 Sense, board.A5 for ESP32-S3
# Controls TFT backlight brightness via PWM signal
display_duty_cycle = 65535  # Values from 0 to 65535
TFT_brightness = pwmio.PWMOut(board.A5, frequency=500, duty_cycle=display_duty_cycle)
TFT_brightness.duty_cycle = 40000


FW.splash_label.text = "Initializing BME280 Sensor..."

# Enable 2nd LDO for vertical stemma
feathers3.set_ldo2_power(True)
# Battery Voltage & 5V USB Sense
# vbat_monitor = feathers3.get_battery_voltage()
# vbus_monitor = feathers3.get_vbus_present()

# Initialize I2C
try:
    i2c2 = board.STEMMA_VERTICAL_I2C()  # uses board.SCL and board.SDA
except RuntimeError as e:
    print(f"I2C Initalize Failure: {e}")
    microcontroller.reset()

# Initialize BME280 Sensor
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c2)
# sea_level_pressure should be set in the while true loop
# bme280.sea_level_pressure = bme280.pressure
# print("Sea Level Pressure: ", bme280.sea_level_pressure)
# print("Altitude = %0.2f meters" % bme280.altitude)
#bme280_to_farenheit = float(bme280.temperature * 1.8 + 32)
#print(f"BME280 Temp: {bme280_to_farenheit}")

# Open-Meteo Free API
DATA_SOURCE = "https://api.open-meteo.com/v1/forecast?"
DATA_SOURCE += "latitude="+LATITUDE
DATA_SOURCE += "&longitude="+LONGITUDE
DATA_SOURCE += "&elevation="+ELEVATION
DATA_SOURCE += "&current=temperature_2m,"
DATA_SOURCE += "relative_humidity_2m,"
DATA_SOURCE += "apparent_temperature,"
DATA_SOURCE += "is_day,"
DATA_SOURCE += "precipitation,"
DATA_SOURCE += "rain,"
DATA_SOURCE += "showers,"
DATA_SOURCE += "snowfall,"
DATA_SOURCE += "weather_code,"
DATA_SOURCE += "cloud_cover,"
DATA_SOURCE += "pressure_msl,"
DATA_SOURCE += "surface_pressure,"
DATA_SOURCE += "wind_speed_10m,"
DATA_SOURCE += "wind_direction_10m,"
DATA_SOURCE += "wind_gusts_10m"
DATA_SOURCE += "&daily=sunrise,sunset"
DATA_SOURCE += "&temperature_unit=fahrenheit"
DATA_SOURCE += "&wind_speed_unit=mph"
DATA_SOURCE += "&precipitation_unit=inch"
DATA_SOURCE += "&timeformat=unixtime"
DATA_SOURCE += "&timezone="+TIMEZONE
HEADER = {"accept": "application/json", "User-Agent": "Blinka", "Contact": "Github.com/Adafruit"}

FW.splash_label.text = "Loading MQTT Functions..."
# Define callback methods when events occur
def connect(mqtt_client, userdata, flags, rc):
    # Method when mqtt_client connected to the broker.
    print(" | ✅ Connected to MQTT Broker!")


def disconnect(mqtt_client, userdata, rc):
    # Method when the mqtt_client disconnects from broker.
    print(" | ✂️ Disconnected from MQTT Broker")


def subscribe(mqtt_client, userdata, topic, granted_qos):
    # Method when the mqtt_client subscribes to a new feed.
    print("Subscribed to {0} with QOS level {1}".format(topic, granted_qos))


def unsubscribe(mqtt_client, userdata, topic, pid):
    # Method when the mqtt_client unsubscribes from a feed.
    print("Unsubscribed from {0} with PID {1}".format(topic, pid))


def publish(mqtt_client, userdata, topic, pid):
    # Method when the mqtt_client publishes data to a feed.
    print(f" | | 📖 Published {topic}")


def message(mqtt_client, topic, message):
    # Method client's subscribed feed has a new value.
    print("New message on topic {0}: {1}".format(topic, message))


def ioerrors(mqtt_client, topic, message):
    # Method for callback errors.
    print("New message on topic {0}: {1}".format(topic, message))


def throttle(mqtt_client, topic, message):
    # Method for callback errors.
    print("New message on topic {0}: {1}".format(topic, message))


# Initialize MQTT Client object
mqtt_client = MQTT.MQTT(
    broker="io.adafruit.com",
    username=aio_username,
    password=aio_key,
    socket_pool=pool,
    ssl_context=SSL_CONTEXT,
)

# Connect callback handlers to mqtt_client
mqtt_client.on_connect = connect
mqtt_client.on_disconnect = disconnect
mqtt_client.on_subscribe = subscribe
mqtt_client.on_unsubscribe = unsubscribe
mqtt_client.on_publish = publish
mqtt_client.on_message = message
mqtt_client.subscribe_to_errors = ioerrors
mqtt_client.subscribe_to_throttling = throttle

FW.splash_label.text = "Loading Sensor Algorithms..."
display_temperature = 0
# Temperature Interpolation Algorithm
# pressure and humidity can affect temperature
# especially in sub-tropical climate!
humid_input_range = [0.0, 100]  # interpolated increase
humid_output_range = [0.0, 2.0]  # with humidity
input_range = [50.0, 69, 72, 73, 75, 76, 80, 88.0, 120.0]
output_range = [
    50.0 - 0.1,
    69,
    72.0 - 1.1,
    73.0 - 1.2,
    75.0 - 1.4,
    76 - 1.5,
    80 - 1.0,
    88.0 - 0.0,
    120.0 - 2.2,
]

last = time.monotonic()
First_Run = True
FW.temp_degree_label.text = "°F"
FW.splash_label.text = "Loading GUI..."
ERROR = " | ❌ Error: "
while True:
    while FW.display.root_group is FW.main_group or FW.loading_splash:
        FW.wallpaper[0] = 0
        if not First_Run and FW.display.root_group is FW.main_group:
            FW.loading_group.append(FW.loading_label)
            FW.loading_label.text = "Loading..."
        bme280.sea_level_pressure = bme280.pressure
        FW.header_label.text = "Feather Weather ESP32-S3 MQTT Touch"
        print("===============================")

        # Account for PCB heating bias, gets slightly hotter as ambient increases
        BME280_humidity = round(bme280.relative_humidity, 1)
        relative_humidity = np.interp(
            BME280_humidity, humid_input_range, humid_output_range
        )
        humidity_adjust = round(relative_humidity[0], 2)
        # print(f"Humidity Adjust: {humidity_adjust}")
        FW.humidity_label.text = "Humidity"
        FW.barometric_label.text = "Pressure"
        temperature = bme280.temperature * 1.8 + 32
        temp_round = round(temperature, 2)
        # print("Temp: ", temperature)  # biased reading
        display_temperature = np.interp(temperature, input_range, output_range)
        BME280_temperature = round(display_temperature[0] + humidity_adjust, 2)
        # print(f"Actual Temp: {BME280_temperature:.1f}")

        debug = False  # Set True for warning popup test
        if debug:
            BME280_pressure = 1005  # Manually test debug warning message
            print(f"BME280 Pressure: {BME280_pressure}")
        else:
            BME280_pressure = round(bme280.pressure, 1)
        BME280_altitude = round(bme280.altitude, 2)

        # Ambient Pressure Warning Popup
        FW.pressure_sensor_warning(BME280_pressure)

        if First_Run and FW.display.root_group is FW.loading_splash:
            FW.splash_label.text = "Initializing WiFi 4..."
        if not First_Run and FW.display.root_group is FW.main_group:
            FW.loading_label.text = "Checking Wifi..."

        # Connect to Wi-Fi
        print("\nConnecting to WiFi...")
        while not wifi.radio.ipv4_address:
            try:
                wifi.radio.connect(ssid, password)
            except ConnectionError as e:
                print(" ❌ Connection Error:", e)
                print(" Retrying in 10 seconds")
        print(" 📡 Wifi!")

        while wifi.radio.ipv4_address:
            try:
                print(" | Attempting to GET Weather...")
                debug_WG = False  # Set true to debug Weather JSON
                if debug_WG:
                    print(f" | Full API GET URL: {DATA_SOURCE}\n{HEADER}")
                    print("\n===============================")
                    with requests.get(DATA_SOURCE, headers=HEADER) as debug_request:
                        status = debug_request.status_code
                        request_header = debug_request.headers
                        print(f"Status Code: {status}")
                        print(f"Raw Headers: {request_header}\n")

                with requests.get(DATA_SOURCE) as request:
                    FW.splash_label.text = "Getting Weather..."
                    response = request.json()
                    print(" | ✅ Connected to Open-Meteo")

                    get_timestamp = int(response['current']['time'])
                    get_offset = int(response['utc_offset_seconds'])
                    get_sunrise = int(response['daily']['sunrise'][0])
                    get_sunset = int(response['daily']['sunset'][0])
                    converted_timestamp = FW.unixtime_to_formattedtime(get_timestamp, get_offset)
                    converted_sunrise = FW.unixtime_to_formattedtime(get_sunrise, get_offset)
                    converted_sunset = FW.unixtime_to_formattedtime(get_sunset, get_offset)
                    current_date = "{}".format(FW._format_date(converted_timestamp))
                    current_time = "{}".format(FW._format_time(converted_timestamp))
                    current_sunrise = "{}".format(FW._format_time(converted_sunrise))
                    current_sunset = "{}".format(FW._format_time(converted_sunset))

                    temperature_2m = response["current"]["temperature_2m"]
                    relative_humidity_2m = response["current"]["relative_humidity_2m"]
                    surface_pressure = response["current"]["surface_pressure"]
                    windspeed_10m = response["current"]["wind_speed_10m"]
                    weather_code = response["current"]["weather_code"]
                    get_isday = int(response['current']['is_day'])  # 0=night 1=day

                    print(f" | | Timestamp: {current_date} {current_time}")
                    print(f" | | Sunrise: {current_sunrise}")
                    print(f" | | Sunset: {current_sunset}")
                    print(f" | | Temperature: {temperature_2m}")
                    print(f" | | Humidity: {relative_humidity_2m}")
                    print(f" | | Pressure: {surface_pressure}")
                    print(f" | | Wind Speed: {windspeed_10m}")

                    if "wind_gusts_10m" in response["current"]:
                        wind_gusts_10m = response["current"]["wind_gusts_10m"]
                        print(f" | | Gust: {wind_gusts_10m}")
                    else:
                        print(" | | Gust: No Data")
                    print(f" | | Weather Code: {weather_code}")

                    print(f" | | Weather Code: {FW.weather_code_parser(weather_code, get_isday)}")
                    print(f" | | Weather Icon: {FW.weather_icon_parser(weather_code, get_isday)}")

                    FW.date_label.text = current_date
                    FW.time_label.text = current_time
                    FW.sunrise_label.text = current_sunrise
                    FW.sunset_label.text = current_sunset
                    FW.online_windspeed_label.text = f"{windspeed_10m:.1f} mph"
                    FW.online_temp_data_label.text = f"{temperature_2m:.1f}"
                    FW.online_humidity_data_label.text = f"{relative_humidity_2m:.1f} %"
                    FW.online_barometric_data_label.text = f"{surface_pressure:.1f}"

            except (ValueError, RuntimeError) as e:
                print(" ❌  ValueError: Failed to get data, retrying\n", e)
                supervisor.reload()
                break
            except OSError as g:
                if g.errno == -2:
                    print(" ❌ gaierror, breaking out of loop\n", g)
                    time.sleep(240)
                    break
            print(" | ✂️ Disconnected from Open-Meteo")

            # Connect to Adafruit IO
            try:
                print(" | Attempting MQTT Broker...")
                mqtt_client.connect()
                if First_Run and FW.display.root_group is FW.loading_splash:
                    FW.splash_label.text = "Publishing to AdafruitIO..."
                if not First_Run and FW.display.root_group is FW.main_group:
                    FW.loading_label.text = "Publishing..."
                mqtt_client.publish(feed_01, temp_round)
                # slight delay required between publishes!
                # otherwise only the 1st publish will succeed
                time.sleep(0.001)
                mqtt_client.publish(feed_02, BME280_temperature)
                time.sleep(1)
                mqtt_client.publish(feed_03, BME280_pressure)
                time.sleep(1)
                mqtt_client.publish(feed_04, BME280_humidity)
                time.sleep(1)
                mqtt_client.publish(feed_05, BME280_altitude)
                time.sleep(1)

            except (
                ValueError,
                RuntimeError,
                ConnectionError,
                OSError,
                MMQTTException,
            ) as ex:
                print(" | ❌ Failed to connect, retrying\n", ex)
                # traceback.print_exception(ex, ex, ex.__traceback__)
                # supervisor.reload()
                time.sleep(10)
                continue
            mqtt_client.disconnect()

            print(" ✂️ Disconnected from Wifi")
            print(f"Board Uptime: {FW.time_calc(time.monotonic())}")
            print("Next Update:", FW.time_calc(SLEEP_TIME))
            print("Finished!")
            print("===============================")

            if not First_Run and FW.display.root_group is FW.main_group:
                FW.loading_label.text = f"Next Update\n{FW.time_calc(SLEEP_TIME)}"
                time.sleep(5)
                FW.loading_group.remove(FW.loading_label)

            if First_Run:
                First_Run = False
                FW.display.root_group = FW.main_group
                # Switch from splash to main_group
                FW.loading_splash.remove(FW.splash_label)
                FW.loading_splash.remove(FW.feather_weather_bg)

            print("Entering Touch Loop")
            while (
                time.monotonic() - last
            ) <= SLEEP_TIME and FW.display.root_group is FW.main_group:

                if time.monotonic() >= 86400:
                    print("24 Hour Uptime Restart")
                    microcontroller.reset()

                # Battery Voltage / USB Sense / Voltage Icon (from function)
                FW.usb_battery_monitor(feathers3.get_battery_voltage(), feathers3.get_vbus_present())

                FW.temp_data_shadow.text = f"{BME280_temperature:.1f}"
                FW.temp_data_label.text = f"{BME280_temperature:.1f}"
                FW.humidity_data_label.text = f"{BME280_humidity:.1f} %"
                FW.barometric_data_label.text = f"{BME280_pressure:.1f}"

                FW.p = FW.touchscreen.touch_point
                if FW.p:
                    FW.menu_switching(FW.main_group,FW.main_group3,FW.main_group2)
                else:
                    # Default state always running
                    FW.group_cleanup()
            last = time.monotonic()
            print("Exited Touch Loop")
            break

    while FW.display.root_group is FW.main_group2:
        FW.wallpaper[0] = 1
        FW.header_label.text = "Feather Weather Page 2"
        while (
            time.monotonic() - last
        ) <= SLEEP_TIME and FW.display.root_group is FW.main_group2:
            FW.p = FW.touchscreen.touch_point
            if FW.p:
                FW.menu_switching(FW.main_group2,FW.main_group,FW.main_group3)
            else:
                # Default state always running
                FW.group_cleanup()
        last = time.monotonic()

    while FW.display.root_group is FW.main_group3:
        FW.wallpaper[0] = 2
        FW.header_label.text = "Feather Weather Page 3"
        while (
            time.monotonic() - last
        ) <= SLEEP_TIME and FW.display.root_group is FW.main_group3:
            FW.p = FW.touchscreen.touch_point
            if FW.p:
                FW.menu_switching(FW.main_group3,FW.main_group2,FW.main_group)
            else:
                # Default state always running
                FW.group_cleanup()
        last = time.monotonic()

    while FW.display.root_group is FW.preferences_group:
        FW.wallpaper[0] = 3
        FW.header_label.text = "Feather Weather Preferences"
        while (
            time.monotonic() - last
        ) <= SLEEP_TIME and FW.display.root_group is FW.preferences_group:
            FW.p = FW.touchscreen.touch_point
            if (
                FW.p
            ):  # Check each slider if the touch point is within the slider touch area
                if FW.my_slider.when_inside(FW.p):
                    try:
                        FW.my_slider.when_selected(FW.p)
                        print(f"Slider Value: {FW.p[0]}")
                        print(f"Slider Adjusted: {int(FW.p[0] / 300 * 65000)}")
                        _Slider_New_Value = int(FW.p[0] / 300 * 65000)
                        print(f"TFT_brightness.duty_cycle : {_Slider_New_Value}")
                        TFT_brightness.duty_cycle = _Slider_New_Value
                        FW.label_preferences_current_brightness.text = "Display Brightness"
                    except Exception as e:
                        print(e)
                        continue
                FW.menu_switching(FW.preferences_group,FW.main_group,FW.main_group)
            else:
                # Default state always running
                FW.group_cleanup()
        last = time.monotonic()

    while FW.display.root_group is FW.wifi_settings_group:
        FW.wallpaper[0] = 3
        FW.header_label.text = "Wifi Settings"
        ssid_len = len(ssid)
        ssid_dash_replace = "*" * (ssid_len - 2)
        ssid_ast = ssid.replace(ssid[2:ssid_len], ssid_dash_replace)
        FW.wifi_settings_ssid.text = f"SSID: \n{ssid_ast}"

        appw_len = len(password)
        appw_dash_replace = "*" * (appw_len - 2)
        appw_ast = password.replace(password[2:appw_len], appw_dash_replace)
        FW.wifi_settings_pw.text = f"Password: \n{appw_ast}"
        FW.wifi_settings_instructions.text = ("To change SSID & Password\n"
                                           "Connect USB cable to PC\n"
                                           "Open CIRCUITPY USB drive\n"
                                           "Edit settings.toml file")

        while (
            time.monotonic() - last
        ) <= SLEEP_TIME and FW.display.root_group is FW.wifi_settings_group:
            FW.p = FW.touchscreen.touch_point
            if FW.p:
                FW.menu_switching(FW.wifi_settings_group,FW.main_group,FW.main_group)
            else:
                # Default state always running
                FW.group_cleanup()
        last = time.monotonic()

    while FW.display.root_group is FW.rssi_group:
        FW.wallpaper[0] = 3
        FW.header_label.text = "WiFi Signal Strength"
        # Displays available networks sorted by RSSI
        networks = []
        NetworkList = []
        for network in wifi.radio.start_scanning_networks():
            networks.append(network)
        wifi.radio.stop_scanning_networks()
        networks = sorted(networks, key=lambda net: net.rssi, reverse=True)
        for network in networks:
            sorted_networks = {
                "ssid": network.ssid,
                "rssi": network.rssi,
                "channel": network.channel,
            }
            NetworkList.append([sorted_networks])
            print(f"ssid: {network.ssid} | rssi: {network.rssi} | "
                  + f"channel: {network.channel}")
        jsonNetworkList = json.dumps(NetworkList)
        json_list = json.loads(jsonNetworkList)
        # print(f"Items in RSSI List: {len(json_list)}")
        FW.rssi_label.text = "SSID\t\t\t\t\t\t\t  RSSI\t\t\t\t    CHANNEL\n"
        rssi_label0 = FW.rssi_label0
        rssi_label1 = FW.rssi_label1
        rssi_label2 = FW.rssi_label2
        rssi_label3 = FW.rssi_label3
        rssi_label4 = FW.rssi_label4
        rssi_label5 = FW.rssi_label5
        rssi_label6 = FW.rssi_label6
        rssi_label7 = FW.rssi_label7
        rssi_label8 = FW.rssi_label8
        rssi_label9 = FW.rssi_label9
        try:
            for i in range(min(10, len(json_list))):
                label_text = (f"{json_list[i][0]['ssid']:<30}\t"
                              + f"{json_list[i][0]['rssi']:<20}\t"
                              + f"{json_list[i][0]['channel']:<20}\n")
                globals()[f"rssi_label{i}"].text = label_text
        except Exception as e:
            print(f"RSSI List Error: {e}")
            pass

        while (
            time.monotonic() - last
        ) <= SLEEP_TIME and FW.display.root_group is FW.rssi_group:
            FW.p = FW.touchscreen.touch_point
            if FW.p:
                FW.menu_switching(FW.rssi_group,FW.main_group,FW.main_group)
            else:
                # Default state always running
                FW.group_cleanup()
        last = time.monotonic()

    while FW.display.root_group is FW.sys_info_group:
        FW.wallpaper[0] = 3
        FW.header_label.text = "System Information"
        # System Stats
        u_name = os.uname()
        FW.sys_info_label1.text = f"Circuit Python Version:\n{u_name[3]}"
        FW.sys_info_label2.text = f"Board: \n{u_name[4]}"
        FW.sys_info_label3.text = f"Logic Chip: {u_name[0]}"
        fs_stat = os.statvfs("/")
        NORdisk_size = fs_stat[0] * fs_stat[2] / 1024 / 1024
        NORfree_space = fs_stat[0] * fs_stat[3] / 1024 / 1024
        FW.sys_info_label4.text = f"Flash Chip Size: {NORdisk_size:.2f} MB"
        NORdisk_used = NORdisk_size - NORfree_space
        if (NORdisk_used) >= 1.0:
            FW.sys_info_label5.text = f"Flash Chip Used: {NORdisk_used:.2f} MB"
        if (NORdisk_used) <= 1.0:
            FW.sys_info_label5.text = f"Flash Chip Used: {NORdisk_used*1024:.2f} KB"
        FW.sys_info_label6.text = f"Flash Chip Free: {NORfree_space:.2f} MB"

        # Volume Information Stats
        try:
            SD_Card_Size = os.statvfs(FW.virtual_root)
            SD_Card_FREE_TOTAL = SD_Card_Size[0] * SD_Card_Size[3] / 1024 / 1024 / 1024
            if (SD_Card_FREE_TOTAL) >= 1.0:
                FW.sys_info_label7.text = f"SD Card Free: {SD_Card_FREE_TOTAL:.2f} GB"
            if (SD_Card_FREE_TOTAL) <= 1.0:
                SD_Card_FREE_TOTAL_MB = SD_Card_Size[0] * SD_Card_Size[3] / 1024 / 1024
                FW.sys_info_label7.text = (
                    f"SD Card Free: {SD_Card_FREE_TOTAL_MB:.2f} MB"
                )
            # storage.umount(vfs)
        except Exception as e:
            print(e)
            pass

        while (
            time.monotonic() - last
        ) <= SLEEP_TIME and FW.display.root_group is FW.sys_info_group:
            FW.p = FW.touchscreen.touch_point
            if FW.p:
                FW.menu_switching(FW.sys_info_group,FW.main_group,FW.main_group)
            else:
                # Default state always running
                FW.group_cleanup()
        last = time.monotonic()

    while FW.display.root_group is FW.wifi_change_group:
        FW.wallpaper[0] = 3
        FW.header_label.text = "Wifi Edit Credentials"
        FW.input_change_wifi.text = "New Password: "

        while (
            time.monotonic() - last
        ) <= SLEEP_TIME and FW.display.root_group is FW.wifi_change_group:
            FW.p = FW.touchscreen.touch_point
            key_value = FW.soft_kbd.check_touches(FW.p)
            if FW.p:
                if key_value in FW.PRINTABLE_CHARACTERS:
                    FW.input_lbl.text += key_value
                elif key_value == 42:  # 0x2a backspace key
                    FW.input_lbl.text = FW.input_lbl.text[:-1]
                elif key_value == 224:  # special character switch key
                    FW.input_lbl.text = FW.input_lbl.text[:-1]
                FW.menu_switching(wifi_change_group,main_group2,main_group)
            else:
                # Default state always running
                FW.group_cleanup()
        last = time.monotonic()
