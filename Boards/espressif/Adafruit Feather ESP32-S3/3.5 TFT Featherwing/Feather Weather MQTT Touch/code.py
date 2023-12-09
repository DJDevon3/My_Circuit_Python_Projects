# SPDX-FileCopyrightText: 2023 DJDevon3
# SPDX-License-Identifier: MIT
# ESP32-S3 Feather Weather MQTT Touchscreen
# Coded for Circuit Python 8.2.x

import os
import supervisor
import time
import board
import displayio
import digitalio
import terminalio
import adafruit_imageload
import ssl
import wifi
import socketpool
import adafruit_requests
import ulab.numpy as np
import adafruit_minimqtt.adafruit_minimqtt as MQTT
from adafruit_minimqtt.adafruit_minimqtt import MMQTTException
from adafruit_display_text import label
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_bitmap_font import bitmap_font
from adafruit_lc709203f import LC709203F
from adafruit_bme280 import basic as adafruit_bme280
from adafruit_hx8357 import HX8357
import adafruit_stmpe610
from adafruit_button.sprite_button import SpriteButton
from adafruit_debouncer import Debouncer
_now = time.monotonic()

# 3.5" TFT Featherwing is 480x320
displayio.release_displays()
DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 320

# Initialize Web Sockets (This should always be near the top of a script!)
# There can be only one pool
pool = socketpool.SocketPool(wifi.radio)

# Use settings.toml for credentials
ssid = os.getenv("WIFI_SSID")
appw = os.getenv("WIFI_PASSWORD")
aio_username = os.getenv("aio_username")
aio_key = os.getenv("aio_key")
# Local time & weather from lat/lon
OWKEY = os.getenv("openweather_token")
OWLAT = os.getenv("openweather_lat")
OWLON = os.getenv("openweather_lon")

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
sleep_time = 900

# Initialize TFT Display
spi = board.SPI()
tft_cs = board.D9
tft_dc = board.D10
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = HX8357(display_bus, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT)
display.rotation = 0
_touch_flip = (False, True)

# Initialize 3.5" TFT Featherwing Touchscreen
ts_cs_pin = digitalio.DigitalInOut(board.D6)
touchscreen = adafruit_stmpe610.Adafruit_STMPE610_SPI(
    board.SPI(),
    ts_cs_pin,
    calibration=((231, 3703), (287, 3787)),
    size=(display.width, display.height),
    disp_rotation=display.rotation,
    touch_flip=_touch_flip,
)

# Initialize BME280 Sensor
i2c = board.STEMMA_I2C()  # uses board.SCL and board.SDA
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
# sea_level_pressure should be set in the while true loop
# bme280.sea_level_pressure = bme280.pressure
# print("Sea Level Pressure: ", bme280.sea_level_pressure)
# print("Altitude = %0.2f meters" % bme280.altitude)

i2c = board.I2C()
battery_monitor = LC709203F(board.I2C())
# LC709203F github repo library
# https://github.com/adafruit/Adafruit_CircuitPython_LC709203F/blob/main/adafruit_lc709203f.py
# only up to 3000 supported, don't use PackSize if battery larger than 3000mah
# battery_monitor.pack_size = PackSize.MAH3000
battery_monitor.thermistor_bconstant = 3950
battery_monitor.thermistor_enable = True

# Converts seconds in minutes/hours/days
# Attribution: Written by DJDevon3 & refined by Elpekenin
def time_calc(input_time):
    if input_time < 60:
        return f"{input_time:.0f} seconds"
    if input_time < 3600:
        return f"{input_time / 60:.0f} minutes"
    if input_time < 86400:
        return f"{input_time / 60 / 60:.0f} hours"
    return f"{input_time / 60 / 60 / 24:.1f} days"

# OpenWeather 2.5 Free API
DATA_SOURCE = "https://api.openweathermap.org/data/2.5/onecall?"
DATA_SOURCE += "lat=" + OWLAT
DATA_SOURCE += "&lon=" + OWLON
DATA_SOURCE += "&exclude=hourly,daily"
DATA_SOURCE += "&appid=" + OWKEY
DATA_SOURCE += "&units=imperial"

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

