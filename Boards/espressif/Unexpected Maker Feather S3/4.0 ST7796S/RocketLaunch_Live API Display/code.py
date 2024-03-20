# SPDX-FileCopyrightText: 2024 DJDevon3
# SPDX-License-Identifier: MIT
# Coded for Circuit Python 8.2.x
"""RocketLaunch.Live Single Launch API Example"""
# pylint: disable=import-error

import os
import time
import board
import terminalio
import displayio
import wifi
import adafruit_connection_manager
import adafruit_requests
import adafruit_imageload
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label, wrap_text_to_pixels
from circuitpython_st7796s import ST7796S

spi = board.SPI()
tft_cs = board.D9
tft_dc = board.D10
tft_rst = board.D17

# 4.0" ST7796S Display
DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 320
DW2 = DISPLAY_WIDTH - 2

displayio.release_displays()
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_rst)
display = ST7796S(display_bus, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, rotation=180)

# Time between API refreshes
# 900=15 mins, 1800=30 mins, 3600=1 hour, 43200=12 hours
SLEEP_TIME = 43200

# Set True to view Full 1 launch JSON Response
DEBUG = False

# Get WiFi details, ensure these are setup in settings.toml
ssid = os.getenv("CIRCUITPY_WIFI_SSID")
password = os.getenv("CIRCUITPY_WIFI_PASSWORD")


def time_calc(input_time):
    """Converts seconds to minutes/hours/days"""
    if input_time < 60:
        return f"{input_time:.0f} seconds"
    if input_time < 3600:
        return f"{input_time / 60:.0f} minutes"
    if input_time < 86400:
        return f"{input_time / 60 / 60:.0f} hours"
    return f"{input_time / 60 / 60 / 24:.1f} days"


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

Arial12_font = bitmap_font.load_font("/fonts/Arial-12.bdf")
Arial16_font = bitmap_font.load_font("/fonts/Arial-16.bdf")

# Label Customizations
loading_label = label.Label(Arial12_font)
loading_label.anchor_point = (0.5, 0.0)
loading_label.anchored_position = (DISPLAY_WIDTH / 2, 10)
loading_label.scale = 1
loading_label.color = TEXT_ORANGE

date_label = label.Label(Arial12_font)
date_label.anchor_point = (0.0, 0.0)
date_label.anchored_position = (5, 20)
date_label.scale = 1
date_label.color = TEXT_ORANGE

date_data = label.Label(Arial12_font)
date_data.anchor_point = (0.0, 0.0)
date_data.anchored_position = (100, 20)
date_data.scale = 1
date_data.color = TEXT_LIGHTBLUE

flightname_label = label.Label(Arial12_font)
flightname_label.anchor_point = (0.0, 0.0)
flightname_label.anchored_position = (5, 40)
flightname_label.scale = 1
flightname_label.color = TEXT_ORANGE

flightname_data = label.Label(Arial12_font)
flightname_data.anchor_point = (0.0, 0.0)
flightname_data.anchored_position = (100, 40)
flightname_data.scale = 1
flightname_data.color = TEXT_LIGHTBLUE

provider_label = label.Label(Arial12_font)
provider_label.anchor_point = (0.0, 0.0)
provider_label.anchored_position = (5, 60)
provider_label.scale = 1
provider_label.color = TEXT_ORANGE

provider_data = label.Label(Arial12_font)
provider_data.anchor_point = (0.0, 0.0)
provider_data.anchored_position = (100, 60)
provider_data.scale = 1
provider_data.color = TEXT_LIGHTBLUE

vehiclename_label = label.Label(Arial12_font)
vehiclename_label.anchor_point = (0.0, 0.0)
vehiclename_label.anchored_position = (5, 80)
vehiclename_label.scale = 1
vehiclename_label.color = TEXT_ORANGE

vehiclename_data = label.Label(Arial12_font)
vehiclename_data.anchor_point = (0.0, 0.0)
vehiclename_data.anchored_position = (100, 80)
vehiclename_data.scale = 1
vehiclename_data.color = TEXT_LIGHTBLUE

window_label = label.Label(Arial12_font)
window_label.anchor_point = (0.0, 0.0)
window_label.anchored_position = (5, 100)
window_label.scale = 1
window_label.color = TEXT_ORANGE

window_data = label.Label(Arial12_font)
window_data.anchor_point = (0.0, 0.0)
window_data.anchored_position = (100, 100)
window_data.scale = 1
window_data.color = TEXT_LIGHTBLUE

