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
import adafruit_imageload
import sdcardio
import storage
import terminalio
import wifi

from adafruit_bitmap_font import bitmap_font
import adafruit_requests
from adafruit_display_text import label, wrap_text_to_pixels
from circuitpython_st7796s import ST7796S
from adafruit_bitmapsaver import save_pixels
from jpegio import JpegDecoder

spi = board.SPI()
tft_cs = board.D9
tft_dc = board.D10
tft_rst = board.D17
sd_cs = board.D5

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
GITHUB_HEADER = {"Accept: application/vnd.github.raw+json"
                 + "Authorization": " token " + token}
GITHUB_SOURCE = f"https://api.github.com/repos/{repository}/issues?state=closed"

# Initialize SPI SDCard prior to other SPI peripherals!
try:
    print("Attempting to mount sd card")
    sdcard = sdcardio.SDCard(spi, sd_cs)
    vfs = storage.VfsFat(sdcard)
    storage.mount(vfs, '/sd')
    print(f"ListDir: {os.listdir('/sd')}")
    avatar_path = "/sd/Github_Avatars/"

except Exception as e:
    print("Error:", e)

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

# Load Bitmap to tile grid first (Background layer)
DiskBMP = displayio.OnDiskBitmap("/images/Astral_Fruit_8bit.bmp")
tile_grid = displayio.TileGrid(
    DiskBMP,
    pixel_shader=DiskBMP.pixel_shader,
    width=1,
    height=1,
    tile_width=DISPLAY_WIDTH,
    tile_height=DISPLAY_HEIGHT)

# Load battery voltage icons (from 1 sprite sheet image)
sprite_sheet, palette = adafruit_imageload.load(
    "/icons/Github_PR_Spritesheet.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette
)
sprite = displayio.TileGrid(
    sprite_sheet, pixel_shader=palette, width=1, height=1, tile_width=75, tile_height=75
)
sprite_group = displayio.Group()
sprite_group.append(sprite)
sprite_group.x = 405
sprite_group.y = 0

decoder = JpegDecoder()
width, height = decoder.open("/sd/Github_Avatars/Octocat.jpg")
image = displayio.Bitmap(width, height, 65535)
decoder.decode(image)
tile_grid_avatar = displayio.TileGrid(
    image,
    x=-100,
    y=-100,
    pixel_shader=displayio.ColorConverter(
        input_colorspace=displayio.Colorspace.RGB565_SWAPPED
    ),
)

Arial12 = bitmap_font.load_font("/fonts/Arial-12.bdf")
Arial16 = bitmap_font.load_font("/fonts/Arial-16.bdf")

# Label Customizations
pr_author_label = label.Label(Arial16)
pr_author_label.anchor_point = (0.0, 0.0)
pr_author_label.anchored_position = (110, 10)
pr_author_label.scale = (1)
pr_author_label.color = TEXT_WHITE

pr_num_label = label.Label(Arial16)
pr_num_label.anchor_point = (1.0, 0.0)
pr_num_label.anchored_position = (DISPLAY_WIDTH-80, 10)
pr_num_label.scale = (1)
pr_num_label.color = TEXT_WHITE

title_value_label = label.Label(Arial12)
title_value_label.anchor_point = (0.0, 0.0)
title_value_label.anchored_position = (5, 110)
title_value_label.scale = (1)
title_value_label.color = TEXT_LIGHTBLUE

pr_state_label = label.Label(Arial12)
pr_state_label.anchor_point = (0.5, 0.5)
pr_state_label.anchored_position = (DISPLAY_WIDTH-37, 10)
pr_state_label.scale = (1)
pr_state_label.color = TEXT_LIGHTBLUE

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
text_group.append(tile_grid_avatar)
text_group.append(sprite_group)
text_group.append(pr_author_label)
text_group.append(pr_num_label)
text_group.append(title_value_label)
text_group.append(pr_state_label)
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


