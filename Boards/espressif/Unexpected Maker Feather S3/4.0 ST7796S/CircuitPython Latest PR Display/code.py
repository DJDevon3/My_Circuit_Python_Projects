# SPDX-FileCopyrightText: 2024 DJDevon3
# SPDX-License-Identifier: MIT
# Coded for Circuit Python 9.x
"""Github API Latest Circuit Python PR's Example"""

import os
import time

import adafruit_connection_manager
import board
import displayio
import fourwire
import terminalio
import wifi

from adafruit_bitmap_font import bitmap_font
import adafruit_requests
from adafruit_display_text import label, wrap_text_to_pixels
from circuitpython_st7796s import ST7796S

spi = board.SPI()
tft_cs = board.D9
tft_dc = board.D10
tft_rst = board.D17

# 3.5" ST7796S Display
DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 320
DW = DISPLAY_WIDTH
DH = DISPLAY_HEIGHT

displayio.release_displays()
display_bus = fourwire.FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_rst)
display = ST7796S(display_bus, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, rotation=180)

# Github developer token required.
username = os.getenv("GITHUB_USERNAME")
token = os.getenv("GITHUB_TOKEN")
repository = "adafruit/circuitpython"

# Get WiFi details, ensure these are setup in settings.toml
ssid = os.getenv("CIRCUITPY_WIFI_SSID")
password = os.getenv("CIRCUITPY_WIFI_PASSWORD")

# API Polling Rate
# 900 = 15 mins, 1800 = 30 mins, 3600 = 1 hour
SLEEP_TIME = 900

# Set debug to True for full JSON response.
# WARNING: may include visible credentials
DEBUG = False

# Initalize Wifi, Socket Pool, Request Session
pool = adafruit_connection_manager.get_radio_socketpool(wifi.radio)
ssl_context = adafruit_connection_manager.get_radio_ssl_context(wifi.radio)
requests = adafruit_requests.Session(pool, ssl_context)
GITHUB_HEADER = {"Accept: application/vnd.github.raw+json \ Authorization": " token " + token}
GITHUB_SOURCE = f"https://api.github.com/repos/{repository}/pulls"

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

Arial12 = bitmap_font.load_font("/fonts/Arial-12.bdf")

# Label Customizations
pr_key_label = label.Label(Arial12)
pr_key_label.anchor_point = (0.0, 0.0)
pr_key_label.anchored_position = (5, 10)
pr_key_label.scale = (1)
pr_key_label.color = TEXT_WHITE

pr_value_label = label.Label(Arial12)
pr_value_label.anchor_point = (0.0, 0.0)
pr_value_label.anchored_position = (110, 10)
pr_value_label.scale = (1)
pr_value_label.color = TEXT_LIGHTBLUE

author_key_label = label.Label(Arial12)
author_key_label.anchor_point = (0.0, 0.0)
author_key_label.anchored_position = (5, 40)
author_key_label.scale = (1)
author_key_label.color = TEXT_WHITE

author_value_label = label.Label(Arial12)
author_value_label.anchor_point = (0.0, 0.0)
author_value_label.anchored_position = (65, 40)
author_value_label.scale = (1)
author_value_label.color = TEXT_LIGHTBLUE

title_value_label = label.Label(terminalio.FONT)
title_value_label.anchor_point = (0.0, 0.0)
title_value_label.anchored_position = (5, 60)
title_value_label.scale = (1)
title_value_label.color = TEXT_LIGHTBLUE

desc_key_label = label.Label(Arial12)
desc_key_label.anchor_point = (0.0, 0.0)
desc_key_label.anchored_position = (5, 130)
desc_key_label.scale = (1)
desc_key_label.color = TEXT_WHITE

desc_value_label = label.Label(terminalio.FONT)
desc_value_label.anchor_point = (0.0, 0.0)
desc_value_label.anchored_position = (5, 150)
desc_value_label.scale = (1)
desc_value_label.color = TEXT_LIGHTBLUE

# Create Display Groups
text_group = displayio.Group()
text_group.append(pr_key_label)
text_group.append(pr_value_label)
text_group.append(author_key_label)
text_group.append(author_value_label)
text_group.append(title_value_label)
text_group.append(desc_key_label)
text_group.append(desc_value_label)
display.root_group = text_group

# Assigning wrap_text_to_pixels to wordwrap
wordwrap = wrap_text_to_pixels
    
