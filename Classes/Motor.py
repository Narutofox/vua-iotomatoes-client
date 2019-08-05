import time
import RPi.GPIO as GPIO

class Motor():
      
    def __init__(self, pin1, pin2):
        #GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin1, GPIO.OUT)
        GPIO.setup(pin2, GPIO.OUT)
        self.pin1 = pin1
        self.pin2 = pin2
        
    def forward(self):
        GPIO.output(self.pin1, GPIO.HIGH)
        GPIO.output(self.pin2, GPIO.LOW) 
        print("Motor: forward")

    
    def reverse(self):
        GPIO.output(self.pin1, GPIO.LOW)
        GPIO.output(self.pin2, GPIO.HIGH) 
        print("Motor: reverse")
    
    def stop(self):
        GPIO.output(self.pin1, GPIO.LOW)
        GPIO.output(self.pin2, GPIO.LOW) 
        print("Motor: stop") 
        
        
        
        