# SPDX-FileCopyrightText: 2024 DJDevon3
# SPDX-License-Identifier: MIT
# Coded with Circuit Python 9.1
""" Fitbit API Graph on TFT Display """

import os
import board
import time
import displayio
import terminalio
import microcontroller
import wifi
import adafruit_connection_manager
import digitalio
import storage
from fourwire import FourWire
import adafruit_sdcard
from adafruit_bitmapsaver import save_pixels
from adafruit_bitmap_font import bitmap_font
import adafruit_imageload
from adafruit_hx8357 import HX8357
from adafruit_display_text import label
from adafruit_displayio_layout.widgets.cartesian import Cartesian
import adafruit_requests

displayio.release_displays()

DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 320

# Initialize TFT Display
spi = board.SPI()
tft_cs = board.D9
tft_dc = board.D10
display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = HX8357(display_bus, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT)
display.auto_refresh = False

# STREAMER WARNING: private data will be viewable while debug True
debug = False  # Set True for full debug view

# No graph from midnight to 00:15 due to lack of 15 values.
# Debug midnight to display something else in this time frame.
midnight_debug = False

# Can use to confirm first instance of NVM is correct refresh token
top_nvm = microcontroller.nvm[0:64].decode()
if debug:
    print(f"Top NVM: {top_nvm}")  # NVM before settings.toml loaded

# --- Fitbit Developer Account & oAuth App Required: ---
# Step 1: Create a personal app here: https://dev.fitbit.com
# Step 2: Use their Tutorial to get the Token and first Refresh Token
# Fitbit's Tutorial Step 4 is as far as you need to go.
# https://dev.fitbit.com/build/reference/web-api/troubleshooting-guide/oauth2-tutorial/

# Ensure these are in settings.toml
# Fitbit_ClientID = "YourAppClientID"
# Fitbit_Token = "Long 256 character string (SHA-256)"
# Fitbit_First_Refresh_Token = "64 character string"
# Fitbit_UserID = "UserID authorizing the ClientID"

Fitbit_ClientID = os.getenv("Fitbit_ClientID")
Fitbit_Token = os.getenv("Fitbit_Token")
Fitbit_First_Refresh_Token = os.getenv("Fitbit_First_Refresh_Token")
Fitbit_UserID = os.getenv("Fitbit_UserID")

wifi_ssid = os.getenv("CIRCUITPY_WIFI_SSID")
wifi_pw = os.getenv("CIRCUITPY_WIFI_PASSWORD")

# Time between API refreshes
# 300 = 5 mins, 900 = 15 mins, 1800 = 30 mins, 3600 = 1 hour
sleep_time = 900

# Initalize Wifi, Socket Pool, Request Session
pool = adafruit_connection_manager.get_radio_socketpool(wifi.radio)
ssl_context = adafruit_connection_manager.get_radio_ssl_context(wifi.radio)
requests = adafruit_requests.Session(pool, ssl_context)


def time_calc(input_time):
    """Converts seconds to minutes/hours/days"""
    if input_time < 60:
        return f"{input_time:.0f} seconds"
    if input_time < 3600:
        return f"{input_time / 60:.0f} minutes"
    if input_time < 86400:
        return f"{input_time / 60 / 60:.0f} hours"
    return f"{input_time / 60 / 60 / 24:.1f} days"


goodtimes16 = bitmap_font.load_font("/fonts/GoodTimesRg-Regular-16.bdf")
arial16 = bitmap_font.load_font("/fonts/Arial-16.bdf")

# Quick Colors for Labels
BLACK = 0x000000
BLUE = 0x0000FF
CYAN = 0x00FFFF
GRAY = 0x8B8B8B
GREEN = 0x00FF00
LIGHTBLUE = 0x90C7FF
MAGENTA = 0xFF0090
ORANGE = 0xFFA500
PINK = 0xFFC0CB
PURPLE = 0x800080
RED = 0xFF0000
WHITE = 0xFFFFFF
YELLOW = 0xFFFF00


