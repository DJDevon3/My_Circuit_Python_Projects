import time
import board
import digitalio
import displayio
import adafruit_sdcard
from adafruit_bitmapsaver import save_pixels
import storage
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
from adafruit_hx8357 import HX8357

# This sketch should also work for the 2.5" TFT Featherwing, just change the size.
DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 320
take_screenshot = False  # True makes a BMP screenshot :)

# Initialize TFT Display
i2c = board.I2C()
spi = board.SPI()
cs = digitalio.DigitalInOut(board.D5)
sdcard = adafruit_sdcard.SDCard(spi, cs)
vfs = storage.VfsFat(sdcard)
displayio.release_displays()
tft_cs = board.D9
tft_dc = board.D10
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = HX8357(display_bus, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT)
virtual_root = "/sd"
storage.mount(vfs, virtual_root)

# Some quick colors. 
text_black = (0x000000)
text_blue = (0x0000FF)
text_cyan = (0x00FFFF)
text_gray = (0x808080)
text_green = (0x00FF00)
text_lightblue = (0x90C7FF)
text_magenta = (0xFF00FF)
text_orange = (0xFFA500)
text_red = (0xFF0000)
text_white = (0xFFFFFF)
text_yellow = (0xFFFF00)
text_ultralightblue = (0xC7E3FF)

# Load Fonts including massive 121 BDF font.
small_font = bitmap_font.load_font("/fonts/Arial-12.bdf")
medium_font = bitmap_font.load_font("/fonts/Arial-16.bdf")
large_font = bitmap_font.load_font("/fonts/GoodTimesRg-Regular-80.bdf")
huge_font = bitmap_font.load_font("/fonts/GoodTimesRg-Regular-121.bdf")


# ============= Foreground Font Labels =============
hello_label = label.Label(small_font)
hello_label.anchor_point = (0.5, 1.0)
hello_label.anchored_position = (DISPLAY_WIDTH/2, 15)
hello_label.scale = (1)
hello_label.color = text_white

ice_label = label.Label(huge_font)
ice_label.anchor_point = (0.5, 1.0)
ice_label.anchored_position = (DISPLAY_WIDTH/2, 110)
ice_label.scale = (1)
ice_label.color = text_ultralightblue

shadow_label = label.Label(medium_font)
shadow_label.anchor_point = (0.5, 1.0)
shadow_label.anchored_position = (150, 155)
shadow_label.scale = (2)
shadow_label.color = text_orange

outline_label = label.Label(medium_font)
outline_label.anchor_point = (0.5, 1.0)
outline_label.anchored_position = (350, 155)
outline_label.scale = (2)
outline_label.color = text_orange

usa_label = label.Label(large_font)
usa_label.anchor_point = (0.5, 1.0)
usa_label.anchored_position = (DISPLAY_WIDTH/2, 225)
usa_label.scale = (1)
usa_label.color = text_lightblue

chrome_label = label.Label(large_font)
chrome_label.anchor_point = (0.5, 1.0)
chrome_label.anchored_position = (DISPLAY_WIDTH/2, 300)
chrome_label.scale = (1)
chrome_label.color = text_white


# ============= Font Styles =============
ice_outline1 = label.Label(huge_font)
ice_outline1.anchor_point = (0.5, 1.0)
ice_outline1.anchored_position = (DISPLAY_WIDTH/2-2, 110-2)
ice_outline1.scale = (1)
ice_outline1.color = text_white

ice_outline2 = label.Label(huge_font)
ice_outline2.anchor_point = (0.5, 1.0)
ice_outline2.anchored_position = (DISPLAY_WIDTH/2-2, 110+2)
ice_outline2.scale = (1)
ice_outline2.color = text_gray

ice_outline3 = label.Label(huge_font)
ice_outline3.anchor_point = (0.5, 1.0)
ice_outline3.anchored_position = (DISPLAY_WIDTH/2+2, 110-2)
ice_outline3.scale = (1)
ice_outline3.color = text_lightblue

ice_outline4 = label.Label(huge_font)
ice_outline4.anchor_point = (0.5, 1.0)
ice_outline4.anchored_position = (DISPLAY_WIDTH/2+2, 110+2)
ice_outline4.scale = (1)
ice_outline4.color = text_gray

shadow_shadow = label.Label(medium_font)
shadow_shadow.anchor_point = (0.5, 1.0)
shadow_shadow.anchored_position = (150, 155+2)
shadow_shadow.scale = (2)
shadow_shadow.color = text_black

outline_outline1 = label.Label(medium_font)
outline_outline1.anchor_point = (0.5, 1.0)
outline_outline1.anchored_position = (350-2, 155-2)
outline_outline1.scale = (2)
outline_outline1.color = text_black

outline_outline2 = label.Label(medium_font)
outline_outline2.anchor_point = (0.5, 1.0)
outline_outline2.anchored_position = (350-2, 155+2)
outline_outline2.scale = (2)
outline_outline2.color = text_black

outline_outline3 = label.Label(medium_font)
outline_outline3.anchor_point = (0.5, 1.0)
outline_outline3.anchored_position = (350+2, 155-2)
outline_outline3.scale = (2)
outline_outline3.color = text_black

