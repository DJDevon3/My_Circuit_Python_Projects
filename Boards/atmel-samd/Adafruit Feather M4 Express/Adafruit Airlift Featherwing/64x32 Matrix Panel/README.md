# Matrix Panel Display
I don't have a Matrix Portal M4 so I basically replicated one using a Feather M4 Express & Airlift Featherwing & custom wiring to a 64x32 Matrix Panel
- [Matrix Panel Display Learn Guide](https://learn.adafruit.com/weather-display-matrix/overview) by John Park 2020 
- updated by DJDevon3 2023
- Coded for Circuit Python 8.2.x
- Updated to use OpenWeatherMap.org 2.5 onecall API
- Condensed code into 1 code.py page
- Uses lattitude/longitude for weather & time
- Added exception handler for wind gust key:value. Gust is a value that might not always be available.

### Requirements:
- [OpenWeatherMap.org](https://www.OpenWeatherMap.org) Account with API Key (Free)
- [Adafruit 64x32 Matrix Panel](https://www.adafruit.com/product/2277)
- [Adafruit Feather M4 Express](https://www.adafruit.com/product/3857) + [Airlift Featherwing](https://www.adafruit.com/product/4264) OR [Matrix Portal M4](https://www.adafruit.com/product/4745)
- If you would rather use a [Matrix Portal S3](https://www.adafruit.com/product/5778) I have [plenty of examples here](https://github.com/DJDevon3/My_Circuit_Python_Projects/tree/main/Boards/espressif/Adafruit%20MatrixPortal%20S3).

### Manually Wiring Feather to Matrix Panel
- The 1st & 5th pins on the top row of the IDC are NC (not connected to anything).
  
![IDC_Wiring](https://github.com/DJDevon3/My_Circuit_Python_Projects/assets/49322231/0235c8fc-88f2-4948-b604-9b2829c80b34)

![IMG_1344](https://github.com/DJDevon3/My_Circuit_Python_Projects/assets/49322231/ad0c3e98-a7ab-4ba5-961f-ef6b04b22575)

![IMG_1340](https://github.com/DJDevon3/My_Circuit_Python_Projects/assets/49322231/378eb2fc-58b0-4718-a46e-7cba7d12a6b8)

![IMG_1341](https://github.com/DJDevon3/My_Circuit_Python_Projects/assets/49322231/36d33599-89b9-40af-a6ca-126250804d2d)
