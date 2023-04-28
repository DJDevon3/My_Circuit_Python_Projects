# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT
import board
import gc
import time
import ssl
import socketpool
import wifi
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import feathers2
from adafruit_dps310.basic import DPS310
from adafruit_io.adafruit_io import IO_MQTT

# Make sure the 2nd LDO is turned on
feathers2.enable_LDO2(True)
# Turn on the internal blue LED
feathers2.led_set(True)

i2c = board.I2C()  # uses board.SCL and board.SDA
dps310 = DPS310(i2c)

# Show available memory
print("Memory Info - gc.mem_free()")
print("---------------------------")
print("{} Bytes\n".format(gc.mem_free()))

try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

aio_username = secrets["aio_username"]
aio_key = secrets["aio_key"]

print("Connecting to %s" % secrets["ssid"])
wifi.radio.connect(secrets["ssid"], secrets["password"])
print("Connected to %s!" % secrets["ssid"])

# Define callback functions which will be called when certain events happen.
# pylint: disable=unused-argument
def connected(client):
    # Connected function will be called when the client is connected to Adafruit IO.
    # This is a good place to subscribe to feed changes.  The client parameter
    # passed to this function is the Adafruit IO MQTT client so you can make
    # calls against it easily.
    print("Connected to Adafruit IO!  Listening for DemoFeed changes...")
    # Subscribe to changes on a feed named DemoFeed.
    client.subscribe("DemoFeed")


def subscribe(client, userdata, topic, granted_qos):
    # This method is called when the client subscribes to a new feed.
    print("Subscribed to {0} with QOS level {1}".format(topic, granted_qos))


def unsubscribe(client, userdata, topic, pid):
    # This method is called when the client unsubscribes from a feed.
    print("Unsubscribed from {0} with PID {1}".format(topic, pid))


# pylint: disable=unused-argument
def disconnected(client):
    # Disconnected function will be called when the client disconnects.
    print("Disconnected from Adafruit IO!")


# pylint: disable=unused-argument
def message(client, feed_id, payload):
    # Message function will be called when a subscribed feed has a new value.
    # The feed_id parameter identifies the feed, and the payload parameter has
    # the new value.
    print("Feed {0} received new value: {1}".format(feed_id, payload))


# Create a socket pool
pool = socketpool.SocketPool(wifi.radio)

# Initialize a new MQTT Client object
mqtt_client = MQTT.MQTT(
    broker="io.adafruit.com",
    port=1883,
    username=secrets["aio_username"],
    password=secrets["aio_key"],
    socket_pool=pool,
    ssl_context=ssl.create_default_context(),
)

# Initialize an Adafruit IO MQTT Client
io = IO_MQTT(mqtt_client)

# Connect the callback methods defined above to Adafruit IO
io.on_connect = connected
io.on_disconnect = disconnected
io.on_subscribe = subscribe
io.on_unsubscribe = unsubscribe
io.on_message = message

# Connect to Adafruit IO
print("Connecting to Adafruit IO...")
try:
    io.connect()
except (ValueError, RuntimeError) as e:
    print("Failed to connect, retrying\n", e)

# Below is an example of manually publishing a new value to Adafruit IO.
last = 0
polling_rate = 10

print("Publishing a new message every " + str(polling_rate) + " seconds...\n")
while True:
    temperature = dps310.temperature
    pressure = dps310.pressure

    #print("Temperature = %.2f *F" % (dps310.temperature * 1.8 + 32))
    #print("Pressure = %.2f hPa" % dps310.pressure)

    try:
        io.loop()
    except (MMQTTException) as e:
        print("MQTTException: \n", e)
        time.sleep(300)
        continue
    # Send a new message every 10 seconds.

    if (time.monotonic() - last) >= polling_rate:
        value = temperature * 1.8 + 32
        print("")
        print("Monotonic: ", time.monotonic())
        print("Monotonic Hours: ", time.monotonic()/60/60)
        print("Publishing {0} to DemoFeed.".format(value))
        io.publish("DemoFeed", value)
        last = time.monotonic()
