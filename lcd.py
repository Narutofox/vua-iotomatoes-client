import RPi.GPIO as GPIO
from Classes import LiquidCrystalPi
import time as time

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

LCD = LiquidCrystalPi.LCD(29, 31, 33, 35, 37, 38)

LCD.begin(16,4)

time.sleep(0.5)
LCD.write("Hello World")
LCD.nextline()
LCD.write("Hello World")
LCD.nextline()
LCD.write("Hello World")



GPIO.cleanup()