def get_file_name(file_path):
    file_name_and_extension = file_path.rsplit('/', 1)[-1].rsplit('.', 1)
    # Remove any characters that are not alphanumeric or underscores
    valid_chars = '-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    file_name = ''.join(
        (char for char in file_name_and_extension[0]
            if char in valid_chars))

    return file_name


def determine_extension(content_type):
    print(f" |  | Avatar content-type: {content_type}")
    if content_type.startswith('image/gif'):
        return '.gif'
    elif content_type.startswith('image/png'):
        return '.png'
    elif content_type.startswith('image/jpeg'):
        return '.jpg'
    else:
        return None


def online_image_to_sd(url):
    file_name = get_file_name(url)
    r = requests.get(url)
    if r.status_code != 200:
        print(f"❌ Failed to fetch image from {url}. Status code: {r.status_code}")
        return None
    content_type = r.headers.get('content-type', '')
    extension = determine_extension(content_type)
    if not extension:
        print(f"Unknown content type: {content_type}")
        return None
    sd_file_path = f"{avatar_path}{file_name}{extension}"
    try:
        with open(sd_file_path, "rb") as fp:
            # If the file exists, skip writing it
            print(" |  | Avatar exists on SDCard -> Skipping Write")
            return sd_file_path  # Return the file path
    except OSError:
        # If the file doesn't exist, write it to the SD card
        try:
            with open(sd_file_path, "wb") as fp:
                fp.write(r.content)
                print(f" |  | Wrote File: {sd_file_path}")
        except OSError as e:
            print(f" | ❌ SD File Path Error: {sd_file_path}")
            print(f" | ❌ OSError: {e}")
    return sd_file_path  # Return the file path


def load_image_from_sd(file_path):
    _, extension = file_path.rsplit('.', 1)
    extension = extension.lower()
    print(f"load_image_from_sd extension: {extension}")
    print(f"load_image_from_sd filepath: {file_path}")
    # Remove the previous tile_grid_avatar from text_group
    for item in text_group:
        if isinstance(item, displayio.TileGrid):
            text_group.remove(item)

    if extension == "png":
        print(f"JPG Path: {file_path}")
        try:
            decoder = JpegDecoder()
            width, height = decoder.open("/sd/Github_Avatars/Octocat.jpg")
            image = displayio.Bitmap(width, height, 65535)
            decoder.decode(image)
            tile_grid_avatar = displayio.TileGrid(
                image,
                pixel_shader=displayio.ColorConverter(
                    input_colorspace=displayio.Colorspace.RGB565_SWAPPED
                ),
            )
            text_group.append(tile_grid_avatar)
            return image, None  # No palette for JPEG images
        except Exception as e:
            print(f"Error loading JPEG file: {e}")
            return None, None

    elif extension in ["jpg", "jpeg"]:
        print(f"JPEG Path: {file_path}")
        try:
            decoder = JpegDecoder()
            width, height = decoder.open(file_path)
            print(f"Image Width: {width}")
            print(f"Image Height: {height}")
            if width > 100 or height > 100:
                scale_factor = max(width/100, height/100)
                scale = min(int(scale_factor), 2)  # Ensure scale is within 0-3 range
                width_scaled = int(width / scale_factor)
                height_scaled = int(height / scale_factor)
                image = displayio.Bitmap(width_scaled, height_scaled, 65535)
                decoder.decode(image, scale=scale)
            else:
                image = displayio.Bitmap(width, height, 65535)
                decoder.decode(image, scale=2)

            tile_grid_avatar = displayio.TileGrid(
                image,
                pixel_shader=displayio.ColorConverter(
                    input_colorspace=displayio.Colorspace.RGB565_SWAPPED
                ),
            )
            text_group.append(tile_grid_avatar)
            return image, None  # No palette for JPEG images
        except Exception as e:
            print(f"Error loading JPEG file: {e}")
            return None, None

    else:
        print(f"Unsupported image format: {extension}")
        return None, None



