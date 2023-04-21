## (Method 2) Windows Task Scheduler, Batch Script, & Python
- This method will use Windows & Python to parse a CSV file for 10 game titles
- It then creates a small JSON file and moves that to the microcontroller for display.

### Create a Scheduled Task
- Setup Triggers (at user logon, scheduled for once every hour)
- Recommend using "Run whether user is logged on or not" and set the password so it runs silently in the background. Otherwise, a black Windows command prompt and MS Edge will launch every hour and take focus no matter what you're doing.

![Task Scheduler Image 1](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/espressif/Adafruit%20Feather%20ESP32-S2/Steam%20Partner%20Metrics%20Display/Method2-Python_Parser/Windows/Downloads/SteamPartner_Python_Metrics/assets/Task_Scheduler1.PNG)

### Set Action to launch batch script
- I designed this to run from the downloads folder.
- You can edit the batch script to download to where you prefer.
- This method is slightly different from Method 1. 
- In actions start parameter put the path to the downloads folder and in Program/Script only put the filename. 
- This ensures it will launch both the batch script and python cleanly as a background task.

![Task Scheduler Image 2](https://raw.githubusercontent.com/DJDevon3/My_Circuit_Python_Projects/main/Boards/espressif/Adafruit%20Feather%20ESP32-S2/Steam%20Partner%20Metrics%20Display/Method2-Python_Parser/Windows/Downloads/SteamPartner_Python_Metrics/assets/Task_Scheduler2.PNG)

### Ensure the PC User and browser (MSEdge) have the following:
- Logged into Steam Partner portal with MSEdge
- Appropriate permissions to download CSV reports from Metrics & Reporting within Steam

The script will continue to refresh the cookie automatically from activity. Steam cookies currently last 48 hours.

### Batch Script Configuration
- Both the batch script and the python file in your downloads folder require minor configuration. Very simple setup.

It should automatically launch the batch script, python, and put the JSON file on the microcontroller. When the microcontroller has a file touched it automatically reboots. That's just the nature of all devices running Circuit Python. It's a very handy feature! For general support with Circuit Python devices, the Adafruit Discord is an excellent place for support in customizing the device to do all sorts of neat things like audio alerts, LED strips, etc... 
