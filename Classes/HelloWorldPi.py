import RPi.GPIO as GPIO
from LiquidCrystalPi import LiquidCrystalPi
import time as time

# GPIO.setmode(GPIO.BOARD)
# GPIO.setwarnings(False)

class LCDScreen:

    def __init__(self, messages):
        self.messages = messages
        self.LCD = LiquidCrystalPi.LCD(29, 31, 33, 35, 37, 38)
        self.LCD.begin(16, 2)

    def displayMessages(self):
        time.sleep(0.5)

        if len(self.messages) > 4:
            print("To many messages")
            return False

        if len(self.messages) == 1:
            self.LCD.write(self.messages[0])
        else:
            for msg in self.messages:
                self.LCD.write(msg)
                self.LCD.nextline()


    def cleanLCD(self):
        self.LCD.clear()



