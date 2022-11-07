# Circuit Python Candle Flicker Example

https://user-images.githubusercontent.com/49322231/178427246-88e6469e-75fa-4512-9f6b-78dbfa2c0e85.mov

Single-color LED candle flicker with Circuit Python using built-in modules. No external libraries required. 

Highly recommend you use a warm white LED instead of cool white LED it's easier on the eyes.

Code uses randomized voltages (0.0v-3.3v) for light intensity and randomized sleep duration (in milliseconds) to produce the flicker effect  

65535 is the maximum intensity of 3.3 volts and 0 is 0.0 volts to the LED. Range of 0-65535 is equal to 0.0-3.3 volts  

# Required Hardware
- 2-pin LED
- Any Adafruit Microcontroller

Instructions: Attach the shorter leg of the LED to the GND terminal and longer leg to any analog pin usually labeled 
A0, A1, etc..

With the Gemma M0 I'm using GND and pin A0 for 1 LED. To add more LEDs simply add analog_out2 = AnalogOut(board.A1) for example.
