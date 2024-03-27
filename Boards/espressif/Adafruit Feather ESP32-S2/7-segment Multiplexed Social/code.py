# SPDX-FileCopyrightText: 2024 DJDevon3
# SPDX-License-Identifier: MIT
# Coded for Circuit Python 9.0
"""Multiplexed 7-segment Social Media Counter"""
# pylint: disable=import-error
import gc
import os
import time

import adafruit_connection_manager
import wifi

import adafruit_requests
import board
import busio
import pwmio
from adafruit_ht16k33 import segments
import adafruit_tca9548a

# Ensure ALL of these are setup in settings.toml
ssid = os.getenv("CIRCUITPY_WIFI_SSID")
password = os.getenv("CIRCUITPY_WIFI_PASSWORD")
TWITCH_CID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CS = os.getenv("TWITCH_CLIENT_SECRET")
# For finding your Twitch User ID
# https://www.streamweasels.com/tools/convert-twitch-username-to-user-id/
TWITCH_UID = os.getenv("TWITCH_USER_ID")
YOUTUBE_UNAME = os.getenv("YOUTUBE_USERNAME")
YOUTUBE_KEY = os.getenv("YOUTUBE_TOKEN")
TWITTER_UNAME = os.getenv("TWITTER_USERNAME")
TWITTER_UID = os.getenv("TWITTER_USERID")
TWITTER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
GITHUB_UID = os.getenv("GITHUB_USERNAME")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# For finding your Mastodon numerical UserID
# Example: https://mastodon.social/api/v1/accounts/lookup?acct=Username@Mastodon.social
MASTODON_SERVER = os.getenv("MASTODON_INSTANCE")  # Set server instance
MASTODON_UID = os.getenv("MASTODON_USERNAME")  # Your server Username
# Requires Steam Developer API key
STEAM_UNUM = os.getenv("STEAM_ID")
STEAM_KEY = os.getenv("STEAM_API_KEY")

# Initialize 7-Segment Backpack
i2c = board.I2C()
i2c2 = busio.I2C(board.D6, board.D5)
# Recommend running "CircuitPython I2C Device Address Scan" to get addresses
# https://learn.adafruit.com/adafruit-esp32-s2-feather/i2c-external-sensor

# Initialize TCA9548A Multiplexor bus object
tca = adafruit_tca9548a.TCA9548A(i2c)

# API Polling Rate
# 900 = 15 mins, 1800 = 30 mins, 3600 = 1 hour
SLEEP_TIME = 900

# Set DEBUG to True for full JSON response.
# STREAMER WARNING: Credentials will be viewable
DEBUG = False

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

def _format_datetime(datetime):
    """F-String formatted struct time conversion"""
    return (
        f"{datetime.tm_mon:02}/"
        + f"{datetime.tm_mday:02}/"
        + f"{datetime.tm_year:02} "
        + f"{datetime.tm_hour:02}:"
        + f"{datetime.tm_min:02}:"
        + f"{datetime.tm_sec:02}"
    )
    
# Initialize & combine backpack addresses
red = segments.Seg7x4(tca[0], address=(0x74, 0x75))
red.fill(0)
red.brightness = 0.5
red.print("youtube")

blue = segments.Seg7x4(tca[7], address=(0x74, 0x75))
blue.fill(0)
blue.brightness = 0.5
blue.print("mastodon")

green = segments.Seg7x4(tca[5], address=(0x74, 0x75))
green.fill(0)
green.brightness = 0.5
green.print("github")

yellow = segments.Seg7x4(tca[2], address=(0x74, 0x75))
yellow.fill(0)
yellow.brightness = 0.5
yellow.print("steam")

white = segments.Seg7x4(i2c2, address=(0x71, 0x72))
white.fill(0)
white.brightness = 0.5
white.print("discord")

# https://youtube.googleapis.com/youtube/v3/channels?part=statistics&forUsername=[YOUR_USERNAME]&key=[YOUR_API_KEY]
YOUTUBE_SOURCE = (
    "https://youtube.googleapis.com/youtube/v3/channels?part=statistics&forUsername="
    + str(YOUTUBE_UNAME)
    + "&key="
    + str(YOUTUBE_KEY)
)

# First we use Client ID & Client Secret to create a token with POST
# You must be logged into Twitch when you do this.
twitch_0auth_header = {"Content-Type": "application/x-www-form-urlencoded"}
TWITCH_0AUTH_TOKEN = "https://id.twitch.tv/oauth2/token"

GITHUB_HEADER = {"Authorization": " token " + GITHUB_TOKEN}
GITHUB_SOURCE = (f"https://api.github.com/users/{GITHUB_UID}")

# Publicly available data no header required
MASTODON_HEADER = {'Content-Type': 'application/json'}
MAST_SOURCE = (f"https://{MASTODON_SERVER}/api/v1/accounts/lookup?"
               + f"acct={MASTODON_UID}@{MASTODON_SERVER}")

