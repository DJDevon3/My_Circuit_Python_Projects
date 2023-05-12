## Feather RP2040 DVI & OBS Weather Station Overlay example

### Hardware Required:
- [Adafruit Feather RP2040 DVI](https://www.adafruit.com/product/5710)
- [HDMI Capture Adapter](https://www.adafruit.com/product/4669)

### Optional Hardware Used:
- [DPS310 (temperature & pressure) Sensor](https://www.adafruit.com/product/4494)
- [AHT20 (temperature & humidity) Sensor](https://www.adafruit.com/product/4566)

### Software Required:
- [OBS studio streaming software (Free)](https://obsproject.com/)

Example of project final output:
[![Watch the video](https://img.youtube.com/vi/05BcstyL144/maxresdefault.jpg)](https://youtu.be/05BcstyL144)


### Setup
- Power the Feather RP2040 DVI via PC USB so you can edit code.py
- Plug HDMI cable into Feather DVI output
- Plug other end of HDMI cable into HDMI capture dongle
- Plug HDMI capture dongle into PC USB port (acts as a video input source for OBS)
- Install & lauch OBS studio

### OBS Layering Advice
- OBS Layers sources from top to bottom (top source being the top most layer). You can re-order your sources (layers) with drag & drop.

### OBS Sources Setup
- Add HDMI capture source (appears as "USB Video" device)

I have an HDMI splitter so it also outputs to a 3rd 1080p monitor but that is unnecessary just to capture the source from the HDMI dongle.
![Screenshot_2023-05-12_07-34-23](https://github.com/DJDevon3/My_Circuit_Python_Projects/assets/49322231/29d07055-537e-43f6-a384-8129e752276b)

### Add Source > Window Capture (National Weather Service Radar browser window)
- Add crop/pad filter 
![Crop-Pad_Background](https://github.com/DJDevon3/My_Circuit_Python_Projects/assets/49322231/870499eb-62a1-434c-86c2-4e4f5e2bf976)

- Using crop/pad it's now cleanly cropped and displaying only the area we want to share
![Crop-Pad_Background_Settings](https://github.com/DJDevon3/My_Circuit_Python_Projects/assets/49322231/4e8607d9-6faf-4cf7-a62b-ef2d321b61b0)

- Add Source > Window Capture (adafruitIO Dashboard browser window)
![AdafruitIO_Capture](https://github.com/DJDevon3/My_Circuit_Python_Projects/assets/49322231/37088f15-fe4d-4c7a-8513-dec5c07d3091)

- Right-click on Source > Blending Mode > Subtract
- This will blend the AdafruitIO dashboard onto the animated radar background
- Blending will change the colors of elements as they'll be blended with the background colors. I've created some additive/subtractive font colors in code.py that might help with blended font colors.
![AdafruitIO_Capture_Blending_Mode](https://github.com/DJDevon3/My_Circuit_Python_Projects/assets/49322231/9f7528a3-b510-42a4-8ff7-9e1b9dc1bf91)

- Also add Blending Mode > Subtract to your HDMI capture (Feather DVI) source
![HDMI_Capture_Blending_Mode](https://github.com/DJDevon3/My_Circuit_Python_Projects/assets/49322231/8b9ccf63-d809-47be-b83e-7fb305cdd3b7)

### 2nd Monitor example:
- This is approximately what your 2nd monitor will look like. 
![Monitor2_Screenshot](https://github.com/DJDevon3/My_Circuit_Python_Projects/assets/49322231/d97c2ac9-bf47-4480-aec9-26e87e68917f)

## Final Output
- This is what it should look like all combined together
- ![Screenshot_2023-05-12_08-27-44](https://github.com/DJDevon3/My_Circuit_Python_Projects/assets/49322231/2623a372-945e-4ac0-979d-1bf3a2b1e796)

This is just a demonstration of using the Feather DVI + HDMI Capture + OBS. 
You can use this method to create practically any combination of data sources you want.
It takes time to manually place elements and text labels using X/Y coordinates. 
DVI/HDMI extends the possibilities of what Circuit Python is capable of heading into the future. 

## Notes
- Please keep in mind the output of the Feather RP2040 DVI is 320x240 then upscaled to 1080p. The upscale is about 4x to 5x the normal output. Fonts will look a little blocky when upscaled.
- The Feather RP2040 DVI doesn't have much RAM left over once it's done processing DVI. It does not work with an Airlift for online capability yet there is simply not enough RAM left over.
- This entire project was a clever work around for the Feather RP2040 DVI not having internet capability.


