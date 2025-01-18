import time
import board
import math
import terminalio
import displayio
import fourwire
import digitalio
import adafruit_imageload
import adafruit_sdcard
import storage
import json
import feathers3
from adafruit_hx8357 import HX8357
import adafruit_stmpe610
from adafruit_display_text import label, outlined_label
from adafruit_bitmap_font import bitmap_font
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_button.sprite_button import SpriteButton
from slider import Slider
from soft_keyboard.soft_keyboard import SoftKeyboard, PRINTABLE_CHARACTERS

# 3.5" TFT Featherwing is 480x320
displayio.release_displays()
DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 320

# Initialize TFT Display
spi = board.SPI()
tft_cs = board.D9
tft_dc = board.D10

display_bus = fourwire.FourWire(spi, command=tft_dc, chip_select=tft_cs)
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

# Initialize SDCard on TFT Featherwing
try:
    cs = digitalio.DigitalInOut(board.D5)
    sdcard = adafruit_sdcard.SDCard(spi, cs)
    vfs = storage.VfsFat(sdcard)
    virtual_root = "/sd"
    storage.mount(vfs, virtual_root)
except Exception as e:
    print(f"Error Loading SD Card: {e}")
    pass


def _format_date(datetime):
    """F-String formatted struct time conversion"""
    return (f"{datetime.tm_year:02}/{datetime.tm_mon:02}/{datetime.tm_mday:02}")

def _format_time(datetime):
    """F-String formatted struct time conversion"""
    return f"{datetime.tm_hour:02}:{datetime.tm_min:02}"

def unixtime_to_formattedtime(unixtime, offset=None):
    local_timestamp = int(unixtime + int(offset))	
    current_unix_time = time.localtime(local_timestamp)
    current_struct_time = time.struct_time(current_unix_time)
    return current_struct_time

# ---- FEATHER WEATHER SPLASH SCREEN -----
feather_weather = displayio.OnDiskBitmap("/images/feather_weather.bmp")
feather_weather_bg = displayio.TileGrid(
    feather_weather,
    pixel_shader=feather_weather.pixel_shader,
    width=1,
    height=1,
    tile_width=DISPLAY_WIDTH,
    tile_height=DISPLAY_HEIGHT,
)

# ---- SPLASH GROUP -----
splash_label = label.Label(terminalio.FONT)
splash_label.anchor_point = (0.5, 0.5)
splash_label.anchored_position = (DISPLAY_WIDTH / 2, DISPLAY_HEIGHT - 20)
splash_label.scale = 1
splash_label.color = 0xFFFFFF
loading_splash = displayio.Group()
loading_splash.append(feather_weather_bg)
loading_splash.append(splash_label)
display.root_group = loading_splash

def make_my_label(font=None,
                  anchor_point=None,
                  anchored_position=None,
                  scale=None,
                  color=None):
    """ Shortens labels to 1 liners """
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

def outline_my_label(font=None,
                     anchor_point=None,
                     anchored_position=None,
                     scale=None,
                     color=None,
                     outline_color=None,
                     outline_size=None,
                     padding_left=None,
                     padding_right=None,
                     padding_top=None,
                     padding_bottom=None):
    """ Shortens labels to 1 liners """
    func_label = outlined_label.OutlinedLabel(font) if font is not None else label.Label()
    if anchor_point is not None:
        func_label.anchor_point = anchor_point
    if anchored_position is not None:
        func_label.anchored_position = anchored_position
    if scale is not None:
        func_label.scale = scale
    if color is not None:
        func_label.color = color
    if outline_color is not None:
        func_label.outline_color = outline_color
    if outline_size is not None:
        func_label.outline_size = outline_size
    if padding_left is not None:
        func_label.padding_left = padding_left
    if padding_right is not None:
        func_label.padding_right = padding_right
    if padding_top is not None:
        func_label.padding_top = padding_top
    if padding_bottom is not None:
        func_label.padding_bottom = padding_bottom
    return func_label