# Fonts are optional
arial_font = bitmap_font.load_font("/fonts/Arial-16.bdf")
small_font = bitmap_font.load_font("/fonts/GoodTimesRg-Regular-16.bdf")
medium_font = bitmap_font.load_font("/fonts/GoodTimesRg-Regular-40.bdf")
huge_font = bitmap_font.load_font("/fonts/GoodTimesRg-Regular-121.bdf")

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

# Function for minimizing labels to 1 liners
# Attribution: Anecdata (thanks!)
def make_my_label(font, anchor_point, anchored_position, scale, color):
    func_label = label.Label(font)
    func_label.anchor_point = anchor_point
    func_label.anchored_position = anchored_position
    func_label.scale = scale
    func_label.color = color
    return func_label

# name_label (FONT, (ANCHOR POINT), (ANCHOR POSITION), SCALE, COLOR)
# loading screen label
loading_label = make_my_label(terminalio.FONT, (0.5, 0.5), (DISPLAY_WIDTH / 2, DISPLAY_HEIGHT-75), 2, TEXT_CYAN)
loading_label_shadow = make_my_label(terminalio.FONT, (0.5, 0.5), (DISPLAY_WIDTH / 2 +3, DISPLAY_HEIGHT-75+3), 2, TEXT_BLACK)
hello_label = make_my_label(
    terminalio.FONT, (0.5, 1.0), (DISPLAY_WIDTH / 2, 15), 1, TEXT_WHITE
)
hello_label_page2 = make_my_label(
    terminalio.FONT, (0.5, 1.0), (DISPLAY_WIDTH / 2, 15), 1, TEXT_WHITE
)
hello_label_page3 = make_my_label(
    terminalio.FONT, (0.5, 1.0), (DISPLAY_WIDTH / 2, 15), 1, TEXT_WHITE
)
warning_label = make_my_label(
    arial_font, (0.5, 0.5), (DISPLAY_WIDTH / 2, DISPLAY_HEIGHT - 103), 1, TEXT_RED
)
menu_popout_label = make_my_label(
    arial_font, (0.0, 0.0), (135, 15), 1, TEXT_CYAN
)
date_label = make_my_label(small_font, (0.0, 0.0), (5, 45), 1, TEXT_LIGHTBLUE)
time_label = make_my_label(small_font, (0.0, 0.0), (5, 65), 2, TEXT_LIGHTBLUE)
temp_label = make_my_label(small_font, (1.0, 1.0), (475, 123), 2, TEXT_ORANGE)
temp_data_label = make_my_label(
    huge_font, (0.5, 0.0), (DISPLAY_WIDTH / 2, 100), 1, TEXT_ORANGE
)
temp_data_shadow = make_my_label(
    huge_font, (0.5, 0.0), (DISPLAY_WIDTH / 2 + 2, 100 + 2), 1, TEXT_BLACK
)
owm_temp_data_label = make_my_label(
    medium_font, (0.5, 0.0), (DISPLAY_WIDTH / 2, 65), 1, TEXT_LIGHTBLUE
)
owm_temp_data_shadow = make_my_label(
    medium_font, (0.5, 0.0), (DISPLAY_WIDTH / 2 + 2, 65 + 2), 1, TEXT_BLACK
)
humidity_label = make_my_label(
    small_font, (0.0, 1.0), (5, DISPLAY_HEIGHT - 40), 1, TEXT_GRAY
)
humidity_data_label = make_my_label(
    medium_font, (0.0, 1.0), (5, DISPLAY_HEIGHT), 1, TEXT_ORANGE
)
owm_humidity_data_label = make_my_label(
    arial_font, (0.0, 1.0), (5, DISPLAY_HEIGHT - 60), 1, TEXT_LIGHTBLUE
)
barometric_label = make_my_label(
    small_font, (1.0, 1.0), (471, DISPLAY_HEIGHT - 40), 1, TEXT_GRAY
)
barometric_data_label = make_my_label(
    medium_font, (1.0, 1.0), (470, DISPLAY_HEIGHT), 1, TEXT_ORANGE
)
owm_barometric_data_label = make_my_label(
    arial_font, (1.0, 1.0), (470, DISPLAY_HEIGHT - 60), 1, TEXT_LIGHTBLUE
)
owm_windspeed_label = make_my_label(
    arial_font, (1.0, 1.0), (DISPLAY_WIDTH - 5, 90), 1, TEXT_LIGHTBLUE
)
vbat_label = make_my_label(arial_font, (1.0, 1.0), (DISPLAY_WIDTH - 15, 60), 1, None)
plugbmp_label = make_my_label(terminalio.FONT, (1.0, 1.0), None, 1, None)
greenbmp_label = make_my_label(terminalio.FONT, (1.0, 1.0), None, 1, None)
bluebmp_label = make_my_label(terminalio.FONT, (1.0, 1.0), None, 1, None)
yellowbmp_label = make_my_label(terminalio.FONT, (1.0, 1.0), None, 1, None)
orangebmp_label = make_my_label(terminalio.FONT, (1.0, 1.0), None, 1, None)
redbmp_label = make_my_label(terminalio.FONT, (1.0, 1.0), None, 1, None)