def make_my_label(
    font=None, anchor_point=None, anchored_position=None, scale=None, color=None
):
    """Shortens labels to 1 liners (any argument optional)"""
    func_label = label.Label(font) if font is not None else label.Label()
    if anchor_point is not None:
        func_label.anchor_point = anchor_point
    if anchored_position is not None:
        func_label.anchored_position = anchored_position
    if scale is not None:
        func_label.scale = scale
    if color is not None:
        func_label.color = color
    return func_label


DH = DISPLAY_HEIGHT
DW = DISPLAY_WIDTH
TERM = terminalio.FONT
activity_status = make_my_label(arial16, (0.5, 0.0), (DW / 2, 30), 1)
error_label = make_my_label(TERM, (0.5, 0.5), (DW / 2, DH / 2), 2, WHITE)
date_label = make_my_label(arial16, (0.0, 0.0), (5, 5), 1, WHITE)
time_label = make_my_label(arial16, (0.0, 0.0), (5, 30), 1, WHITE)
midnight_label = make_my_label(TERM, (0.0, 0.0), (5, 40), 1, WHITE)
watch_bat_label = make_my_label(arial16, (1.0, 0.0), (DW - 5, 5), 1, WHITE)
watch_bat_shadow = make_my_label(arial16, (1.0, 0.0), (DW - 4, 6), 1, WHITE)
pulse_label = make_my_label(TERM, (0.5, 0.0), (344, 200), 2, PINK)


def bar_color(heart_rate):
    """ Range Mapping with Text Color & Status Output"""
    color_mapping = {
        (float("-inf"), 60): (RED, "Dangerously Low"),
        (60, 75): (BLUE, "Very Low"),
        (75, 85): (LIGHTBLUE, "Sleeping"),
        (85, 95): (CYAN, "Relaxing"),
        (95, 105): (GREEN, "Awake"),
        (105, 120): (YELLOW, "Active"),
        (120, 135): (ORANGE, "Very Active"),
        (135, float("inf")): (MAGENTA, "Exertion"),
    }
    for heart_range, (color, status) in color_mapping.items():
        if heart_range[0] <= heart_rate < heart_range[1]:
            heart_rate_color = color
            activity_status.color = color
            activity_status.text = status
            break
    return heart_rate_color


# Load Fitbit Icon
sprite_sheet, palette = adafruit_imageload.load(
    "icons/Fitbit_Logo.bmp",
    bitmap=displayio.Bitmap,
    palette=displayio.Palette,
)
palette.make_transparent(0)
fitbit_icon = displayio.TileGrid(
    sprite_sheet,
    pixel_shader=palette,
    x=5,
    y=5,
    width=1,
    height=1,
    tile_width=112,
    tile_height=32,
    default_tile=0,
)

# Load Picture
DiskBMP = displayio.OnDiskBitmap("/images/Grandma.bmp")
grandma = displayio.TileGrid(
    DiskBMP,
    pixel_shader=DiskBMP.pixel_shader,
    tile_width=480,
    tile_height=320,
)

# Create subgroups (layers)
text_group = displayio.Group()
plot_group = displayio.Group()
midnight_group = displayio.Group()
main_group = displayio.Group()

# Add subgroups to main group
main_group.append(plot_group)
main_group.append(text_group)
main_group.append(midnight_group)

# Append labels to subgroups (sublayers)
text_group.append(date_label)
text_group.append(time_label)
text_group.append(pulse_label)
text_group.append(error_label)
midnight_group.append(grandma)
midnight_group.append(fitbit_icon)
midnight_group.append(watch_bat_shadow)
midnight_group.append(watch_bat_label)
midnight_group.append(midnight_label)
midnight_group.append(activity_status)

# Combine and Show
display.root_group = main_group

# Authenticates Client ID & SHA-256 Token to POST
fitbit_oauth_header = {"Content-Type": "application/x-www-form-urlencoded"}
fitbit_oauth_token = "https://api.fitbit.com/oauth2/token"