# Quick Colors for Labels
splash_label.text = "Loading Font Colors..."
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
TEXT_TEAL = 0xB2D8D8
TEXT_WHITE = 0xFFFFFF
TEXT_YELLOW = 0xFFFF00

# Custom BDF or PCF fonts
splash_label.text = "Loading Fonts..."
forkawesome_font = bitmap_font.load_font("/fonts/forkawesome-12.pcf")
Arial_16 = bitmap_font.load_font("/fonts/Arial-16.bdf")
GoodTimes_16 = bitmap_font.load_font("/fonts/GoodTimesRg-Regular-16.bdf")
GoodTimes_22 = bitmap_font.load_font("/fonts/GoodTimesRg-Regular-22.bdf")
GoodTimes_30 = bitmap_font.load_font("/fonts/GoodTimesRg-Regular-30.bdf")
GoodTimes_40 = bitmap_font.load_font("/fonts/GoodTimesRg-Regular-40.bdf")
GoodTimes_121 = bitmap_font.load_font("/fonts/GoodTimesRg-Regular-121.bdf")

splash_label.text = "Loading Labels..."

# name_label (FONT, (ANCHOR POINT), (ANCHOR POSITION), SCALE, COLOR)
loading_label = make_my_label(terminalio.FONT, (0.5, 0.5), (DISPLAY_WIDTH / 2, DISPLAY_HEIGHT - 20), 1, TEXT_WHITE)
header_label = make_my_label(terminalio.FONT, (0.5, 1.0), (DISPLAY_WIDTH / 2 +10, 15), 1, TEXT_WHITE)
sunrise_label = outline_my_label(GoodTimes_16, (0.0, 0.0), (125, 20), 1, TEXT_LIGHTBLUE, TEXT_BLACK, 1,0,0,0,0)
sunset_label = outline_my_label(GoodTimes_16, (1.0, 0.0), (370, 20), 1, TEXT_LIGHTBLUE, TEXT_BLACK, 1,0,0,0,0)
preferences_value = make_my_label(terminalio.FONT, (0.5, 0.5), (DISPLAY_WIDTH / 2, 5), 1, TEXT_WHITE)
label_preferences_current_brightness = make_my_label(terminalio.FONT, (1.0, 1.0), (DISPLAY_WIDTH - 10, 80), 1, TEXT_CYAN)
wifi_settings_ssid = make_my_label(terminalio.FONT, (0.0, 0.0), (DISPLAY_WIDTH / 3, 50), 2, TEXT_WHITE)
wifi_settings_pw = make_my_label(terminalio.FONT, (0.0, 0.0), (DISPLAY_WIDTH / 3, 150), 2, TEXT_WHITE)
wifi_settings_instructions = make_my_label(terminalio.FONT, (0.5, 0.0), (DISPLAY_WIDTH / 2, 250), 1, TEXT_WHITE)
sys_info_label1 = make_my_label(terminalio.FONT, (0.0, 0.0), (5, 50), 2, TEXT_WHITE)
sys_info_label2 = make_my_label(terminalio.FONT, (0.0, 0.0), (5, 150), 1, TEXT_WHITE)
sys_info_label3 = make_my_label(terminalio.FONT, (0.0, 0.0), (5, 150 + 32), 1, TEXT_WHITE)
sys_info_label4 = make_my_label(terminalio.FONT, (0.0, 0.0), (5, 150 + 48), 1, TEXT_WHITE)
sys_info_label5 = make_my_label(terminalio.FONT, (0.0, 0.0), (5, 150 + 64), 1, TEXT_WHITE)
sys_info_label6 = make_my_label(terminalio.FONT, (0.0, 0.0), (5, 150 + 80), 1, TEXT_WHITE)
sys_info_label7 = make_my_label(terminalio.FONT, (0.0, 0.0), (5, 150 + 96), 1, TEXT_WHITE)
rssi_label = make_my_label(terminalio.FONT, (0.0, 0.0), (5, 60), 1, TEXT_MAGENTA)
rssi_label0 = make_my_label(terminalio.FONT, (0.0, 0.0), (5, 60 + 20), 1, TEXT_WHITE)
rssi_label1 = make_my_label(terminalio.FONT, (0.0, 0.0), (5, 60 + 40), 1, TEXT_WHITE)
rssi_label2 = make_my_label(terminalio.FONT, (0.0, 0.0), (5, 60 + 60), 1, TEXT_WHITE)
rssi_label3 = make_my_label(terminalio.FONT, (0.0, 0.0), (5, 60 + 80), 1, TEXT_WHITE)
rssi_label4 = make_my_label(terminalio.FONT, (0.0, 0.0), (5, 60 + 100), 1, TEXT_WHITE)
rssi_label5 = make_my_label(terminalio.FONT, (0.0, 0.0), (5, 60 + 120), 1, TEXT_WHITE)
rssi_label6 = make_my_label(terminalio.FONT, (0.0, 0.0), (5, 60 + 140), 1, TEXT_WHITE)
rssi_label7 = make_my_label(terminalio.FONT, (0.0, 0.0), (5, 60 + 160), 1, TEXT_WHITE)
rssi_label8 = make_my_label(terminalio.FONT, (0.0, 0.0), (5, 60 + 180), 1, TEXT_WHITE)
rssi_label9 = make_my_label(terminalio.FONT, (0.0, 0.0), (5, 60 + 200), 1, TEXT_WHITE)
input_change_wifi = make_my_label(terminalio.FONT, (0.0, 0.0), (5, 50), 1, TEXT_WHITE)
input_new_cred = make_my_label(terminalio.FONT, (0.0, 0.0), (100, 50), 1, TEXT_WHITE)
input_lbl = label.Label(terminalio.FONT, scale=2, text="", color=0xFFFFFF, background_color=0x00000)
input_lbl.x = 100
input_lbl.y = 50