github_json = {}
first_run = True
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

        if DEBUG:
            print("Full API GET URL: ", GITHUB_SOURCE)
            print(github_json)

        STATUS_CODE = str(github_response.status_code)
        STATUS_DESCRIPTION = str(github_response.status_code)
        print_http_status(STATUS_CODE, STATUS_DESCRIPTION)
        github_response.close()
        print("✂️ Disconnected Github API")

        print("\nFinished!")
        print(f"Board Uptime: {time_calc(time.monotonic())}")
        print(f"Next Update: {time_calc(SLEEP_TIME)}")
        print("===============================\n")
    except (ValueError, RuntimeError) as e:
        print(f"Failed to get data, retrying\n {e}")
        time.sleep(60)
        break

    if time.monotonic() - now <= SLEEP_TIME:
        for i in range(25):
            # Get the latest submission
            response_buffer = github_json[i]
            PR_NUM = response_buffer["number"]
            PR_URL = response_buffer["html_url"]
            PR_AUTHOR = response_buffer["user"]["login"]
            PR_AUTHOR_URL = response_buffer["user"]["url"]
            PR_AUTHOR_AVATAR = response_buffer["user"]["avatar_url"]
            PR_STATE = response_buffer["state"]
            if PR_STATE == "closed":
                pr_state_label.color = TEXT_PURPLE
                sprite[0] = 0
            elif PR_STATE == "draft":
                pr_state_label.color = TEXT_RED
                sprite[0] = 1
            elif PR_STATE == "merged":
                pr_state_label.color = TEXT_PURPLE
                sprite[0] = 2
            elif PR_STATE == "closed":
                pr_state_label.color = TEXT_PURPLE
                sprite[0] = 3
            else:
                pr_state_label.color = TEXT_GREEN
                sprite[0] = 3

            print(f"{'-'*40} {PR_NUM} {'-'*40}")
            print(f" |  | Index: {i} PR->{PR_URL}")
            print(f" |  | Author: {PR_AUTHOR} -> {PR_AUTHOR_URL}")
            print(f" |  | Avatar URL: {PR_AUTHOR_AVATAR}")

            # If Avatar is not on SD Card yet, download avatar to SD
            file_name = get_file_name(PR_AUTHOR_AVATAR)
            sd_file_path = online_image_to_sd(PR_AUTHOR_AVATAR)
            print(f" |  | Avatar SD File: {file_name}")
            print(f" |  | Avatar SD Path: {sd_file_path}")

            # Display Avatar from SD Card
            sdcard_avatar = load_image_from_sd(sd_file_path)

            print(f" |  | Pull Request: {PR_NUM}")
            pr_num_label.text = f"{PR_NUM}"
            pr_author_label.text = f"{PR_AUTHOR}"


            print(f" |  | Status: {PR_STATE}")
            pr_state_label.text = f"{PR_STATE}"

            PR_TITLE = response_buffer["title"]
            print(f" |  | Title: {PR_TITLE}")
            truncated_text1, total_lines, total_chars = truncate_text_to_lines(
                    PR_TITLE, 75, 4)
            pixelwrapped1 = "\n".join(
                    wrap_text_to_pixels(
                        truncated_text1, DISPLAY_WIDTH-2, terminalio.FONT))

            title_value_label.text = f"{pixelwrapped1}"
            if response_buffer["body"] != None:
                PR_DESCRIPTION = response_buffer["body"][:800]
                print(f" |  | Description: {PR_DESCRIPTION}\n\n")
                truncated_text2, total_lines, total_chars = truncate_text_to_lines(
                        PR_DESCRIPTION, 75, 11)
                desc_key_label.text = "Description:"
                pixelwrapped2 = "\n".join(wrap_text_to_pixels(
                        truncated_text2, DISPLAY_WIDTH-2, terminalio.FONT))
                desc_value_label.text = f"{pixelwrapped2}"

            time.sleep(5)
            # Rotate through the submissions
            github_json.append(github_json.pop(0))
            first_run = False
    else:  # When its time to poll, break to top of while True loop.
        break
