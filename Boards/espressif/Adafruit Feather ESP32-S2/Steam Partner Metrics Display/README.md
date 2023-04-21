# Steam Partner Metrics Display Demo
There are 2 different versions of this project.

### Example of Method 2: Python Parsing
[![YouTubeScreenshot](https://user-images.githubusercontent.com/49322231/233666226-39a74c38-475c-45a7-a338-b4ceaca4aa9e.PNG)](https://www.youtube.com/watch?v=sdJcgPCqKFE)

### (Method 1) CSV Parsing on the Microcontroller
- This example only parses 1 CSV file because a microcontroller cannot handle much data. 
- Uses a task scheduled batch script to download the report
- Required: user logged into Steam Partner portal using MSEdge with the appropriate permissions to download the metric data
- Exports 1 CSV file to the Adafruit Feather ESP32-S2 microcontroller which it then parses (this can take a long time).
- Displays updated data on alphanumeric display

### (Method 2) CSV Parsing with Python, Export JSON to Microcontroller
- This example downloads & parses 10 CSV files (as a demo). 
- Uses a task scheduled batch script to download the reports
- Uses batch script to execute a python CSV parsing script (much faster).
- Required: user logged into Steam Partner portal using MSEdge with the appropriate permissions to download the metric data
- Required: Python installed on the PC with batch script configured to the Python launch location
- Exports a .json file to Adafruit Feather ESP32-S2 microcontroller as a 200 byte file which it can parse instantly.
- Displays updated data on alphanumeric display
- This is by far the faster and more efficient method.

### 3D Printed Enclosure
[Download available on my Printables page](https://www.printables.com/model/443221-adafruit-alphanumeric-backpack-enclosure)
