# 192x128 12-panel display

### Hardware
- 12x [64x32 5mm Pitch RGB Matrix Panels](https://www.adafruit.com/product/2277) (includes 1 20cm IDC cable & 1 power cable splitter per panel)
- 1x [Adafruit MatrixPortal S3](https://www.adafruit.com/product/5778) 
- 1x [Adafruit BME688 I2C sensor module for temp, humidity, pressure, & VOC](https://www.adafruit.com/product/5046)
- 3x [30cm IDC cable](https://www.amazon.com/dp/B07FZWH9S6) (you will need these for serpentine connections)
- 2x [5V 18A Meanwell PSU](https://www.amazon.com/dp/B018TEAPRQ)
- 2x 3-prong (USA spec) PC power cord. Most people have an extra laying around. If you don't have one you'll need to source one.
- 2x [AC Rocker Switch Socket](https://www.amazon.com/dp/B07RQV2NPN)
- 2x [20A Fuses](https://www.amazon.com/dp/B0B1CPZ7XH)
- [3D Printed Brackets available on Printables](https://www.printables.com/model/578204-hub75-5mm-pitch-4-panel-bracket)



![12_Panels](https://github.com/DJDevon3/My_Circuit_Python_Projects/assets/49322231/bb3ea441-6083-4da1-8876-994200ea287f)

### Rear view of panels (flipped downward)
- When displayed the controller will be in the top right position
- Shows serpentine nature of the overall IDC ribbon connections
- 3D printed brackets are hefty enough to support the weight
- There are different types of brackets I specifically designed for these 5mm pitch panels

![Brackets_Serpentine](https://github.com/DJDevon3/My_Circuit_Python_Projects/assets/49322231/eec78007-a293-42a4-8191-aef792ff34d9)

### Front view of the panel arrangement.
- When displayed the controller will be in the top right position.
- Notice that every 2nd rows of panels must be physically mounted upside down
- This is how the RGBMatrix library expects them to be oriented

![12-Panel_Arrangement](https://github.com/DJDevon3/My_Circuit_Python_Projects/assets/49322231/1daa959e-2b40-4c0f-a766-a66f73924987)

Power supply and wire routing. I use 2x 5V 20A meanwell power supplies.

![IMG_1163](https://github.com/DJDevon3/My_Circuit_Python_Projects/assets/49322231/c276226f-f087-406f-b61a-a1f137811b7a)

Includes fireworks animation example coded by Todbot

https://github.com/DJDevon3/My_Circuit_Python_Projects/assets/49322231/36f9f95f-79bd-4e58-98f7-084944f9ba2c

