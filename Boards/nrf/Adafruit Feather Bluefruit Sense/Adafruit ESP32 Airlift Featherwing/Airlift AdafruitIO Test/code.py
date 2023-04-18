import time
import board
import busio
import displayio
from digitalio import DigitalInOut
import adafruit_bmp280
import adafruit_sht31d
import neopixel
import json
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager
from adafruit_hx8357 import HX8357
displayio.release_displays()

# Should also work for the 2.5" TFT Featherwing, just change the size.
DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 320

i2c = board.I2C()
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)
sht31d = adafruit_sht31d.SHT31D(i2c)
bmp280.sea_level_pressure = bmp280.pressure

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("Secrets File Import Error")
    raise

# Initialize SPI bus
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)

# Initilize ESP32 Airlift on SPI bus
esp32_cs = DigitalInOut(board.D13)
esp32_ready = DigitalInOut(board.D11)
esp32_reset = DigitalInOut(board.D12)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
status_light = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2)
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)

# Initialize TFT Display on SPI bus
tft_cs = board.D9
tft_dc = board.D10
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = HX8357(display_bus, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT)

# Connect to WiFi
print("\n===============================")
print("Connecting to WiFi...")
wifi.connect()
print("Connected!\n")

# Each of your feeds will have an individual feed key
feed_key = "sense-temp"
sleep_time = 8000  # Timeout between Get/Post updates

if (sleep_time) < 60:
    sleep_time_conversion = "seconds"
elif (sleep_time) >= 60 and (sleep_time) < 3600:
    sleep_int = sleep_time / 60
    sleep_time_conversion = "minutes"
elif (sleep_time) >= 3600:
    sleep_int = sleep_time / 60 / 60
    sleep_time_conversion = "hours"
    
print("Connecting to AdafruitIO...")
while True:
    try:
        print("Connected!")
        print("===============================\n")
        print("POST Value...")
        publish = {"value": "{:.1f}".format(bmp280.temperature*1.8+32)}
        post = wifi.post(
            "https://io.adafruit.com/api/v2/"
            + secrets["aio_username"]
            + "/feeds/"
            + feed_key
            + "/data",
            json=publish,
            headers={"X-AIO-KEY": secrets["aio_key"]},
        )
        print(post.json())
        post.close()

        print("\nGET Response...")
        # time.sleep(10)
        get = wifi.get(
            "https://io.adafruit.com/api/v2/"
            + secrets["aio_username"]
            + "/feeds/"
            + feed_key
            + "/data?limit=1",
            json=None,
            headers={"X-AIO-KEY": secrets["aio_key"]},
        )
        array_val = get.json()
        json_str = json.dumps(array_val)
        resp = json.loads(json_str)
        dictionary = resp[0]
        print("Number of Items in Dictionary: ", len(dictionary))
        print(dictionary)
        print("Circuit Python Object Type :", type(dictionary))
        print("Return Single Value! :", dictionary['value'])  # Single Value Return Yay!
        get.close()
        print("\nNext Update in %s %s" % (int(sleep_int), sleep_time_conversion))
        print("\n===============================")
    except (ValueError, RuntimeError) as e:
        print("Failed to get data, retrying\n", e)
        wifi.reset()
        time.sleep(60)
        continue
    response = None
    time.sleep(sleep_time)