menu_popout_label = make_my_label(terminalio.FONT, (0.5, 0.5), (DISPLAY_WIDTH / 2, 25), 1, TEXT_CYAN)
date_label = make_my_label(GoodTimes_16, (0.0, 0.0), (5, 45), 1, TEXT_LIGHTBLUE)
time_label = make_my_label(GoodTimes_30, (0.0, 0.0), (5, 65), 1, TEXT_LIGHTBLUE)
temp_degree_label = make_my_label(GoodTimes_16, (1.0, 1.0), (475, 123), 2, TEXT_ORANGE)
temp_data_label = make_my_label(GoodTimes_121, (0.5, 0.0), (DISPLAY_WIDTH / 2, 100), 1, TEXT_ORANGE)
temp_data_shadow = make_my_label(GoodTimes_121, (0.5, 0.0), (DISPLAY_WIDTH / 2 + 2, 100 + 2), 1, TEXT_BLACK)
online_temp_data_label = outline_my_label(GoodTimes_40, (0.5, 0.0), (DISPLAY_WIDTH / 2, 60), 1, TEXT_LIGHTBLUE, TEXT_BLACK, 1,0,0,0,0)
humidity_label = make_my_label(GoodTimes_16, (0.0, 1.0), (5, DISPLAY_HEIGHT - 40), 1, TEXT_GRAY)
humidity_data_label = make_my_label(GoodTimes_40, (0.0, 1.0), (5, DISPLAY_HEIGHT), 1, TEXT_ORANGE)
online_humidity_data_label = make_my_label(GoodTimes_22, (0.0, 1.0), (5, DISPLAY_HEIGHT - 60), 1, TEXT_LIGHTBLUE)
barometric_label = make_my_label(GoodTimes_16, (1.0, 1.0), (471, DISPLAY_HEIGHT - 40), 1, TEXT_GRAY)
barometric_data_label = make_my_label(GoodTimes_40, (1.0, 1.0), (470, DISPLAY_HEIGHT), 1, TEXT_ORANGE)
online_barometric_data_label = make_my_label(GoodTimes_22, (1.0, 1.0), (470, DISPLAY_HEIGHT - 60), 1, TEXT_LIGHTBLUE)
online_windspeed_label = make_my_label(GoodTimes_22, (1.0, 1.0), (DISPLAY_WIDTH - 5, 90), 1, TEXT_LIGHTBLUE)
vbat_label = make_my_label(GoodTimes_22, (1.0, 1.0), (DISPLAY_WIDTH - 15, 60), 1, None)
plugbmp_label = make_my_label(terminalio.FONT, (1.0, 1.0), None, 1, None)
greenbmp_label = make_my_label(terminalio.FONT, (1.0, 1.0), None, 1, None)
bluebmp_label = make_my_label(terminalio.FONT, (1.0, 1.0), None, 1, None)
yellowbmp_label = make_my_label(terminalio.FONT, (1.0, 1.0), None, 1, None)
orangebmp_label = make_my_label(terminalio.FONT, (1.0, 1.0), None, 1, None)
redbmp_label = make_my_label(terminalio.FONT, (1.0, 1.0), None, 1, None)
warning_label = outline_my_label(Arial_16,(0.5, 0.5),(DISPLAY_WIDTH / 2, DISPLAY_HEIGHT - 103),1, TEXT_ORANGE, TEXT_BLACK, 1,0,0,0,0)

