import tty
import sys
import termios
from keyboardserial import KeyboardSerial

ks = KeyboardSerial()
ks.connect(sys.argv[1])


orig_settings = termios.tcgetattr(sys.stdin)

tty.setraw(sys.stdin)
x = 0
while x != chr(3):
    x=sys.stdin.read(1)[0]
    ks.update_leds({x: 3})

termios.tcsetattr(sys.stdin, termios.TCSADRAIN, orig_settings)
