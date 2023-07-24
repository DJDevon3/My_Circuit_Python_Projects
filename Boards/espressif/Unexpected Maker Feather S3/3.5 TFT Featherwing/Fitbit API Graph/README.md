### Circuit Python Fitbit API Graphing Example

![TFT Featherwing Screenshot](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/espressif/Unexpected%20Maker%20Feather%20S3/3.5%20TFT%20Featherwing/Fitbit%20API%20Graph/screenshot.jpg)

Fitbit API walkthrough for getting API Token & Initial Refresh Token
- Step 1: Create a personal app here: https://dev.fitbit.com
- Step 2: Use their Tutorial to get the Token and first Refresh Token
- Fitbit's Tutorial Step 4 is as far as you need to go.
- https://dev.fitbit.com/build/reference/web-api/troubleshooting-guide/oauth2-tutorial/
  
![Fitbit_Tutorial_Walkthrough](https://github.com/DJDevon3/My_Circuit_Python_Projects/assets/49322231/83e6a90a-069c-4a52-a89b-d58469a96e2c)

- Because I'm using their example salt (PKCE Verifier) & their refresh token expire every 8 hours. I'm not the least bit worried about showing these tokens. 

Code.py Serial Output:
```py
-----Token Refresh POST Attempt -------
Next Refresh Token:  c29ad89203d9d26094b1f4019e4ea6f64f8bc284202e024e8bf98c03d519aa0a

Attempting to GET FITBIT Stats!
===============================
Fitbit Date: 2023-07-24
Fitbit Time: 10:34
Today's Logged Pulses : 635
Latest 15 Minute Averages: 91,87,85,83,84,83,84,84,97,95,87,86,86,87,88
Board Uptime:  2.3 days

Finished!
Next Update in:  15 minutes
===============================
```
To make a change to code.py while keeping refresh token valid
- Copy/paste the next refresh token into settings.toml any time you want to make a change to code.py
- Save settings.toml replacing Next Refresh Token with Initial Refresh Token manually, then immediately save code.py with new changes
- I will be looking for a way to automate this process in the future with file appends.

To run the script forever without making a change to code.py
- Fitbit Token only needs to be generated by the tutorial once and copied to settings.toml
- Refresh tokens automatically replace each other during normal script run updating every 15 minutes forever.