"""DJDevon3 Simple Offline Weatherstation"""
import gc
import time
import board
import adafruit_bmp280
import adafruit_sht31d
import displayio
import digitalio
import adafruit_imageload
import adafruit_sdcard
import adafruit_gps
import rtc
import busio
from adafruit_bitmapsaver import save_pixels
import storage
import pwmio
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
from adafruit_hx8357 import HX8357
from analogio import AnalogIn
# import audiobusio
# from audiomp3 import MP3Decoder

# This sketch should also work for the 2.5" TFT, just change the size.
DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 320
take_screenshot = False  # Set to True to take a screenshot :)

# Initialize Busses
i2c = board.I2C()
spi = board.SPI()
# Initialize SD Card First
cs = digitalio.DigitalInOut(board.D5)
sdcard = adafruit_sdcard.SDCard(spi, cs)
vfs = storage.VfsFat(sdcard)
displayio.release_displays()
# Initialize TFT
tft_cs = board.D9
tft_dc = board.D10
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = HX8357(display_bus, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT)
virtual_root = "/sd"
storage.mount(vfs, virtual_root)
# Initialize GPS
uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=10)
gps = adafruit_gps.GPS(uart, debug=False)
gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
gps.send_command(b"PMTK220,500")
rtc.set_time_source(gps)
the_rtc = rtc.RTC()

# Initialize I2S Audio Module
"""
mp3files = ["Hello.mp3"]
mp3 = open(mp3files[0], "rb")
decoder = MP3Decoder(mp3)
audio = audiobusio.I2SOut(board.A1, board.A2, board.A0)
for filename in mp3files:
    decoder.file = open(filename, "rb")
    audio.play(decoder, loop=False)
    # print("playing", filename)
    # This allows you to do other things while the audio plays!
    while audio.playing:
        pass
    time.sleep(1)
    audio.stop()
"""
def _format_date(datetime):
    return "{:02}/{:02}/{}".format(
        datetime.tm_mon,
        datetime.tm_mday,
        datetime.tm_year,
    )
def _format_time(datetime):
    return "{:02}:{:02}".format(
        datetime.tm_hour,
        datetime.tm_min,
    )
# Initialize Battery Gauge
vbat_voltage = AnalogIn(board.VOLTAGE_MONITOR)
def get_voltage(pin):
    return (pin.value * 3.3) / 65536 * 2
vbat = get_voltage(vbat_voltage)
# Initalize Sensors
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)
sht31d = adafruit_sht31d.SHT31D(i2c)

# BMP280 altitude sensor changes with barometric pressure!
# I set sea level pressure to sensor pressure because I'm always at sea level.
# Set manually if it doesn't work well for your elevation.
# bmp280.sea_level_pressure = 1010.80
bmp280.sea_level_pressure = bmp280.pressure

# Quick Colors for Labels
text_black = (0x000000)
text_blue = (0x0000FF)
text_cyan = (0x00FFFF)
text_gray = (0x8B8B8B)
text_green = (0x00FF00)
text_lightblue = (0x90C7FF)
text_magenta = (0xFF00FF)
text_orange = (0xFFA500)
text_purple = (0x800080)
text_red = (0xFF0000)
text_white = (0xFFFFFF)
text_yellow = (0xFFFF00)

# Fonts are optional
medium_font = bitmap_font.load_font("/fonts/Arial-16.bdf")
huge_font = bitmap_font.load_font("/fonts/GoodTimesRg-Regular-121.bdf")

# Individual customizable position labels
# https://learn.adafruit.com/circuitpython-display-support-using-displayio/text
date_label = label.Label(medium_font)
# Anchor point bottom center of text
date_label.anchor_point = (0.0, 0.0)
# Display width divided in half for center of display (x,y)
date_label.anchored_position = (5, 5)
date_label.scale = (1)
date_label.color = text_white

time_label = label.Label(medium_font)
# Anchor point bottom center of text
time_label.anchor_point = (0.5, 0.0)
# Display width divided in half for center of display (x,y)
time_label.anchored_position = (DISPLAY_WIDTH/2, 5)
time_label.scale = (1)
time_label.color = text_white

hello_label = label.Label(medium_font)
# Anchor point bottom center of text
hello_label.anchor_point = (0.5, 0.0)
# Display width divided in half for center of display (x,y)
hello_label.anchored_position = (DISPLAY_WIDTH/2, 30)
hello_label.scale = (1)
hello_label.color = text_white

