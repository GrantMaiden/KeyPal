import sys, time
from ser.keyboardserial import KeyboardSerial

# python light_keys.py "`cat input.txt`"


def light(char, state):
	if (char == ' '):
		ks.update_leds({'SPACE_LEFT': state})
		ks.update_leds({'SPACE_RIGHT': state})
	else:
		key = KeyboardSerial.KEYS[KeyboardSerial.CHAR_MAP[char]]
		ks.update_leds({key: state})


TARGET = sys.argv[1]
#TARGET = "the quick brown fox jumped over the lazy dog"

ks = KeyboardSerial()

ks.autoconnect()
if ks.is_connected():
    print("Successfully connected")

last = '1'
for c in TARGET.lower():
	light(last, 1)
	light(c, 2)
	last = c
	time.sleep(.2)

light(last, 1)
ks.disconnect()
