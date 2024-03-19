# 3.5" TFT Featherwing LITE Mod

To have display brightness control on the TFT Featherwing a hardware modification is necessary. 

Solder the LITE pad to pin D2 with a jumper wire as shown here.

![](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/nrf/Adafruit%20Feather%20Bluefruit%20Sense/Adafruit%203.5%20TFT%20Featherwing/TFT%20Featherwing%20LITE%20mod/TFT_Featherwing_LITE_Mod.jpg)

Full Bright (display_duty_cycle = 65000)

![](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/nrf/Adafruit%20Feather%20Bluefruit%20Sense/Adafruit%203.5%20TFT%20Featherwing/TFT%20Featherwing%20LITE%20mod/Full_Brightness.png)

Dimmed Display (display_duty_cycle = 600)

![](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/nrf/Adafruit%20Feather%20Bluefruit%20Sense/Adafruit%203.5%20TFT%20Featherwing/TFT%20Featherwing%20LITE%20mod/Dimmed_Display.png)

To adjust brightness use this code and adjust the duty cycle. The TFT Featherwing frequency should be left at 500.

```import pwmio
    display_duty_cycle = 10000  # Brightness Values from 0 to 65000
    brightness = pwmio.PWMOut(
            board.D2,
            frequency=500,
            duty_cycle=display_duty_cycle)
```
- NRF52840 Bluefruit Sense Board
  
![sensors_Feather_Sense_top](https://github.com/DJDevon3/My_Circuit_Python_Projects/assets/49322231/1516c51c-9d57-4b6f-9f6d-e37f4c57b3f2)

Pin D2 only exists in that location on the NRF52840 boards!


- ESP32-S3 Feather
  
![adafruit_products_FESPS3_pinouts](https://github.com/DJDevon3/My_Circuit_Python_Projects/assets/49322231/a47295eb-41e1-4aff-a8e0-2cb06ac70cec)
- On The ESP32-S2/S3 board that physical location for the jumper wire will end up going to DB for Debugging pin which cannot be accessed and does not have PWM!
- You will have to move the jumper wire to a different pin on an ESP32
- If you have an ESP32-S2 or ESP32-S3 I recommend wiring to board.A5 instead. It works well but you will lose board.A5 permanently for other uses.