temp_label = label.Label(medium_font)
temp_label.anchor_point = (1.0, 1.0)
temp_label.anchored_position = (475, 145)
temp_label.scale = (2)
temp_label.color = text_orange

temp_data_label = label.Label(huge_font)
temp_data_label.anchor_point = (0.5, 1.0)
temp_data_label.anchored_position = (DISPLAY_WIDTH/2, 200)
temp_data_label.scale = (1)
temp_data_label.color = text_orange

humidity_label = label.Label(medium_font)
# Anchor point bottom left of text
humidity_label.anchor_point = (0.0, 1.0)
humidity_label.anchored_position = (5, DISPLAY_HEIGHT)
humidity_label.scale = (1)
humidity_label.color = text_gray

humidity_data_label = label.Label(medium_font)
humidity_data_label.anchor_point = (0.0, 1.0)
humidity_data_label.anchored_position = (5, DISPLAY_HEIGHT-25)
humidity_data_label.scale = (1)
humidity_data_label.color = text_white

barometric_label = label.Label(medium_font)
# Anchor point bottom center of text
barometric_label.anchor_point = (0.5, 1.0)
barometric_label.anchored_position = (DISPLAY_WIDTH/2, DISPLAY_HEIGHT)
barometric_label.scale = (1)
barometric_label.color = text_gray

barometric_data_label = label.Label(medium_font)
barometric_data_label.anchor_point = (0.5, 1.0)
barometric_data_label.anchored_position = (DISPLAY_WIDTH/2, DISPLAY_HEIGHT-25)
barometric_data_label.scale = (1)
barometric_data_label.color = text_white

altitude_label = label.Label(medium_font)
# Anchor point bottom right of text
altitude_label.anchor_point = (1.0, 1.0)
altitude_label.anchored_position = (470, DISPLAY_HEIGHT)
altitude_label.scale = (1)
altitude_label.color = text_gray

altitude_data_label = label.Label(medium_font)
altitude_data_label.anchor_point = (1.0, 1.0)
altitude_data_label.anchored_position = (470, DISPLAY_HEIGHT-25)
altitude_data_label.scale = (1)
altitude_data_label.color = text_white

vbat_label = label.Label(medium_font)
vbat_label.anchor_point = (1.0, 0.0)
vbat_label.anchored_position = (DISPLAY_WIDTH-15, 5)
vbat_label.scale = (1)

plugbmp_label = label.Label(medium_font)
plugbmp_label.anchor_point = (1.0, 0.0)
plugbmp_label.scale = (1)

greenbmp_label = label.Label(medium_font)
greenbmp_label.anchor_point = (1.0, 0.0)
greenbmp_label.scale = (1)

bluebmp_label = label.Label(medium_font)
bluebmp_label.anchor_point = (1.0, 0.0)
bluebmp_label.scale = (1)

yellowbmp_label = label.Label(medium_font)
yellowbmp_label.anchor_point = (1.0, 0.0)
yellowbmp_label.scale = (1)

orangebmp_label = label.Label(medium_font)
orangebmp_label.anchor_point = (1.0, 0.0)
orangebmp_label.scale = (1)

redbmp_label = label.Label(medium_font)
redbmp_label.anchor_point = (1.0, 0.0)
redbmp_label.scale = (1)

# ============= Shadow & Outline Font Styles ===========
temp_data_shadow = label.Label(huge_font)
temp_data_shadow.anchor_point = (0.5, 1.0)
temp_data_shadow.anchored_position = (DISPLAY_WIDTH/2+2, 200+2)
temp_data_shadow.scale = (1)
temp_data_shadow.color = text_black

# Load Bitmap to tile grid first (Background Layer)
DiskBMP = displayio.OnDiskBitmap("/images/Astral_Fruit_8bit.bmp")
tile_grid = displayio.TileGrid(
    DiskBMP,
    pixel_shader=DiskBMP.pixel_shader,
    width=1,
    height=1,
    tile_width=DISPLAY_WIDTH,
    tile_height=DISPLAY_HEIGHT)

# Load battery voltage icons (from 1 sprite sheet image)
sprite_sheet, palette = adafruit_imageload.load("/icons/vbat_spritesheet.bmp",
                                                bitmap=displayio.Bitmap,
                                                palette=displayio.Palette)
sprite = displayio.TileGrid(sprite_sheet, pixel_shader=palette,
                            width=1,
                            height=1,
                            tile_width=11,
                            tile_height=20,
                            default_tile=3)
sprite_group = displayio.Group(scale=1)
sprite_group.append(sprite)
sprite_group.x = 470
sprite_group.y = 5

