# SPDX-FileCopyrightText: 2023 DJDevon3
# SPDX-License-Identifier: MIT
# Coded for Circuit Python 8.2

import os
import board
import time
import displayio
import digitalio
import terminalio
import microcontroller
import ssl
import wifi
import socketpool
import adafruit_sdcard
from adafruit_bitmapsaver import save_pixels
import storage
from adafruit_hx8357 import HX8357
from adafruit_display_text import label
from adafruit_displayio_layout.widgets.cartesian import Cartesian
import adafruit_requests

displayio.release_displays()

# Initialize WiFi Pool (There can be only 1 pool & top of script)
pool = socketpool.SocketPool(wifi.radio)

DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 320

# Initialize TFT Display
spi = board.SPI()
tft_cs = board.D9
tft_dc = board.D10
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = HX8357(display_bus, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT)
display.auto_refresh = False

# STREAMER WARNING: private data will be viewable while debug True
debug = False  # Set True for full debug view

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
TEXT_PINK = 0XFFC0CB
TEXT_PURPLE = 0x800080
TEXT_RED = 0xFF0000
TEXT_WHITE = 0xFFFFFF
TEXT_YELLOW = 0xFFFF00

def bar_color(heart_rate):
    if heart_rate < 60:
        heart_rate_color = TEXT_PURPLE
    elif 60 <= heart_rate < 75:
        heart_rate_color = TEXT_BLUE
    elif 75 <= heart_rate < 85:
        heart_rate_color = TEXT_LIGHTBLUE
    elif 85 <= heart_rate < 100:
        heart_rate_color = TEXT_GREEN
    elif 100 <= heart_rate < 110:
        heart_rate_color = TEXT_YELLOW
    elif 110 <= heart_rate < 120:
        heart_rate_color = TEXT_ORANGE
    else:
        heart_rate_color = TEXT_RED
    return heart_rate_color

hello_label = label.Label(terminalio.FONT)
hello_label.anchor_point = (0.5, 0.0)
hello_label.anchored_position = (DISPLAY_WIDTH/2, 5)
hello_label.scale = (1)
hello_label.color = TEXT_WHITE

date_label = label.Label(terminalio.FONT)
date_label.anchor_point = (0.0, 0.0)
date_label.anchored_position = (5, 5)
date_label.scale = (2)
date_label.color = TEXT_WHITE

time_label = label.Label(terminalio.FONT)
time_label.anchor_point = (0.0, 0.0)
time_label.anchored_position = (5, 30)
time_label.scale = (2)
time_label.color = TEXT_WHITE

midnight_label = label.Label(terminalio.FONT)
midnight_label.anchor_point = (0.5, 0.0)
midnight_label.anchored_position = (DISPLAY_WIDTH/2, DISPLAY_HEIGHT/2-50)
midnight_label.scale = (2)
midnight_label.color = TEXT_WHITE

watch_bat_label = label.Label(terminalio.FONT)
watch_bat_label.anchor_point = (1.0, 0.0)
watch_bat_label.anchored_position = (DISPLAY_WIDTH, 5)
watch_bat_label.scale = (2)
watch_bat_label.color = TEXT_WHITE

pulse_label = label.Label(terminalio.FONT)
pulse_label.anchor_point = (0.5, 0.0)
pulse_label.anchored_position = (344, 200)
pulse_label.scale = (2)
pulse_label.color = TEXT_PINK

# Create subgroups (layers)
text_group = displayio.Group()
midnight_group = displayio.Group()
plot_group = displayio.Group()
main_group = displayio.Group()

# Add subgroups to main group
main_group.append(plot_group)
main_group.append(text_group)
main_group.append(midnight_group)

# Append labels to subgroups (sublayers)
text_group.append(hello_label)
text_group.append(date_label)
text_group.append(time_label)
text_group.append(watch_bat_label)
text_group.append(pulse_label)

# Combine and Show
display.show(main_group)

