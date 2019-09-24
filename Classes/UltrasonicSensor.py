import time
import RPi.GPIO as GPIO

class UltrasonicSensor():
	def __init__(self, triggerPin,echoPin):
        GPIO.setup(triggerPin, GPIO.OUT)
		GPIO.setup(echoPin, GPIO.IN)
        self.triggerPin = triggerPin
		self.echoPin = echoPin
		
	def getDistanceInCentimeters(self):
		GPIO.output(self.triggerPin, False)
		time.sleep(2)
		
		GPIO.output(self.triggerPin, True)
		time.sleep(0.00001)
		GPIO.output(self.triggerPin, False)
		
		while GPIO.input(self.echoPin)==0:
			pulse_start = time.time()
		while GPIO.input(self.echoPin)==1:
			pulse_end = time.time()       
		
		pulse_duration = pulse_end - pulse_start		
		distance = pulse_duration x 17150
		distance = round(distance, 2)
		return distance