# Load Bitmap to tile grid first (Background layer)
DiskBMP = displayio.OnDiskBitmap("/images/Astral_Fruit_8bit.bmp")
tile_grid = displayio.TileGrid(
    DiskBMP,
    pixel_shader=DiskBMP.pixel_shader,
    width=1,
    height=1,
    tile_width=DISPLAY_WIDTH,
    tile_height=DISPLAY_HEIGHT,
)

# Load battery voltage icons (from 1 sprite sheet image)
sprite_sheet, palette = adafruit_imageload.load(
    "/icons/vbat_spritesheet.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette
)
sprite = displayio.TileGrid(
    sprite_sheet, pixel_shader=palette, width=1, height=1, tile_width=11, tile_height=20
)
sprite_group = displayio.Group(scale=1)
sprite_group.append(sprite)
sprite_group.x = 470
sprite_group.y = 45

# Warning label RoundRect
roundrect = RoundRect(
    int(10),
    int(DISPLAY_HEIGHT - 125),
    DISPLAY_WIDTH-10,
    40,
    10,
    fill=0x0,
    outline=0xFFFFFF,
    stroke=1,
)

# Menu RoundRect
menu_roundrect = RoundRect(
    int(130),  # start corner x
    int(5),  # start corner y
    DISPLAY_WIDTH-200,  # width
    200,  # height
    10,  # corner radius
    fill=None,
    outline=0xFFFFFF,
    stroke=0,
)

# Button width & height must be multiple of 16
# otherwise you'll get a tilegrid_inflator error
BUTTON_WIDTH = 16 * 16
BUTTON_HEIGHT = 3 * 16
BUTTON_MARGIN = 5

# Defiine the button
menu_button = SpriteButton(
    x=BUTTON_MARGIN,
    y=BUTTON_MARGIN,
    width=7*16,
    height=2*16,
    label="MENU",
    label_font=small_font,
    label_color=TEXT_WHITE,
    bmp_path="icons/gradient_button_0.bmp",
    selected_bmp_path="icons/gradient_button_1.bmp",
    transparent_index=0,
)

next_button = SpriteButton(
    x=DISPLAY_WIDTH-3*16,
    y=BUTTON_MARGIN,
    width=3*16,
    height=2*16,
    label=">",
    label_font=arial_font,
    label_color=TEXT_WHITE,
    bmp_path="icons/gradient_button_0.bmp",
    selected_bmp_path="icons/gradient_button_1.bmp",
    transparent_index=0,
)

prev_button = SpriteButton(
    x=DISPLAY_WIDTH-6*16-5,
    y=BUTTON_MARGIN,
    width=3*16,
    height=2*16,
    label="<",
    label_font=arial_font,
    label_color=TEXT_WHITE,
    bmp_path="icons/gradient_button_0.bmp",
    selected_bmp_path="icons/gradient_button_1.bmp",
    transparent_index=0,
)

item1_button = SpriteButton(
    x=135,
    y=15,
    width=BUTTON_WIDTH,
    height=BUTTON_HEIGHT,
    label="Page 2",
    label_font=arial_font,
    label_color=TEXT_WHITE,
    bmp_path="icons/gradient_button_0.bmp",
    selected_bmp_path="icons/gradient_button_1.bmp",
    transparent_index=0,
)

