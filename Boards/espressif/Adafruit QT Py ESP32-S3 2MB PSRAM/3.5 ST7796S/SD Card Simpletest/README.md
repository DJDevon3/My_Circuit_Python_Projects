### Adafruit QT Py 4mb Flash 2mb PSRAM
- Tests SDCard using built-in sdcardio library
- prints system and sdcard stats
- displays system and sdcard stats on a ST7796S display
- Coded for Circuit Python 8.2.10

Example serial output:
```
Attempting to mount sd card
['System Volume Information']
Board:  Adafruit QT Py ESP32-S3 4MB Flash 2MB PSRAM with ESP32S3
Type:  ESP32S3
Version:  8.2.10 on 2024-02-14


SD Card Info:
===========================
Block Size:  131072
Fragment Size:  131072
Free Blocks:  975802
Free Blocks Unpriv:  975802
Inodes:  0
Free Inodes:  0
Free Inodes Unpriv:  0
Mount Flags:  0
Max Filename Length:  255
Free Space GB:  119.116


SD Card Files:
===========================
System Volume Information/               Size:       0 by
   IndexerVolumeGuid                     Size:      76 by
   WPSettings.dat                        Size:      12 by
```