launchsite_label = label.Label(Arial12_font)
launchsite_label.anchor_point = (0.0, 0.0)
launchsite_label.anchored_position = (5, 120)
launchsite_label.scale = 1
launchsite_label.color = TEXT_ORANGE

launchsite_data = label.Label(Arial12_font)
launchsite_data.anchor_point = (0.0, 0.0)
launchsite_data.anchored_position = (100, 120)
launchsite_data.scale = 1
launchsite_data.color = TEXT_LIGHTBLUE

padname_label = label.Label(Arial12_font)
padname_label.anchor_point = (0.0, 0.0)
padname_label.anchored_position = (5, 140)
padname_label.scale = 1
padname_label.color = TEXT_ORANGE

padname_data = label.Label(Arial12_font)
padname_data.anchor_point = (0.0, 0.0)
padname_data.anchored_position = (100, 140)
padname_data.scale = 1
padname_data.color = TEXT_LIGHTBLUE

description_label = label.Label(Arial12_font)
description_label.anchor_point = (0.0, 0.0)
description_label.anchored_position = (5, 160)
description_label.scale = 1
description_label.color = TEXT_ORANGE

LDWT = label.Label(terminalio.FONT)
LDWT.anchor_point = (0.0, 0.0)
LDWT.anchored_position = (5, 180)
LDWT.scale = 1
LDWT.color = TEXT_LIGHTBLUE

mission_label = label.Label(Arial12_font)
mission_label.anchor_point = (0.0, 0.0)
mission_label.anchored_position = (5, 225)
mission_label.scale = 1
mission_label.color = TEXT_ORANGE

MWT = label.Label(terminalio.FONT)
MWT.anchor_point = (0.0, 0.0)
MWT.anchored_position = (5, 245)
MWT.scale = 1
MWT.color = TEXT_LIGHTBLUE

sprite_sheet, palette = adafruit_imageload.load(
    "icons/rocket.bmp",
    bitmap=displayio.Bitmap,
    palette=displayio.Palette,
)
palette.make_transparent(0)
rocket_icon = displayio.TileGrid(
    sprite_sheet,
    pixel_shader=palette,
    x=DISPLAY_WIDTH - 80,
    y=2,
    width=1,
    height=1,
    tile_width=80,
    tile_height=82,
    default_tile=0,
)

# Create Display Groups
text_group = displayio.Group()
text_group.append(loading_label)
text_group.append(date_label)
text_group.append(date_data)
text_group.append(flightname_label)
text_group.append(flightname_data)
text_group.append(provider_label)
text_group.append(provider_data)
text_group.append(vehiclename_label)
text_group.append(vehiclename_data)
text_group.append(window_label)
text_group.append(window_data)
text_group.append(padname_label)
text_group.append(padname_data)
text_group.append(launchsite_label)
text_group.append(launchsite_data)
text_group.append(description_label)
text_group.append(LDWT)
text_group.append(mission_label)
text_group.append(MWT)
text_group.append(rocket_icon)
display.root_group = text_group

# Publicly available data no header required
# The number at the end is the amount of launches (max 5 free api)
ROCKETLAUNCH_SOURCE = "https://fdo.rocketlaunch.live/json/launches/next/1"

# Initalize Wifi, Socket Pool, Request Session
pool = adafruit_connection_manager.get_radio_socketpool(wifi.radio)
ssl_context = adafruit_connection_manager.get_radio_ssl_context(wifi.radio)
requests = adafruit_requests.Session(pool, ssl_context)

