import time
import RPi.GPIO as GPIO

class Peltier():
      
    def __init__(self, pin):
        #GPIO.setmode(GPIO.BCM)
	GPIO.setup(pin, GPIO.OUT)
	self.pin = pin     
        
    def on(self):
        GPIO.output(self.pin, GPIO.HIGH) #Turn pelt on
	print("Peltier: ON")

    
    def off(self):
        GPIO.output(self.pin, GPIO.LOW) #Turn pelt off
	print("Peltier: OFF")          
        
        
        
        