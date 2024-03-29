# Rechargeable BLE Candle
Controlled with Adafruit Connect mobile app by DJDevon3

## Hardware Used:
- [Adafruit ItsyBitsy NRF52840 Express](https://www.adafruit.com/product/4481)
- [Cedar Grove ItsyBitsy Breadboard Adapter](https://github.com/CedarGroveStudios/ItsyBitsyBreadboardAdapter)
- [Adafruit 500mah LiPo battery](https://www.adafruit.com/product/1578)
- [Repurposed dead LED candle from Amazon](https://www.amazon.com/gp/product/B077WT8FKV)
- Common Anode 3mm 4-Pin RGB LED

### Candle Effects
- Solid Color Picker
- Flicker
- Rainbow
- Pulse

![BLE Candle](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/nrf/ItsyBitsy%20NRF52840%20Express/BLE%20Candle/Candle.jpg)

Ignore the wiring colors. They are not indicative of polarity.

![BLE Candle Wiring](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/nrf/ItsyBitsy%20NRF52840%20Express/BLE%20Candle/Candle_Wiring.jpg)

![IMG_0963](https://github.com/DJDevon3/My_Circuit_Python_Projects/assets/49322231/64a7c783-afdc-409b-b8f6-2bb536821ba1)

![IMG_0964](https://github.com/DJDevon3/My_Circuit_Python_Projects/assets/49322231/3f2749fe-e61a-4156-8403-cd54f1c7534c)

![Bluefruit_Connect](https://github.com/DJDevon3/My_Circuit_Python_Projects/assets/49322231/2c49af98-d2c8-4f42-8c47-211fbf07a992)

## Fritzing Wiring Diagram
Not exact because there's no ItsyBitsy NRF52840 or Cedar Grove Adapter Board in their parts database. 

All of the pin names are the same but in different locations.

This uses a 4-pin common anode RGB LED. The annode leg is the longest and should go to 3V.

Switch goes to the EN (enable) pin which will turn the board off regardless if it's battery powered or not. 

Can only recharge battery while on. You can turn LED off during recharging or not, up to you, it has pass-through charging.

![Candle_Fritzing](https://github.com/DJDevon3/My_Circuit_Python_Projects/assets/49322231/b5f15513-a911-4709-99e3-c70a4253f7a0)

The projects in this section are specifically for NRF based boards running Circuit Python.
