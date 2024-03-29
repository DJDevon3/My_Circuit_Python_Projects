# Adafruit ATECC Crypto Module Serial Output Only (non-TFT example)
- Prints Serial Number
- Prints Random Value
- Prints Count (bytearray)
- Prints SHA Digest (bytearray)

Do not lock the chip until you've filled in the configuration details!  Once the eeprom chip is writen it's permanently locked and can never be reconfigured! If you've locked the chip please see the [CSR example here](https://github.com/DJDevon3/My_Circuit_Python_Projects/tree/main/Boards/espressif/Unexpected%20Maker%20Feather%20S3/4.0%20ST7796S/ATECC%20Crypto%20Module%20CSR%20Write).

### Code.py Output: (results obfuscated)
```py
ATECC Serial:  0123xxxxxxx
Random Value:  xxxx
ATECC Counter #1 Value:  bytearray(b'xxxxxxxxxxxx')
Appending to the digest...
Appending to the digest...
SHA Digest:  bytearray(b'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')

Code done running.