def truncate_text_to_lines(text, max_chars_per_line, max_lines):
    lines = text.split('\r\n')
    truncated_lines = []
    total_chars = 0
    total_lines = 0
    
    for line in lines:
        if total_lines >= max_lines:
            break
        
        # Subtract 2 characters for the newline characters at the end of each line
        if len(line) == 0:
            # Treat consecutive newlines as blank lines with 78 characters
            if truncated_lines and truncated_lines[-1] != "":
                total_chars += 78
                total_lines += 1
                truncated_lines.append(line)
        elif len(line) <= max_chars_per_line:
            truncated_lines.append(line)
            total_chars += len(line)
            total_chars -= 2
            total_lines += 1
        else:
            # If the line exceeds max_chars_per_line, truncate it
            truncated_lines.append(line[:max_chars_per_line] + '...')
            total_chars += max_chars_per_line
            total_chars -= 2
            total_lines += 1
                
    # Add any newlines as 78 characters to the total_chars count
    total_chars += text.count('\r\n\r\n') * 78
    
    # Adjust total_lines for consecutive newlines
    total_lines += text.count('\r\n\r\n')
    
    # Remove blank lines from the truncated text
    truncated_text = '\r\n'.join(line for line in truncated_lines if line.strip())
    
    return truncated_text, min(total_lines, max_lines), total_chars
    
def time_calc(input_time):
    """Converts seconds to minutes/hours/days"""
    if input_time < 60:
        return f"{input_time:.0f} seconds"
    if input_time < 3600:
        return f"{input_time / 60:.0f} minutes"
    if input_time < 86400:
        return f"{input_time / 60 / 60:.0f} hours"
    return f"{input_time / 60 / 60 / 24:.1f} days"

def print_http_status(code, description):
    """Returns HTTP status code and description"""
    if "100" <= code <= "103":
        print(f" | ⚠️ Server Code: {code} - {description}")
    elif "200" == code:
        print(f" | 🆗 Server Code: {code} - {description}")
    elif "201" <= code <= "299":
        print(f" | ⚠️ Server Code: {code} - {description}")
    elif "300" <= code <= "600":
        print(f" | ❌ Server Code: {code} - {description}")
    else:
        print(f" | Unknown Response Status: {code} - {description}")
        
github_json = {}

while True:
    now = time.monotonic()
    # Connect to Wi-Fi
    print("\nConnecting to WiFi...")
    while not wifi.radio.ipv4_address:
        try:
            wifi.radio.connect(ssid, password)
        except ConnectionError as e:
            print("❌ Connection Error:", e)
            print("Retrying in 10 seconds")
    print("✅ Wifi!")

    try:
        print(" | Attempting to GET Github JSON!")
        try:
            github_response = requests.get(url=GITHUB_SOURCE, headers=GITHUB_HEADER)
            github_json = github_response.json()
        except ConnectionError as e:
            print("Connection Error:", e)
        print(" | ✅ Github JSON")
        
        STATUS_CODE = str(github_response.status_code)
        STATUS_DESCRIPTION = str(github_response.status_code)
        print_http_status(STATUS_CODE, STATUS_DESCRIPTION)
        github_response.close()
        print("✂️ Disconnected Github API")

        print("\nFinished!")
        print(f"Board Uptime: {time_calc(time.monotonic())}")
        print(f"Next Update: {time_calc(SLEEP_TIME)}")
        print("===============================")
    except (ValueError, RuntimeError) as e:
        print(f"Failed to get data, retrying\n {e}")
        time.sleep(60)
        break
        
    if time.monotonic() - now <= SLEEP_TIME:
        for i in range(10):
            # Get the latest submission
            submission = github_json[i]
            print(f"Index: {i}")

            PR_NUM = submission["number"]
            print(f" |  | Pull Request: {PR_NUM}")
            pr_key_label.text = "Pull Request:"
            pr_value_label.text = f"{PR_NUM}"

            PR_AUTHOR = submission["user"]["login"]
            print(f" |  | Author: {PR_AUTHOR}")
            author_key_label.text = "Author:"
            author_value_label.text = f"{PR_AUTHOR}"
            
            PR_TITLE = github_json[1]["title"]
            print(f" |  | Title: {PR_TITLE}")
            truncated_text1, total_lines, total_chars = truncate_text_to_lines(PR_TITLE, 75, 4)
            pixelwrapped1 = "\n".join(wrap_text_to_pixels(truncated_text1, DISPLAY_WIDTH-2, terminalio.FONT))
            title_value_label.text = f"{pixelwrapped1}"

            PR_DESCRIPTION = github_json[1]["body"]
            print(f" |  | Description: {PR_DESCRIPTION}")
            truncated_text2, total_lines, total_chars = truncate_text_to_lines(PR_DESCRIPTION, 75, 15)
            desc_key_label.text = "Description:"
            pixelwrapped2 = "\n".join(wrap_text_to_pixels(truncated_text2, DISPLAY_WIDTH-2, terminalio.FONT))
            desc_value_label.text = f"{pixelwrapped2}"

            if DEBUG:
                print("Full API GET URL: ", GITHUB_SOURCE)
                print(submission)
            time.sleep(10)
            # Rotate through the submissions
            github_json.append(github_json.pop(0))
    else:  # When its time to poll, break to top of while True loop.
        break