def show_warning(text):
    # Function to display weather popup warning
    warning_label.text = text
    warning_group.hidden = False


def hide_warning():
    # Function to hide weather popup warning
    warning_group.hidden = True

def pressure_sensor_warning(pressure):
    if pressure <= 919:  # pray you never see this message
        show_warning("HOLY COW: Seek Shelter!")
    elif 920 <= pressure <= 979:
        show_warning("DANGER: Major Hurricane")
    elif 980 <= pressure <= 989:
        show_warning("DANGER: Minor Hurricane")
    elif 990 <= pressure <= 1001:
        show_warning("WARNING: Tropical Storm")
    elif 1002 <= pressure <= 1009:  # sudden gusty downpours
        show_warning("Low Pressure System")
    elif 1019 <= pressure <= 1025:  # sudden light cold rain
        show_warning("High Pressure System")
    elif pressure >= 1026:
        show_warning("WARNING: Hail & Tornados?")
    else:
        hide_warning()  # Normal pressures: 1110-1018 (no message)

splash_label.text = "Loading Icons..."
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
sprite_group.y = 40

# Warning label RoundRect
roundrect = RoundRect(
    int(10),
    int(DISPLAY_HEIGHT - 125),
    DISPLAY_WIDTH - 10,
    40,
    10,
    fill=None,
    outline=0xFFFFFF,
    stroke=0,
)

# Menu RoundRect
menu_roundrect = RoundRect(
    int(130),  # start corner x
    int(5),  # start corner y
    DISPLAY_WIDTH - 200,  # width
    200,  # height
    10,  # corner radius
    fill=None,
    outline=0xFFFFFF,
    stroke=0,
)

splash_label.text = "Loading Touch Buttons..."
# Button width & height must be multiple of 3
# otherwise you'll get a tilegrid_inflator error
BUTTON_WIDTH = 12 * 16
BUTTON_HEIGHT = 3 * 16
BUTTON_MARGIN = 5

# Defiine the button
menu_button = SpriteButton(
    x=BUTTON_MARGIN,
    y=BUTTON_MARGIN,
    width=7 * 16,
    height=2 * 16,
    label="MENU",
    label_font=GoodTimes_16,
    label_color=TEXT_WHITE,
    bmp_path="icons/gradient_button_0.bmp",
    selected_bmp_path="icons/gradient_button_1.bmp",
    transparent_index=0,
)

next_button = SpriteButton(
    x=DISPLAY_WIDTH - 3 * 16,
    y=BUTTON_MARGIN,
    width=3 * 16,
    height=2 * 16,
    label=">",
    label_font=Arial_16,
    label_color=TEXT_WHITE,
    bmp_path="icons/gradient_button_0.bmp",
    selected_bmp_path="icons/gradient_button_1.bmp",
    transparent_index=0,
)

