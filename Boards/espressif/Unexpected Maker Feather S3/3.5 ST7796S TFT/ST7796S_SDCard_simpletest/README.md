### ST7796S SD Card Simpletest
- Tests the sd card reader built into the ST7796S display
- Shares the same SPI bus as the display so results will be output to the display in repl mode.
- Lists filenames of files on the sdcard.

You'll want to ensure your sdcard has some files on it to display. 

Code.py output:
```py
Attempting to mount sd card
['System Volume Information', 'Astral_Fruit_8bit.bmp', 'vbat_spritesheet.bmp', 'purbokeh_8.bmp']
Board:  FeatherS3 with ESP32S3
Type:  ESP32S3
Version:  8.2.9 on 2023-12-06

Code done running.
```
