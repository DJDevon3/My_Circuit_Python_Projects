# SPDX-FileCopyrightText: 2023 DJDevon3
#
# SPDX-License-Identifier: MIT
# Used with Adafruit MatrixPortal S3
# Coded for Circuit Python 8.x
# Fireworks code by Todbot

import time
import random
import board
import displayio
import rgbmatrix
import framebufferio
import adafruit_imageload
import rainbowio

displayio.release_displays()
DISPLAY_WIDTH = 192
DISPLAY_HEIGHT = 128
DISPLAY_ROTATION = 0
BIT_DEPTH = 2
AUTO_REFRESH = True


matrix = rgbmatrix.RGBMatrix(
    width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, bit_depth=BIT_DEPTH,
    rgb_pins=[
        board.MTX_R1,
        board.MTX_G1,
        board.MTX_B1,
        board.MTX_R2,
        board.MTX_G2,
        board.MTX_B2],
    addr_pins=[board.MTX_ADDRA, board.MTX_ADDRB, board.MTX_ADDRC, board.MTX_ADDRD],
    clock_pin=board.MTX_CLK,
    latch_pin=board.MTX_LAT,
    output_enable_pin=board.MTX_OE,
    tile=4,
    serpentine=True,
    doublebuffer=True)

# Associate the RGB matrix with a Display so we can use displayio
display = framebufferio.FramebufferDisplay(matrix, auto_refresh=AUTO_REFRESH, rotation=DISPLAY_ROTATION)

fireworks_count = 5
sprite_fname = "images/fireworks_spritesheet.bmp"
sprite_count = 30*1
sprite_w,sprite_h = 64,64

dw,dh = DISPLAY_WIDTH, DISPLAY_HEIGHT  # convenience values

sprite_sheet, sprite_palette = adafruit_imageload.load(sprite_fname)

maingroup = displayio.Group()  # all fireworks go on 'maingroup'
display.show(maingroup)

def random_xy():
    return random.randint(0, dw-sprite_w), random.randint(dh//2, dh//2+20)

def copy_palette(p):  # this is fastest way to copy a palette it seems
    new_p = displayio.Palette(len(p))
    for i in range(len(p)):  new_p[i] = p[i]
    return new_p

def new_colors(p):  # first two colors after bg seem to be the "tails" 
    p[1] = rainbowio.colorwheel( random.randint(0,255) )
    p[2] = rainbowio.colorwheel( random.randint(0,255) )
    
    
# holds list of sprites,sprite_index,x,y,launch_time
fireworks = [(None,0,0,0, 0) ] * fireworks_count
# make our fireworks    
for i in range(len(fireworks)):
    pal = copy_palette(sprite_palette)
    pal.make_transparent(0)  # make background color transparent
    x,y = random_xy()
    start_index = random.randint(0,sprite_count-1)  # pick random point in fireworks life to start
    fwsprite = displayio.TileGrid(sprite_sheet, pixel_shader=pal,
                            width = 1, height = 1,
                            tile_width = sprite_w, tile_height = sprite_h)
    fireworks[i]= (fwsprite, start_index, x, y, pal)  # add sprite, and initial index, x,y, palette
    maingroup.append(fwsprite)

while True:
    for i in range(len(fireworks)):
        (sprite, sprite_index, x,y, palette) = fireworks[i]  # get firework state
        # update firework state
        launching = sprite_index == 0 and random.random() < 0.9
        if launching:
            y = y - 3  # move towards top of screen
        else: 
            sprite_index = sprite_index + 1  # explode!
        # firework finished
        if sprite_index == sprite_count:
            sprite_index = 0   # firework is reborn, make a new x,y for it
            x,y = random_xy()  #random.randint(dw//4, 3*dw//4), random.randint(dh//2,dh//2+20)
            new_colors(palette)
        # update firework on screen
        sprite[0] = sprite_index  # set next sprite in animation
        sprite.x, sprite.y = x,y  # set its x,y
        # save the firework state
        fireworks[i] = (sprite, sprite_index, x,y, palette)
    time.sleep(0.008)  # determines our framerate