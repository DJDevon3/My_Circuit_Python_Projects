    import pwmio
    display_duty_cycle = 10000  # Brightness Values from 0 to 65000
    brightness = pwmio.PWMOut(
            board.D2,
            frequency=500,
            duty_cycle=display_duty_cycle)