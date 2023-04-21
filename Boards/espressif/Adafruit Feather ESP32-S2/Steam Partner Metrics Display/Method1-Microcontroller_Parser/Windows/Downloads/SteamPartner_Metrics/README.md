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
