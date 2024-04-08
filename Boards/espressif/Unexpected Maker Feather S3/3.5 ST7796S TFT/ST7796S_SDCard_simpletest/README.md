### ST7796S SD Card Simpletest (uses built-in sdcardio library)
- Tests the sd card reader built into the ST7796S display
- Shares the same SPI bus as the display so results will be output to the display in repl mode.
- Lists filenames of files on the sdcard

You'll want to ensure your sdcard has some files on it to display. 

Serial example output:
```
Attempting to mount sd card
['System Volume Information']
Board:  FeatherS3 with ESP32S3
Type:  ESP32S3
Version:  9.0.0 on 2024-03-19

🛠️ SD Card Info:
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

💾 SD Card Files:
===========================
System Volume Information/               Size:       0 by
   IndexerVolumeGuid                     Size:      76 by
   WPSettings.dat                        Size:      12 by


Code done running.
```
