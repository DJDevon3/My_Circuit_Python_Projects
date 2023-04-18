# SPDX-FileCopyrightText: 2022 DJDevon3
# SPDX-License-Identifier: MIT
# Coded for Circuit Python 8.0
"""Adafruit Feather ESP32-S2 10x 7-segment Social Media Counter"""
#  pylint: disable=line-too-long
import gc
import time
import board
import terminalio
import digitalio
import busio
import ssl
import wifi
import json
import socketpool
import adafruit_requests
from analogio import AnalogOut
from adafruit_ht16k33 import segments
import adafruit_tca9548a
# Both the PCA9548 & TCA9548 use the TCA library

# These are public, don't belong in secrets, must be filled in.
Twitch_UserID = "0000000"
Mastodon_UserID = "000000000000000000"

# Initialize WiFi Pool (There can be only one pool)
pool = socketpool.SocketPool(wifi.radio)

# Initialize I2C bus for 7-Segment Backpacks
i2c = board.I2C()
# Initalize a 2nd I2C bus for the non-stemma (not on multiplexer) backpacks
i2c2 = busio.I2C(board.D6, board.D5)
# Recommend running "Simple Test Example Code" to get TCA addresses
# https://learn.adafruit.com/adafruit-pca9548-8-channel-stemma-qt-qwiic-i2c-multiplexer/circuitpython-python

# Initialize TCA9548A Multiplexor bus object
tca = adafruit_tca9548a.TCA9548A(i2c)

# Time between API refreshes
# 900 = 15 mins, 1800 = 30 mins, 3600 = 1 hour
sleep_time = 900

# I have a physical arcade button for board reset
Reset_LED = AnalogOut(board.A0)
Reset_LED.value = 65535

# Initialize & combine backpack addresses
red = segments.Seg7x4(tca[0], address=(0x74,0x75))
red.fill(0)
red.brightness = 0.5
red.print("youtube")

blue = segments.Seg7x4(tca[7], address=(0x74,0x75))
blue.fill(0)
blue.brightness = 0.5
blue.print("twitter")

green = segments.Seg7x4(tca[5], address=(0x74,0x75))
green.fill(0)
green.brightness = 0.5
green.print("github")

yellow = segments.Seg7x4(tca[2], address=(0x74,0x75))
yellow.fill(0)
yellow.brightness = 0.5
yellow.print("mastodon")

white = segments.Seg7x4(i2c2, address=(0x71, 0x72))
white.fill(0)
white.brightness = 0.5
white.print("discord")

try:
    from secrets import secrets
except ImportError:
    print("Secrets File Import Error")
    raise

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
    elif 86400 <= input_time < 432000:
        sleep_int = input_time / 60 / 60 / 24
        time_output = f"{sleep_int:.1f} days"
    else:  # if > 5 days convert float to int & display whole days
        sleep_int = input_time / 60 / 60 / 24
        time_output = f"{sleep_int:.0f} days"
    return time_output

print("Calc Time: ", time_calc(900))  # time conversion testing

# https://youtube.googleapis.com/youtube/v3/channels?part=statistics&forUsername=[YOUR_USERNAME]&key=[YOUR_API_KEY]
YT_SOURCE = (
    "https://youtube.googleapis.com/youtube/v3/channels?"
    + "part=statistics"
    + "&forUsername="
    + secrets["YT_username"]
    + "&key="
    + secrets["YT_token"]
)

# TWITTER
# Used with any Twitter 0auth request. Twitter developer account bearer token required.
twitter_header = {'Authorization': 'Bearer ' + secrets["TW_bearer_token"]}
# Twitter UserID is a number.
# https://api.twitter.com/2/users/[ID]?user.fields=public_metrics,created_at,pinned_tweet_id&expansions=pinned_tweet_id&tweet.fields=created_at,public_metrics,source,context_annotations,entities
TW_SOURCE = (
    "https://api.twitter.com/2/users/"
    + secrets["TW_userid"]
    + "?user.fields=public_metrics,created_at,pinned_tweet_id&expansions=pinned_tweet_id&tweet.fields=created_at,public_metrics,source,context_annotations,entities"
)

# First we use Client ID & Client Secret to create a token with POST
# You must be logged into Twitch when you do this.
twitch_0auth_header = {'Content-Type': 'application/x-www-form-urlencoded'}
TWITCH_0AUTH_TOKEN = (
    "https://id.twitch.tv/oauth2/token"
)

github_header = {'Authorization':' token ' + secrets["Github_token"]}
GH_SOURCE = (
    "https://api.github.com/users/"
    + secrets["Github_username"]
)

# Publicly available data no header required
MAST_SOURCE = (
    "https://mastodon.cloud/api/v1/accounts/"
    + Mastodon_UserID
    + "/statuses?limit=1"
)

# https://img.shields.io/discord/327254708534116352.svg
ADA_DISCORD_SVG = (
    "https://img.shields.io/discord/327254708534116352.json"
)

discord_header = {'Authorization':'' + secrets['Discord_Authorization']}
ADA_DISCORD_SOURCE = (
    "https://discord.com/api/v10/guilds/"
    + secrets['Discord_Adafruit_Channel']
    + "/preview"
)

