# Steam Partner Metrics Display Demo

![vlcsnap-2023-04-01-14h19m02s748](https://user-images.githubusercontent.com/49322231/232206766-70ba77bf-ca96-45cc-a6e1-faad5edabf66.png)


There are 2 different versions of this project.

### CSV Parsing on the Microcontroller
- This example only parses 1 CSV file because a microcontroller cannot handle much data. 
- Uses a task scheduled batch script.
- Required: user logged into Steam Partner portal using MSEdge with the appropriate permissions to download the metric data
- Exports 1 CSV file to the Adafruit Feather ESP32-S2 microcontroller which it then parses (this can take a long time).
- Displays output on alphanumeric display

### CSV Parsing with Python, Export JSON to Microcontroller
- This example downloads & parses 10 CSV files (as a demo). 
- Uses a task scheduled batch script which executes a python CSV parsing script.
- Required: user logged into Steam Partner portal using MSEdge with the appropriate permissions to download the metric data
- Exports a .json file to Adafruit Feather ESP32-S2 microcontroller as a 200 byte file which it can parse instantly.
- Displays output on alphanumeric display
- This is by far the faster and more efficient method.

### Example of Method 2: Python CSV Parsing
[YouTube Demo](https://www.youtube.com/watch?v=sdJcgPCqKFE)
