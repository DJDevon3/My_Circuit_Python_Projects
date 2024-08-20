## Motion Activated Peristaltic Soap Dispenser
- Can also be used for motion activated plant watering

### Hardware:
- [Adafruit ESP32-S3 Feather 4MB Flash 2MB PSRAM](https://www.adafruit.com/product/5477) (Any feather will work, this is what I had laying around)
- [Adafruit DC Motor Featherwing](https://www.adafruit.com/product/2927) (add-on for Feather boards)
- [Adafruit 5V Peristaltic Liquid Pump](https://www.adafruit.com/product/3910)
- [Adafruit PIR Motion Sensor](https://www.adafruit.com/product/189)
- [12V 5A Power Supply](https://www.adafruit.com/product/352)
- [5.5mm x 2.1mm Female Barrel Jack](https://www.amazon.com/UltraPoE-Connector-%EF%BC%8C10pcs-Security-Monitoring/dp/B09XQZ5L6G)

### Software (Circuit Python Libraries):
- adafruit_motorkit

You cannot drive 5V-12V motors from a 3.3V microcontroller alone.

### Motor Featherwing Requires External Power Supply:
- You can drive the motor featherwing with an external 5V, 9V, or 12V power supply rated for at least 1.5 amps.
- A female barrel jack adapter is required to get power to the terminals on the featherwing.

![Motor_FeatherWing](https://github.com/user-attachments/assets/c5faf3c9-ce86-4347-8d9f-8b8e53042343)

### Wiring:
- Feather must be powered separately from the Featherwing, either with a USB cable or 3.7V LiPo
- For motors that require more than 3.3V or 500ma load a dedicated motor driver must be used.
- The Adafruit Motor Featherwing is excellent but also overkill since only 1 motor is used here (it can run up to 4).

![IMG_0072](https://github.com/user-attachments/assets/28b96c72-c33c-4c0f-b874-d79c48edd41e)

## PIR Sensor:
- Sensitivity & Time should be adjusted to their lowest settings
- Sensor FOV is 180 degrees
- Reduce vision of PIR sensor with a housing so it only activates in a small area.

### Advantages:
- Every component is easily replaceable or repairable compared to commercial dispensers
- Easily custom code all dispenser logic with Circuit Python

### Disadvantages:
- Finding a suitable recharageable battery at higher voltages means going with 2S or 3S RC battery (7.2V or 11.1V) and Deans Plug for swapping out batteries.
- There is no easy rechargable solution because this setup requires 2 power sources of different voltages.
- Feather must be 5V USB or 3.7V LiPo powered.
- Feather cannot use power from DC Motor Featherwing.
- This causes a Feather stack, batteries, PIR sensor, and motor to require a much larger enclosure.
