import time
import json
import RPi.GPIO as GPIO
import os.path

class Lamp():
    
    path = os.path.dirname(__file__) + '/../data.json'
    
    def __init__(self, pin):
        #GPIO.setmode(GPIO.BCM)
	GPIO.setup(pin, GPIO.OUT)
	self.pin = pin
	self.readJSON()
	
    def readJSON(self):
        with open(self.path) as f:
            self.data = json.load(f)
        
        if 'lamp' not in self.data:
            raise ValueError('No lamp field in json')
        
    
    def writeJSON(self):
        print self.data
        with open(self.path,'w') as f:
            json.dump(self.data, f)
        
    def on(self):
        if self.data['lamp'] == False:
            GPIO.output(self.pin, GPIO.HIGH) #Turn lamp on
	    print("Lamp: ON")
	    self.data['lamp'] = True
	    self.writeJSON()
    
    def off(self):
        if self.data['lamp'] == True:
            GPIO.output(self.pin, GPIO.LOW) #Turn lamp off
	    print("Lamp: OFF")
	    self.data['lamp'] = False
	    self.writeJSON()
    
    def toggle(self):
        if self.data['lamp'] == False:
            self.on()
        else:
            self.off()
        
            
        
        
        
        