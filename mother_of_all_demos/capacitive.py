import sys, time
from ser.keyboardserial import KeyboardSerial

ks = KeyboardSerial()

ks.autoconnect()
if ks.is_connected():
    print("Successfully connected")
		
def threshhold(x):
    if x > 13:
        return 2
    return 1

oldData = {}
while True:
    data = ks.get_sensor_data()
    # DO DATA PROCESSING
    data = list(map(threshhold, data))
    ks.update_leds({'a': data[5], 's': data[1], 'd': data[4], 'f': data[3], 'j': data[0], 'k': data[2], 'l': data[7], ';': data[6]})
    time.sleep(0.01)
	
ks.disconnect()
