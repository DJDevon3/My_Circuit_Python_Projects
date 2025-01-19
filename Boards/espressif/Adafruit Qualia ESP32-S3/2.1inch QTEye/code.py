from displayio import release_displays
release_displays()

import time
import displayio
import busio
import board
import adafruit_imageload
import dotclockframebuffer
from framebufferio import FramebufferDisplay

init_sequence_TL021WVC02 = bytes((
    0xff, 0x05, 0x77, 0x01, 0x00, 0x00, 0x10,
    0xc0, 0x02, 0x3b, 0x00,
    0xc1, 0x02, 0x0b, 0x02,
    0xc2, 0x02, 0x00, 0x02,
    0xcc, 0x01, 0x10,
    0xcd, 0x01, 0x08,
    0xb0, 0x10, 0x02, 0x13, 0x1b, 0x0d, 0x10, 0x05, 0x08, 0x07, 0x07, 0x24, 0x04, 0x11, 0x0e, 0x2c, 0x33, 0x1d,
    0xb1, 0x10, 0x05, 0x13, 0x1b, 0x0d, 0x11, 0x05, 0x08, 0x07, 0x07, 0x24, 0x04, 0x11, 0x0e, 0x2c, 0x33, 0x1d,
    0xff, 0x05, 0x77, 0x01, 0x00, 0x00, 0x11,
    0xb0, 0x01, 0x5d,
    0xb1, 0x01, 0x43,
    0xb2, 0x01, 0x81,
    0xb3, 0x01, 0x80,
    0xb5, 0x01, 0x43,
    0xb7, 0x01, 0x85,
    0xb8, 0x01, 0x20,
    0xc1, 0x01, 0x78,
    0xc2, 0x01, 0x78,
    0xd0, 0x01, 0x88,
    0xe0, 0x03, 0x00, 0x00, 0x02,
    0xe1, 0x0b, 0x03, 0xa0, 0x00, 0x00, 0x04, 0xa0, 0x00, 0x00, 0x00, 0x20, 0x20,
    0xe2, 0x0d, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0xe3, 0x04, 0x00, 0x00, 0x11, 0x00,
    0xe4, 0x02, 0x22, 0x00,
    0xe5, 0x10, 0x05, 0xec, 0xa0, 0xa0, 0x07, 0xee, 0xa0, 0xa0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0xe6, 0x04, 0x00, 0x00, 0x11, 0x00,
    0xe7, 0x02, 0x22, 0x00,
    0xe8, 0x10, 0x06, 0xed, 0xa0, 0xa0, 0x08, 0xef, 0xa0, 0xa0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0xeb, 0x07, 0x00, 0x00, 0x40, 0x40, 0x00, 0x00, 0x00,
    0xed, 0x10, 0xff, 0xff, 0xff, 0xba, 0x0a, 0xbf, 0x45, 0xff, 0xff, 0x54, 0xfb, 0xa0, 0xab, 0xff, 0xff, 0xff,
    0xef, 0x06, 0x10, 0x0d, 0x04, 0x08, 0x3f, 0x1f,
    0xff, 0x05, 0x77, 0x01, 0x00, 0x00, 0x13,
    0xef, 0x01, 0x08,
    0xff, 0x05, 0x77, 0x01, 0x00, 0x00, 0x00,
    0x36, 0x01, 0x00,
    0x3a, 0x01, 0x60,
    0x11, 0x80, 0x64,
    0x29, 0x80, 0x32,
))

tft_pins = dict(board.TFT_PINS)

tft_timings = {
    "frequency": 16_000_000,
    "width": 480,
    "height": 480,
    "hsync_pulse_width": 20,
    "hsync_front_porch": 40,
    "hsync_back_porch": 40,
    "vsync_pulse_width": 10,
    "vsync_front_porch": 40,
    "vsync_back_porch": 40,
    "hsync_idle_low": False,
    "vsync_idle_low": False,
    "de_idle_high": False,
    "pclk_active_high": True,
    "pclk_idle_high": False,
}

board.I2C().deinit()
i2c = busio.I2C(board.SCL, board.SDA)
tft_io_expander = dict(board.TFT_IO_EXPANDER)
#tft_io_expander['i2c_address'] = 0x38 # uncomment for rev B
dotclockframebuffer.ioexpander_send_init_sequence(i2c, init_sequence_TL021WVC02, **tft_io_expander)
i2c.deinit()

bitmap = displayio.OnDiskBitmap("/images/eye_ball_720p.bmp")
iris_bitmap, iris_pal = adafruit_imageload.load("images/iris-720p.bmp")
iris_pal.make_transparent(249)

fb = dotclockframebuffer.DotClockFramebuffer(**tft_pins, **tft_timings)
display = FramebufferDisplay(fb, auto_refresh=False)

dw, dh = 480,480  # display dimensions
# compute or declare some useful info about the eyes
iris_w, iris_h = iris_bitmap.width, iris_bitmap.height  # iris is normally 110x110
iris_cx, iris_cy = dw//2 - iris_w//2, dh//2 - iris_h//2
r = 15  # allowable deviation from center for iris

# Create a TileGrid to hold the bitmap
tile_grid = displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader)
iris = displayio.TileGrid(iris_bitmap, pixel_shader=iris_pal, x=iris_cx,y=iris_cy)
# Center the image
tile_grid.x -= (bitmap.width - display.width) // 2
tile_grid.y -= (bitmap.height - display.height) // 2

# Create a Group to hold the TileGrid
group = displayio.Group()

# Add the TileGrid to the Group
group.append(tile_grid)
group.append(iris)

# Add the Group to the Display
display.root_group = group

display.auto_refresh = True

# Loop forever so you can enjoy your image
while True:
    for iris.x in range(100,201,10):
        iris.x += 1
        time.sleep(0.1)
    for iris.x in range(200,100,-10):
        iris.x -= 1
        time.sleep(0.1)
    pass