from ser.keyboardserial import KeyboardSerial
import sys, time

ks = KeyboardSerial()

RED = 3
GREEN = 2
OFF = 0

def auto_snake():
    while(True):
        snake(GREEN, 1.5)
        time.sleep(.04)
        snake(RED, 1.5, 1)
        time.sleep(.04)

def manual_snake():
    option = int(input("Enter option: "))
    while (option != 9):
        snake(option, 1.5)
        option = int(input("Enter option: "))

def snake(state, seconds, dir = 0):
    delay = seconds / len(ks.KEYS)
    if (dir == 0):
        for i in range(len(ks.KEYS)):
            ks.update_leds({ks.KEYS[i] : state})
            time.sleep(delay)
    else:
        for i in range(len(ks.KEYS)-1, 0, -1):
            ks.update_leds({ks.KEYS[i]: state})
            time.sleep(delay)

def main():
    print("Connecting to serial port on " + sys.argv[1])
    ks.connect(sys.argv[1])
    if ks.is_connected():
        print("Successfully connected")
    else:
        print("Could not connect")
        sys.exit()

    manual_snake()
    #auto_snake()

    ks.disconnect()







if __name__ == '__main__':
    main()