prev_button = SpriteButton(
    x=DISPLAY_WIDTH - 6 * 16 - 5,
    y=BUTTON_MARGIN,
    width=3 * 16,
    height=2 * 16,
    label="<",
    label_font=Arial_16,
    label_color=TEXT_WHITE,
    bmp_path="icons/gradient_button_0.bmp",
    selected_bmp_path="icons/gradient_button_1.bmp",
    transparent_index=0,
)

item1_button = SpriteButton(
    x=135,
    y=50,
    width=BUTTON_WIDTH,
    height=BUTTON_HEIGHT,
    label="Preferences",
    label_font=Arial_16,
    label_color=TEXT_WHITE,
    bmp_path="icons/gradient_button_0.bmp",
    selected_bmp_path="icons/gradient_button_1.bmp",
    transparent_index=0,
)

item2_button = SpriteButton(
    x=135,
    y=105,
    width=BUTTON_WIDTH,
    height=BUTTON_HEIGHT,
    label="WiFi Credentials",
    label_font=Arial_16,
    label_color=TEXT_WHITE,
    bmp_path="icons/gradient_button_0.bmp",
    selected_bmp_path="icons/gradient_button_1.bmp",
    transparent_index=0,
)

item3_button = SpriteButton(
    x=135,
    y=160,
    width=BUTTON_WIDTH,
    height=BUTTON_HEIGHT,
    label="RSSI Scan",
    label_font=Arial_16,
    label_color=TEXT_WHITE,
    bmp_path="icons/gradient_button_0.bmp",
    selected_bmp_path="icons/gradient_button_1.bmp",
    transparent_index=0,
)

item4_button = SpriteButton(
    x=135,
    y=215,
    width=BUTTON_WIDTH,
    height=BUTTON_HEIGHT,
    label="System Info",
    label_font=Arial_16,
    label_color=TEXT_WHITE,
    bmp_path="icons/gradient_button_0.bmp",
    selected_bmp_path="icons/gradient_button_1.bmp",
    transparent_index=0,
)

item5_button = SpriteButton(
    x=135,
    y=270,
    width=BUTTON_WIDTH,
    height=BUTTON_HEIGHT,
    label="Change Credentials",
    label_font=Arial_16,
    label_color=TEXT_WHITE,
    bmp_path="icons/gradient_button_0.bmp",
    selected_bmp_path="icons/gradient_button_1.bmp",
    transparent_index=0,
)

my_slider = Slider(x=5, y=50, width=300, value=40000)

splash_label.text = "Loading Soft Keyboard..."
soft_kbd = SoftKeyboard(
    2,
    100,
    DISPLAY_WIDTH - 2,
    DISPLAY_HEIGHT - 100,
    terminalio.FONT,
    forkawesome_font,
    keypress_cooldown = 0.1,
    highlight_duration = 0.1,
    layout_config="mobile_layout.json",
)
"""
soft_kbd2 = SoftKeyboard(
    2,
    100,
    DISPLAY_WIDTH - 2,
    DISPLAY_HEIGHT - 100,
    terminalio.FONT,
    forkawesome_font,
    layout_config="mobile_layout_special.json",
)
"""

splash_label.text = "Loading Background Images..."
# Load Bitmap to tile grid first (Background layer)
DiskBMP = displayio.OnDiskBitmap("/images/Wallpaper_Spritesheet_8bit.bmp")
wallpaper = displayio.TileGrid(
    DiskBMP,
    pixel_shader=DiskBMP.pixel_shader,
    tile_width=480,
    tile_height=320,
)

splash_label.text = "Loading Display Groups..."
# Create subgroups
wallpaper_group = displayio.Group()
wallpaper_group.append(wallpaper)
splash = displayio.Group()
text_group = displayio.Group()
temp_group = displayio.Group()
warning_group = displayio.Group()
loading_group = displayio.Group()
menu_button_group = displayio.Group()
menu_popout_group = displayio.Group()
menu_popout_group_items = displayio.Group()

main_group = displayio.Group()
main_group2 = displayio.Group()
main_group3 = displayio.Group()
preferences_group = displayio.Group()
wifi_settings_group = displayio.Group()
rssi_group = displayio.Group()
sys_info_group = displayio.Group()
wifi_change_group = displayio.Group()

