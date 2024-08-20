# SPDX-FileCopyrightText: 2024 DJDevon3
# SPDX-License-Identifier: MIT
# Motion Activated Soap Dispenser w/Motor Featherwing
# Coded for CircuitPython 9.1.1

import time
import board
import digitalio
from adafruit_motorkit import MotorKit

PIR_PIN = board.D12  # Pin number connected to PIR sensor output wire.
pir = digitalio.DigitalInOut(PIR_PIN)
pir.direction = digitalio.Direction.INPUT

kit = MotorKit(i2c=board.I2C())
kit.motor1.throttle = 0

cooldown_time = 10   # Cooldown time in seconds
dispense_time = 6    # Time the motor will dispense soap
running = False
cooling_down = False
last_activation_time = 0
print("Waiting for first use...\n")
while True:
    pir_value = pir.value

    # Log current pir_value for debugging
    # print(f"pir_value: {pir_value}, running: {running}, cooling_down: {cooling_down}")

    # Check if we are in cooldown period
    current_time = time.monotonic()  # Use time.monotonic() for time tracking in CircuitPython
    if cooling_down and current_time - last_activation_time < cooldown_time:
        # Stay in cooldown, ignore PIR sensor
        time.sleep(0.1)  # Small sleep to avoid overloading the loop
        continue
    elif cooling_down and current_time - last_activation_time >= cooldown_time:
        # Exit cooldown period
        cooling_down = False
        #print(f"Uptime: {current_time}")
        print("✅ Exit Cooldown, system ready.\n")

    # If PIR detects movement and we're not currently running
    if pir_value and not running and not cooling_down:
        running = True
        print("🧼 Start Dispensing")

        # Gradually increase motor speed
        for i in range(0, 101):
            speed = i * 0.01
            kit.motor1.throttle = speed
            time.sleep(0.01)

        # Gradually decrease motor speed
        for i in range(100, -1, -1):
            speed = i * 0.01
            kit.motor1.throttle = speed
            time.sleep(0.01)

        print("🧼 Stop Dispensing")
        kit.motor1.throttle = 0

        # Delay to simulate dispense time (motor running duration)
        time.sleep(dispense_time)

        # Enter cooldown period
        cooling_down = True
        last_activation_time = current_time
        running = False
        print("Entering cooldown...")

    time.sleep(1)
