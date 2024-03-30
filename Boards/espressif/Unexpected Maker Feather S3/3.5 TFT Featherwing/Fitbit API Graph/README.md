## Circuit Python Fitbit API Graph Example

![Cartesian Graph Screenshot](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/espressif/Unexpected%20Maker%20Feather%20S3/3.5%20TFT%20Featherwing/Fitbit%20API%20Graph/screenshots/Relaxing.bmp)
- Past 15 minutes of heart rate data plotted in cartesian graph. Fitbit must be running in the background on a mobile device to relay data to Fitbits server.

Everyone has their own resting heart rate that should be tailored to the individual.  You can do that here:
```py
def bar_color(heart_rate):
    """ Range Mapping with Text Color & Status Output"""
    color_mapping = {
        (float("-inf"), 60): (RED, "Dangerously Low"),
        (60, 75): (BLUE, "Very Low"),
        (75, 85): (LIGHTBLUE, "Sleeping"),
        (85, 95): (CYAN, "Relaxing"),
        (95, 105): (GREEN, "Awake"),
        (105, 120): (YELLOW, "Active"),
        (120, 135): (ORANGE, "Very Active"),
        (135, float("inf")): (MAGENTA, "Exertion"),
    }
    for heart_range, (color, status) in color_mapping.items():
        if heart_range[0] <= heart_rate < heart_range[1]:
            heart_rate_color = color
            activity_status.color = color
            activity_status.text = status
            break
    return heart_rate_color
```

![Grandma Screenshot](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/espressif/Unexpected%20Maker%20Feather%20S3/3.5%20TFT%20Featherwing/Fitbit%20API%20Graph/screenshots/Grandma.bmp)
- Values reset daily at midnight. From midnight to 00:15 there aren't enough values to plot so a wallpaper is used instead. Defaults to wallpaper if the Fitbit app is not running in the background on the mobile device (not updating values). Shows Fitbit logo, notice of not enough values to create a graph, and watch battery charge percentage. The wallpaper is a picture of my mom at a physical rehabilitation facility. The image is an 8-bit indexed bmp (256 colors), please personalize the wallpaper image how you prefer. I'm leaving her wallpaper here so you can see why this project has personal meaning to me.

# Fitbit API Token & Initial Refresh Token walkthrough:
- Step 1: Create a personal app here: https://dev.fitbit.com
- Step 2: Use https://www.fitbit.com as the callback url
- Step 3: Use their Tutorial to get the Token and first Refresh Token
- Fitbit's Tutorial Step 4 is as far as you need to go.
- https://dev.fitbit.com/build/reference/web-api/troubleshooting-guide/oauth2-tutorial/
  
![Fitbit_Tutorial_Walkthrough](https://github.com/DJDevon3/My_Circuit_Python_Projects/assets/49322231/f70ec67f-d06d-4d6f-9823-934fb3936fd9)


- Because I'm using their example salt (PKCE Verifier) & I've already generated a new token after this guide... plus I'm generating a new refresh token every 15 minutes. I'm not the least bit worried about showing these tokens. 

## Serial Output Differences:
- Script is smart enough to know if it's an initial run, manual file save, or automated poll update.

## Initial Run: Serial Output
- The first time you ever run the script.
- The script will detect if it's a first ever provided token.
```py
code.py output:

===============================
Connecting to WiFi...
Connected!

------ FIRST RUN SETTINGS.TOML TOKEN-------
Next token written to NVM Successfully!

Attempting to GET FITBIT Intraday Stats!
===============================
Fitbit Date: 2023-08-07
Fitbit Time: 09:15
Today's Logged Pulses: 553
Latest 15 Minute Averages: 92,95,90,94,90,93,90,94,92,93,91,93,93,91,99
Watch Battery %: 60
Board Uptime: 2.1 days

Finished!
Next Update in: 30 seconds
===============================
```

### Manual Save (Ctrl+S): Serial Output
- During development on file save it will detect the manual intervention and adjust accordingly so you can have faster iterations.
- This avoids the slow progress of having to generate & input a new token into settings.toml every time you want to iterate during development.
```py
Auto-reload is on. Simply save files over USB to run them or enter REPL to disable.
code.py output:

===============================
Connecting to WiFi...
Connected!

------ MANUAL REBOOT TOKEN DIFFERENCE -------
Next token written to NVM Successfully!

Attempting to GET FITBIT Intraday Stats!
===============================
Fitbit Date: 2024-03-30
Fitbit Time: 03:10
Today's Logged Pulses: 188
Latest 15 Minute Averages: [78, 81, 82, 80, 81, 86, 88, 88, 90, 91, 88, 87, 87, 87, 86]
Watch Battery %: 85

Finished!
Board Uptime: 3 hours
Next Update in: 15 minutes
===============================
```
### Indefinite Run: Serial Output
- Automated request attempt. Set sleep_time to 30 seconds for development testing purposes only.
- If you post/request too many attempts you will get temporarily banned. 
- Please set it back to 900 seconds after testing.
- Indefinite run is the end goal to have it work 24/7 without interruption polling every 15 minutes (900 seconds).
```py
===============================
------ INDEFINITE RUN -------
Next token written to NVM Successfully!

Attempting to GET FITBIT Intraday Stats!
===============================
Fitbit Date: 2023-08-07
Fitbit Time: 09:15
Today's Logged Pulses: 553
Latest 15 Minute Averages: 92,95,90,94,90,93,90,94,92,93,91,93,93,91,99
Watch Battery %: 60
Board Uptime: 2.1 days

Finished!
Next Update in: 30 seconds
===============================
```

- SHA-256 Token expires every 8 hours
- SHA-256 Token & Refresh Token only needs to be generated by the tutorial once and copied to settings.toml
- Refresh tokens automatically replace each other updating every 15 minutes.
- The refresh token effectively acts as a "keep alive" token for the main SHA-256 token.
- As long as you continually feed new refresh tokens the SHA-256 token will stay alive indefinitely.
- If you do not make a request at least once every 8 hours you will need to generate new tokens using their tutorial.
  
### microcontroller.nvm token storage
- Settings.toml Refresh token automatically replaced with next refresh token.
- Next refresh token stored in Non-Volatile Memory (NVM)
- NVM token used during the next request (cycle repeats indefinitely).
- NVM token will persist through:
  - hard reset
  - soft reboot
  - entering bootloader mode
    - upgrading or reinstalling Circuit Python UF2! (except for Teensy Boards)
  - exiting bootloader mode

# Fitbit Time (Latest Sync Time)
- Automatically refreshes from the Fitbit Watch to the mobile app every 15 minutes.
- Polling every 1min, 5min, 7min, 10min, with Intraday you'll always return the same data until next Sync.
- 15 minute poll intervals recommended, it's pointless to poll faster.
- If you get temp banned for too many requests, the temp ban is lifted at the top of every hour, this at least helps ensure your token will not expire after 8 hours.
