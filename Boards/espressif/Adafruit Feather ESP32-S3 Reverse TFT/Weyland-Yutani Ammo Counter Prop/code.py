import time
import board
import displayio
import digitalio
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font

display = board.DISPLAY
DISPLAY_WIDTH = 240
DISPLAY_HEIGHT = 135

fire_btn = digitalio.DigitalInOut(board.D0)
fire_btn.direction = digitalio.Direction.INPUT
fire_btn.pull = digitalio.Pull.UP

reset_btn = digitalio.DigitalInOut(board.D2)
reset_btn.direction = digitalio.Direction.INPUT
reset_btn.pull = digitalio.Pull.DOWN

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

font1 = bitmap_font.load_font("/fonts/weyland10.bdf")
font2 = bitmap_font.load_font("/fonts/weyland12.bdf")
font3 = bitmap_font.load_font("/fonts/weyland14.bdf")
font4 = bitmap_font.load_font("/fonts/weyland36.bdf")
font5 = bitmap_font.load_font("/fonts/weyland72.bdf")

header_label = label.Label(font3)
header_label.anchor_point = (0.5, 0.5)
header_label.anchored_position = (DISPLAY_WIDTH / 2, 10)
header_label.color = TEXT_RED

subheader_label = label.Label(font2)
subheader_label.anchor_point = (0.5, 0.5)
subheader_label.anchored_position = (DISPLAY_WIDTH / 2, 35)
subheader_label.color = TEXT_BLUE

result_label = label.Label(font5)
result_label.anchor_point = (0.5, 1.0)
result_label.anchored_position = (DISPLAY_WIDTH / 2, DISPLAY_HEIGHT - 2)
result_label.color = TEXT_YELLOW

main_group = displayio.Group()
main_group.append(header_label)
main_group.append(subheader_label)
main_group.append(result_label)
display.root_group = main_group

DEBOUNCE_DELAY = 0.1
ammo = 100
last_reset_state = False
last_reset_time = time.monotonic()
last_fire_state = False
last_fire_time = time.monotonic()

header_label.text = "Weyland-Yutani"
subheader_label.text = "A Stark Subsidiary"
while True:
    current_time = time.monotonic()

    if current_time - last_reset_time > DEBOUNCE_DELAY:
        current_reset_state = reset_btn.value
        if current_reset_state != last_reset_state:
            last_reset_state = current_reset_state
            if current_reset_state:
                ammo = 99
                result_label.text = str(ammo)
                print("reset")
            last_reset_time = current_time

    if current_time - last_fire_time > DEBOUNCE_DELAY:
        current_fire_state = fire_btn.value
        if current_fire_state != last_fire_state:
            last_fire_state = current_fire_state
            if current_fire_state:
                if ammo > 0:
                    ammo -= 1
                    result_label.text = str(ammo)
                    print("Fire!")
                else:
                    print("Reload!")
                    pass
            last_fire_time = current_time