# Create sub-groups
text_group = displayio.Group()
text_group.append(tile_grid)
temp_group = displayio.Group()
main_group = displayio.Group()

# Add sub-groups to main display group
main_group.append(text_group)
main_group.append(temp_group)
main_group.append(sprite_group)

# Label Display Group (foreground layer)
text_group.append(hello_label)
text_group.append(date_label)
text_group.append(time_label)
text_group.append(vbat_label)
temp_group.append(temp_label)
temp_group.append(temp_data_shadow)
temp_group.append(temp_data_label)
text_group.append(humidity_label)
text_group.append(humidity_data_label)
text_group.append(barometric_label)
text_group.append(barometric_data_label)
text_group.append(altitude_label)
text_group.append(altitude_data_label)
text_group.append(plugbmp_label)
text_group.append(greenbmp_label)
text_group.append(bluebmp_label)
text_group.append(yellowbmp_label)
text_group.append(orangebmp_label)
text_group.append(redbmp_label)
display.show(main_group)

display_duty_cycle = 50000  # Brightness Values from 0 to 65000
brightness = pwmio.PWMOut(
        board.D2,
        frequency=500,
        duty_cycle=display_duty_cycle)

# source_index = 0
had_a_fix = False
last_print = time.monotonic()
while True:
    gc.collect()
    gps.update()
    if gps.timestamp_utc and not had_a_fix:
        # print("Setting the time")
        the_rtc.datetime = gps.datetime
        TIMEZONE = int(-4)
        # Below line causing: Error: overflow converting long int to machine word
        the_rtc.datetime = time.localtime(int(time.time() + TIMEZONE * 3600))
        had_a_fix = True
    # Every second print out current time from GPS, RTC and time.localtime()
    current = time.monotonic()
    if current - last_print >= 1.0:
        last_print = current
        if not gps.timestamp_utc:
            date_label.text = "RTC Set"
            time_label.text = "{}".format(_format_time(the_rtc.datetime))
            continue
        date_label.text = "{}".format(_format_date(the_rtc.datetime))
        time_label.text = "{}".format(_format_time(the_rtc.datetime))

    # Label.text in the loop for sensor data updates
    hello_label.text = ""
    # Changes battery voltage color depending on charge level
    if vbat_label.text >= str(4.23):
        vbat_label.color = text_white
        sprite[0] = 3
    elif vbat_label.text >= str(4.10) and vbat_label.text <= str(4.22):
        vbat_label.color = text_green
        sprite[0] = 1
    elif vbat_label.text >= str(4.00) and vbat_label.text <= str(4.09):
        vbat_label.color = text_lightblue
        sprite[0] = 0
    elif vbat_label.text >= str(3.90) and vbat_label.text <= str(3.99):
        vbat_label.color = text_yellow
        sprite[0] = 5
    elif vbat_label.text >= str(3.80) and vbat_label.text <= str(3.89):
        vbat_label.color = text_orange
        sprite[0] = 2
    elif vbat_label.text <= str(3.79):
        vbat_label.color = text_red
        sprite[0] = 4
    else:
        vbat_label.color = text_white
    gc.collect()

    # source_index += 1
    # print(source_index)
    vbat_label.text = "{:.2f}".format(vbat)
    temp_label.text = "°F"
    temperature = "{:.1f}".format(bmp280.temperature*1.8+32)
    temp_data_shadow.text = temperature
    temp_data_label.text = temperature
    humidity_label.text = "Humidity"
    humidity_data_label.text = "{:.1f} %".format(sht31d.relative_humidity)
    altitude_label.text = "Altitude"
    altitude_data_label.text = "{:.1f} f".format(bmp280.altitude*3.28)
    barometric_label.text = "Pressure"
    barometric_data_label.text = f"{bmp280.pressure:.1f}"

    # Serial printout for debugging
    # print("Temperature: {:.1f} F".format(bmp280.temperature*1.8+32))
    # print("Humidity: {:.1f} %".format(sht31d.relative_humidity))
    # print("Barometric pressure:", bmp280.pressure)
    # print("Altitude: {:.1f} m".format(bmp280.altitude))
    # print("VBat voltage: {:.2f}".format(vbat))
    # print("Background Index Count: {:.2f}".format(source_index))

    if take_screenshot is True and had_a_fix is True:  # and source_index > 20:
        print("Taking Screenshot... ")
        save_pixels("/sd/screenshot.bmp", display)
        print("Screenshot taken")
        time.sleep(30.0)
    else:
        # take_screenshot = False
        pass
    time.sleep(30.0)
    pass
