# Todbot's QT Eyes
Gator Eyes by DJDevon3

If you find the iris isn't correctly removing the white section it's because you must specific the color to be removed using GIMP's>tools>map>color map. Use the color index of the color you want to be removed.
`iris_pal.make_transparent(244)` in this case white is index color 244 within the BMP color pallete for this particular image.

https://user-images.githubusercontent.com/49322231/227809892-15315a96-636d-402e-b265-6fd26c661dcf.mp4

These were designed to be used in my [Halloween 2022 Dragon Skull Mask](https://github.com/DJDevon3/My_Circuit_Python_Projects/tree/main/Multi-Board%20Projects/Dragon%20Mask%20Halloween%202022).

The projects in this section are specifically for Adafruit ESP32-S2 based boards running Circuit Python.
