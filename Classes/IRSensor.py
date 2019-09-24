import time
import RPi.GPIO as GPIO

class IRSensor():
	def __init__(self, pin1):
        GPIO.setup(pin, GPIO.IN)
        self.pin = pin
		
	def check(self):
		return GPIO.input(self.pin);