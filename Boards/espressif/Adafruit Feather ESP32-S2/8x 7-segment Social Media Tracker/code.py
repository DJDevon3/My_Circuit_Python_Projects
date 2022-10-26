# SPDX-FileCopyrightText: 2022 DJDevon3
# SPDX-License-Identifier: MIT
# Coded for Circuit Python 8.0
"""DJDevon3 Adafruit Feather ESP32-S2 Social Media Counter"""
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
import re
from analogio import AnalogOut
from adafruit_ht16k33 import segments

# Initialize WiFi Pool (This should always be near the top of a script!)
# anecdata: you only want to do this once early in your code pool.
# Highlander voice: "There can be only one pool"
pool = socketpool.SocketPool(wifi.radio)

# Initialize 7-Segment Backpack
i2c = busio.I2C(board.SCL, board.SDA)
# Recommend running "CircuitPython I2C Device Address Scan" to get addresses
# https://learn.adafruit.com/adafruit-esp32-s2-feather/i2c-external-sensor

# Time between API refreshes
# 900 = 15 mins, 1800 = 30 mins, 3600 = 1 hour
sleep_time = 900

# I have a physical arcade button for board reset
Reset_LED = AnalogOut(board.A0)
Reset_LED.value = 65535

# Initialize & combine backpack addresses
red = segments.Seg7x4(i2c, address=(0x75, 0x70))
red.fill(0)
red.brightness = 0.5
red.print("youtube")  # Default test fill

blue = segments.Seg7x4(i2c, address=(0x74, 0x73))
blue.fill(0)
blue.brightness = 0.5
blue.print("twitter")

green = segments.Seg7x4(i2c, address=(0x76, 0x77))
green.fill(0)
green.brightness = 0.5
green.print("github")

white = segments.Seg7x4(i2c, address=(0x71, 0x72))
white.fill(0)
white.brightness = 0.5
white.print("discord")

try:
    from secrets import secrets
except ImportError:
    print("Secrets File Import Error")
    raise

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

# https://youtube.googleapis.com/youtube/v3/channels?part=statistics&forUsername=[YOUR_USERNAME]&key=[YOUR_API_KEY]
YT_SOURCE = (
    "https://youtube.googleapis.com/youtube/v3/channels?"
    + "part=statistics"
    + "&forUsername="
    + secrets["YT_username"]
    + "&key="
    + secrets["YT_token"]
)

# Used with any Twitter 0auth request. Twitter developer account bearer token required.
twitter_header = {'Authorization': 'Bearer ' + secrets["TW_bearer_token"]}
# Twitter UserID is a number.
# https://api.twitter.com/2/users/[ID]?user.fields=public_metrics,created_at,pinned_tweet_id&expansions=pinned_tweet_id&tweet.fields=created_at,public_metrics,source,context_annotations,entities
TW_SOURCE = (
    "https://api.twitter.com/2/users/"
    + secrets["TW_userid"]
    + "?user.fields=public_metrics,created_at,pinned_tweet_id&expansions=pinned_tweet_id&tweet.fields=created_at,public_metrics,source,context_annotations,entities"
)

