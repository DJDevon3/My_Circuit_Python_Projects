# Matrix Panel Display
I don't have a Matrix Portal M4 so I basically replicated one using a Feather M4 Express & Airlift Featherwing & custom wiring to a 64x32 Matrix Panel
- [Matrix Panel Display Learn Guide](https://learn.adafruit.com/weather-display-matrix/overview) by John Park 2020 
- updated by DJDevon3 2023
- Coded for Circuit Python 8.2.x
- Updated to use OpenWeatherMap.org 2.5 onecall API
- Condensed code into 1 code.py page
- Uses latitude/longitude for weather & time
- Added exception handler for wind gust key:value. Gust is a JSON key that might not always be available.

### Required:
- [OpenWeatherMap.org](https://www.OpenWeatherMap.org) Account with API Key (Free)

### Hardware:
- [Adafruit 64x32 Matrix Panel](https://www.adafruit.com/product/2277)
- [5V 18A Power Supply](https://www.amazon.com/gp/product/B018TEAPRQ)
- [On/Off Rocker Safety Switch](https://www.amazon.com/gp/product/B07RQV2NPN)
- [Adafruit Feather M4 Express](https://www.adafruit.com/product/3857) + [Airlift Featherwing](https://www.adafruit.com/product/4264) OR [Matrix Portal M4](https://www.adafruit.com/product/4745)
- If you would rather use a [Matrix Portal S3](https://www.adafruit.com/product/5778) I have [plenty of examples here](https://github.com/DJDevon3/My_Circuit_Python_Projects/tree/main/Boards/espressif/Adafruit%20MatrixPortal%20S3).

### Manually Wiring Feather to Matrix Panel
- The 1st & 5th pins on the top row of the IDC are NC (not connected to anything).
  
![IDC_Wiring](https://github.com/DJDevon3/My_Circuit_Python_Projects/assets/49322231/ec4f888d-5c31-4563-a524-2a304d3d9f2a)

The above wiring corresponds with the Matrix setup in code.py
```py
matrix = rgbmatrix.RGBMatrix(
    width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, bit_depth=4,
    # R1, B1, G1, R2, B2, G2
    rgb_pins=[board.D6, board.D5, board.D9, board.D4, board.D10, board.SCL],
    # A, B, C, D
    addr_pins=[board.A5, board.A4, board.A3, board.A2],
    clock_pin=board.A1,
    latch_pin=board.RX,
    output_enable_pin=board.TX,
    doublebuffer=True)
```

![IMG_1344](https://github.com/DJDevon3/My_Circuit_Python_Projects/assets/49322231/ad0c3e98-a7ab-4ba5-961f-ef6b04b22575)

![IMG_1340](https://github.com/DJDevon3/My_Circuit_Python_Projects/assets/49322231/378eb2fc-58b0-4718-a46e-7cba7d12a6b8)

![IMG_1341](https://github.com/DJDevon3/My_Circuit_Python_Projects/assets/49322231/36d33599-89b9-40af-a6ca-126250804d2d)
