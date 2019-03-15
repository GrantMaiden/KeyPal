import sys, time
from keyboardserial import KeyboardSerial

ks = KeyboardSerial()

print("Connecting to serial port on " + sys.argv[1])
ks.connect(sys.argv[1])
if ks.is_connected():
        print("Successfully connected")
start = time.time()
ks.update_leds({'a': 3, 'j': 3, 'f': 3, 'k': 2, 'm': 2, 'v': 4})
end = time.time()
print(end - start)
print(ks.get_sensor_data())
ks.disconnect()