while True:
    # Connect to Wi-Fi
    print("\n===============================")
    print("Connecting to WiFi...")
    loading_label.text = "Connecting to Wifi"
    while not wifi.radio.ipv4_address:
        try:
            wifi.radio.connect(ssid, password)
        except ConnectionError as e:
            print("❌ Connection Error:", e)
            print("Retrying in 10 seconds")
    print("✅ Wifi!")
    try:
        # Print Request to Serial
        print(" | Attempting to GET RocketLaunch.Live JSON!")
        loading_label.text = "Getting Next Rocket Launch"
        time.sleep(1)

        try:
            rocketlaunch_response = requests.get(url=ROCKETLAUNCH_SOURCE)
            rocketlaunch_json = rocketlaunch_response.json()
        except ConnectionError as e:
            print("Connection Error:", e)
            print("Retrying in 10 seconds")
        print(" | ✅ RocketLaunch.Live JSON!")

        if DEBUG:
            print("Full API GET URL: ", ROCKETLAUNCH_SOURCE)
            print(rocketlaunch_json)

        # JSON Endpoints
        RLFN = str(rocketlaunch_json["result"][0]["name"])
        RLWO = str(rocketlaunch_json["result"][0]["win_open"])
        TZERO = str(rocketlaunch_json["result"][0]["t0"])
        RLWC = str(rocketlaunch_json["result"][0]["win_close"])
        RLP = str(rocketlaunch_json["result"][0]["provider"]["name"])
        RLVN = str(rocketlaunch_json["result"][0]["vehicle"]["name"])
        RLPN = str(rocketlaunch_json["result"][0]["pad"]["name"])
        RLLS = str(rocketlaunch_json["result"][0]["pad"]["location"]["name"])
        RLLD = str(rocketlaunch_json["result"][0]["launch_description"])
        RLM = str(rocketlaunch_json["result"][0]["mission_description"])
        RLDATE = str(rocketlaunch_json["result"][0]["date_str"])

        # Print to serial & display label if endpoint not "None"
        loading_label.text = ""
        if RLDATE != "None":
            print(f" |  | Date: {RLDATE}")
            date_label.text = "Date: "
            date_data.text = f"{RLDATE}\n"
        if RLFN != "None":
            print(f" |  | Flight: {RLFN}")
            flightname_label.text = "Flight: "
            flightname_data.text = f"{RLFN}\n"
        if RLP != "None":
            print(f" |  | Provider: {RLP}")
            provider_label.text = "Provider: "
            provider_data.text = f"{RLP}\n"
        if RLVN != "None":
            print(f" |  | Vehicle: {RLVN}")
            vehiclename_label.text = "Vehicle: "
            vehiclename_data.text = f"{RLVN}\n"

        # Launch time can sometimes be Window Open to Close, T-Zero, or weird combination.
        # Should obviously be standardized but they're not input that way.
        # Have to account for every combination of 3 conditions.
        # T-Zero Launch Time Conditionals
        if RLWO == "None" and TZERO != "None" and RLWC != "None":
            print(f" |  | Window: {TZERO} | {RLWC}")
            window_label.text = "Window: "
            window_data.text = f"{TZERO} | {RLWC}\n"
        elif RLWO != "None" and TZERO != "None" and RLWC == "None":
            print(f" |  | Window: {RLWO} | {TZERO}")
            window_label.text = "Window: "
            window_data.text = f"{RLWO} | {TZERO}\n"
        elif RLWO != "None" and TZERO == "None" and RLWC != "None":
            print(f" |  | Window: {RLWO} | {RLWC}")
            window_label.text = "Window: "
            window_data.text = f"{RLWO} | {RLWC}\n"
        elif RLWO != "None" and TZERO != "None" and RLWC != "None":
            print(f" |  | Window: {RLWO} | {TZERO} | {RLWC}")
            window_label.text = "Window: "
            window_data.text = f"{RLWO} | {TZERO} | {RLWC}\n"
        elif RLWO == "None" and TZERO != "None" and RLWC == "None":
            print(f" |  | Window: {TZERO}")
            window_label.text = "Window: "
            window_data.text = f"{TZERO}\n"
        elif RLWO != "None" and TZERO == "None" and RLWC == "None":
            print(f" |  | Window: {RLWO}")
            window_label.text = "Window: "
            window_data.text = f"{RLWO}\n"
        elif RLWO == "None" and TZERO == "None" and RLWC != "None":
            print(f" |  | Window: {RLWC}")
            window_label.text = "Window: "
            window_data.text = f"{RLWC}\n"

        if RLLS != "None":
            print(f" |  | Site: {RLLS}")
            launchsite_label.text = "Site: "
            launchsite_data.text = f"{RLLS}\n"
        if RLPN != "None":
            print(f" |  | Pad: {RLPN}")
            padname_label.text = "Pad: "
            padname_data.text = f"{RLPN}\n"
        if RLLD != "None":
            print(f" |  | Description: {RLLD}")
            description_label.text = "Description: "
            LDWT.text = "\n".join(wrap_text_to_pixels(RLLD, DW2, terminalio.FONT))
        if RLM != "None":
            print(f" |  | Mission: {RLM}")
            mission_label.text = "Mission: "
            MWT.text = "\n".join(wrap_text_to_pixels(RLM, DW2, terminalio.FONT))

        rocketlaunch_response.close()
        print("✂️ Disconnected from RocketLaunch.Live API")

        print("\nFinished!")
        print(f"Board Uptime: {time_calc(time.monotonic())}")
        print(f"Next Update: {time_calc(SLEEP_TIME)}")
        print("===============================")

    except (ValueError, RuntimeError) as e:
        print("Failed to get data, retrying\n", e)
        time.sleep(60)
        break
    time.sleep(SLEEP_TIME)
