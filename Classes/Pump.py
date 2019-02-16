import RPi.GPIO as GPIO
import time as time

class Pump:
        


	def __init__(self, pin, time=1, actuatorId = 0):
		#GPIO.setmode(GPIO.BCM)
		GPIO.setup(pin, GPIO.OUT)
		self.time = time
		self.pin = pin
		self.actuatorId = actuatorId

	def runPump(self, sec=None):
                if sec is not None:
                    self.time = sec
                self.pump_on()
                time.sleep(self.time)
                self.pump_off()


	def pump_on(self):
		GPIO.output(self.pin, GPIO.HIGH) #Turn pump on
		print("Pump " + str(self.pin) + " is on")


	def pump_off(self):
		GPIO.output(self.pin, GPIO.LOW) #Turn pump off
		print("Pump " + str(self.pin) + " is off")
	
	def clean_gpio(self):
                GPIO.cleanup()