# Authenticates Client ID & SHA-256 Token to POST
fitbit_oauth_header = {"Content-Type": "application/x-www-form-urlencoded"}
fitbit_oauth_token = "https://api.fitbit.com/oauth2/token"

# Connect to Wi-Fi
print("\n===============================")
print("Connecting to WiFi...")
requests = adafruit_requests.Session(pool, ssl.create_default_context())
while not wifi.radio.ipv4_address:
    try:
        wifi.radio.connect(wifi_ssid, wifi_pw)
    except ConnectionError as e:
        print("Connection Error:", e)
        print("Retrying in 10 seconds")
    time.sleep(10)
print("Connected!\n")

# First run uses settings.toml token
Refresh_Token = Fitbit_First_Refresh_Token
First_Run = True
if debug: 
    print(f"Top NVM Again (just to make sure): {top_nvm}")
    print(f"Settings.toml Initial Refresh Token: {Fitbit_First_Refresh_Token}")
    
while True:
    # hello_label.text = "Circuit Python 8.2.2 Fitbit API"
    
    if top_nvm is not Refresh_Token and First_Run is False:
        First_Run = False
        Refresh_Token = microcontroller.nvm[0:64].decode()
        print("------ INDEFINITE RUN -------")
        if debug:
            print("Top NVM is Fitbit First Refresh Token")
            # NVM 64 should match Current Refresh Token
            print(f"NVM 64: {microcontroller.nvm[0:64].decode()}")
            print(f"Current Refresh_Token: {Refresh_Token}")
            
    if top_nvm != Fitbit_First_Refresh_Token and First_Run is True:
        if debug:
            print(f"Top NVM: {top_nvm}")
            print(f"First Refresh: {Refresh_Token}")
            print(f"First Run: {First_Run}")
        Refresh_Token = top_nvm
        First_Run = False
        print("------ MANUAL CTRL+S TOKEN DIFFERENCE -------")
        if debug:
            # NVM 64 should not match Current Refresh Token
            print("Top NVM is NOT Fitbit First Refresh Token")
            print(f"NVM 64: {microcontroller.nvm[0:64].decode()}")
            print(f"Current Refresh_Token: {Refresh_Token}")
            
    if top_nvm == Refresh_Token and First_Run is True:
        if debug:
            print(f"Top NVM: {top_nvm}")
            print(f"First Refresh: {Refresh_Token}")
            print(f"First Run: {First_Run}")
        Refresh_Token = Fitbit_First_Refresh_Token
        nvmtoken = b''+Refresh_Token
        microcontroller.nvm[0:64] = nvmtoken
        First_Run = False
        print("------ FIRST RUN SETTINGS.TOML TOKEN-------")
        if debug:
            # NVM 64 should match Current Refresh Token
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
        fitbit_oauth_refresh_POST = requests.post(
            url=fitbit_oauth_token,
            data=fitbit_oauth_refresh_token,
            headers=fitbit_oauth_header
        )
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
                nvmtoken = b''+fitbit_new_refesh_token
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
            "https://api.fitbit.com/1/user/"
            + Fitbit_UserID
            + "/devices.json"
        )

        print("\nAttempting to GET FITBIT Intraday Stats!")
        print("===============================")
        fitbit_get_response = requests.get(url=FITBIT_INTRADAY_SOURCE, headers=fitbit_header)
        try:
            fitbit_json = fitbit_get_response.json()
        except ConnectionError as e:
            print("Connection Error:", e)
            print("Retrying in 10 seconds")

        if debug:
            print(f"Full API GET URL: {FITBIT_INTRADAY_SOURCE}")
            print(f"Header: {fitbit_header}")
            # print(f"JSON Full Response: {fitbit_json}")
            Intraday_Response = fitbit_json["activities-heart-intraday"]["dataset"]
            # print(f"Intraday Full Response: {Intraday_Response}")

        try:
            # Fitbit's sync to mobile device & server every 15 minutes in chunks.
            # Pointless to poll their API faster than 15 minute intervals.
            activities_heart_value = fitbit_json["activities-heart-intraday"]["dataset"]
            response_length = len(activities_heart_value)
            if response_length >= 15:
                midnight_label.text = ("")
                activities_timestamp = fitbit_json["activities-heart"][0]["dateTime"]
                print(f"Fitbit Date: {activities_timestamp}")
                activities_latest_heart_time = fitbit_json["activities-heart-intraday"][
                    "dataset"
                ][response_length - 1]["time"]
                print(f"Fitbit Time: {activities_latest_heart_time[0:-3]}")
                print(f"Today's Logged Pulses: {response_length}")

                # Each 1min heart rate is a 60 second average
                activities_latest_heart_value0 = fitbit_json[
                    "activities-heart-intraday"
                ]["dataset"][response_length - 1]["value"]
                activities_latest_heart_value1 = fitbit_json[
                    "activities-heart-intraday"
                ]["dataset"][response_length - 2]["value"]
                activities_latest_heart_value2 = fitbit_json[
                    "activities-heart-intraday"
                ]["dataset"][response_length - 3]["value"]
                activities_latest_heart_value3 = fitbit_json[
                    "activities-heart-intraday"
                ]["dataset"][response_length - 4]["value"]
                activities_latest_heart_value4 = fitbit_json[
                    "activities-heart-intraday"
                ]["dataset"][response_length - 5]["value"]
                activities_latest_heart_value5 = fitbit_json[
                    "activities-heart-intraday"
                ]["dataset"][response_length - 6]["value"]
                activities_latest_heart_value6 = fitbit_json[
                    "activities-heart-intraday"
                ]["dataset"][response_length - 7]["value"]
                activities_latest_heart_value7 = fitbit_json[
                    "activities-heart-intraday"
                ]["dataset"][response_length - 8]["value"]
                activities_latest_heart_value8 = fitbit_json[
                    "activities-heart-intraday"
                ]["dataset"][response_length - 9]["value"]
                activities_latest_heart_value9 = fitbit_json[
                    "activities-heart-intraday"
                ]["dataset"][response_length - 10]["value"]
                activities_latest_heart_value10 = fitbit_json[
                    "activities-heart-intraday"
                ]["dataset"][response_length - 11]["value"]
                activities_latest_heart_value11 = fitbit_json[
                    "activities-heart-intraday"
                ]["dataset"][response_length - 12]["value"]
                activities_latest_heart_value12 = fitbit_json[
                    "activities-heart-intraday"
                ]["dataset"][response_length - 13]["value"]
                activities_latest_heart_value13 = fitbit_json[
                    "activities-heart-intraday"
                ]["dataset"][response_length - 14]["value"]
                activities_latest_heart_value14 = fitbit_json[
                    "activities-heart-intraday"
                ]["dataset"][response_length - 15]["value"]
                latest_15_avg = "Latest 15 Minute Averages"
                print(
                    f"{latest_15_avg}: "
                    + f"{activities_latest_heart_value14},"
                    + f"{activities_latest_heart_value13},"
                    + f"{activities_latest_heart_value12},"
                    + f"{activities_latest_heart_value11},"
                    + f"{activities_latest_heart_value10},"
                    + f"{activities_latest_heart_value9},"
                    + f"{activities_latest_heart_value8},"
                    + f"{activities_latest_heart_value7},"
                    + f"{activities_latest_heart_value6},"
                    + f"{activities_latest_heart_value5},"
                    + f"{activities_latest_heart_value4},"
                    + f"{activities_latest_heart_value3},"
                    + f"{activities_latest_heart_value2},"
                    + f"{activities_latest_heart_value1},"
                    + f"{activities_latest_heart_value0}"
                )
                list_data = [activities_latest_heart_value14,
                             activities_latest_heart_value13,
                             activities_latest_heart_value12,
                             activities_latest_heart_value11,
                             activities_latest_heart_value10,
                             activities_latest_heart_value9,
                             activities_latest_heart_value8,
                             activities_latest_heart_value7,
                             activities_latest_heart_value6,
                             activities_latest_heart_value5,
                             activities_latest_heart_value4,
                             activities_latest_heart_value3,
                             activities_latest_heart_value2,
                             activities_latest_heart_value1,
                             activities_latest_heart_value0]
                # print(f"Data : {list_data}")
                lowest_y = sorted(list((list_data)))  # Get lowest sorted value
                highest_y = sorted(list_data, reverse=True)  # Get highest sorted value

                # Display Labels
                new_line = '\n'
                date_label.text = f"{activities_timestamp}"
                time_label.text = f"{activities_latest_heart_time[0:-3]}"

                my_plane = Cartesian(
                    x=30,  # x position for the plane
                    y=60,  # y plane position
                    width=DISPLAY_WIDTH-20,  # display width
                    height=DISPLAY_HEIGHT-80,  # display height
                    xrange=(0, 14),  # x range
                    yrange=(lowest_y[0], highest_y[0]),  # y range
                    axes_color=bar_color(highest_y[0]),
                    pointer_color=TEXT_PINK,
                    axes_stroke=4,
                    major_tick_stroke=2,
                    subticks=True,
                )
                my_plane.clear_plot_lines()
                plot_group.append(my_plane)
                data = [
                    (0, activities_latest_heart_value14),
                    (1, activities_latest_heart_value13),
                    (2, activities_latest_heart_value12),
                    (3, activities_latest_heart_value11),
                    (4, activities_latest_heart_value10),
                    (5, activities_latest_heart_value9),
                    (6, activities_latest_heart_value8),
                    (7, activities_latest_heart_value7),
                    (8, activities_latest_heart_value6),
                    (9, activities_latest_heart_value5),
                    (10, activities_latest_heart_value4),
                    (11, activities_latest_heart_value3),
                    (12, activities_latest_heart_value2),
                    (13, activities_latest_heart_value1),
                    (14, activities_latest_heart_value0),
                ]
                try:
                    for x, y in data:
                        my_plane.add_plot_line(x, y)
                        time.sleep(0.5)
                except (IndexError) as e:
                    print("Index Error:", e)
                    continue
            else :
                midnight_label.text = (
                    f"Not enough values for today.{new_line}"
                    + "No display from midnight to 00:15"
                )
                print("Waiting for latest sync...")
                print("Not enough values for today to display yet.")
        except (KeyError) as keyerror:
            print(f"Key Error: {keyerror}")
            print("Too Many Requests, "
                  + "Expired token, "
                  + "invalid permission, "
                  + "or (key:value) pair error."
                  )
            time.sleep(60)
            continue
            
        fitbit_get_device_response = requests.get(url=FITBIT_DEVICE_SOURCE, headers=fitbit_header)
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
        print(f"Watch Battery %: {Device_Response}")
        watch_bat_label.text = f"Battery: {Device_Response}%"
        print("Board Uptime:", time_calc(time.monotonic()))  # Board Up-Time seconds
        print("\nFinished!")
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
        cs = digitalio.DigitalInOut(board.D5)
        sdcard = adafruit_sdcard.SDCard(spi, cs)
        vfs = storage.VfsFat(sdcard)
        virtual_root = "/sd"  # /sd is root dir of SD Card
        storage.mount(vfs, virtual_root)

        print("Taking Screenshot... ")
        save_pixels("/sd/screenshot.bmp", display)
        print("Screenshot Saved")
        storage.umount(vfs)
        print("SD Card Unmounted")  # Do not remove SD card until unmounted
    try:
        plot_group.remove(my_plane)
    except (NameError, ValueError, RuntimeError) as e:
        print("Final Exception Failure:\n", e)
        print(f"Not enough values for today yet{new_line}"
              + f"Needs 15 values.{new_line}No display from midnight to 00:15"
              )
        print("Next Update in: ", time_calc(sleep_time))
        print("===============================")
        time.sleep(60)
        pass
    time.sleep(sleep_time)