# Add subgroups to main display group
main_group.append(splash)
main_group.append(wallpaper_group)
main_group.append(header_label)
main_group.append(text_group)
main_group.append(warning_group)
main_group.append(loading_group)
main_group.append(temp_group)
main_group.append(sprite_group)
main_group.append(menu_button_group)
main_group.append(menu_popout_group)
main_group.append(menu_popout_group_items)

# Add warning popup group
warning_group.append(roundrect)
warning_group.append(warning_label)

# Label Display Group (foreground layer)
text_group.append(date_label)
text_group.append(time_label)
temp_group.append(temp_degree_label)
temp_group.append(temp_data_shadow)
temp_group.append(temp_data_label)
temp_group.append(online_temp_data_label)
temp_group.append(sunrise_label)
temp_group.append(sunset_label)
text_group.append(humidity_label)
text_group.append(humidity_data_label)
text_group.append(online_humidity_data_label)
text_group.append(barometric_label)
text_group.append(barometric_data_label)
text_group.append(online_barometric_data_label)
text_group.append(online_windspeed_label)
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
menu_popout_group_items.append(item1_button)
menu_popout_group_items.append(item2_button)
menu_popout_group_items.append(item3_button)
menu_popout_group_items.append(item4_button)
menu_popout_group_items.append(item5_button)
menu_button_group.append(menu_button)
menu_button_group.append(next_button)
menu_button_group.append(prev_button)
# display.root_group = main_group

def usb_battery_monitor(vbat_monitor,vbus_monitor):
    """ Set battery icon and voltage label """
    try:
        vbat_label.text = f"{vbat_monitor:.2f}v"
    except (ValueError, RuntimeError, OSError) as e:
        print("Voltage Monitor Error: \n", e)

    # print("USB Sense: ", usb_sense)  # Boolean value
    if vbus_monitor:  # if on USB power show plug sprite icon
        vbat_label.color = TEXT_LIGHTBLUE
        sprite[0] = 5
    else:  # if on battery power only
        # Changes battery voltage color depending on charge level
        if vbat_label.text >= "4.23":
            vbat_label.color = TEXT_LIGHTBLUE
            sprite[0] = 5
        elif "4.10" <= vbat_label.text <= "4.22":
            vbat_label.color = TEXT_GREEN
            sprite[0] = 0
        elif "4.00" <= vbat_label.text <= "4.09":
            vbat_label.color = TEXT_TEAL
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

def show_menu():
    # Function to display popup menu
    menu_popout_label.text = "Menu Popout"
    menu_popout_group.hidden = False
    menu_popout_group_items.hidden = False


def hide_menu():
    # Function to hide popup menu
    menu_popout_group.hidden = True
    menu_popout_group_items.hidden = True


