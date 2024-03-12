### Adafruit ATECC Crypto Module Certificate Signing Request (CSR) Test on TFT Display
Displayed on TFT:
- Serial Number
- Random Value
- Count (bytearray)
- Memory Slot Used
- Country
- State
- City
- Organization
- Department (section)

### Example Output
```py
code.py output:
WE MADE IT OUT OF THE LIBRARY LOOP!
[Errno 19] No such device
ATECC Serial:  000000000000000000
Random Value:  538
ATECC Counter: bytearray(b'\x0f#B\xff')
ATECC Counter ASCII: ['0xf', '0x23', '0x42', '0xff']
ATECC Counter Big Int: 253969151
ATECC Counter Little Int: 4282524431
Generating Certificate Signing Request...
-----BEGIN CERTIFICATE REQUEST-----

MIIBOTCB4AIBADB+MQswCQYDVQQGEwJVUzEQMA4GA1UECBMHRmxvcmlkYTEOMAwGA1UEBxMFTWlhbWkxHzAdBgNVBAoTFlRyZWFzdXJlIENvYXN0IERlc2lnbnMxDzANBgNVBAsTBkNyeXB0bzEbMBkGA1UEAxMSMDAwMDAwMDAwMDAwMDAwMDAwMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEDyNC/////////////////////////////////////////////////////////////////////////////////6AAMAoGCCqGSM49BAMCA0gAMEUCIA8jQv//////////////////////////////////////AiEA//////////////////////////////////////////8=

-----END CERTIFICATE REQUEST-----
```