item2_button = SpriteButton(
    x=135,
    y=70,
    width=BUTTON_WIDTH,
    height=BUTTON_HEIGHT,
    label="WiFi Credentials",
    label_font=arial_font,
    label_color=TEXT_WHITE,
    bmp_path="icons/gradient_button_0.bmp",
    selected_bmp_path="icons/gradient_button_1.bmp",
    transparent_index=0,
)

item3_button = SpriteButton(
    x=135,
    y=125,
    width=BUTTON_WIDTH,
    height=BUTTON_HEIGHT,
    label="RSSI Scan",
    label_font=arial_font,
    label_color=TEXT_WHITE,
    bmp_path="icons/gradient_button_0.bmp",
    selected_bmp_path="icons/gradient_button_1.bmp",
    transparent_index=0,
)

# Create subgroups
splash = displayio.Group()
text_group = displayio.Group()
text_group.append(tile_grid)
temp_group = displayio.Group()
warning_group = displayio.Group()
loading_group = displayio.Group()
menu_popout_group = displayio.Group()
main_group = displayio.Group()

# Page 2 Groups
main_group2 = displayio.Group()
main_group2.append(hello_label_page2)

# Page 3 Groups
main_group3 = displayio.Group()
main_group3.append(hello_label_page3)

# Add subgroups to main display group
main_group.append(text_group)
main_group.append(warning_group)
main_group.append(loading_group)
main_group.append(temp_group)
main_group.append(sprite_group)
main_group.append(menu_popout_group)
main_group.append(splash)

# Add warning popup group
warning_group.append(roundrect)
warning_group.append(warning_label)

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
text_group.append(owm_windspeed_label)
text_group.append(vbat_label)
text_group.append(plugbmp_label)
text_group.append(greenbmp_label)
text_group.append(bluebmp_label)
text_group.append(yellowbmp_label)
text_group.append(orangebmp_label)
text_group.append(redbmp_label)

# Add Menu popup group
menu_popout_group.append(menu_roundrect)
menu_popout_group.append(menu_popout_label)
menu_popout_group.append(item1_button)
menu_popout_group.append(item2_button)
menu_popout_group.append(item3_button)
splash.append(menu_button)
splash.append(next_button)
splash.append(prev_button)

display.root_group = main_group

def show_warning(text):
    # Function to display weather popup warning
    warning_label.text = text
    warning_group.hidden = False


def hide_warning():
    # Function to hide weather popup warning
    warning_group.hidden = True
    
def show_menu():
    # Function to display popup menu
    menu_popout_group.hidden = False

def hide_menu():
    # Function to hide popup menu
    menu_popout_group.hidden = True
    
hide_warning()
hide_menu()

# Define callback methods when events occur
def connect(mqtt_client, userdata, flags, rc):
    # Method when mqtt_client connected to the broker.
    print("| | ✅ Connected to MQTT Broker!")


def disconnect(mqtt_client, userdata, rc):
    # Method when the mqtt_client disconnects from broker.
    print("| | ✂️ Disconnected from MQTT Broker")


def subscribe(mqtt_client, userdata, topic, granted_qos):
    # Method when the mqtt_client subscribes to a new feed.
    print("Subscribed to {0} with QOS level {1}".format(topic, granted_qos))


def unsubscribe(mqtt_client, userdata, topic, pid):
    # Method when the mqtt_client unsubscribes from a feed.
    print("Unsubscribed from {0} with PID {1}".format(topic, pid))


def publish(mqtt_client, userdata, topic, pid):
    # Method when the mqtt_client publishes data to a feed.
    print(f"| | | Published {topic}")


def message(mqtt_client, topic, message):
    # Method client's subscribed feed has a new value.
    print("New message on topic {0}: {1}".format(topic, message))

def ioerrors(mqtt_client, topic, message):
    # Method for callback errors.
    print("New message on topic {0}: {1}".format(topic, message))

def throttle(mqtt_client, topic, message):
    # Method for callback errors.
    print("New message on topic {0}: {1}".format(topic, message))


