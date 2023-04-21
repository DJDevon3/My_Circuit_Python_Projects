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
[Downloadable STL files available on my Printables page](https://www.printables.com/model/443221-adafruit-alphanumeric-backpack-enclosure)

### Bill of Materials
- 1 [Adafruit Feather ESP32-S2](https://www.adafruit.com/product/5000) $17.50
- 2 [Adafruit Alphanumeric Display Backpacks](https://www.adafruit.com/product/1912) $14x2
- 1 [150mah Lipo Battery](https://www.adafruit.com/product/1317) $6
- 1 [Mini Latching On/Off Switch](https://www.amazon.com/dp/B086L2GPGX) $11
- 1 [Polymaker Dual-Silk PLA (Blue-Green)](https://www.amazon.com/dp/B0BF55RCF5) $30
- Cost: $92.50
- Total Cost with S&H: $115