# Originally attempted to use SVG. Found JSON exists with same filename.
# https://img.shields.io/discord/327254708534116352.svg
ADA_DISCORD_JSON = "https://img.shields.io/discord/327254708534116352.json"

# Deconstruct URL (pylint hates long lines)
# http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/
# ?key=XXXXXXXXXXXXXXXXXXXXX&include_played_free_games=1&steamid=XXXXXXXXXXXXXXXX&format=json
STEAM_SOURCE = ("http://api.steampowered.com/IPlayerService/"
                + "GetOwnedGames/v0001/?" +
                f"key={STEAM_KEY}" +
                "&include_played_free_games=1" +
                f"&steamid={STEAM_UNUM}" +
                "&format=json"
                )

while True:
    # Arcade button for board reset. This powers the LED.
    Reset_LED = pwmio.PWMOut(board.A0, frequency=25000, duty_cycle=0)
    Reset_LED.duty_cycle = 32768  # duty cycle is brightness (0-65535)
    gc.collect()
    # Connect to Wi-Fi
    print("\nConnecting to WiFi...")
    while not wifi.radio.ipv4_address:
        try:
            wifi.radio.connect(ssid, password)
        except ConnectionError as e:
            print("❌ Connection Error:", e)
            print("Retrying in 10 seconds")
        gc.collect()
    print("✅ Wifi!")
    print(" | Shuffling data to 7-Segment Displays")
    print(" | This could take a minute...")

    try:
        with requests.get(YOUTUBE_SOURCE) as youtube_response:
            try:
                youtube_json = youtube_response.json()
            except ConnectionError as e:
                print("Connection Error:", e)
                print("Retrying in 10 seconds")

            if DEBUG:
                print(f" | Full API GET URL: {YOUTUBE_SOURCE}")
                print(f" | Full API Dump: {youtube_json}")
            # Key:Value RESPONSES
            if "items" in youtube_json:
                YT_viewCount = youtube_json["items"][0]["statistics"]["viewCount"]
                YT_subsCount = youtube_json["items"][0]["statistics"]["subscriberCount"]
                
            # YouTube 7-Segment Display
            red.brightness = 0.8
            red.fill(0)
            red.print("eyes")
            time.sleep(2)
            red.fill(0)
            red.print(YT_viewCount)
            time.sleep(2)
            red.fill(0)
            red.print("subs")
            time.sleep(2)
            red.fill(0)
            red.print(YT_subsCount)
            gc.collect()
            # Marquee scrolling, 2nd parameter speed in seconds
            # red.marquee(YT_response_channel_subscriberCount, 0.9)
            youtube_response.close()
        
        # Mastodon
        try:
            mastodon_response = requests.get(url=MAST_SOURCE, headers=MASTODON_HEADER)
            mastodon_json = mastodon_response.json()
        except ConnectionError as e:
            print(f"Connection Error: {e}")
            print("Retrying in 10 seconds")
        DEBUG_RESPONSE = False
        if DEBUG_RESPONSE:
            print(f" |  | Full API GET URL: {MASTODON_HEADER} {MAST_SOURCE}")
        mastodon_follower_count = mastodon_json["followers_count"]
        mastodon_toot_count = mastodon_json["statuses_count"]
        # Mastodon 7-Segment Display
        blue.brightness = 0.8
        blue.fill(0)
        blue.print("toots")
        time.sleep(2)
        blue.fill(0)
        blue.print(mastodon_toot_count)
        time.sleep(2)
        blue.fill(0)
        blue.print("subs")
        time.sleep(2)
        blue.fill(0)
        blue.print(mastodon_follower_count)
        gc.collect()
        mastodon_response.close()

        # ------------- POST FOR TWITCH BEARER TOKEN -----------------
        if DEBUG:
            print(f"Full API GET URL: {TWITCH_0AUTH_TOKEN}")
        twitch_0auth_data = (
            "&client_id="
            + TWITCH_CID
            + "&client_secret="
            + TWITCH_CS
            + "&grant_type=client_credentials"
        )

        # POST REQUEST
        twitch_0auth_response = requests.post(
            url=TWITCH_0AUTH_TOKEN,
            data=twitch_0auth_data,
            headers=twitch_0auth_header,
        )
        try:
            twitch_0auth_json = twitch_0auth_response.json()
            twitch_access_token = twitch_0auth_json["access_token"]
        except ConnectionError as e:
            print(f"Connection Error: {e}")
            print("Retrying in 10 seconds")

        # STREAMER WARNING: your client secret will be viewable
        if DEBUG:
            print(f"JSON Dump: {twitch_0auth_json}")
            print(f"Header: {twitch_0auth_header}")
            print(f"Access Token: {twitch_access_token}")
        # Twitch 7-Segment Display
        yellow.brightness = 0.8
        yellow.fill(0)
        yellow.print("twitch")
        time.sleep(2)

        # -----------------------TWITCH GET DATA --------------------
        # Bearer token is refreshed every time script runs :)
        # Twitch sets token expiration to about 64 days
        # Helix is the name of the current Twitch API
        # Now that we have POST bearer token we can do a GET for data
        # -----------------------------------------------------------
        twitch_header = {
            "Authorization": "Bearer " + twitch_access_token + "",
            "Client-Id": "" + TWITCH_CID + "",
        }
        TWITCH_FOLLOWERS_SOURCE = (
            "https://api.twitch.tv/helix/channels"
            + "/followers?"
            + "broadcaster_id="
            + TWITCH_UID
        )
        
        # Twitch GET
        twitch_response = requests.get(
            url=TWITCH_FOLLOWERS_SOURCE, headers=twitch_header
        )
        try:
            twitch_json = twitch_response.json()
        except ConnectionError as e:
            print(f"Connection Error: {e}")
            print("Retrying in 10 seconds")
        if DEBUG:
            print(f" | Full API GET URL: {TWITCH_FOLLOWERS_SOURCE}")
            print(f" | Header: {twitch_header}")
            print(f" | JSON Full Response: {twitch_json}")
        # Error Responses
        if "status" in twitch_json:
            twitch_error_status = twitch_json["status"]
            print(f"❌ Status: {twitch_error_status}")
        if "error" in twitch_json:
            twitch_error = twitch_json["error"]
            print(f"❌ Error: {twitch_error}")
        if "message" in twitch_json:
            twitch_error_msg = twitch_json["message"]
            print(f"❌ Message: {twitch_error_msg}")
        # Key:Value Responses
        if "total" in twitch_json:
            twitch_followers = twitch_json["total"]
        # Twitch 7-Segment Display
        yellow.brightness = 0.8
        yellow.fill(0)
        yellow.print("subs")
        time.sleep(2)
        yellow.fill(0)
        yellow.print(twitch_followers)
        gc.collect()
        twitch_response.close()

        # Github
        try:
            github_response = requests.get(url=GITHUB_SOURCE, headers=GITHUB_HEADER)
            github_json = github_response.json()
        except ConnectionError as e:
            print("Connection Error:", e)
            print("Retrying in 10 seconds")
        if DEBUG:
            print("Full API GET URL: ", GITHUB_SOURCE)
            print(github_json)
        # Error Response
        if "message" in github_json:
            github_error_message = github_json["message"]
            print(f"❌ Error: {github_error_message}")
        else:
            github_followers = github_json["followers"]
            # Github 7-Segment Display
            green.brightness = 0.8
            green.fill(0)
            green.print("subs")
            time.sleep(2)
            green.fill(0)
            green.print(github_followers)
            gc.collect()
        github_response.close()
        
        # Discord Adafruit Shields.io
        try:
            shieldsio_response = requests.get(url=ADA_DISCORD_JSON)
            shieldsio_json = shieldsio_response.json()
        except ConnectionError as e:
            print(f"Connection Error: {e}")
            print("Retrying in 10 seconds")
        DEBUG_RESPONSE = False
        if DEBUG_RESPONSE:
            print(" |  | Full API GET URL: ", ADA_DISCORD_JSON)
            print(" |  | JSON Dump: ", shieldsio_json)
        ada_users = shieldsio_json["value"]
        ONLINE_STRING = " online"
        REPLACE_WITH_NOTHING = ""
        discord_users = ada_users.replace(ONLINE_STRING, REPLACE_WITH_NOTHING)
        # Discord 7-Segment Display
        white.fill(0)
        white.print("online")
        time.sleep(2)
        white.fill(0)
        white.print(discord_users)
        gc.collect()
        shieldsio_response.close()
        
        # STEAM
        with requests.get(STEAM_SOURCE) as steam_response:
            try:
                steam_json = steam_response.json()
            except ConnectionError as e:
                print("Connection Error:", e)
        DEBUG_STEAM = False
        if DEBUG_STEAM:
            print("Full API GET URL: ", STEAM_SOURCE)
            # STEAM full response is a baaaad idea but its here if your into bad ideas.
            # print(steam_json)  # uncomment at your microcontrollers peril
        game_count = steam_json["response"]["game_count"]
        # Mastodon 7-Segment Display
        green.brightness = 0.8
        time.sleep(2)
        green.fill(0)
        green.print("steam")
        time.sleep(2)
        green.fill(0)
        green.print("games")
        time.sleep(2)
        green.fill(0)
        green.print(game_count)
        time.sleep(2)
        gc.collect()
        steam_response.close()
        print("✂️ Disconnected from all API's")
        
    except (ValueError, RuntimeError) as e:
        print(f"Failed to get data: {e}")

    print("\nFinished!")
    print(f"Board Uptime: {time_calc(time.monotonic())}")
    print(f"Next Update: {time_calc(SLEEP_TIME)}")
    print("===============================")
    gc.collect()
    time.sleep(SLEEP_TIME)
