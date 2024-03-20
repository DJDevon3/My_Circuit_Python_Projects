# Adafruit ATECC Crypto Module Serial Output Only (non-TFT example)
- Prints Serial Number
- Prints Random Value
- Prints Count (bytearray)
- Prints SHA Digest (bytearray)

This example only works prior to locking the chip!  Once the chip is locked it's permanently locked and can never be reconfigured and this script wil not work!

### Code.py Output: (results obfuscated)
```py
ATECC Serial:  0123xxxxxxx
Random Value:  xxxx
ATECC Counter #1 Value:  bytearray(b'xxxxxxxxxxxx')
Appending to the digest...
Appending to the digest...
SHA Digest:  bytearray(b'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')

Code done running.