outline_outline4 = label.Label(medium_font)
outline_outline4.anchor_point = (0.5, 1.0)
outline_outline4.anchored_position = (350+2, 155+2)
outline_outline4.scale = (2)
outline_outline4.color = text_black

usa_outline1 = label.Label(large_font)
usa_outline1.anchor_point = (0.5, 1.0)
usa_outline1.anchored_position = (DISPLAY_WIDTH/2-3, 225-3)
usa_outline1.scale = (1)
usa_outline1.color = text_white

usa_outline2 = label.Label(large_font)
usa_outline2.anchor_point = (0.5, 1.0)
usa_outline2.anchored_position = (DISPLAY_WIDTH/2-3, 225+3)
usa_outline2.scale = (1)
usa_outline2.color = text_red

usa_outline3 = label.Label(large_font)
usa_outline3.anchor_point = (0.5, 1.0)
usa_outline3.anchored_position = (DISPLAY_WIDTH/2+3, 225-3)
usa_outline3.scale = (1)
usa_outline3.color = text_blue

usa_outline4 = label.Label(large_font)
usa_outline4.anchor_point = (0.5, 1.0)
usa_outline4.anchored_position = (DISPLAY_WIDTH/2+3, 225+3)
usa_outline4.scale = (1)
usa_outline4.color = text_white

chrome_outline1 = label.Label(large_font)
chrome_outline1.anchor_point = (0.5, 1.0)
chrome_outline1.anchored_position = (DISPLAY_WIDTH/2-2, 300-2)
chrome_outline1.scale = (1)
chrome_outline1.color = text_gray

chrome_outline2 = label.Label(large_font)
chrome_outline2.anchor_point = (0.5, 1.0)
chrome_outline2.anchored_position = (DISPLAY_WIDTH/2-2, 300+2)
chrome_outline2.scale = (1)
chrome_outline2.color = text_black

chrome_outline3 = label.Label(large_font)
chrome_outline3.anchor_point = (0.5, 1.0)
chrome_outline3.anchored_position = (DISPLAY_WIDTH/2+2, 300-2)
chrome_outline3.scale = (1)
chrome_outline3.color = text_white

chrome_outline4 = label.Label(large_font)
chrome_outline4.anchor_point = (0.5, 1.0)
chrome_outline4.anchored_position = (DISPLAY_WIDTH/2+2, 300+2)
chrome_outline4.scale = (1)
chrome_outline4.color = text_gray


# Load Bitmap to tile grid first (background layer)
bitmap = displayio.OnDiskBitmap("/images/purbokeh_8.bmp")
tile_grid = displayio.TileGrid(
    bitmap,
    pixel_shader=bitmap.pixel_shader,
    width=1,
    height=1,
    tile_width=DISPLAY_WIDTH,
    tile_height=DISPLAY_HEIGHT)

text_group = displayio.Group()
text_group.append(tile_grid)

main_group = displayio.Group()
main_group.append(text_group)

# Text Foreground Layer
# It's very important to append style before its foreground text.
text_group.append(hello_label)

text_group.append(ice_outline1)
text_group.append(ice_outline2)
text_group.append(ice_outline3)
text_group.append(ice_outline4)
text_group.append(ice_label)

text_group.append(shadow_shadow)
text_group.append(shadow_label)

text_group.append(outline_outline1)
text_group.append(outline_outline2)
text_group.append(outline_outline3)
text_group.append(outline_outline4)
text_group.append(outline_label)

text_group.append(usa_outline1)
text_group.append(usa_outline2)
text_group.append(usa_outline3)
text_group.append(usa_outline4)
text_group.append(usa_label)

text_group.append(chrome_outline1)
text_group.append(chrome_outline2)
text_group.append(chrome_outline3)
text_group.append(chrome_outline4)
text_group.append(chrome_label)

display.show(main_group)

ice_demo = "ICE"
shadow_demo = "Shadow"
outline_demo = "Outline"
usa_demo = "USA"
chrome_demo = "CHROME"

while True:
    hello_label.text = "Font Style Demo"
    
    ice_outline1.text = ice_demo
    ice_outline2.text = ice_demo
    ice_outline3.text = ice_demo
    ice_outline4.text = ice_demo
    ice_label.text = ice_demo
    
    shadow_shadow.text = shadow_demo
    shadow_label.text = shadow_demo
    
    outline_outline1.text = outline_demo
    outline_outline2.text = outline_demo
    outline_outline3.text = outline_demo
    outline_outline4.text = outline_demo
    outline_label.text = outline_demo
    
    usa_outline1.text = usa_demo
    usa_outline2.text = usa_demo
    usa_outline3.text = usa_demo
    usa_outline4.text = usa_demo
    usa_label.text = usa_demo
    
    chrome_outline1.text = chrome_demo
    chrome_outline2.text = chrome_demo
    chrome_outline3.text = chrome_demo
    chrome_outline4.text = chrome_demo
    chrome_label.text = chrome_demo
    
    time.sleep(30.0)
    # if take_screenshot variable is set to true
    if take_screenshot:
        print("Taking Screenshot... ")
        save_pixels("/sd/screenshot.bmp", display)
        print("Screenshot taken")
    else:
        # take_screenshot False takes no screenshot
        pass
pass
