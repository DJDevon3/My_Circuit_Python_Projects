## Windows Task Scheduler & Batch Script Setup
- This method will use the microcontroller to parse a CSV file for 1 game title

### Create a Scheduled Task
- Setup Triggers (at user logon, scheduled for once every hour)

![Task Scheduler Image 1](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/espressif/Adafruit%20Feather%20ESP32-S2/Steam%20Partner%20Metrics%20Display/Method1-Microcontroller_Parser/Windows/Downloads/SteamPartner_Metrics/assets/TaskScheduler1_CSV.PNG)

### Set Action to launch batch script
- I designed this to run from the downloads folder.
- You can edit the batch script to download to where you prefer.

![Task Scheduler Image 2](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/espressif/Adafruit%20Feather%20ESP32-S2/Steam%20Partner%20Metrics%20Display/Method1-Microcontroller_Parser/Windows/Downloads/SteamPartner_Metrics/assets/TaskScheduler2_CSV.PNG)

### Ensure the PC User and browser (MSEdge) have the following:
- Logged into Steam Partner portal with MSEdge
- Appropriate permissions to download CSV reports from Metrics & Reporting within Steam

The script will continue to refresh the cookie automatically from activity. Steam cookies currently last 48 hours.

### Batch Script Configuration
- There are only 2 lines that should require configuration. 
AppID is the game title you would like to parse the report from.
Ensure you change the drive letter to point at the CIRCUITPY USB device, I use drive H as an example. 

```py
set appID=xxxxxxx
copy C:\Users\%USERNAME%\Downloads\SteamPartner_Metrics\SteamWishlists_GameAppID_all.csv H:\CSV\SteamWishlists_GameAppID_all.csv
```

When the microcontroller has a file touched it automatically reboots. That's just the nature of all devices running Circuit Python. It's a very handy feature! For general support with Circuit Python devices, the Adafruit Discord is an excellent place for support in customizing the device to do all sorts of neat things like audio alerts, LED strips, etc... 