# Page Switching Function (FROM, TO)
def root_group_switch(SHOUTY_REMOVE, SHOUTY_APPEND):
    # Removal order is less important than append order
    hide_menu()
    SHOUTY_REMOVE.remove(wallpaper_group)
    SHOUTY_REMOVE.remove(header_label)
    SHOUTY_REMOVE.remove(menu_button_group)
    SHOUTY_REMOVE.remove(menu_popout_group)
    SHOUTY_REMOVE.remove(menu_popout_group_items)
    if SHOUTY_REMOVE == main_group:
        SHOUTY_REMOVE.remove(text_group)
        SHOUTY_REMOVE.remove(warning_group)
        SHOUTY_REMOVE.remove(loading_group)
        SHOUTY_REMOVE.remove(temp_group)
        SHOUTY_REMOVE.remove(sprite_group)
    if SHOUTY_REMOVE == preferences_group:
        SHOUTY_REMOVE.remove(label_preferences_current_brightness)
        SHOUTY_REMOVE.remove(my_slider)
    if SHOUTY_REMOVE == wifi_settings_group:
        SHOUTY_REMOVE.remove(wifi_settings_ssid)
        SHOUTY_REMOVE.remove(wifi_settings_pw)
        SHOUTY_REMOVE.remove(wifi_settings_instructions)
    if SHOUTY_REMOVE == rssi_group:
        SHOUTY_REMOVE.remove(rssi_label)
        SHOUTY_REMOVE.remove(rssi_label0)
        SHOUTY_REMOVE.remove(rssi_label1)
        SHOUTY_REMOVE.remove(rssi_label2)
        SHOUTY_REMOVE.remove(rssi_label3)
        SHOUTY_REMOVE.remove(rssi_label4)
        SHOUTY_REMOVE.remove(rssi_label5)
        SHOUTY_REMOVE.remove(rssi_label6)
        SHOUTY_REMOVE.remove(rssi_label7)
        SHOUTY_REMOVE.remove(rssi_label8)
        SHOUTY_REMOVE.remove(rssi_label9)
    if SHOUTY_REMOVE == sys_info_group:
        SHOUTY_REMOVE.remove(sys_info_label1)
        SHOUTY_REMOVE.remove(sys_info_label2)
        SHOUTY_REMOVE.remove(sys_info_label3)
        SHOUTY_REMOVE.remove(sys_info_label4)
        SHOUTY_REMOVE.remove(sys_info_label5)
        SHOUTY_REMOVE.remove(sys_info_label6)
        SHOUTY_REMOVE.remove(sys_info_label7)
    if SHOUTY_REMOVE == wifi_change_group:
        SHOUTY_REMOVE.remove(input_change_wifi)
        SHOUTY_REMOVE.remove(input_new_cred)
        SHOUTY_REMOVE.remove(soft_kbd)
        SHOUTY_REMOVE.remove(input_lbl)

    # Page Switching & Layer Loading Order
    # Append order is layer order background (top) to foreground (bottom).
    SHOUTY_APPEND.append(wallpaper_group)  # always load wallpaper 1st
    if SHOUTY_APPEND == main_group:
        SHOUTY_APPEND.append(text_group)
        SHOUTY_APPEND.append(warning_group)
        SHOUTY_APPEND.append(loading_group)
        SHOUTY_APPEND.append(temp_group)
        SHOUTY_APPEND.append(sprite_group)
    if SHOUTY_APPEND == preferences_group:
        SHOUTY_APPEND.append(label_preferences_current_brightness)
        SHOUTY_APPEND.append(my_slider)
    if SHOUTY_APPEND == wifi_settings_group:
        SHOUTY_APPEND.append(wifi_settings_ssid)
        SHOUTY_APPEND.append(wifi_settings_pw)
        SHOUTY_APPEND.append(wifi_settings_instructions)
    if SHOUTY_APPEND == rssi_group:
        SHOUTY_APPEND.append(rssi_label)
        SHOUTY_APPEND.append(rssi_label0)
        SHOUTY_APPEND.append(rssi_label1)
        SHOUTY_APPEND.append(rssi_label2)
        SHOUTY_APPEND.append(rssi_label3)
        SHOUTY_APPEND.append(rssi_label4)
        SHOUTY_APPEND.append(rssi_label5)
        SHOUTY_APPEND.append(rssi_label6)
        SHOUTY_APPEND.append(rssi_label7)
        SHOUTY_APPEND.append(rssi_label8)
        SHOUTY_APPEND.append(rssi_label9)
    if SHOUTY_APPEND == sys_info_group:
        SHOUTY_APPEND.append(sys_info_label1)
        SHOUTY_APPEND.append(sys_info_label2)
        SHOUTY_APPEND.append(sys_info_label3)
        SHOUTY_APPEND.append(sys_info_label4)
        SHOUTY_APPEND.append(sys_info_label5)
        SHOUTY_APPEND.append(sys_info_label6)
        SHOUTY_APPEND.append(sys_info_label7)
    if SHOUTY_APPEND == wifi_change_group:
        SHOUTY_APPEND.append(input_change_wifi)
        SHOUTY_APPEND.append(input_new_cred)
        SHOUTY_APPEND.append(soft_kbd)
        SHOUTY_APPEND.append(input_lbl)

    SHOUTY_APPEND.append(header_label)
    SHOUTY_APPEND.append(menu_button_group)
    SHOUTY_APPEND.append(menu_popout_group)
    SHOUTY_APPEND.append(menu_popout_group_items)
    display.root_group = SHOUTY_APPEND


