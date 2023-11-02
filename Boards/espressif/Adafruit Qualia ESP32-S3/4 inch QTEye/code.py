from displayio import release_displays
release_displays()

import time
import displayio
import busio
import board
import adafruit_imageload
import dotclockframebuffer
from framebufferio import FramebufferDisplay

init_sequence_hd40015c40 = bytes((
    b'\xff\x010'
    b'\xff\x01R'
    b'\xff\x01\x01'
    b'\xe3\x01\x00'
    b'\n\x01\x11'
    b'#\x01\xa0'
    b'$\x012'
    b'%\x01\x12'
    b'&\x01.'
    b"'\x01."
    b')\x01\x02'
    b'*\x01\xcf'
    b'2\x014'
    b'8\x01\x9c'
    b'9\x01\xa7'
    b":\x01'"
    b';\x01\x94'
    b'B\x01m'
    b'C\x01\x83'
    b'\x81\x01\x00'
    b'\x91\x01g'
    b'\x92\x01g'
    b'\xa0\x01R'
    b'\xa1\x01P'
    b'\xa4\x01\x9c'
    b'\xa7\x01\x02'
    b'\xa8\x01\x02'
    b'\xa9\x01\x02'
    b'\xaa\x01\xa8'
    b'\xab\x01('
    b'\xae\x01\xd2'
    b'\xaf\x01\x02'
    b'\xb0\x01\xd2'
    b'\xb2\x01&'
    b'\xb3\x01&'
    b'\xff\x010'
    b'\xff\x01R'
    b'\xff\x01\x02'
    b'\xb1\x01\n'
    b'\xd1\x01\x0e'
    b'\xb4\x01/'
    b'\xd4\x01-'
    b'\xb2\x01\x0c'
    b'\xd2\x01\x0c'
    b'\xb3\x010'
    b'\xd3\x01*'
    b'\xb6\x01\x1e'
    b'\xd6\x01\x16'
    b'\xb7\x01;'
    b'\xd7\x015'
    b'\xc1\x01\x08'
    b'\xe1\x01\x08'
    b'\xb8\x01\r'
    b'\xd8\x01\r'
    b'\xb9\x01\x05'
    b'\xd9\x01\x05'
    b'\xbd\x01\x15'
    b'\xdd\x01\x15'
    b'\xbc\x01\x13'
    b'\xdc\x01\x13'
    b'\xbb\x01\x12'
    b'\xdb\x01\x10'
    b'\xba\x01\x11'
    b'\xda\x01\x11'
    b'\xbe\x01\x17'
    b'\xde\x01\x17'
    b'\xbf\x01\x0f'
    b'\xdf\x01\x0f'
    b'\xc0\x01\x16'
    b'\xe0\x01\x16'
    b'\xb5\x01.'
    b'\xd5\x01?'
    b'\xb0\x01\x03'
    b'\xd0\x01\x02'
    b'\xff\x010'
    b'\xff\x01R'
    b'\xff\x01\x03'
    b'\x08\x01\t'
    b'\t\x01\n'
    b'\n\x01\x0b'
    b'\x0b\x01\x0c'
    b'(\x01"'
    b'*\x01\xe9'
    b'+\x01\xe9'
    b'4\x01Q'
    b'5\x01\x01'
    b'6\x01&'
    b'7\x01\x13'
    b'@\x01\x07'
    b'A\x01\x08'
    b'B\x01\t'
    b'C\x01\n'
    b'D\x01"'
    b'E\x01\xdb'
    b'F\x01\xdc'
    b'G\x01"'
    b'H\x01\xdd'
    b'I\x01\xde'
    b'P\x01\x0b'
    b'Q\x01\x0c'
    b'R\x01\r'
    b'S\x01\x0e'
    b'T\x01"'
    b'U\x01\xdf'
    b'V\x01\xe0'
    b'W\x01"'
    b'X\x01\xe1'
    b'Y\x01\xe2'
    b'\x80\x01\x1e'
    b'\x81\x01\x1e'
    b'\x82\x01\x1f'
    b'\x83\x01\x1f'
    b'\x84\x01\x05'
    b'\x85\x01\n'
    b'\x86\x01\n'
    b'\x87\x01\x0c'
    b'\x88\x01\x0c'
    b'\x89\x01\x0e'
    b'\x8a\x01\x0e'
    b'\x8b\x01\x10'
    b'\x8c\x01\x10'
    b'\x8d\x01\x00'
    b'\x8e\x01\x00'
    b'\x8f\x01\x1f'
    b'\x90\x01\x1f'
    b'\x91\x01\x1e'
    b'\x92\x01\x1e'
    b'\x93\x01\x02'
    b'\x94\x01\x04'
    b'\x96\x01\x1e'
    b'\x97\x01\x1e'
    b'\x98\x01\x1f'
    b'\x99\x01\x1f'
    b'\x9a\x01\x05'
    b'\x9b\x01\t'
    b'\x9c\x01\t'
    b'\x9d\x01\x0b'
    b'\x9e\x01\x0b'
    b'\x9f\x01\r'
    b'\xa0\x01\r'
    b'\xa1\x01\x0f'
    b'\xa2\x01\x0f'
    b'\xa3\x01\x00'
    b'\xa4\x01\x00'
    b'\xa5\x01\x1f'
    b'\xa6\x01\x1f'
    b'\xa7\x01\x1e'
    b'\xa8\x01\x1e'
    b'\xa9\x01\x01'
    b'\xaa\x01\x03'
    b'\xff\x010'
    b'\xff\x01R'
    b'\xff\x01\x00'
    b'6\x01\n'
    b'\x11\x81\x00\xc8'
    b')\x81\x00d'
))

tft_pins = dict(board.TFT_PINS)

tft_timings = {
    "frequency": 16000000,
    "width": 720,
    "height": 720,

    "hsync_pulse_width": 2,
    "hsync_back_porch": 44,
    "hsync_front_porch": 46,
    "hsync_idle_low": False,

    "vsync_pulse_width": 16,
    "vsync_back_porch": 16,
    "vsync_front_porch": 50,
    "vsync_idle_low": False,

    "pclk_active_high": True,
    "pclk_idle_high": False,
    "de_idle_high": False,
}

board.I2C().deinit()
i2c = busio.I2C(board.SCL, board.SDA)
tft_io_expander = dict(board.TFT_IO_EXPANDER)
#tft_io_expander['i2c_address'] = 0x38 # uncomment for rev B
dotclockframebuffer.ioexpander_send_init_sequence(i2c, init_sequence_hd40015c40, **tft_io_expander)
i2c.deinit()

bitmap = displayio.OnDiskBitmap("/images/eye_ball_720p.bmp")
iris_bitmap, iris_pal = adafruit_imageload.load("images/iris-720p.bmp")
iris_pal.make_transparent(249)

fb = dotclockframebuffer.DotClockFramebuffer(**tft_pins, **tft_timings)
display = FramebufferDisplay(fb, auto_refresh=False)

dw, dh = 720,720  # display dimensions
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
