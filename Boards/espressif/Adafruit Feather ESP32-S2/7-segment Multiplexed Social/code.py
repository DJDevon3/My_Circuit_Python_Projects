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
from analogio import AnalogOut
from adafruit_ht16k33 import segments
import adafruit_tca9548a

# Get WiFi details, ensure these are setup in settings.toml
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

# Mastodon V1 API - Public access (no dev creds or app required)
# Visit https://docs.joinmastodon.org/client/public/ for API docs
# For finding your Mastodon numerical UserID
# Example: https://mastodon.YOURSERVER/api/v1/accounts/lookup?acct=YourUserName
MASTODON_SERVER = os.getenv("MASTODON_SERVER")  # Set server instance
MASTODON_USERID = os.getenv("MASTODON_USERID")  # Numerical UserID endpoints from


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


# I have a physical arcade button for board reset
Reset_LED = AnalogOut(board.A0)
Reset_LED.value = 65535

# Initialize & combine backpack addresses
red = segments.Seg7x4(tca[0], address=(0x74, 0x75))
red.fill(0)
red.brightness = 0.5
red.print("youtube")

blue = segments.Seg7x4(tca[7], address=(0x74, 0x75))
blue.fill(0)
blue.brightness = 0.5
blue.print("twitter")

green = segments.Seg7x4(tca[5], address=(0x74, 0x75))
green.fill(0)
green.brightness = 0.5
green.print("github")

yellow = segments.Seg7x4(tca[2], address=(0x74, 0x75))
yellow.fill(0)
yellow.brightness = 0.5
yellow.print("mastodon")

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

# TWITTER
# Used with any Twitter 0auth request. Twitter developer account bearer token required.
twitter_header = {"Authorization": "Bearer " + str(TWITTER_TOKEN)}
# Twitter UserID is a number.
# https://api.twitter.com/2/users/[ID]?user.fields=public_metrics,created_at,pinned_tweet_id&expansions=pinned_tweet_id&tweet.fields=created_at,public_metrics,source,context_annotations,entities
TW_SOURCE = ("https://api.twitter.com/2/users/"
             + TWITTER_UID
             + "?user.fields=public_metrics,"
             + "created_at,"
             + "pinned_tweet_id"
             + "&expansions=pinned_tweet_id"
             + "&tweet.fields=created_at,"
             + "public_metrics,"
             + "source,"
             + "context_annotations,"
             + "entities"
             )

# First we use Client ID & Client Secret to create a token with POST
# You must be logged into Twitch when you do this.
twitch_0auth_header = {"Content-Type": "application/x-www-form-urlencoded"}
TWITCH_0AUTH_TOKEN = "https://id.twitch.tv/oauth2/token"

GITHUB_HEADER = {"Authorization": " token " + GITHUB_TOKEN}
GITHUB_SOURCE = "https://api.github.com/users/" + GITHUB_UID

# Publicly available data no header required
MAST_SOURCE = (
    "https://"
    + MASTODON_SERVER
    + "/api/v1/accounts/"
    + MASTODON_USERID
    + "/statuses?limit=1"
)

# Originally attempted to use SVG. Found JSON exists with same filename.
# https://img.shields.io/discord/327254708534116352.svg
ADA_DISCORD_JSON = "https://img.shields.io/discord/327254708534116352.json"

