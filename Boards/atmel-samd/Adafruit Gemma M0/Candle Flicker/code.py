# SPDX-FileCopyrightText: 2022 DJDevon3 for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""CircuitPython Analog Out Single-Color LED Candle Flicker Example"""
import board
import time
import random
from analogio import AnalogOut

analog_out = AnalogOut(board.A0)

# Manually Set Flicker Type = Breeze or Gust
Flicker_Type = ("Breeze")

Breeze_Low = random.randint(40000, 50000)
Breeze_High = random.randint(50000, 60000)

Gust_Low = random.randint(10000, 50000)
Gust_High = random.randint(50000, 60000)

random_low = random.randint(1000, 50000)
random_high = random.randint(60000, 65535)
rand_sleep = random.uniform(.005, 0.007)
while True:
    if Flicker_Type == ("Breeze"):
        Breeze_Low = random_low
        Breeze_High = random_high
        rand_sleep = random.uniform(.005, 0.007)
    elif Flicker_Type == ("Gust"):
        Gust_Low = random_low
        Gust_High = random_high
        rand_sleep = random.uniform(.01, 0.03)
    else:
        random_low
        random_high
        rand_sleep = random.uniform(.001, 0.003)
        pass
    
    # Random LED Flicker Low/High and Random Sleep Value
    analog_out.value = random.randint(random_low, random_high)
    time.sleep(rand_sleep)
    pass