# First run uses settings.toml token
Refresh_Token = Fitbit_First_Refresh_Token
First_Run = True
if debug:
    print(f"Top NVM Again (just to make sure): {top_nvm}")
    print(f"Settings.toml Initial Refresh Token: {Fitbit_First_Refresh_Token}")

new_line = "\n"
while True:
    # Connect to Wi-Fi
    board_uptime = time.monotonic()
    print("\n===============================")
    print("Connecting to WiFi...")
    while not wifi.radio.ipv4_address:
        try:
            wifi.radio.connect(wifi_ssid, wifi_pw)
        except ConnectionError as e:
            print("Connection Error:", e)
            print("Retrying in 10 seconds")
            continue
        time.sleep(10)
    print("Connected!\n")

    if not First_Run:
        First_Run = False
        Refresh_Token = microcontroller.nvm[0:64].decode()
        print("------ INDEFINITE RUN -------")
        if debug:
            print("Top NVM is Fitbit First Refresh Token")
            print(f"NVM 64: {microcontroller.nvm[0:64].decode()}")
            print(f"Current Refresh_Token: {Refresh_Token}")
    elif top_nvm != Fitbit_First_Refresh_Token and First_Run:
        if debug:
            print(f"Top NVM: {top_nvm}")
            print(f"First Refresh: {Refresh_Token}")
            print(f"First Run: {First_Run}")
        Refresh_Token = top_nvm
        First_Run = False
        print("------ MANUAL REBOOT TOKEN DIFFERENCE -------")
        if debug:
            print("Top NVM is NOT Fitbit First Refresh Token")
            print(f"NVM 64: {microcontroller.nvm[0:64].decode()}")
            print(f"Current Refresh_Token: {Refresh_Token}")
    elif top_nvm == Refresh_Token and First_Run:
        if debug:
            print(f"Top NVM: {top_nvm}")
            print(f"First Refresh: {Refresh_Token}")
            print(f"First Run: {First_Run}")
        Refresh_Token = Fitbit_First_Refresh_Token
        nvmtoken = b"" + Refresh_Token
        microcontroller.nvm[0:64] = nvmtoken
        First_Run = False
        print("------ FIRST RUN SETTINGS.TOML TOKEN-------")
        if debug:
            print("Top NVM IS Fitbit First Refresh Token")
            print(f"NVM 64: {microcontroller.nvm[0:64].decode()}")
            print(f"Current Refresh_Token: {Refresh_Token}")

    try:
        if debug:
            print("\n-----Token Refresh POST Attempt -------")
        fitbit_oauth_refresh_token = (
            "&grant_type=refresh_token"
            + "&client_id="
            + str(Fitbit_ClientID)
            + "&refresh_token="
            + str(Refresh_Token)
        )

        # ----------------------------- POST FOR REFRESH TOKEN -----------------------
        if debug:
            print(
                "FULL REFRESH TOKEN POST:"
                + f"{fitbit_oauth_token}{fitbit_oauth_refresh_token}"
            )
            print(f"Current Refresh Token: {Refresh_Token}")
        # TOKEN REFRESH POST
        try:
            fitbit_oauth_refresh_POST = requests.post(
                url=fitbit_oauth_token,
                data=fitbit_oauth_refresh_token,
                headers=fitbit_oauth_header,
            )
        except adafruit_requests.OutOfRetries as ex:
            print(f"OutOfRetries: {ex}")
            break
        try:
            fitbit_refresh_oauth_json = fitbit_oauth_refresh_POST.json()

            fitbit_new_token = fitbit_refresh_oauth_json["access_token"]
            if debug:
                print("Your Private SHA-256 Token: ", fitbit_new_token)
            fitbit_access_token = fitbit_new_token  # NEW FULL TOKEN

            # Overwrites Initial/Old Refresh Token with Next/New Refresh Token
            fitbit_new_refesh_token = fitbit_refresh_oauth_json["refresh_token"]
            Refresh_Token = fitbit_new_refesh_token

            fitbit_token_expiration = fitbit_refresh_oauth_json["expires_in"]
            fitbit_scope = fitbit_refresh_oauth_json["scope"]
            fitbit_token_type = fitbit_refresh_oauth_json["token_type"]
            fitbit_user_id = fitbit_refresh_oauth_json["user_id"]
            if debug:
                print("Next Refresh Token: ", Refresh_Token)
            try:
                # Stores Next token in NVM
                nvmtoken = b"" + fitbit_new_refesh_token
                microcontroller.nvm[0:64] = nvmtoken
                if debug:
                    print(f"Next Token for NVM: {nvmtoken.decode()}")
                print("Next token written to NVM Successfully!")
            except (OSError) as e:
                print("OS Error:", e)
                continue

            if debug:
                print("Token Expires in: ", time_calc(fitbit_token_expiration))
                print("Scope: ", fitbit_scope)
                print("Token Type: ", fitbit_token_type)
                print("UserID: ", fitbit_user_id)

        except (KeyError) as e:
            print("Key Error:", e)
            print("Expired token, invalid permission, or (key:value) pair error.")
            time.sleep(300)
            continue

        # ----------------------------- GET DATA -------------------------------------
        # Now that we have POST response with next refresh token we can GET for data
        # 64-bit Refresh tokens will "keep alive" SHA-256 token indefinitely
        # Fitbit main SHA-256 token expires in 8 hours unless refreshed!
        # ----------------------------------------------------------------------------
        detail_level = "1min"  # Supported: 1sec | 1min | 5min | 15min
        requested_date = "today"  # Date format yyyy-MM-dd or today
        fitbit_header = {
            "Authorization": "Bearer " + fitbit_access_token + "",
            "Client-Id": "" + Fitbit_ClientID + "",
        }
        # Heart Intraday Scope
        FITBIT_INTRADAY_SOURCE = (
            "https://api.fitbit.com/1/user/"
            + Fitbit_UserID
            + "/activities/heart/date/today"
            + "/1d/"
            + detail_level
            + ".json"
        )
        # Device Details
        FITBIT_DEVICE_SOURCE = (
            "https://api.fitbit.com/1/user/" + Fitbit_UserID + "/devices.json"
        )

        print("\nAttempting to GET FITBIT Intraday Stats!")
        print("===============================")
        FBIS = FITBIT_INTRADAY_SOURCE
        FBH = fitbit_header
        fitbit_get_response = requests.get(url=FBIS, headers=FBH)
        try:
            fitbit_json = fitbit_get_response.json()
        except ConnectionError as e:
            print("Connection Error:", e)
            print("Retrying in 10 seconds")

        if debug:
            print(f"Full API GET URL: {FBIS}")
            print(f"Header: {fitbit_header}")
            # print(f"JSON Full Response: {fitbit_json}")
            Intraday_Response = fitbit_json["activities-heart-intraday"]["dataset"]
            # print(f"Intraday Full Response: {Intraday_Response}")

        try:
            activities_heart_value = fitbit_json.get(
                "activities-heart-intraday", {}
            ).get("dataset", [])
            response_length = len(activities_heart_value)
            if response_length >= 15:
                midnight_label.text = ""
                activities_timestamp = fitbit_json.get("activities-heart", [{}])[0].get(
                    "dateTime", ""
                )
                activities_latest_heart_time = activities_heart_value[-1].get(
                    "time", ""
                )
                print(f"Fitbit Date: {activities_timestamp}")
                print(f"Fitbit Time: {activities_latest_heart_time[0:-3]}")
                print(f"Today's Logged Pulses: {response_length}")

                latest_15_values = [
                    data["value"] for data in activities_heart_value[-15:]
                ]
                print("Latest 15 Minute Averages:", latest_15_values[::-1])

                list_data = latest_15_values
                lowest_y = sorted(list_data)
                highest_y = sorted(list_data, reverse=True)

                date_label.text = f"{activities_timestamp}"
                time_label.text = f"{activities_latest_heart_time[0:-3]}"

                my_plane = Cartesian(
                    x=30,
                    y=60,
                    width=DISPLAY_WIDTH - 20,
                    height=DISPLAY_HEIGHT - 80,
                    xrange=(0, 14),
                    yrange=(lowest_y[0], highest_y[0]),
                    axes_color=bar_color(highest_y[0]),
                    pointer_color=PINK,
                    axes_stroke=4,
                    major_tick_stroke=2,
                    subticks=True,
                )
                my_plane.clear_plot_lines()
                plot_group.append(my_plane)
                fitbit_icon.hidden = True
                grandma.hidden = True

                data = [(i, val) for i, val in enumerate(latest_15_values[::-1])]
                for x, y in data:
                    my_plane.add_plot_line(x, y)
                    time.sleep(0.5)
            else:
                grandma.hidden = False
                fitbit_icon.hidden = False
                activity_status.text = ""
                midnight_label.text = "No values for today yet."
                print("Waiting for latest sync...")
                print("Not enough values for today to display yet.")
        except KeyError as keyerror:
            print(f"Key Error: {keyerror}")
            print(
                "Too Many Requests, "
                + "Expired token, "
                + "invalid permission, "
                + "or (key:value) pair error."
            )
            time.sleep(60)
            continue

        FBDS = FITBIT_DEVICE_SOURCE
        FBH = fitbit_header
        fitbit_get_device_response = requests.get(url=FBDS, headers=FBH)
        try:
            fitbit_device_json = fitbit_get_device_response.json()
        except ConnectionError as e:
            print("Connection Error:", e)
            print("Retrying in 10 seconds")

        if debug:
            print(f"Full API GET URL: {FITBIT_DEVICE_SOURCE}")
            print(f"Header: {fitbit_header}")
            print(f"JSON Full Response: {fitbit_device_json}")

        Device_Response = fitbit_device_json[0]["batteryLevel"]
        error_label.text = ""
        print(f"Watch Battery %: {Device_Response}")
        watch_bat_shadow.text = f"Battery: {Device_Response}%"
        watch_bat_label.text = f"Battery: {Device_Response}%"
        
        print("\nFinished!")
        print("Board Uptime:", time_calc(time.monotonic()))  # Board Up-Time seconds
        if board_uptime > 86400:
            print("24 Hour Uptime Restart")
            microcontroller.reset()
        else:
            print("Next Update in:", time_calc(sleep_time))
        print("===============================")

    except (ValueError, RuntimeError) as e:
        print("Failed to get data, retrying\n", e)
        time.sleep(60)
        continue

    display.refresh()
    TAKE_SCREENSHOT = False  # Set to True to take a screenshot
    if TAKE_SCREENSHOT:
        # Initialize SD Card & Mount Virtual File System
        SD_CS = board.D5
        cs = digitalio.DigitalInOut(SD_CS)
        sdcard = adafruit_sdcard.SDCard(spi, cs)
        vfs = storage.VfsFat(sdcard)
        storage.mount(vfs, "/sd")
        print("Taking Screenshot... ")
        save_pixels("/sd/Active.bmp", display)
        print("Screenshot Saved")
        storage.umount(vfs)
        print("SD Card Unmounted")  # Do not remove SD card until unmounted
    try:
        plot_group.remove(my_plane)
    except (NameError, ValueError, RuntimeError) as e:
        error_label.text = "No data for today yet"
        print("Final Exception Failure:\n", e)
        print(
            "Not enough values for today yet",
            "Needs 15 values.",
            "No display from midnight to 00:15",
            sep="\n",
        )
        print("Next Update in: ", time_calc(sleep_time))
        print("===============================")
        time.sleep(60)
        pass

    time.sleep(sleep_time)