# Connect to Wi-Fi
print("\n===============================")
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
print("Connected!\n")

while True:
    try:
        gc.collect()
        print("Attempting to GET YouTube Stats!")  # ----------------------------------
        # Uncomment line below to print API URL with all data filled in
        # print("Full API GET URL: ", YT_SOURCE)
        print("===============================")
        try:
            response = requests.get(YT_SOURCE).json()
        except ConnectionError as e:
            print("Connection Error:", e)
            print("Retrying in 10 seconds")

        # Print Full JSON to Serial
        full_yt_json_response = False  # Change to true to see full response
        if full_yt_json_response:
            dump_object = json.dumps(response)
            print("JSON Dump: ", dump_object)

        # Print Debugging to Serial
        yt_debug = True  # Set to True to print Serial data
        if yt_debug:
            print("Matching Results: ", response['pageInfo']['totalResults'])

            YT_response_channel_kind = response['kind']
            print("Response Kind: ", YT_response_channel_kind)

            YT_response_channel_kind = response['items'][0]['kind']
            print("Request Kind: ", YT_response_channel_kind)

            YT_response_channel_id = response['items'][0]['id']
            print("Channel ID: ", YT_response_channel_id)

            YT_response_channel_videoCount = response['items'][0]['statistics']['videoCount']
            print("Videos: ", YT_response_channel_videoCount)

            YT_response_channel_viewCount = response['items'][0]['statistics']['viewCount']
            print("Views: ", YT_response_channel_viewCount)

            YT_response_channel_subscriberCount = response['items'][0]['statistics']['subscriberCount']
            print("Subscribers: ", YT_response_channel_subscriberCount)
            print("Monotonic: ", time.monotonic())

        # YouTube 7-Segment Display
        red.brightness = 0.8
        red.fill(0)
        red.print("eyes")
        time.sleep(2)
        red.fill(0)
        red.print(YT_response_channel_viewCount)
        time.sleep(2)
        red.fill(0)
        red.print("subs")
        time.sleep(2)
        red.fill(0)
        red.print(YT_response_channel_subscriberCount)
        # Marquee scrolling, 2nd parameter speed in seconds
        # red.marquee(YT_response_channel_subscriberCount, 0.9)

        print("\nAttempting to GET TWITTER Stats!")  # --------------------------------
        print("===============================")
        twitter_response = requests.get(url=TW_SOURCE, headers=twitter_header)
        try:
            twitter_json = twitter_response.json()
        except ConnectionError as e:
            print("Connection Error:", e)
            print("Retrying in 10 seconds")
        twitter_json = twitter_json['data']
        # Uncomment line below to print API URL you're sending to Twitter
        # print("Full API GET URL: ", TW_SOURCE)
        # print(twitter_json)
        twitter_userid = twitter_json['id']
        print("User ID: ", twitter_userid)
        twitter_username = twitter_json['name']
        print("Name: ", twitter_username)
        twitter_join_date = twitter_json['created_at']
        print("Member Since: ", twitter_join_date)
        twitter_tweet_count = twitter_json['public_metrics']['tweet_count']
        print("Tweets: ", twitter_tweet_count)
        twitter_follower_count = twitter_json['public_metrics']['followers_count']
        print("Followers: ", twitter_follower_count)
        print("Monotonic: ", time.monotonic())

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
        print("\nAttempting to GENERATE Twitch Bearer Token!")  # ---------------------
        print("===============================")
        twitch_0auth_data = ("&client_id="
                             + secrets["Twitch_ClientID"]
                             + "&client_secret="
                             + secrets["Twitch_Client_Secret"]
                             + "&grant_type=client_credentials"
                             )

        twitch_0auth_response = requests.post(url=TWITCH_0AUTH_TOKEN, data=twitch_0auth_data, headers=twitch_0auth_header)
        try:
            twitch_0auth_json = twitch_0auth_response.json()
        except ConnectionError as e:
            print("Connection Error:", e)
            print("Retrying in 10 seconds")
        # Uncomment line below to print API URL you're sending to Twitter
        # print("Full API GET URL: ", TWITCH_0AUTH_TOKEN)
        # print("JSON Dump: ", twitch_0auth_json)
        twitch_access_token = twitch_0auth_json['access_token']
        # print("Access Token: ", twitch_access_token)
        twitch_token_expiration = twitch_0auth_json['expires_in']
        print("Token Expires in: ", time_calc(twitch_token_expiration))

        twitch_token_type = twitch_0auth_json['token_type']
        print("Token Type: ", twitch_token_type)
        print("Monotonic: ", time.monotonic())

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

        # Helix is the name of the current Twitch API
        # Twitch API versioning uses names not numbers
        # Recommend for finding your User ID
        # https://www.streamweasels.com/tools/convert-twitch-username-to-user-id/
        twitch_header = {
        'Authorization': 'Bearer '+twitch_access_token+'',
        'Client-Id': ''+ secrets["Twitch_ClientID"] +''
        }
        TWITCH_FOLLOWERS_SOURCE = (
            "https://api.twitch.tv/helix/users"
            + "/follows?"
            + "to_id="
            + Twitch_UserID
            + "&first=1"
        )
        print("\nAttempting to GET TWITCH Stats!")  # ---------------------------------
        print("===============================")
        twitch_followers_response = requests.get(url=TWITCH_FOLLOWERS_SOURCE, headers=twitch_header)
        try:
            twitch_followers_json = twitch_followers_response.json()
        except ConnectionError as e:
            print("Connection Error:", e)
            print("Retrying in 10 seconds")
        # Uncomment line below to print API URL you're sending to Twitter
        # print("Full API GET URL: ", TWITCH_FOLLOWERS_SOURCE)
        # print("Header: ", twitch_header)
        # print("JSON Full Response: ", twitch_followers_json)
        twitch_username = twitch_followers_json['data'][0]['to_name']
        print("Username: ", twitch_username)
        twitch_followers = twitch_followers_json['total']
        print("Followers: ", twitch_followers)

        # Twitch 7-Segment Display
        yellow.brightness = 0.8
        yellow.fill(0)
        yellow.print("subs")
        time.sleep(2)
        yellow.fill(0)
        yellow.print(twitch_followers)
        print("Monotonic: ", time.monotonic())

        print("\nAttempting to GET GITHUB Stats!")  # ---------------------------------
        # Uncomment line below to print API URL with all data filled in
        # print("Full API GET URL: ", GH_SOURCE)
        print("===============================")
        github_response = requests.get(url=GH_SOURCE, headers=github_header).json()

        # Print Full JSON to Serial
        full_github_json_response = False  # Change to true to see full response
        if full_github_json_response:
            dump_object = json.dumps(github_response)
            print("JSON Dump: ", dump_object)

        # Print Debugging to Serial
        github_debug = True  # Set to True to print Serial data
        if github_debug:
            github_id = github_response['id']
            print("UserID: ", github_id)
            github_username = github_response['name']
            print("Username: ", github_username)
            github_followers = github_response['followers']
            print("Followers: ", github_followers)
        print("Monotonic: ", time.monotonic())

        # Github 7-Segment Display
        green.brightness = 0.8
        green.fill(0)
        green.print("subs")
        time.sleep(2)
        green.fill(0)
        green.print(github_followers)

        print("\nAttempting to GET MASTODON Stats!")  # -------------------------------
        print("===============================")
        mastodon_response = requests.get(url=MAST_SOURCE)
        try:
            mastodon_json = mastodon_response.json()
        except ConnectionError as e:
            print("Connection Error:", e)
            print("Retrying in 10 seconds")
        mastodon_json = mastodon_json[0]
        # Uncomment line below to print API URL you're sending to Mastodon
        # print("Full API GET URL: ", MAST_SOURCE)
        # print(mastodon_json)
        mastodon_userid = mastodon_json['account']['id']
        print("User ID: ", mastodon_userid)
        mastodon_username = mastodon_json['account']['display_name']
        print("Name: ", mastodon_username)
        mastodon_join_date = mastodon_json['account']['created_at']
        print("Member Since: ", mastodon_join_date)
        mastodon_toot_count = mastodon_json['account']['statuses_count']
        print("Toots: ", mastodon_toot_count)
        mastodon_follower_count = mastodon_json['account']['followers_count']
        print("Followers: ", mastodon_follower_count)
        print("Monotonic: ", time.monotonic())

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

        print("\nAttempting to GET DISCORD PREVIEW!")  # ------------------------------
        # Uncomment line below to print API URL with all data filled in
        # print("Full API GET URL: ", ADA_DISCORD_SOURCE)
        print("===============================")
        try:
            ada_discord_response = requests.get(url=ADA_DISCORD_SOURCE, headers=discord_header).json()
        except ConnectionError as e:
            print("Connection Error:", e)
            print("Retrying in 10 seconds")

        # Print Full JSON to Serial
        full_ada_discord_json_response = False  # Change to true to see full response
        if full_ada_discord_json_response:
            ada_discord_dump_object = json.dumps(ada_discord_response)
            print("JSON Dump: ", ada_discord_dump_object)

        # Print Debugging to Serial
        ada_discord_debug = True  # Set to True to print Serial data
        if ada_discord_debug:
            ada_dc_members = ada_discord_response['approximate_member_count']
            print("Members: ", ada_dc_members)
            ada_dc_prescence = ada_discord_response['approximate_presence_count']
            print("Online: ", ada_dc_prescence)
        print("Monotonic: ", time.monotonic())

        # Discord 7-Segment Display
        white.fill(0)
        white.print("subs")
        time.sleep(2)
        white.fill(0)
        white.print(ada_dc_members)
        time.sleep(2)
        white.fill(0)
        white.print("online")
        time.sleep(2)
        white.fill(0)
        white.print(ada_dc_prescence)

        print("\nFinished!")
        print("Next Update in: ", time_calc(sleep_time))
        print("===============================")
        gc.collect()
    # pylint: disable=broad-except
    except (ValueError, RuntimeError) as e:
        print("Failed to get data, retrying\n", e)
        time.sleep(60)
        continue
    # response = None
    time.sleep(sleep_time)