def group_cleanup():
    # When touch moves outside of button
    item1_button.selected = False
    item2_button.selected = False
    item3_button.selected = False
    item4_button.selected = False
    item5_button.selected = False
    menu_button.selected = False
    prev_button.selected = False
    next_button.selected = False


def menu_switching(
    current_group=None,
    prev_target=None,
    next_target=None,
    item1_target=preferences_group,
    item2_target=wifi_settings_group,
    item3_target=rssi_group,
    item4_target=sys_info_group,
    item5_target=wifi_change_group,
):
    """ Touchscreen Popout Menu for root_group_switch """
    if menu_button.contains(p):
        if not menu_button.selected:
            menu_button.selected = True
            time.sleep(0.25)
            print("Menu Pressed")
            show_menu()
    elif prev_button.contains(p):
        if not prev_button.selected:
            prev_button.selected = True
            time.sleep(0.1)
            print("Previous Pressed")
            root_group_switch(current_group, prev_target)
    elif next_button.contains(p):
        if not next_button.selected:
            next_button.selected = True
            time.sleep(0.5)
            print("Next Pressed")
            root_group_switch(current_group, next_target)
    elif not menu_popout_group.hidden:
        if item1_button.contains(p):
            if not item1_button.selected:
                item1_button.selected = True
                time.sleep(0.25)
                print("Item 1 Pressed")
                root_group_switch(current_group, item1_target)
        elif item2_button.contains(p):
            if not item2_button.selected:
                item2_button.selected = True
                time.sleep(0.25)
                print("Item 2 Pressed")
                root_group_switch(current_group, item2_target)
        elif item3_button.contains(p):
            if not item3_button.selected:
                item3_button.selected = True
                time.sleep(0.25)
                print("Item 3 Pressed")
                root_group_switch(current_group, item3_target)
        elif item4_button.contains(p):
            if not item4_button.selected:
                item4_button.selected = True
                time.sleep(0.25)
                print("Item 4 Pressed")
                root_group_switch(current_group, item4_target)
        elif item5_button.contains(p):
            if not item5_button.selected:
                item5_button.selected = True
                time.sleep(0.25)
                print("Item 5 Pressed")
                root_group_switch(current_group, item5_target)
        else:
            group_cleanup()
            hide_menu()
    else:
        group_cleanup()
        hide_menu()


hide_warning()  # sets default weather warning to hidden
hide_menu()  # sets default menu popout to hidden

def time_calc(input_time):
    # Attribution: Elpekenin
    if input_time < 60.0:
        return f"{math.floor(input_time)} seconds"
    if input_time < 3600.0:
        return f"{math.floor(input_time / 60.0)} minutes"
    if input_time < 86400.0:
        return f"{math.floor(input_time / 3600.0)} hours"
    return f"{math.floor(input_time / 86400.0)} days"

def weather_code_parser(code, is_day):
    weather_codes_file = "weather_codes.py"
    with open(f"{weather_codes_file}", "r") as wc:
        weather_codes_json = json.loads(wc.read())
        if is_day == 1:
            day_description = weather_codes_json[code]["day"]["description"]
            return (day_description)
        if is_day == 0:
            night_description = weather_codes_json[code]["night"]["description"]
            return (night_description)

def weather_icon_parser(code, is_day):
    weather_codes_file = "weather_codes.py"
    with open(f"{weather_codes_file}", "r") as wc:
        weather_codes_json = json.loads(wc.read())
        if is_day == 1:
            day_icon = weather_codes_json[code]["day"]["image"]
            return (day_icon)
        if is_day == 0:
            night_icon = weather_codes_json[code]["night"]["image"]
            return (night_icon)