# Initialize a new MQTT Client object
mqtt_client = MQTT.MQTT(
    broker="io.adafruit.com",
    port=8883,
    username=aio_username,
    password=aio_key,
    socket_pool=pool,
    ssl_context=ssl.create_default_context(),
    is_ssl=True,
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

display_temperature = 0
# Define the input range and output range
# pressure at 1014 & 88F at 100% accurate. sea level pressure affects temp?
input_range = [50.0, 70, 76, 80, 88.0, 120.0]
output_range = [50.0 - 0.1, 70.0 - 1.4, 76 - 1.5, 80 - 1.0, 88.0 - 0.0, 120.0 - 2.2]

# adafruit_requests.Session should always be outside the loop
# otherwise you get Out of Socket errors.
requests = adafruit_requests.Session(pool, ssl.create_default_context())

# Loading Label
loading_label_shadow.text = "Loading..."
loading_label.text = "Loading..."
last = time.monotonic()
LAST_PRESS_TIME = -1
while True:
    while display.root_group is main_group:
        item1_button.selected = False
        item2_button.selected = False
        item3_button.selected = False
        menu_button.selected = False
        prev_button.selected = False
        next_button.selected = False
        debug_OWM = False  # Set True for Serial Print Debugging
        bme280.sea_level_pressure = bme280.pressure
        loading_group.append(loading_label_shadow)
        loading_group.append(loading_label)
        hello_label.text = "ESP32-S3 MQTT Feather Weather"
        print("===============================")

        # USB Power Sensing
        try:
            vbat_label.text = f"{battery_monitor.cell_voltage:.2f}v"
        except (ValueError, RuntimeError, OSError) as e:
            print("LC709203F Error: \n", e)
        # Set USB plug icon and voltage label to white
        usb_sense = supervisor.runtime.usb_connected
        if debug_OWM:
            print("USB Sense: ", usb_sense)  # Boolean value
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
            # TFT cutoff voltage is 3.70
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
        print("Temp: ", temperature)  # biased reading
        display_temperature = np.interp(temperature, input_range, output_range)
        BME280_temperature = round(display_temperature[0], 2)
        print(f"Actual Temp: {BME280_temperature:.1f}")
        if debug_OWM:
            BME280_pressure = 1005  # Manually set debug warning message
            print(f"BME280 Pressure: {BME280_pressure}")
        else:
            BME280_pressure = round(bme280.pressure, 1)
        BME280_humidity = round(bme280.relative_humidity, 1)
        BME280_altitude = round(bme280.altitude, 2)

        temp_data_shadow.text = f"{BME280_temperature:.1f}"
        temp_data_label.text = f"{BME280_temperature:.1f}"
        humidity_label.text = "Humidity"
        humidity_data_label.text = f"{BME280_humidity:.1f} %"
        barometric_label.text = "Pressure"
        barometric_data_label.text = f"{BME280_pressure:.1f}"

        # Warnings based on local sensors
        if BME280_pressure <= 919:  # pray you never see this message
            show_warning("HOLY COW: Seek Shelter!")
        elif 920 <= BME280_pressure <= 979:
            show_warning("DANGER: Major Hurricane")
        elif 980 <= BME280_pressure <= 989:
            show_warning("DANGER: Minor Hurricane")
        elif 990 <= BME280_pressure <= 1001:
            show_warning("WARNING: Tropical Storm")
        elif 1002 <= BME280_pressure <= 1009:  # sudden gusty downpours
            show_warning("CAUTION: Low Pressure System")
        elif 1019 <= BME280_pressure <= 1025:  # sudden light cold rain
            show_warning("CAUTION: High Pressure System")
        elif BME280_pressure >= 1026:
            show_warning("WARNING: Hail & Tornados?")
        else:
            hide_warning()  # Normal pressures: 1110-1018 (no message)
        
        print("| Connecting to WiFi...")
        loading_label_shadow.text = "Checking Wifi..."
        loading_label.text = "Checking Wifi..."
        First_Run = True
        
        while not wifi.radio.ipv4_address and display.root_group is main_group:
            try:
                wifi.radio.connect(ssid, appw)
            except ConnectionError as e:
                print("Connection Error:", e)
                print("Retrying in 10 seconds")
                time.sleep(10)
        print("| ✅ WiFi!")

        while wifi.radio.ipv4_address and display.root_group is main_group:
            try:
                print("| | Attempting to GET Weather!")
                if debug_OWM:
                    print("Full API GET URL: ", DATA_SOURCE)
                    print("\n===============================")
                with requests.get(DATA_SOURCE) as owm_request:

                    # uncomment the 2 lines below to see full json response
                    # warning: returns ALL JSON data, could crash your board
                    # dump_object = json.dumps(owm_request)
                    # print("JSON Dump: ", dump_object)
                    try:
                        owm_response = owm_request.json()
                        if owm_response["message"]:
                            print(f"| | ❌ OpenWeatherMap Error:  {owm_response['message']}")
                            owm_request.close()
                    except (KeyError) as e:
                        loading_label_shadow.text = "Getting Weather..."
                        loading_label.text = "Getting Weather..."
                        owm_response = owm_request.json()
                        print("| | Account within Request Limit", e)
                        print("| | ✅ Connected to OpenWeatherMap")

                        # Timezone & offset automatically returned based on lat/lon
                        get_timezone_offset = int(owm_response["timezone_offset"])  # 1
                        tz_offset_seconds = get_timezone_offset
                        if debug_OWM:
                            print(f"Timezone Offset (in seconds): {get_timezone_offset}")
                        get_timestamp = int(owm_response["current"]["dt"] + int(tz_offset_seconds))  # 2
                        current_unix_time = time.localtime(get_timestamp)
                        current_struct_time = time.struct_time(current_unix_time)
                        current_date = "{}".format(_format_date(current_struct_time))
                        current_time = "{}".format(_format_time(current_struct_time))

                        sunrise = int(owm_response["current"]["sunrise"] + int(tz_offset_seconds))  # 3
                        sunrise_unix_time = time.localtime(sunrise)
                        sunrise_struct_time = time.struct_time(sunrise_unix_time)
                        sunrise_time = "{}".format(_format_time(sunrise_struct_time))

                        sunset = int(owm_response["current"]["sunset"] + int(tz_offset_seconds))  # 4
                        sunset_unix_time = time.localtime(sunset)
                        sunset_struct_time = time.struct_time(sunset_unix_time)
                        sunset_time = "{}".format(_format_time(sunset_struct_time))

                        owm_temp = owm_response["current"]["temp"] # 5
                        owm_pressure = owm_response["current"]["pressure"]  # 6
                        owm_humidity = owm_response["current"]["humidity"]  # 7
                        weather_type = owm_response["current"]["weather"][0]["main"]  # 8
                        owm_windspeed = float(owm_response["current"]["wind_speed"])  # 9

                        print("| | | Sunrise:", sunrise_time)
                        print("| | | Sunset:", sunset_time)
                        print("| | | Temp:", owm_temp)
                        print("| | | Pressure:", owm_pressure)
                        print("| | | Humidity:", owm_humidity)
                        print("| | | Weather Type:", weather_type)
                        print("| | | Wind Speed:", owm_windspeed)
                        print("| | | Timestamp:", current_date + " " + current_time)

                        date_label.text = current_date
                        time_label.text = current_time
                        owm_windspeed_label.text = f"{owm_windspeed:.1f} mph"
                        owm_temp_data_shadow.text = f"{owm_temp:.1f}"
                        owm_temp_data_label.text = f"{owm_temp:.1f}"
                        owm_humidity_data_label.text = f"{owm_humidity:.1f} %"
                        owm_barometric_data_label.text = f"{owm_pressure:.1f}"
                        pass

            except (ValueError, RuntimeError) as e:
                print("ValueError: Failed to get OWM data, retrying\n", e)
                supervisor.reload()
                break
            except OSError as g:
                if g.errno == -2:
                    print("gaierror, breaking out of loop\n", g)
                    time.sleep(240)
                    break
            print("| | ✂️ Disconnected from OpenWeatherMap")

            # Connect to Adafruit IO
            try:
                mqtt_client.connect()
                loading_label_shadow.text = "Publishing..."
                loading_label.text = "Publishing..."
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

            except (ValueError, RuntimeError, ConnectionError, OSError, MMQTTException) as ex:
                print("| | ❌ Failed to connect, retrying\n", ex)
                # traceback.print_exception(ex, ex, ex.__traceback__)
                # supervisor.reload()
                continue
            mqtt_client.disconnect()
            
            if First_Run:
                loading_group.remove(loading_label_shadow)
                loading_group.remove(loading_label)
            print("| ✂️ Disconnected from Wifi")
            print(f"Loading Time: {time.monotonic() - _now}")
            print("Next Update: ", time_calc(sleep_time))
            First_Run = False
            
            print("Entering Sleep Loop")
            while (time.monotonic() - last) <= sleep_time and display.root_group is main_group:
                p = touchscreen.touch_point
                _now = time.monotonic()
                if p:
                    print(f"if p: {p[0]}")
                    print(f"Loading Time: {_now - LAST_PRESS_TIME}")
                    if _now - LAST_PRESS_TIME > 15:
                        print(f"Now - Last Press: {(p[0], p[1], p[2])}")
                        if menu_button.contains(p):
                            menu_button.selected = True
                            time.sleep(0.25)
                            print("Menu Pressed")
                            show_menu()
                        elif prev_button.contains(p):
                            prev_button.selected = True
                            time.sleep(0.1)
                            print("Previous Pressed")
                            hide_menu()
                            main_group.remove(menu_popout_group)
                            main_group.remove(splash)
                            main_group3.append(menu_popout_group)
                            main_group3.append(splash)
                            display.root_group = main_group3
                        elif next_button.contains(p):
                            next_button.selected = True
                            time.sleep(0.1)
                            print("Next Pressed")
                            hide_menu()
                            main_group.remove(menu_popout_group)
                            main_group.remove(splash)
                            main_group2.append(menu_popout_group)
                            main_group2.append(splash)
                            display.root_group = main_group2
                        elif item1_button.contains(p):
                            item1_button.selected = True
                            time.sleep(0.25)
                            print("Item 1 Pressed") 
                        elif item2_button.contains(p):
                            item2_button.selected = True
                            time.sleep(0.25)
                            print("Item 2 Pressed")
                        elif item3_button.contains(p):
                            item3_button.selected = True
                            time.sleep(0.25)
                            print("Item 3 Pressed")
                        else:
                            print("Else end why")
                            item1_button.selected = False
                            item2_button.selected = False
                            item3_button.selected = False
                            menu_button.selected = False  # When touch moves outside of button
                            prev_button.selected = False
                            next_button.selected = False
                            hide_menu()
                    LAST_PRESS_TIME = _now
                else:
                    # Default state always running
                    item1_button.selected = False
                    item2_button.selected = False
                    item3_button.selected = False
                    menu_button.selected = False  # When button is released
                    prev_button.selected = False
                    next_button.selected = False
                
                if display.root_group is main_group2:
                    print("Passed")
                    pass
            last = time.monotonic()
            print("Exited Sleep Loop")
            #time.sleep(sleep_time)
            if display.root_group is main_group2 or main_group3:
                pass
            else:
                break
                
    while display.root_group is main_group2:
        item1_button.selected = False
        item2_button.selected = False
        item3_button.selected = False
        menu_button.selected = False
        prev_button.selected = False
        next_button.selected = False
        hello_label_page2.text = "Feather Weather Page 2"
        print("Page 2! Yep this works!")
        while (time.monotonic() - last) <= sleep_time and display.root_group is main_group2:
            p = touchscreen.touch_point
            _now = time.monotonic()
            if p:
                print(f"if p: {p[0]}")
                print(f"Loading Time: {_now - LAST_PRESS_TIME}")
                if _now - LAST_PRESS_TIME > 1:
                    print(f"Now - Last Press: {(p[0], p[1], p[2])}")
                    if menu_button.contains(p):
                        menu_button.selected = True
                        time.sleep(0.25)
                        print("Menu Pressed")
                        show_menu()
                    elif prev_button.contains(p):
                        prev_button.selected = True
                        time.sleep(0.5)
                        print("Previous Pressed")
                        hide_menu()
                        main_group2.remove(menu_popout_group)
                        main_group2.remove(splash)
                        main_group.append(menu_popout_group)
                        main_group.append(splash)
                        display.root_group = main_group
                    elif next_button.contains(p):
                        next_button.selected = True
                        time.sleep(0.1)
                        print("Next Pressed")
                        hide_menu()
                        main_group2.remove(menu_popout_group)
                        main_group2.remove(splash)
                        main_group3.append(menu_popout_group)
                        main_group3.append(splash)
                        display.root_group = main_group3
                    elif item1_button.contains(p):
                        item1_button.selected = True
                        time.sleep(0.25)
                        print("Item 1 Pressed") 
                    elif item2_button.contains(p):
                        item2_button.selected = True
                        time.sleep(0.25)
                        print("Item 2 Pressed")
                    elif item3_button.contains(p):
                        item3_button.selected = True
                        time.sleep(0.25)
                        print("Item 3 Pressed")
                    else:
                        print("Else end why")
                        item1_button.selected = False
                        item2_button.selected = False
                        item3_button.selected = False
                        menu_button.selected = False  # When touch moves outside of button
                        prev_button.selected = False
                        next_button.selected = False
                        hide_menu()
                LAST_PRESS_TIME = _now
            else:
                # Default state always running
                item1_button.selected = False
                item2_button.selected = False
                item3_button.selected = False
                menu_button.selected = False  # When button is released
                prev_button.selected = False
                next_button.selected = False
        last = time.monotonic()
        if display.root_group is main_group2 or main_group3:
            pass
        else:
            break
                
    while display.root_group is main_group3:
        item1_button.selected = False
        item2_button.selected = False
        item3_button.selected = False
        menu_button.selected = False
        prev_button.selected = False
        next_button.selected = False
        hello_label_page3.text = "Feather Weather Page 3"
        print("Page 3! Yep this works!")
        while (time.monotonic() - last) <= sleep_time and display.root_group is main_group3:
            p = touchscreen.touch_point
            _now = time.monotonic()
            if p:
                print(f"if p: {p[0]}")
                print(f"Loading Time: {_now - LAST_PRESS_TIME}")
                if _now - LAST_PRESS_TIME > 1:
                    print(f"Now - Last Press: {(p[0], p[1], p[2])}")
                    if menu_button.contains(p):
                        menu_button.selected = True
                        time.sleep(0.25)
                        print("Menu Pressed")
                        show_menu()
                    elif prev_button.contains(p):
                        prev_button.selected = True
                        time.sleep(0.1)
                        print("Previous Pressed")
                        hide_menu()
                        main_group3.remove(menu_popout_group)
                        main_group3.remove(splash)
                        main_group2.append(menu_popout_group)
                        main_group2.append(splash)
                        display.root_group = main_group2
                    elif next_button.contains(p):
                        next_button.selected = True
                        time.sleep(0.5)
                        print("Next Pressed")
                        hide_menu()
                        print(f"After Hide Menu {p}")
                        main_group3.remove(menu_popout_group)
                        main_group3.remove(splash)
                        main_group.append(menu_popout_group)
                        main_group.append(splash)
                        display.root_group = main_group
                    elif item1_button.contains(p):
                        item1_button.selected = True
                        time.sleep(0.25)
                        print("Item 1 Pressed") 
                    elif item2_button.contains(p):
                        item2_button.selected = True
                        time.sleep(0.25)
                        print("Item 2 Pressed")
                    elif item3_button.contains(p):
                        item3_button.selected = True
                        time.sleep(0.25)
                        print("Item 3 Pressed")
                    else:
                        print("Bottom Else, Why?")
                        item1_button.selected = False
                        item2_button.selected = False
                        item3_button.selected = False
                        menu_button.selected = False  # When touch moves outside of button
                        prev_button.selected = False
                        next_button.selected = False
                        hide_menu()
                LAST_PRESS_TIME = _now
            else:
                # Default state always running
                item1_button.selected = False
                item2_button.selected = False
                item3_button.selected = False
                menu_button.selected = False  # When button is released
                prev_button.selected = False
                next_button.selected = False
        last = time.monotonic()