github_header = {'Authorization':' token ' + secrets["Github_token"]}
GH_SOURCE = (
    "https://api.github.com/users/"
    + secrets["Github_username"]
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
        print("Attempting to GET YouTube Stats!")  # ------------------------------------------------
        # Uncomment line below to print API URL with all data filled in
        # print("Full API GET URL: ", YT_SOURCE)
        print("===============================")
        try:
            response = requests.get(YT_SOURCE).json()
        except ConnectionError as e:
            print("Connection Error:", e)
            print("Retrying in 10 seconds")
            
        # Print Full JSON to Serial
        full_yt_json_response = False # Change to true to see full response
        if full_yt_json_response:
            dump_object = json.dumps(response)
            print("JSON Dump: ", dump_object)
            
        # Print Debugging to Serial
        yt_debug = True # Set to True to print Serial data
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
        
        print("\nAttempting to GET TWITTER Stats!")  # ------------------------------------------------
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
        
        print("\nAttempting to GET GITHUB Stats!")  # ------------------------------------------------
        # Uncomment line below to print API URL with all data filled in
        print("Full API GET URL: ", GH_SOURCE)
        print("===============================")
        github_response = requests.get(url=GH_SOURCE, headers=github_header).json()
        
        # Print Full JSON to Serial
        full_github_json_response = False # Change to true to see full response
        if full_github_json_response:
            dump_object = json.dumps(github_response)
            print("JSON Dump: ", dump_object)
            
        # Print Debugging to Serial
        github_debug = True # Set to True to print Serial data
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
        
        print("\nAttempting to GET DISCORD SVG!")  # ------------------------------------------------
        # Uncomment line below to print API URL with all data filled in
        # print("Full API GET URL: ", ADA_DISCORD_SVG)
        print("===============================")
        try:
            ada_SVG_response = requests.get(ADA_DISCORD_SVG).json()
        except ConnectionError as e:
            print("Connection Error:", e)
            print("Retrying in 10 seconds")
            
        # Print Full JSON to Serial
        full_ada_SVG_json_response = False # Change to true to see full response
        if full_ada_SVG_json_response:
            ada_SVG_dump_object = json.dumps(ada_SVG_response)
            print("JSON Dump: ", ada_SVG_dump_object)
            
        # Print Debugging to Serial
        ada_SVG_debug = True # Set to True to print Serial data
        if ada_SVG_debug:
            ada_SVG_users = ada_SVG_response['value']
            print("SVG Value: ", ada_SVG_users)
            regex = " online"
            replace_with_nothing = ""
            regex_users = re.sub(regex, replace_with_nothing, ada_SVG_users)
            print("Regex Value: ", regex_users)
        print("Monotonic: ", time.monotonic())
        
        # Discord SVG 7-Segment Display
        white.brightness = 0.8
        white.fill(0)
        white.print("online")
        time.sleep(2)
        white.fill(0)
        white.print(regex_users)
        
        print("\nAttempting to GET DISCORD PREVIEW!")  # ------------------------------------------------
        # Uncomment line below to print API URL with all data filled in
        print("Full API GET URL: ", ADA_DISCORD_SOURCE)
        print("===============================")
        try:
            ada_discord_response = requests.get(url=ADA_DISCORD_SOURCE, headers=discord_header).json()
        except ConnectionError as e:
            print("Connection Error:", e)
            print("Retrying in 10 seconds")
            
        # Print Full JSON to Serial
        full_ada_discord_json_response = False # Change to true to see full response
        if full_ada_discord_json_response:
            ada_discord_dump_object = json.dumps(ada_discord_response)
            print("JSON Dump: ", ada_discord_dump_object)
            
        # Print Debugging to Serial
        ada_discord_debug = True # Set to True to print Serial data
        if ada_discord_debug:
            ada_discord_all_members = ada_discord_response['approximate_member_count']
            print("Members: ", ada_discord_all_members)
            ada_discord_all_members_online = ada_discord_response['approximate_presence_count']
            print("Online: ", ada_discord_all_members_online)
        print("Monotonic: ", time.monotonic())
        
        # Discord 7-Segment Display
        white.fill(0)
        white.print("total users")
        time.sleep(2)
        white.fill(0)
        white.print(ada_discord_all_members)
        time.sleep(2)
        white.fill(0)
        white.print("online")
        time.sleep(2)
        white.fill(0)
        white.print(ada_discord_all_members_online)
        
        print("\nFinished!")
        print("Next Update in %s %s" % (int(sleep_int), sleep_time_conversion))
        print("===============================")
        gc.collect()
    # pylint: disable=broad-except
    except (ValueError, RuntimeError) as e:
        print("Failed to get data, retrying\n", e)
        time.sleep(60)
        continue
    # response = None
    time.sleep(sleep_time)
