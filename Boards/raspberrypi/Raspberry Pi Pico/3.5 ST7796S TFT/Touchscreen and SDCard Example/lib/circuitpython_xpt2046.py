"""
XPT2046 Touch module for CircuitPython
Modified by DJDevon3 2024
Modified from xpt2046.py of rdagger/micropython-ili9341
https://github.com/rdagger/micropython-ili9341/blob/master/xpt2046.py
"""
from time import sleep
import digitalio
from adafruit_bus_device.spi_device import SPIDevice

class Touch(object):
    """Serial interface for XPT2046 Touch Screen Controller."""

    # Command bits from xpt2046 datasheet
    # https://grobotronics.com/images/datasheets/xpt2046-datasheet.pdf
    # First start bit always 1 (0b1)
    # Next 3 bits (001) in datasheet page 15
    # Commands are 4 bits
    GET_X = const(0b10010000)  # X position
    GET_Y = const(0b11010000)  # Y position
    GET_Z1 = const(0b10110000)  # Z1 position
    GET_Z2 = const(0b11000000)  # Z2 position
    GET_TEMP0 = const(0b10000000)  # Temperature 0
    GET_TEMP1 = const(0b11110000)  # Temperature 1
    GET_BATTERY = const(0b10100000)  # Battery monitor
    GET_AUX = const(0b11100000)  # Auxiliary input to ADC
    
    """ For interrupt pin support
    def __init__(self, spi, cs, int_pin=None, int_handler=None,
                 width=240, height=320,
                 x_min=100, x_max=1962, y_min=100, y_max=1900):
    """
    
    def __init__(self, spi, cs, width, height, rotation=0,
                 x_min=100, x_max=1996, y_min=100, y_max=1996):
        """Initialize touch screen controller.

        Args:
            spi (Class Spi):  SPI interface for OLED
            cs (Class Pin):  Chip select pin
            int_pin (Class Pin):  Touch controller interrupt pin
            int_handler (function): Handler for screen interrupt
            width (int): Width of LCD screen
            height (int): Height of LCD screen
            x_min (int): Minimum x coordinate
            x_max (int): Maximum x coordinate
            y_min (int): Minimum Y coordinate
            y_max (int): Maximum Y coordinate
        """
        self.spi = spi

        self.cs_io = digitalio.DigitalInOut(cs)
        self.cs_io.direction = digitalio.Direction.OUTPUT
        self.cs_io.value=1
        self.device = SPIDevice(self.spi, self.cs_io)
        
        self.rx_buf = bytearray(3)  # Receive buffer
        self.tx_buf = bytearray(3)  # Transmit buffer
        self.width = width
        self.height = height
        self.rotation = rotation

        # Set calibration
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        
        if self.rotation == 0:
            self.x_multiplier = width / (x_max - x_min)
            self.x_add = x_min * -self.x_multiplier
            self.y_multiplier = height / (y_max - y_min)
            self.y_add = y_min * -self.y_multiplier
        elif self.rotation == 90:
            # Interpolate over different dimensions of the screen             
            self.x_multiplier = height / (x_max - x_min)
            self.x_add = x_min * -self.x_multiplier
            self.y_multiplier = width / (y_max - y_min)
            self.y_add = y_min * -self.y_multiplier
        elif self.rotation == 180:
            # Interpolate over different dimensions of the screen             
            self.x_multiplier = width / (x_max - x_min)
            self.x_add = x_min * -self.x_multiplier
            self.y_multiplier = height / (y_max - y_min)
            self.y_add = y_min * -self.y_multiplier
        
    def get_touch(self):
        """Take multiple samples to get accurate touch reading."""
        timeout = 2  # set timeout to 2 seconds
        confidence = 5
        buff = [[0, 0] for x in range(confidence)]
        buf_length = confidence  # Require a confidence of 5 good samples
        buffptr = 0  # Track current buffer position
        nsamples = 0  # Count samples
        while timeout > 0:
            if nsamples == buf_length:
                meanx = sum([c[0] for c in buff]) // buf_length
                meany = sum([c[1] for c in buff]) // buf_length
                dev = sum([(c[0] - meanx)**2 +
                          (c[1] - meany)**2 for c in buff]) / buf_length
                if dev <= 50:  # Deviation should be under margin of 50
                    return self.normalize(meanx, meany)
            # get a new value
            sample = self.raw_touch()  # get a touch
            if sample is None:
                nsamples = 0    # Invalidate buff
            else:
                buff[buffptr] = sample  # put in buff
                buffptr = (buffptr + 1) % buf_length  # Incr, until rollover
                nsamples = min(nsamples + 1, buf_length)  # Incr. until max

            sleep(.05)
            timeout -= .05
        return None
    
    def normalize(self, x, y):
        """Normalize mean X,Y values to match LCD screen."""
        x = int(self.x_multiplier * x + self.x_add)
        y = int(self.y_multiplier * y + self.y_add)
        return x, y

    def raw_touch(self):
        """Read raw X,Y touch values.

        Returns:
            tuple(int, int): X, Y
        """ 
        # Raw values imply the display is in a factory orientation
        # regardless of rotation register, rotation or size param
        # All x,y,rotation adjustment math is based on these raws factory values
        if self.rotation == 0:
            y = self.send_command(self.GET_X)
            x = self.send_command(self.GET_Y)
        if self.rotation == 180:
            x = self.send_command(self.GET_X)
            y = self.send_command(self.GET_Y)
        # Calibration
#        if x > 0 and x < 2047:
#            if y > 0 and y < 2047:
#                print(x, y)

        if self.x_min <= x <= self.x_max and self.y_min <= y <= self.y_max:
            return (x, y)
        else:
            return None

    def send_command(self, command):
        """Write command to XT2046 (MicroPython).

        Args:
            command (byte): XT2046 command code.
        Returns:
            int: 12 bit response
        """
        self.tx_buf[0] = command

        # Prefer with context from SPIDevice
        with self.device as spi:
            spi.write_readinto(self.tx_buf, self.rx_buf)

        return (self.rx_buf[1] << 4) | (self.rx_buf[2] >> 4)