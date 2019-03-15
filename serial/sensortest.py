import sys, time, keyboardserial
from keyboardserial import KeyboardSerial

ks = KeyboardSerial()
ks.connect(sys.argv[1])

while (True):
    data = ks.get_sensor_data()
    print(data)   
    time.sleep(0.5)