while True:
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

    try:
        print(" | Attempting to GET YouTube JSON...")
        with requests.get(YOUTUBE_SOURCE) as youtube_response:
            try:
                youtube_json = youtube_response.json()
            except ConnectionError as e:
                print("Connection Error:", e)
                print("Retrying in 10 seconds")
            print(" | ✅ YouTube JSON!")

            if DEBUG:
                print(f" | Full API GET URL: {YOUTUBE_SOURCE}")
                print(f" | Full API Dump: {youtube_json}")
            # Key:Value RESPONSES
            if "pageInfo" in youtube_json:
                totalResults = youtube_json["pageInfo"]["totalResults"]
                print(f" |  | Matching Results: {totalResults}")
            if "items" in youtube_json:
                YT_request_kind = youtube_json["items"][0]["kind"]
                print(f" |  | Request Kind: {YT_request_kind}")

                YT_channel_id = youtube_json["items"][0]["id"]
                print(f" |  | Channel ID: {YT_channel_id}")

                YT_videoCount = youtube_json["items"][0]["statistics"]["videoCount"]
                print(f" |  | Videos: {YT_videoCount}")

                YT_viewCount = youtube_json["items"][0]["statistics"]["viewCount"]
                print(f" |  | Views: {YT_viewCount}")

                YT_subsCount = youtube_json["items"][0]["statistics"]["subscriberCount"]
                print(f" |  | Subscribers: {YT_subsCount}")
            if "kind" in youtube_json:
                YT_response_kind = youtube_json["kind"]
                print(f" |  | Response Kind: {YT_response_kind}")

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

        print("\nAttempting to GET TWITTER Stats!")
        print("===============================")
        with requests.get(url=TW_SOURCE, headers=twitter_header) as twitter_response:
            try:
                twitter_json = twitter_response.json()
            except ConnectionError as e:
                print("Connection Error:", e)
                print("Retrying in 10 seconds")
            twitter_json = twitter_json["data"]
            # Uncomment line below to print API URL you're sending to Twitter
            # print("Full API GET URL: ", TW_SOURCE)
            # print(twitter_json)
            twitter_userid = twitter_json["id"]
            print("User ID: ", twitter_userid)
            twitter_username = twitter_json["name"]
            print("Name: ", twitter_username)
            twitter_join_date = twitter_json["created_at"]
            print("Member Since: ", twitter_join_date)
            twitter_tweet_count = twitter_json["public_metrics"]["tweet_count"]
            print("Tweets: ", twitter_tweet_count)
            twitter_follower_count = twitter_json["public_metrics"]["followers_count"]
            print("Followers: ", twitter_follower_count)

            # Twitter 7-Segment Display
            blue.brightness = 0.8
            blue.fill(0)
            blue.print("tweets")
            time.sleep(2)
            blue.fill(0)
            blue.print(twitter_tweet_count)
            time.sleep(2)
            blue.fill(0)
            blue.print("subs")
            time.sleep(2)
            blue.fill(0)
            blue.print(twitter_follower_count)
            gc.collect()

        # ------------- POST FOR BEARER TOKEN -----------------
        print(" | Attempting Bearer Token Request!")
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
        print(" | 🔑 Token Authorized!")

        # STREAMER WARNING: your client secret will be viewable
        if DEBUG:
            print(f"JSON Dump: {twitch_0auth_json}")
            print(f"Header: {twitch_0auth_header}")
            print(f"Access Token: {twitch_access_token}")
            twitch_token_type = twitch_0auth_json["token_type"]
            print(f"Token Type: {twitch_token_type}")
        twitch_token_expiration = twitch_0auth_json["expires_in"]
        print(f" | Token Expires in: {time_calc(twitch_token_expiration)}")

        # Twitch 7-Segment Display
        yellow.brightness = 0.8
        yellow.fill(0)
        yellow.print("twitch")
        time.sleep(2)
        yellow.fill(0)
        yellow.print("token")
        time.sleep(2)
        yellow.fill(0)
        yellow.print(twitch_token_type)
        gc.collect()

        # ----------------------------- GET DATA --------------------
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
        print(" | Attempting to GET Twitch JSON!")
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
        if "status" in twitch_json:
            twitch_error_status = twitch_json["status"]
            print(f"❌ Status: {twitch_error_status}")
        if "error" in twitch_json:
            twitch_error = twitch_json["error"]
            print(f"❌ Error: {twitch_error}")
        if "message" in twitch_json:
            twitch_error_msg = twitch_json["message"]
            print(f"❌ Message: {twitch_error_msg}")
        if "total" in twitch_json:
            print(" | ✅ Twitch JSON!")
            twitch_followers = twitch_json["total"]
            print(f" |  | Followers: {twitch_followers}")
        # Twitch 7-Segment Display
        yellow.brightness = 0.8
        yellow.fill(0)
        yellow.print("subs")
        time.sleep(2)
        yellow.fill(0)
        yellow.print(twitch_followers)
        gc.collect()

        twitch_response.close()
        print("✂️ Disconnected from Twitch API")

        print(" | Attempting to GET Github JSON!")
        try:
            github_response = requests.get(url=GITHUB_SOURCE, headers=GITHUB_HEADER)
            github_json = github_response.json()
        except ConnectionError as e:
            print("Connection Error:", e)
            print("Retrying in 10 seconds")
        print(" | ✅ Github JSON!")

        github_joined = github_json["created_at"]
        print(" |  | Join Date: ", github_joined)

        github_id = github_json["id"]
        print(" |  | UserID: ", github_id)

        github_location = github_json["location"]
        print(" |  | Location: ", github_location)

        github_name = github_json["name"]
        print(" |  | Username: ", github_name)

        github_repos = github_json["public_repos"]
        print(" |  | Respositores: ", github_repos)

        github_followers = github_json["followers"]
        print(" |  | Followers: ", github_followers)
        github_bio = github_json["bio"]
        print(" |  | Bio: ", github_bio)

        if DEBUG:
            print("Full API GET URL: ", GITHUB_SOURCE)
            print(github_json)
        # Github 7-Segment Display
        green.brightness = 0.8
        green.fill(0)
        green.print("subs")
        time.sleep(2)
        green.fill(0)
        green.print(github_followers)
        gc.collect()

        github_response.close()
        print("✂️ Disconnected from Github API")

        print(" | Attempting to GET MASTODON JSON!")
        # Set debug to True for full JSON response.
        # WARNING: may include visible credentials
        # MICROCONTROLLER WARNING: might crash by returning too much data
        DEBUG_RESPONSE = False

        try:
            mastodon_response = requests.get(url=MAST_SOURCE)
            mastodon_json = mastodon_response.json()
        except ConnectionError as e:
            print(f"Connection Error: {e}")
            print("Retrying in 10 seconds")
        mastodon_json = mastodon_json[0]
        print(" | ✅ Mastodon JSON!")

        if DEBUG_RESPONSE:
            print(" |  | Full API GET URL: ", MAST_SOURCE)
            mastodon_userid = mastodon_json["account"]["id"]
            print(f" |  | User ID: {mastodon_userid}")
            print(mastodon_json)
        mastodon_name = mastodon_json["account"]["display_name"]
        print(f" |  | Name: {mastodon_name}")
        mastodon_join_date = mastodon_json["account"]["created_at"]
        print(f" |  | Member Since: {mastodon_join_date}")
        mastodon_follower_count = mastodon_json["account"]["followers_count"]
        print(f" |  | Followers: {mastodon_follower_count}")
        mastodon_following_count = mastodon_json["account"]["following_count"]
        print(f" |  | Following: {mastodon_following_count}")
        mastodon_toot_count = mastodon_json["account"]["statuses_count"]
        print(f" |  | Toots: {mastodon_toot_count}")
        mastodon_last_toot = mastodon_json["account"]["last_status_at"]
        print(f" |  | Last Toot: {mastodon_last_toot}")
        mastodon_bio = mastodon_json["account"]["note"]
        print(f" |  | Bio: {mastodon_bio[3:-4]}")  # removes html "<p> & </p>"

        # Mastodon 7-Segment Display
        green.brightness = 0.8
        time.sleep(2)
        green.fill(0)
        green.print("mastodon")
        time.sleep(2)
        green.fill(0)
        green.print("toots")
        time.sleep(2)
        green.fill(0)
        green.print(mastodon_toot_count)
        time.sleep(2)
        green.fill(0)
        green.print("subs")
        time.sleep(2)
        green.fill(0)
        green.print(mastodon_follower_count)
        gc.collect()

        mastodon_response.close()
        print("✂️ Disconnected from Mastodon API")

        print(" | Attempting to GET Adafruit Discord JSON!")
        # Set debug to True for full JSON response.
        DEBUG_RESPONSE = True

        try:
            shieldsio_response = requests.get(url=ADA_DISCORD_JSON)
            shieldsio_json = shieldsio_response.json()
        except ConnectionError as e:
            print(f"Connection Error: {e}")
            print("Retrying in 10 seconds")
        print(" | ✅ Adafruit Discord JSON!")

        if DEBUG_RESPONSE:
            print(" |  | Full API GET URL: ", ADA_DISCORD_JSON)
            print(" |  | JSON Dump: ", shieldsio_json)
        ada_users = shieldsio_json["value"]
        ONLINE_STRING = " online"
        REPLACE_WITH_NOTHING = ""
        discord_users = ada_users.replace(ONLINE_STRING, REPLACE_WITH_NOTHING)
        print(f" |  | Active Online Users: {discord_users}")

        # Discord 7-Segment Display
        white.fill(0)
        white.print("online")
        time.sleep(2)
        white.fill(0)
        white.print(discord_users)
        gc.collect()

        shieldsio_response.close()
        print("✂️ Disconnected from Discord Shields.io API")
    except (ValueError, RuntimeError) as e:
        print(f"Failed to get data: {e}")

    print("\nFinished!")
    print(f"Board Uptime: {time_calc(time.monotonic())}")
    print(f"Next Update: {time_calc(SLEEP_TIME)}")
    print("===============================")
    gc.collect()
    time.sleep(SLEEP_TIME)
