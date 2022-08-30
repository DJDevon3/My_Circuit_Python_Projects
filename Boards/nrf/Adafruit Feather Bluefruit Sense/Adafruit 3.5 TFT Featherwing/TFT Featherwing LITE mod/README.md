# 3.5" TFT Featherwing LITE Mod

To get display brightness on the TFT Featherwing a hardware modification is necessary. 

Solder the LITE pad to pin D2 with a jumper wire as shown here.

![](https://raw.githubusercontent.com/DJDevon3/CircuitPython/main/TFT%20Featherwing%20LITE%20mod/TFT_Featherwing_LITE_Mod.jpg)

Full Bright (display_duty_cycle = 65000)

![](https://raw.githubusercontent.com/DJDevon3/CircuitPython/main/TFT%20Featherwing%20LITE%20mod/Full_Brightness.png)

Dimmed Display (display_duty_cycle = 600)

![](https://raw.githubusercontent.com/DJDevon3/CircuitPython/main/TFT%20Featherwing%20LITE%20mod/Dimmed_Display.png)

To adjust brightness use this code and adjust the duty cycle. The TFT Featherwing frequency should be left at 500.

```import pwmio
    display_duty_cycle = 10000  # Brightness Values from 0 to 65000
    brightness = pwmio.PWMOut(
            board.D2,
            frequency=500,
            duty_cycle=display_duty_cycle)
