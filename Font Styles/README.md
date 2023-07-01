# Real Font Styles in Circuit Python

![](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Font%20Styles/example_output.png)

![](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Font%20Style%20Demo/screenshot.bmp)

![](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Font%20Style%20Demo/screenshot2.bmp)

# GUI Design for TFT's
I've figured out how to create drop shadow and outline font styles from scratch using
Adafruit's displayio tilegrid (x,y) coordinate system. This type of font styling is 100% impossible on Arduino with existing graphic libraries.
This is just one of hundreds of reasons for everyone to port their existing Arduino sketches to circuit python.
This demonstrates for TFT displays, graphics and GUI design, circuit python is far superior to Arduino.

# Bitmap Font Love/Hate Relationship
Bitmap fonts don't scale up well without pixelation and you cannot scale down a font lower than 1. 
The starting size of a font is the smallest it will ever possibly be. It's extremely
important to know the exact font size you want before you start creating your own font. BDF fonts are not TTF fonts, images never scale without artifacts.
In order to create clean looking fonts you must use a font designed for the pixel height you want to use. It's actually very easy to [create your own BDF fonts
with fontforge](https://learn.adafruit.com/custom-fonts-for-pyportal-circuitpython-display/overview) for each label's size need. Keep in mind the more fonts, labels, and bitmaps you load, the slower your TFT display will be because circut python is very RAM hungry, it's a trade-off.  

# Glyph Characters Spritesheet
Fonts in adafruits graphic library are treated like sprite sheets. 
The font characters (glyphs) are just a series of images so the more glyphs you have in a font the slower it will be.
It's important to remove & detach all glyphs that won't be used in order to optimize the font for your project.
With a highly optimized font it will hopefully leave you with enough memory overhead to play with font styles. :)
